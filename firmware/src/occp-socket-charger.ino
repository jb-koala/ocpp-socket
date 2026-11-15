#include "WiFiProvisioning.h"
#include "esp_task_wdt.h"
#include <Adafruit_NeoPixel.h>
#include <HTTPClient.h>
#include <MicroOcpp.h>
#include <MicroOcpp/Core/Connection.h>
#include <MicroOcpp/Core/Context.h>
#include <MicroOcpp/Model/FirmwareManagement/FirmwareService.h>
#include <Preferences.h>
#include <U8g2lib.h>
#include <Update.h>
#include <WebServer.h>
#include <WiFi.h>
#include <Wire.h>

#include "Version.h"

// Clave del OTA HTTP local (puerto 8266). Se define en build_flags de platformio.ini
// o en un archivo local no versionado; sin definir, el endpoint /update queda deshabilitado.
#ifndef OTA_HTTP_PASS
#define OTA_HTTP_PASS ""
#endif

String globalChargePointId = "OCPP-SOCKET-01";
String globalOcppUrl = "ws://72.60.9.174:8080/ws";
const char *CHARGE_POINT_MODEL = "OCCP Scocket Charger";
const char *CHARGE_POINT_VENDOR = "Fluxio";

WiFiProvisioning provisioning;
Preferences energyPrefs;
WebServer *otaServer = nullptr;
WebServer *dashboardServer = nullptr;

const int PIN_BOTON = 4;
const int PIN_LED = 48;
const int PIN_RELAY = 5;
const int PIN_BOOT = 0; // Botón BOOT onboard — INPUT_PULLUP, LOW = presionado
const int PIN_RESET_EXT = 7; // Pulsador externo para reset — INPUT_PULLUP, conectado a GND
Adafruit_NeoPixel pixels(1, PIN_LED, NEO_GRB + NEO_KHZ800);

// ── SCT-013-030 — Sensor de corriente ────────────────────────────────────
#define PIN_SCT           6       // GPIO6 — ADC1_CH5 (no usar ADC2, interfiere con WiFi)
#define SCT_NUM_MUESTRAS  1480    // ~148ms de captura → ~7 ciclos a 50Hz
#define SCT_UMBRAL_A      2.0    // Umbral de ruido ambiental (A) — suprimir EMI
#define SCT_INTERVAL      5000   // Intervalo entre mediciones (ms)
#define OCPP_TIMEOUT_SIN_CONSUMO  420000 // 7 minutos de inactividad (ms)
float SCT_CALIBRACION = 47.2f;  // Cargado desde NVS al arrancar (default: 47.2)
static uint16_t _sctMuestras[SCT_NUM_MUESTRAS];

int ledEstadoActual = -1;
unsigned long lastHeartbeatPrint = 0;
unsigned long lastMeterUpdate = 0;
unsigned long lastSCTUpdate = 0;
unsigned long ultimoBotonazoAt = 0;
unsigned long ultimoConsumoDetectadoAt = 0; // Timestamp del último consumo activo registrado
bool ocppConectadoAnterior = false;
bool transaccionAnterior = false;
unsigned long autocutAt = 0; // Timestamp del autocut (0 = sin autocut pendiente)
bool autocutEnabled = true;  // Cargado desde NVS — habilita/deshabilita desconexion por inactividad

// ── UpdateFirmware OCPP — estado de descarga e instalación OTA ─────────────
enum class FwDownloadState { Idle, InProgress, Done, Failed };
enum class FwInstallState  { Idle, InProgress, Done, Failed };
static FwDownloadState fwDownloadState = FwDownloadState::Idle;
static FwInstallState  fwInstallState  = FwInstallState::Idle;

// ── Pantalla OLED SSD1306 I2C (128x32) ────────────────────────────────────
// Constructor U8g2 para SSD1306 de 128x32 por hardware I2C, rotación normal (R0)
U8G2_SSD1306_128X32_UNIVISION_F_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE, /* clock=*/ 9, /* data=*/ 8);

unsigned long oledLastActivityAt = 0;    // Timestamp para apagar la pantalla
unsigned long oledLastUpdateAt = 0;      // Timestamp del último renderizado
bool oledPowerOn = true;                 // Estado encendido/apagado de la pantalla
const unsigned long OLED_TIMEOUT_MS = 180000; // 3 minutos de inactividad
const unsigned long OLED_REFRESH_MS = 1000;   // 1 segundo de intervalo de refresco

// Función para despertar la pantalla ante cualquier acción
void despertarOled() {
  oledLastActivityAt = millis();
  if (!oledPowerOn) {
    u8g2.setPowerSave(0); // Encender pantalla
    oledPowerOn = true;
    Serial.println("[OLED] Despertando pantalla por actividad");
  }
}

// ── HTML Dashboard de Monitoreo (Puerto 80) ──────────────────────────────
static const char HTML_DASHBOARD[] PROGMEM = R"rawhtml(
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Fluxio Ev Charger — Monitor</title>
  <style>
    :root {
      --mint: #56cbc4;
      --bg: #f5f7f9;
      --text: #2d3436;
      --sub: #636e72;
      --blue: #0984e3;
      --orange: #e17055;
      --red: #d63031;
    }
    * { margin:0; padding:0; box-sizing:border-box }
    body { min-height:100vh; background:var(--bg); display:flex; align-items:center; justify-content:center; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; padding:20px; color:var(--text) }
    .card { background:#fff; border-radius:24px; padding:40px 28px; width:100%; max-width:440px; box-shadow: 0 15px 35px rgba(0,0,0,0.05); text-align:center }
    .logo { margin-bottom:28px; width:100%; max-width:200px; margin-left:auto; margin-right:auto }
    .logo svg { width:100%; height:auto }
    .status-badge { display:inline-block; padding:8px 16px; border-radius:30px; font-size:13px; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:24px }
    .status-available { background:rgba(86,203,196,0.12); color:var(--mint) }
    .status-charging { background:rgba(9,132,227,0.12); color:var(--blue); animation: pulse 2s infinite }
    .status-error { background:rgba(214,48,49,0.12); color:var(--red) }
    .status-wait { background:rgba(225,112,85,0.12); color:var(--orange) }
    @keyframes pulse {
      0% { opacity: 0.7 }
      50% { opacity: 1 }
      100% { opacity: 0.7 }
    }
    .metrics-grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:24px }
    .metric-box { background:#f8fafc; border:1px solid #edf2f7; border-radius:16px; padding:18px 12px; text-align:center }
    .metric-box.full { grid-column: 1 / span 2 }
    .metric-val { font-size:22px; font-weight:800; color:var(--text); margin-bottom:4px }
    .metric-label { font-size:11px; font-weight:700; color:var(--sub); text-transform:uppercase; letter-spacing:0.5px }
    .system-info { margin-top:24px; padding-top:20px; border-top:1px solid #edf2f7; text-align:left }
    .info-row { display:flex; justify-content:space-between; font-size:13px; margin-bottom:10px }
    .info-lbl { color:var(--sub); font-weight:500 }
    .info-val { color:var(--text); font-weight:600 }
  </style>
</head>
<body>
  <div class="card">
    <div class="logo">
      <img src="https://fluxio.mobi/assets/img/logo-fluxio.png" alt="Fluxio Logo" style="width:100%; max-width:180px; height:auto;">
    </div>
    <div id="status-badge" class="status-badge status-available">Disponible</div>
    
    <div class="metrics-grid">
      <div class="metric-box">
        <div id="power-val" class="metric-val">0.0 kW</div>
        <div class="metric-label">Potencia</div>
      </div>
      <div class="metric-box">
        <div id="current-val" class="metric-val">0.0 A</div>
        <div class="metric-label">Corriente</div>
      </div>
      <div class="metric-box">
        <div id="energy-val" class="metric-val">0.00 kWh</div>
        <div class="metric-label">Energía Sesión</div>
      </div>
      <div class="metric-box">
        <div id="time-val" class="metric-val">00:00:00</div>
        <div class="metric-label">Tiempo Carga</div>
      </div>
      <div class="metric-box full">
        <div id="total-val" class="metric-val">0.00 kWh</div>
        <div class="metric-label">Histórico Acumulado (NVS)</div>
      </div>
      <div class="metric-box full" style="margin-top:-8px; background:#f0faf9; border-color:#d2f4f2;">
        <div id="meter-wh-val" class="metric-val" style="color:#3ba49e;">0 Wh</div>
        <div class="metric-label" style="color:#56cbc4;">Medidor Total (OCPP Wh)</div>
      </div>
    </div>

    <div class="system-info">
      <div class="info-row">
        <span class="info-lbl">Estado del Cargador</span>
        <span id="sys-state" class="info-val">Iniciando...</span>
      </div>
      <div class="info-row">
        <span class="info-lbl">Conexión OCPP</span>
        <span id="sys-ocpp" class="info-val">Buscando...</span>
      </div>
      <div class="info-row">
        <span class="info-lbl">SSID WiFi</span>
        <span id="sys-wifi" class="info-val">...</span>
      </div>
      <div class="info-row">
        <span class="info-lbl">IP del Dispositivo</span>
        <span id="sys-ip" class="info-val">...</span>
      </div>
      <div class="info-row">
        <span class="info-lbl">Calibración SCT</span>
        <span id="sys-sct" class="info-val">...</span>
      </div>
      <div class="info-row">
        <span class="info-lbl">Desconexión por Inactividad</span>
        <span id="sys-autocut" class="info-val">...</span>
      </div>
      <div class="info-row">
        <span class="info-lbl">Firmware Versión</span>
        <span id="sys-fw" class="info-val">__FW_VER__</span>
      </div>
    </div>
  </div>

  <script>
    function updateMetrics() {
      // Usamos el endpoint de status en el mismo puerto 80
      fetch('/status')
        .then(res => res.json())
        .then(data => {
          document.getElementById('sys-fw').textContent = data.firmware;
          document.getElementById('sys-ip').textContent = data.ip;
          document.getElementById('sys-wifi').textContent = data.wifi ? "Conectado" : "Desconectado";
          document.getElementById('sys-ocpp').textContent = data.ocpp_online ? "En línea" : "Desconectado";
          document.getElementById('sys-sct').textContent = data.sct_cal + " A";
          document.getElementById('sys-autocut').textContent = data.autocut_enabled ? "Habilitada (7 min)" : "Deshabilitada";

          // Estado del conector
          const badge = document.getElementById('status-badge');
          const stateTxt = document.getElementById('sys-state');
          badge.className = 'status-badge';

          if (data.transaction_active) {
            badge.textContent = 'Cargando';
            badge.classList.add('status-charging');
            stateTxt.textContent = 'En carga activa';
          } else if (data.wifi && data.ocpp_online) {
            badge.textContent = 'Disponible';
            badge.classList.add('status-available');
            stateTxt.textContent = 'Listo';
          } else if (!data.wifi) {
            badge.textContent = 'Sin Red';
            badge.classList.add('status-error');
            stateTxt.textContent = 'Error WiFi';
          } else {
            badge.textContent = 'Sin Servidor';
            badge.classList.add('status-wait');
            stateTxt.textContent = 'Error Servidor OCPP';
          }

          // Métricas
          document.getElementById('power-val').textContent = (data.potencia_W / 1000.0).toFixed(2) + " kW";
          document.getElementById('current-val').textContent = data.corriente_A.toFixed(2) + " A";
          document.getElementById('energy-val').textContent = data.energia_sesion_kwh.toFixed(4) + " kWh";
          document.getElementById('total-val').textContent = data.energia_total_kwh.toFixed(4) + " kWh";
          document.getElementById('meter-wh-val').textContent = data.meter_wh.toLocaleString('es-AR') + " Wh";

          // Calcular tiempo en base a la sesion
          if (data.transaction_active && data.corriente_A > 0.3) {
            // El tiempo se calcula dinámicamente o se mantiene con reloj en cliente
          }
        })
        .catch(err => console.error("Error al obtener status:", err));
    }
    
    // Cronómetro visual para la sesión en cliente
    let lastActiveSecs = 0;
    setInterval(() => {
      fetch('/status')
        .then(res => res.json())
        .then(data => {
          if (data.transaction_active && data.corriente_A > 0.30) {
            lastActiveSecs++;
            let hr = Math.floor(lastActiveSecs / 3600);
            let min = Math.floor((lastActiveSecs / 60) % 60);
            let sec = lastActiveSecs % 60;
            const pad = (n) => String(n).padStart(2, '0');
            document.getElementById('time-val').textContent = `${pad(hr)}:${pad(min)}:${pad(sec)}`;
          } else {
            lastActiveSecs = 0;
            document.getElementById('time-val').textContent = "00:00:00";
          }
        });
    }, 1000);

    // Actualizar metrics inicial y periódica
    updateMetrics();
    setInterval(updateMetrics, 2000);
  </script>
</body>
</html>
)rawhtml";
float energia_kWh = 0.0;      // Energía de la sesión actual (RAM)
float totalEnergia_kWh = 0.0; // Acumulado histórico (NVS — solo suma, nunca resta)
float potencia_kW = 0.0;      // Medida en tiempo real por SCT-013
float corriente_A  = 0.0;     // Corriente RMS medida (A)
float raw_corriente_A = 0.0;  // Corriente RMS cruda sin filtrar (A)
const unsigned long HEARTBEAT_INTERVAL = 5000;
const unsigned long METER_INTERVAL = 1000;

// ── Medición de corriente RMS con SCT-013 ────────────────────────────────
// Algoritmo de dos pasadas: captura N muestras → calcula media (DC offset) →
// calcula RMS de (muestra - media) → convierte a amperios con factor de calibración.
double medirIrms() {
  long sumaADC = 0;
  for (int i = 0; i < SCT_NUM_MUESTRAS; i++) {
    _sctMuestras[i] = (uint16_t)analogRead(PIN_SCT);
    sumaADC += _sctMuestras[i];
    delayMicroseconds(100);
  }
  double media = (double)sumaADC / SCT_NUM_MUESTRAS;
  double sumaCuadrados = 0.0;
  for (int i = 0; i < SCT_NUM_MUESTRAS; i++) {
    double d = (double)_sctMuestras[i] - media;
    sumaCuadrados += d * d;
  }
  double irms = sqrt(sumaCuadrados / SCT_NUM_MUESTRAS) * (3.3 / 4096.0) * SCT_CALIBRACION;
  raw_corriente_A = (float)irms;
  return (irms < SCT_UMBRAL_A) ? 0.0 : irms;
}

void guardarEnergiaNVS() {
  energyPrefs.begin("fluxio-meter", false);
  energyPrefs.putFloat("total_kwh", totalEnergia_kWh);
  energyPrefs.end();
  Serial.printf("[METER] Guardado en NVS: %.4f kWh\n", totalEnergia_kWh);
}

void cargarEnergiaNVS() {
  energyPrefs.begin("fluxio-meter", true);
  totalEnergia_kWh = energyPrefs.getFloat("total_kwh", 0.0);
  energyPrefs.end();
  Serial.printf("[METER] Acumulado historico desde NVS: %.4f kWh\n", totalEnergia_kWh);
}

bool checkOcppConnection() {
  auto ctx = getOcppContext();
  return (ctx && ctx->getConnection().isConnected());
}

void actualizarLed(int r, int g, int b, int estadoID) {
  if (ledEstadoActual != estadoID) {
    pixels.setPixelColor(0, pixels.Color(r, g, b));
    pixels.show();
    ledEstadoActual = estadoID;
  }
}

void setupOtaServer() {
  otaServer = new WebServer(8266);

  otaServer->on("/", HTTP_GET, []() {
    otaServer->send(200, "text/plain",
      "Fluxio OTA Server\nFirmware: " + String(FIRMWARE_VERSION) +
      "\nIP: " + WiFi.localIP().toString() +
      "\nGET  /status — estado del charger" +
      "\nPOST /update con header X-OTA-Pass");
  });

  otaServer->on("/status", HTTP_GET, []() {
    bool txActive = isTransactionActive();
    String json = "{";
    json += "\"firmware\":\"" + String(FIRMWARE_VERSION) + "\",";
    json += "\"ip\":\"" + WiFi.localIP().toString() + "\",";
    json += "\"wifi\":" + String(WiFi.status() == WL_CONNECTED ? "true" : "false") + ",";
    json += "\"ocpp_online\":" + String(checkOcppConnection() ? "true" : "false") + ",";
    json += "\"sct_cal\":" + String(SCT_CALIBRACION, 1) + ",";
    json += "\"autocut_enabled\":" + String(autocutEnabled ? "true" : "false") + ",";
    json += "\"transaction_active\":" + String(txActive ? "true" : "false") + ",";
    json += "\"energia_sesion_kwh\":" + String(energia_kWh, 4) + ",";
    json += "\"energia_total_kwh\":" + String(totalEnergia_kWh, 4) + ",";
    json += "\"corriente_A\":" + String(corriente_A, 2) + ",";
    json += "\"raw_corriente_A\":" + String(raw_corriente_A, 2) + ",";
    json += "\"potencia_W\":" + String(potencia_kW * 1000.0f, 1) + ",";
    json += "\"meter_wh\":" + String((int)((totalEnergia_kWh + energia_kWh) * 1000));
    json += "}";
    otaServer->send(200, "application/json", json);
  });

  // ── Servidor Dashboard (Puerto 80) ──────────────────────────────────
  dashboardServer = new WebServer(80);

  dashboardServer->on("/", HTTP_GET, []() {
    String page = String(HTML_DASHBOARD);
    page.replace("__FW_VER__", FIRMWARE_VERSION);
    dashboardServer->send(200, "text/html", page);
  });

  // Duplicamos el endpoint /status en el puerto 80 para la consulta AJAX
  dashboardServer->on("/status", HTTP_GET, []() {
    bool txActive = isTransactionActive();
    String json = "{";
    json += "\"firmware\":\"" + String(FIRMWARE_VERSION) + "\",";
    json += "\"ip\":\"" + WiFi.localIP().toString() + "\",";
    json += "\"wifi\":" + String(WiFi.status() == WL_CONNECTED ? "true" : "false") + ",";
    json += "\"ocpp_online\":" + String(checkOcppConnection() ? "true" : "false") + ",";
    json += "\"sct_cal\":" + String(SCT_CALIBRACION, 1) + ",";
    json += "\"autocut_enabled\":" + String(autocutEnabled ? "true" : "false") + ",";
    json += "\"transaction_active\":" + String(txActive ? "true" : "false") + ",";
    json += "\"energia_sesion_kwh\":" + String(energia_kWh, 4) + ",";
    json += "\"energia_total_kwh\":" + String(totalEnergia_kWh, 4) + ",";
    json += "\"corriente_A\":" + String(corriente_A, 2) + ",";
    json += "\"raw_corriente_A\":" + String(raw_corriente_A, 2) + ",";
    json += "\"potencia_W\":" + String(potencia_kW * 1000.0f, 1) + ",";
    json += "\"meter_wh\":" + String((int)((totalEnergia_kWh + energia_kWh) * 1000));
    json += "}";
    dashboardServer->send(200, "application/json", json);
  });

  dashboardServer->begin();
  Serial.println("[DASHBOARD] Servidor web iniciado en puerto 80");

  otaServer->on("/update", HTTP_POST,
    []() {
      bool ok = !Update.hasError();
      otaServer->send(200, "text/plain", ok ? "OK — Reiniciando..." : "ERROR en la actualizacion");
      delay(500);
      ESP.restart();
    },
    []() {
      if (strlen(OTA_HTTP_PASS) == 0 || otaServer->header("X-OTA-Pass") != OTA_HTTP_PASS) {
        otaServer->send(401, "text/plain", "No autorizado");
        return;
      }
      HTTPUpload &upload = otaServer->upload();
      if (upload.status == UPLOAD_FILE_START) {
        Serial.printf("[OTA-HTTP] Recibiendo: %s (%u bytes)\n", upload.filename.c_str(), upload.totalSize);
        Update.begin(UPDATE_SIZE_UNKNOWN);
      } else if (upload.status == UPLOAD_FILE_WRITE) {
        Update.write(upload.buf, upload.currentSize);
      } else if (upload.status == UPLOAD_FILE_END) {
        Update.end(true);
        Serial.printf("[OTA-HTTP] Listo: %u bytes. Reiniciando...\n", upload.totalSize);
      }
    }
  );

  const char *hdrs[] = {"X-OTA-Pass"};
  otaServer->collectHeaders(hdrs, 1);
  otaServer->begin();
  Serial.printf("[OTA-HTTP] Servidor en http://%s:8266/update\n", WiFi.localIP().toString().c_str());
}

void scanWiFiNetworks(const String &targetSSID) {
  Serial.println("[WIFI-SCAN] Escaneando redes disponibles...");
  int n = WiFi.scanNetworks(false, true); // sync, show hidden
  if (n <= 0) {
    Serial.println("[WIFI-SCAN] No se encontraron redes!");
  } else {
    bool found = false;
    Serial.printf("[WIFI-SCAN] %d redes encontradas:\n", n);
    for (int i = 0; i < n; i++) {
      String netSSID = WiFi.SSID(i);
      int32_t rssi = WiFi.RSSI(i);
      wifi_auth_mode_t auth = WiFi.encryptionType(i);
      const char *authStr = "OPEN";
      if (auth == WIFI_AUTH_WPA2_PSK) authStr = "WPA2";
      else if (auth == WIFI_AUTH_WPA3_PSK) authStr = "WPA3";
      else if (auth == WIFI_AUTH_WPA2_WPA3_PSK) authStr = "WPA2/WPA3";
      else if (auth == WIFI_AUTH_WPA_WPA2_PSK) authStr = "WPA/WPA2";
      else if (auth == WIFI_AUTH_WEP) authStr = "WEP";
      
      bool isTarget = netSSID.equals(targetSSID);
      Serial.printf("  %s [%d] %-32s  %ddBm  %s  ch%d\n",
                     isTarget ? ">>>" : "   ", i, netSSID.c_str(),
                     rssi, authStr, WiFi.channel(i));
      if (isTarget) found = true;
    }
    if (!found) {
      Serial.println("[WIFI-SCAN] ⚠ RED OBJETIVO NO ENCONTRADA!");
      Serial.println("[WIFI-SCAN] Posibles causas:");
      Serial.println("  - iPhone Hotspot en 5GHz (activar 'Maximizar Compatibilidad')");
      Serial.println("  - Hotspot apagado o iPhone bloqueado");
      Serial.println("  - SSID mal escrito en el formulario");
    }
  }
  WiFi.scanDelete();
}

// Función auxiliar para esperar de forma interactiva durante la conexión WiFi
// Si el botón de reset se mantiene presionado 5 segundos seguidos, hace factory reset y reinicia.
void verificarBotonResetDuranteEspera(unsigned int ms) {
  unsigned long start = millis();
  static unsigned long bootPressedAt = 0;
  static bool bootHeld = false;

  while (millis() - start < ms) {
    bool isResetPressed = (digitalRead(PIN_BOOT) == LOW || digitalRead(PIN_RESET_EXT) == HIGH);
    
    if (isResetPressed) {
      if (!bootHeld) {
        bootHeld = true;
        bootPressedAt = millis();
        Serial.println("[RESET SETUP] Botón presionado durante espera de conexión...");
      }
      unsigned long heldMs = millis() - bootPressedAt;
      if (heldMs >= 5000) {
        Serial.println("[RESET SETUP] !!! FACTORY RESET WIFI DESDE SETUP !!!");
        provisioning.clearCredentials();
        delay(500);
        ESP.restart();
      }
    } else {
      bootHeld = false;
    }
    delay(50); // Muestreo cada 50ms para no saturar la CPU
  }
}

void conectarWiFi() {
  String ssid = provisioning.getSSID();
  String pass = provisioning.getPassword();
  Serial.printf("[WIFI] Conectando a '%s'...\n", ssid.c_str());

  // ── Compatibilidad con iPhone Hotspot ──────────────────────────────────
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.setSleep(false);

  // ── Diagnóstico: escanear redes visibles ───────────────────────────────
  scanWiFiNetworks(ssid);

  // ── Múltiples ciclos de conexión (iPhone hotspot es inestable) ──────────
  // Ciclo externo: disconnect + reconnect (necesario para iPhone hotspot
  // que puede tardar en empezar a emitir después de que el usuario
  // cierra la pantalla del captive portal)
  const int MAX_CYCLES = 3;
  for (int cycle = 0; cycle < MAX_CYCLES; cycle++) {
    Serial.printf("\n[WIFI] Ciclo de conexión %d/%d\n", cycle + 1, MAX_CYCLES);
    
    WiFi.disconnect(true);
    verificarBotonResetDuranteEspera(1000);
    WiFi.begin(ssid.c_str(), pass.c_str());
    
    int intentos = 0;
    while (WiFi.status() != WL_CONNECTED && intentos < 30) {
      Serial.print(".");
      verificarBotonResetDuranteEspera(500);
      intentos++;
      if (intentos % 10 == 0) {
        int st = WiFi.status();
        Serial.printf("\n[WIFI] Intento %d/30 — Status: %d", intentos, st);
        if (st == 1) Serial.print(" (SSID no encontrado)");
        if (st == 4) Serial.print(" (Auth fallida — ¿WPA3/contraseña?)");
        if (st == 6) Serial.print(" (Desconectado — reintentando)");
        Serial.println();
      }
    }
    
    if (WiFi.status() == WL_CONNECTED) break;
    
    // Entre ciclos: re-escanear para ver si la red apareció
    if (cycle < MAX_CYCLES - 1) {
      Serial.println("\n[WIFI] Fallo. Re-escaneando redes...");
      scanWiFiNetworks(ssid);
    }
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\n[WIFI] ✓ Conectado. IP: %s | RSSI: %ddBm\n",
                  WiFi.localIP().toString().c_str(), WiFi.RSSI());
  } else {
    Serial.println("\n[WIFI] ✗ Fallo al conectar tras 3 ciclos.");
    Serial.println("[WIFI] Reintentando en 15s...");
    Serial.println("[WIFI] (Para factory reset, mantener BOOT 5s)");
    verificarBotonResetDuranteEspera(15000);
    ESP.restart();
  }
}

void setup() {
  Serial.begin(115200);
  unsigned long startSerial = millis();
  while (!Serial && millis() - startSerial < 5000)
    delay(10);

  Serial.println("\n\n==========================================");
  Serial.println("   FLUXIO EV CHARGER - CONTROL REMOTO OK");
  Serial.println("==========================================\n");

  esp_task_wdt_deinit();
  pinMode(PIN_BOTON, INPUT_PULLDOWN);
  pinMode(PIN_RELAY, OUTPUT);
  digitalWrite(PIN_RELAY, LOW);
  pinMode(PIN_BOOT, INPUT_PULLUP);
  pinMode(PIN_RESET_EXT, INPUT_PULLUP);

  analogReadResolution(12);                            // ADC 12-bit (0–4095)
  analogSetPinAttenuation(PIN_SCT, ADC_11db);          // Rango 0–3.3V para SCT-013

  // Iniciar bus I2C en pines 8 y 9
  Wire.begin(8, 9);
  
  // Inicializar pantalla OLED
  u8g2.begin();
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_5x7_tr);
  u8g2.drawStr(10, 20, "Iniciando...");
  u8g2.sendBuffer();
  oledLastActivityAt = millis();

  if (!provisioning.hasCredentials()) {
    Serial.println("[BOOT] Sin credenciales. Iniciando modo AP...");
    pixels.begin();
    pixels.setBrightness(50);
    actualizarLed(255, 255, 255, 99); // Blanco = AP mode
    provisioning.startAPMode();
    return;
  }

  cargarEnergiaNVS();
  conectarWiFi();

  if (WiFi.status() == WL_CONNECTED) {
    globalChargePointId = provisioning.getChargePointId();
    globalOcppUrl = provisioning.getOcppUrl();
    SCT_CALIBRACION = provisioning.getSctCalibration();
    Serial.printf("[SCT] Calibracion cargada desde NVS: %.1f\n", SCT_CALIBRACION);
    autocutEnabled = provisioning.getAutocutEnabled();
    Serial.printf("[AUTOCUT] Desconexion por inactividad: %s\n", autocutEnabled ? "HABILITADA" : "DESHABILITADA");

    // Evitar duplicación del ID del cargador en la URL si el usuario ya lo escribió al final
    String cleanOcppUrl = globalOcppUrl;
    if (cleanOcppUrl.endsWith("/")) {
      cleanOcppUrl = cleanOcppUrl.substring(0, cleanOcppUrl.length() - 1);
    }
    if (cleanOcppUrl.endsWith(globalChargePointId)) {
      int idx = cleanOcppUrl.lastIndexOf(globalChargePointId);
      if (idx > 0 && cleanOcppUrl.charAt(idx - 1) == '/') {
        cleanOcppUrl = cleanOcppUrl.substring(0, idx - 1);
      } else {
        cleanOcppUrl = cleanOcppUrl.substring(0, idx);
      }
    }

    Serial.printf("[OCPP] Conectando a: %s (Base: %s) con ID: %s\n", 
                  globalOcppUrl.c_str(), cleanOcppUrl.c_str(), globalChargePointId.c_str());

    mocpp_initialize(cleanOcppUrl.c_str(), globalChargePointId.c_str(), CHARGE_POINT_MODEL,
                     CHARGE_POINT_VENDOR, FIRMWARE_VERSION);

    // Logs Específicos para el control remoto
    setOnReceiveRequest("RemoteStartTransaction", [](JsonObject payload) {
      Serial.print("[REMOTO] Peticion Start RECIBIDA: ");
      serializeJson(payload, Serial);
      Serial.println();
    });

    setOnReceiveRequest("RemoteStopTransaction", [](JsonObject payload) {
      Serial.print("[REMOTO] Peticion Stop RECIBIDA: ");
      serializeJson(payload, Serial);
      Serial.println();
    });

    // ── Reset OCPP → Factory Reset WiFi ──────────────────────────────────
    // Cuando el servidor envía un Hard Reset, borrar credenciales WiFi
    // para que al reiniciar entre en modo AP y se pueda reconfigurar.
    setOnReceiveRequest("Reset", [](JsonObject payload) {
      String type = payload["type"] | "Soft";
      Serial.printf("[OCPP] Reset '%s' recibido\n", type.c_str());
      if (type == "Hard") {
        Serial.println("[OCPP] Hard Reset → borrando credenciales WiFi...");
        provisioning.clearCredentials();
        Serial.println("[OCPP] Credenciales borradas. Al reiniciar entrará en modo AP.");
      }
    });

    // ── UnlockConnector OCPP → liberar conector + soft reset ─────────────
    setOnUnlockConnectorInOut([]() {
      Serial.println("[OCPP] UnlockConnector solicitado -> Unlocked + programando Soft Reset...");
      autocutAt = millis(); // Reutiliza el mismo mecanismo de reset diferido
      return UnlockConnectorResult_Unlocked;
    });

    // Configuracion de estados criticos
    setConnectorPluggedInput([]() { return true; }); // Simular cable puesto
    setStartTxReadyInput([]() { return true; }); // Siempre listo para empezar
    setStopTxReadyInput([]() { return true; });  // Siempre listo para parar

    setEnergyMeterInput([]() { return (int)((totalEnergia_kWh + energia_kWh) * 1000); });

    // ── MeterValues reales: Potencia (W), Corriente (A), Voltaje (V) ─────
    // Estos valores se envían periódicamente al CPMS durante una transacción
    // según el MeterValueSampleInterval configurado en el servidor.
    setPowerMeterInput([]() { return potencia_kW * 1000.0f; }); // W (float)

    addMeterValueInput([]() -> float { return corriente_A; },
                       "Current.Import", "A", "Outlet", nullptr);

    addMeterValueInput([]() -> float { return 220.0f; },
                       "Voltage", "V", "Outlet", nullptr);

    Serial.println("[OCPP] MeterValues configurados: Energy(Wh) + Power(W) + Current(A) + Voltage(V)");

    // ── UpdateFirmware OCPP — descarga HTTP + flash con Update.h ────────────
    // El CPMS envia UpdateFirmware(url, fecha, reintentos, intervalo).
    // MicroOcpp llama a setOnDownload() cuando llega el momento de descargar.
    // Nosotros descargamos el .bin en streaming directamente a la flash OTA.
    if (auto *fwSvc = getFirmwareService()) {

      // 1. Callback de descarga: recibe la URL, arranca el flash en streaming
      fwSvc->setOnDownload([](const char *location) -> bool {
        Serial.printf("[FW] UpdateFirmware: descargando desde %s\n", location);
        fwDownloadState = FwDownloadState::InProgress;
        fwInstallState  = FwInstallState::Idle;

        HTTPClient http;
        http.begin(location);
        http.setTimeout(30000);
        int httpCode = http.GET();

        if (httpCode != HTTP_CODE_OK) {
          Serial.printf("[FW] Error HTTP %d\n", httpCode);
          http.end();
          fwDownloadState = FwDownloadState::Failed;
          return false;
        }

        int contentLen = http.getSize();
        Serial.printf("[FW] Tamano: %d bytes\n", contentLen);

        if (!Update.begin(contentLen > 0 ? contentLen : UPDATE_SIZE_UNKNOWN)) {
          Serial.printf("[FW] Update.begin fallo: %s\n", Update.errorString());
          http.end();
          fwDownloadState = FwDownloadState::Failed;
          return false;
        }

        WiFiClient *stream = http.getStreamPtr();
        uint8_t buf[512];
        size_t written = 0;
        unsigned long startMs = millis();

        while (http.connected() && (contentLen < 0 || written < (size_t)contentLen)) {
          size_t avail = stream->available();
          if (avail == 0) {
            if (millis() - startMs > 15000) { // timeout 15s sin datos
              Serial.println("[FW] Timeout esperando datos");
              Update.abort();
              http.end();
              fwDownloadState = FwDownloadState::Failed;
              return false;
            }
            delay(1);
            continue;
          }
          startMs = millis();
          size_t toRead = min(avail, sizeof(buf));
          size_t read = stream->readBytes(buf, toRead);
          size_t w = Update.write(buf, read);
          if (w != read) {
            Serial.printf("[FW] Error escritura: %u != %u\n", w, read);
            Update.abort();
            http.end();
            fwDownloadState = FwDownloadState::Failed;
            return false;
          }
          written += w;
        }

        http.end();

        if (!Update.end(true)) {
          Serial.printf("[FW] Update.end fallo: %s\n", Update.errorString());
          fwDownloadState = FwDownloadState::Failed;
          return false;
        }

        Serial.printf("[FW] Descarga e instalacion OK (%u bytes). Reiniciando...\n", written);
        fwDownloadState = FwDownloadState::Done;
        fwInstallState  = FwInstallState::Done;
        return true;
      });

      // 2. MicroOcpp consulta este callback para saber si la descarga terminó
      fwSvc->setDownloadStatusInput([]() -> MicroOcpp::DownloadStatus {
        switch (fwDownloadState) {
          case FwDownloadState::Done:   return MicroOcpp::DownloadStatus::Downloaded;
          case FwDownloadState::Failed: return MicroOcpp::DownloadStatus::DownloadFailed;
          default:                      return MicroOcpp::DownloadStatus::NotDownloaded;
        }
      });

      // 3. Callback de instalacion: el flash ya ocurrio en onDownload, solo reiniciamos
      fwSvc->setOnInstall([](const char *) -> bool {
        Serial.println("[FW] Instalacion completa. Reiniciando en 2s...");
        fwInstallState = FwInstallState::InProgress;
        delay(2000);
        ESP.restart();
        return true;
      });

      // 4. MicroOcpp consulta este callback para saber si la instalacion terminó
      fwSvc->setInstallationStatusInput([]() -> MicroOcpp::InstallationStatus {
        switch (fwInstallState) {
          case FwInstallState::Done:   return MicroOcpp::InstallationStatus::Installed;
          case FwInstallState::Failed: return MicroOcpp::InstallationStatus::InstallationFailed;
          default:                     return MicroOcpp::InstallationStatus::NotInstalled;
        }
      });

      Serial.println("[FW] UpdateFirmware OCPP configurado (HTTP + Update.h)");
    } else {
      Serial.println("[FW] ADVERTENCIA: FirmwareService no disponible");
    }

    Serial.println("[SISTEMA] Escuchando comandos de la web...");
    setupOtaServer();
  }

  pixels.begin();
  pixels.setBrightness(50);
  actualizarLed(255, 0, 0, 0);
}

void loop() {
  // ── Comando Serial: 'C' → factory reset ─────────────────────────────────
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'C' || c == 'c') {
      Serial.println("[SERIAL] Factory reset...");
      provisioning.clearCredentials();
      delay(500);
      ESP.restart();
    }
  }

  // ── Botón BOOT / Pulsador Externo: long press 5s → factory reset WiFi ───────
  static unsigned long bootPressedAt = 0;
  static bool bootHeld = false;
  bool isResetPressed = (digitalRead(PIN_BOOT) == LOW || digitalRead(PIN_RESET_EXT) == HIGH);
  if (isResetPressed) {
    if (!bootHeld) {
      bootHeld = true;
      bootPressedAt = millis();
      Serial.println("[RESET BTN] Presionado (BOOT o Externo)...");
    }
    unsigned long heldMs = millis() - bootPressedAt;
    static unsigned long lastBootPrint = 0;
    if (heldMs >= 2000 && millis() - lastBootPrint >= 1000) {
      Serial.printf("[RESET BTN] Hold: %ds / 5s — suelta para cancelar\n", (int)(heldMs / 1000));
      lastBootPrint = millis();
      actualizarLed(255, 180, 0, 97); // Amarillo = advertencia
      ledEstadoActual = -1;           // Forzar refresco en el próximo ciclo
    }
    if (heldMs >= 5000) {
      Serial.println("[RESET BTN] !!! FACTORY RESET WIFI !!!");
      provisioning.clearCredentials();
      delay(500);
      ESP.restart();
    }
  } else if (bootHeld) {
    bootHeld = false;
    Serial.println("[RESET BTN] Soltado — reset cancelado");
    ledEstadoActual = -1; // Forzar refresco del LED
  }

  // ── Modo AP: manejar portal captive ─────────────────────────────────────
  if (provisioning.isAPMode()) {
    // Parpadeo blanco no bloqueante
    static unsigned long lastBlink = 0;
    static bool blinkOn = false;
    if (millis() - lastBlink > 500) {
      blinkOn = !blinkOn;
      actualizarLed(blinkOn ? 255 : 0, blinkOn ? 255 : 0, blinkOn ? 255 : 0, blinkOn ? 99 : 98);
      lastBlink = millis();
    }

    if (provisioning.handleAPLoop()) {
      Serial.println("[AP] Credenciales guardadas. Reiniciando...");
      delay(3000);
      ESP.restart();
    }

    if (millis() > 600000) {
      Serial.println("[AP] Timeout 10min. Reiniciando...");
      ESP.restart();
    }
    return;
  }

  if (WiFi.status() != WL_CONNECTED) {
    conectarWiFi();
  }

  if (otaServer) otaServer->handleClient();
  if (dashboardServer) dashboardServer->handleClient();
  mocpp_loop();

  // ── Detección de fin de transacción → guardar en NVS + programar Soft Reset ─
  static bool txWasActive = false;
  bool txIsActive = isTransactionActive();

  if (txWasActive && !txIsActive) {
    totalEnergia_kWh += energia_kWh;
    guardarEnergiaNVS();
    Serial.printf("[METER] Sesion finalizada: +%.4f kWh | Total historico: %.4f kWh\n",
                  energia_kWh, totalEnergia_kWh);
    energia_kWh = 0.0;
    // Programar Soft Reset para liberar conector ante cualquier finalización de sesión
    if (autocutAt == 0) {
      autocutAt = millis();
      Serial.println("[TX-END] Sesion finalizada -> programando Soft Reset para liberar conector...");
    }
  }
  txWasActive = txIsActive;

  // Boton Local con debounce de 50ms continuo para filtrar ruidos EMI de conmutación del relé
  static unsigned long botonPresionadoDesde = 0;
  static bool botonPresionadoFiltrado = false;
  
  if (digitalRead(PIN_BOTON) == HIGH) {
    if (botonPresionadoDesde == 0) {
      botonPresionadoDesde = millis();
    } else if (millis() - botonPresionadoDesde >= 50) {
      if (!botonPresionadoFiltrado && (millis() - ultimoBotonazoAt > 1000)) {
        botonPresionadoFiltrado = true;
        ultimoBotonazoAt = millis();
        Serial.println("[BOTON] Touch validado (50ms)");
        
        despertarOled();
        if (!checkOcppConnection()) {
          Serial.println("[ERROR] OCPP No conectado");
        } else if (isTransactionActive()) {
          stopTransaction();
        } else {
          energia_kWh = 0.0;
          startTransaction("045740224D6080");
        }
      }
    }
  } else {
    botonPresionadoDesde = 0;
    botonPresionadoFiltrado = false;
  }

  // ── Medición SCT-013 — cada 5s (148ms bloqueante, ~3% duty cycle) ────────
  if (millis() - lastSCTUpdate >= SCT_INTERVAL) {
    corriente_A = (float)medirIrms();
    potencia_kW = (corriente_A * 220.0f) / 1000.0f;
    lastSCTUpdate = millis();
    Serial.printf("[SCT] %.2f A | %.1f W | %.3f kW\n",
                  corriente_A, corriente_A * 220.0f, potencia_kW);
  }

  // Energia (sesion actual) — acumula con potencia real del sensor
  if (txIsActive && millis() - lastMeterUpdate >= METER_INTERVAL) {
    energia_kWh += (potencia_kW / 3600.0f);
    lastMeterUpdate = millis();
  }

  // ── Soft Reset al finalizar sesión o ante UnlockConnector del CPMS ────────
  // autocutAt se asigna al finalizar cualquier sesión (txWasActive→!txIsActive)
  // o cuando el CPMS envía UnlockConnector. El reset libera el conector y
  // hace que al reconectar se envíe StatusNotification: Available.
  if (autocutAt > 0 && millis() - autocutAt >= 5000) {
    Serial.println("[TX-END] Ejecutando Soft Reset -> conector liberado (StatusNotification:Available)");
    delay(200);
    ESP.restart();
  }

  // Heartbeat
  if (millis() - lastHeartbeatPrint >= HEARTBEAT_INTERVAL) {
    Serial.printf("[ALIVE] WiFi=%s | OCPP=%s | TX=%s | %.2fA | %.2fkW | Sesion=%.4f kWh | Total=%.4f kWh\n",
                  WiFi.status() == WL_CONNECTED ? "OK" : "OFF",
                  checkOcppConnection() ? "ONLINE" : "OFFLINE",
                  txIsActive ? "ACTIVE" : "IDLE",
                  corriente_A, potencia_kW,
                  energia_kWh, totalEnergia_kWh);
    lastHeartbeatPrint = millis();
  }

  // LED + Relay logic
  if (isTransactionActive()) {
    actualizarLed(0, 0, 255, 2);
    digitalWrite(PIN_RELAY, HIGH);
  } else {
    if (WiFi.status() != WL_CONNECTED)
      actualizarLed(255, 0, 0, 0);
    else if (!checkOcppConnection())
      actualizarLed(255, 100, 0, 1);
    else
      actualizarLed(0, 255, 0, 3);
    digitalWrite(PIN_RELAY, LOW);
  }

  // ── Actualización de Pantalla OLED y Salvapantallas ────────────────────
  unsigned long ahora = millis();
  
  // Apagar la pantalla tras tiempo de inactividad (solo si no se está cargando)
  if (oledPowerOn && !txIsActive && (ahora - oledLastActivityAt >= OLED_TIMEOUT_MS)) {
    u8g2.setPowerSave(1); // Apagar pantalla (modo ahorro)
    oledPowerOn = false;
    Serial.println("[OLED] Pantalla apagada por inactividad (Salvapantallas)");
  }

  // Despertar pantalla si empieza una carga
  if (!oledPowerOn && txIsActive) {
    despertarOled();
  }

  // Refrescar contenido de la pantalla cada 1 segundo si está encendida
  if (oledPowerOn && (ahora - oledLastUpdateAt >= OLED_REFRESH_MS)) {
    oledLastUpdateAt = ahora;
    u8g2.clearBuffer();

    if (provisioning.isAPMode()) {
      // MODO CONFIGURACIÓN (AP)
      u8g2.setFont(u8g2_font_6x12_tf);
      u8g2.drawStr(0, 11, "FLUXIO SETUP AP");
      u8g2.drawStr(0, 28, "Web: http://192.168.4.1");
    } else if (WiFi.status() != WL_CONNECTED) {
      // SIN CONEXIÓN WIFI
      u8g2.setFont(u8g2_font_6x12_tf);
      u8g2.drawStr(0, 11, "FLUXIO - SIN RED");
      u8g2.drawStr(0, 28, "Conectando WiFi...");
    } else if (!checkOcppConnection()) {
      // SIN CONEXIÓN OCPP
      u8g2.setFont(u8g2_font_6x12_tf);
      u8g2.drawStr(0, 11, "FLUXIO - ERROR OCPP");
      u8g2.drawStr(0, 28, "Reconectando servidor...");
    } else if (txIsActive) {
      // EN TRANSACCIÓN DE CARGA
      // Línea 1: Potencia y Amperaje
      u8g2.setFont(u8g2_font_7x14_tf); // Fuente mediana
      String powerLine = String(potencia_kW, 1) + "kW  " + String(corriente_A, 1) + "A";
      u8g2.drawStr(0, 13, powerLine.c_str());
      
      // Línea 2: Energía Sesión y Cronómetro
      u8g2.setFont(u8g2_font_6x12_tf);
      String kwhStr = String(energia_kWh, 2) + "kWh";
      u8g2.drawStr(0, 29, kwhStr.c_str());

      // Calcular tiempo transcurrido
      unsigned long sec = (ahora - ultimoConsumoDetectadoAt) / 1000;
      if (corriente_A <= 0.30f) {
        sec = 0; // Si no hay consumo, reiniciar reloj visual
      }
      unsigned long min = (sec / 60) % 60;
      unsigned long hr = sec / 3600;
      char timeBuf[12];
      sprintf(timeBuf, "%02d:%02d:%02d", (int)hr, (int)min, (int)(sec % 60));
      u8g2.drawStr(70, 29, timeBuf);
    } else {
      // DISPONIBLE / REPOSO
      u8g2.setFont(u8g2_font_7x14_tf);
      u8g2.drawStr(0, 13, "FLUXIO CHARGER");
      u8g2.setFont(u8g2_font_6x12_tf);
      u8g2.drawStr(0, 29, "DISPONIBLE - Listo");
    }

    u8g2.sendBuffer();
  }
}

