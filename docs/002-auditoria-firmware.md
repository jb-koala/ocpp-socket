# Auditoría del firmware v1.0.23 (importado 2026-11-15)

Fuente: proyecto Arduino `occp-socket-charger`, 18 commits (jul–nov 2026), 1.031 líneas en el `.ino`
más 3 módulos. Corre en campo desde agosto. Esto es lo que hay que saber antes de tocarlo.

## Lo que está bien y no hay que romper

- **OCPP 1.6-J con MicroOcpp**: Boot, Heartbeat, Start/StopTransaction, Remote Start/Stop, Reset,
  UnlockConnector, MeterValues (Energy, Power, Current, Voltage), **UpdateFirmware** con descarga HTTP
  en streaming a la partición OTA. Esto es lo que vale: 4 meses sin caerse.
- Portal cautivo de provisioning con NVS: SSID, URL del CSMS, ID del punto de carga, calibración del
  sensor, flag de autocorte. Factory reset por botón (5 s), por serial y por `Reset Hard` de OCPP.
- Medición True-RMS de dos pasadas sobre ADC1 (evita la interferencia Wi-Fi del ADC2), calibración por
  unidad en NVS. Energía acumulada histórica en NVS que solo suma.
- Relé en estado seguro (LOW) en `setup()` y solo HIGH mientras `isTransactionActive()`.
- Lecciones documentadas (`firmware/docs/lecciones.md`): particiones OTA, idTag, debounce táctil.

## Hallazgos, por prioridad

### P0 — seguridad / facturación (resolver en Gate 1)

| # | Hallazgo | Dónde | Qué hacer |
|---|---|---|---|
| 1 | **Credenciales embebidas**: SSID y contraseña de una red de laboratorio en el HTML del portal; clave del OTA HTTP en texto plano | `WiFiProvisioning.cpp`, `.ino` | **Hecho al importar**: botón "WiFi Lab" eliminado; clave OTA pasa a `platformio.local.ini` no versionado. La historia git original (en la máquina de JB) todavía las contiene: no subir ese `.git` a ningún remoto |
| 2 | **Sin TLS**: `ws://` al CSMS por IP pública; OTA por HTTP sin verificar firma | `.ino` L19, `setOnDownload` | REQ012: `wss://` con CA en flash, credenciales por dispositivo (BasicAuth OCPP), verificación de hash/firma del `.bin` antes de `Update.end()` |
| 3 | **Umbral de ruido 2 A**: toda corriente < 2 A se reporta como 0 | `SCT_UMBRAL_A` | Una e-bike o e-moto carga a 0.5–1.5 A: **no se factura**. Es el mercado de flotas del deck. Bajar el piso de ruido por hardware (filtro, offset estable) y por software (sustraer RMS de ruido medido en vacío) |
| 4 | **Tensión fija en 220 V**: potencia = I × 220; `Voltage` reportado como constante | `.ino` L666, L916 | Con 100–240 V de entrada (REQ010) el error de energía es de hasta ±10 %. Rev B con IC de medición (0006) lo resuelve; mientras tanto, medir V con el ZMPT101L de la PCB |
| 5 | **Watchdog desactivado** (`esp_task_wdt_deinit()`) | `setup()` | Un cuelgue deja el relé en el estado en que estaba. Reactivar el WDT y alimentarlo en `loop()`; la descarga OTA es el único bloque largo y se puede alimentar adentro |
| 6 | **Dashboard y /status sin autenticación** en puerto 80 y 8266 | `setupOtaServer()` | Exponen IP, SSID, calibración y estado. Mínimo: deshabilitar en producción o pedir clave |

### P1 — robustez

| # | Hallazgo | Qué hacer |
|---|---|---|
| 7 | **`ESP.restart()` al terminar cada sesión** para "liberar el conector" | Es un parche sobre un estado de MicroOcpp que no se resetea. Encontrar la causa (probablemente `setConnectorPluggedInput` siempre `true` + `Finishing`) y sacar el reinicio: en producción, reiniciar entre sesiones mata el log, la conexión y el OTA en curso |
| 8 | `setConnectorPluggedInput` siempre `true` | Conectar al sensor de traba de tapa (REQ006) cuando exista; hoy el CSMS cree que siempre hay cable |
| 9 | `medirIrms()` bloquea 148 ms cada 5 s | Pasar a muestreo por timer/DMA (`adc_continuous`) o a tarea FreeRTOS en el otro core |
| 10 | idTag local hardcodeado (`045740224D6080`) para el botón | Pasar a NVS (lista de tarjetas offline, REQ008) |
| 11 | Energía de sesión integrada cada 1 s con potencia que se actualiza cada 5 s | Integrar en el mismo lugar donde se mide, o guardar timestamp de la última medición |
| 12 | `conectarWiFi()` bloquea hasta 3 ciclos × 15 s + reinicio | Aceptable en boot; en `loop()` deja el relé sin supervisión. Mover a máquina de estados no bloqueante |

### P2 — mantenibilidad

- `LedController` y `RelayController` existen pero el `.ino` no los usa (lección L-005: se desintegraron
  tras un refactor fallido). Reintegrarlos de a uno, con test en hardware entre cada paso.
- `/status` está duplicado en dos servidores (80 y 8266). Un solo servidor.
- `CLAUDE.md` del proyecto original era un prompt genérico de "workflow"; las reglas de este repo lo
  reemplazan (`/CLAUDE.md`). Las lecciones sí se conservaron en `firmware/docs/lecciones.md`.

## Desfasaje firmware ↔ hardware

El firmware apunta al **prototipo en devkit** (`firmware/legacy/MATERIALES-prototipo-devkit.md`):
SCT-013-030 en GPIO6, NeoPixel en GPIO48, módulo relé de 5 V en GPIO5, botón táctil en GPIO4, OLED
I2C en 8/9. La **PCB FLUXIO-PCB-01** tiene otra cosa: ZMCT102 + ZMPT101L (corriente **y tensión**),
relé de 12 V con driver a transistor, pulsador RGB, buzzer, sin OLED, headers P5 (6) y P6 (10).

Hay que confirmar: ¿qué corre hoy en campo, el devkit cableado o la PCB? Si es la PCB, ¿con qué
pinout? Ese pinout tiene que quedar en `hw/mainboard-revA/pinout.md` y el firmware necesita una capa
`board/` (un `.h` por placa) para compilar contra las dos.

## Orden de trabajo sugerido

1. **Compilar en CI** (`pio run -e esp32s3`) sin cambiar nada: línea base.
2. P0-5 (watchdog) y P0-6 (dashboard): chicos, sin riesgo.
3. `board/` con pinout de devkit y de PCB-01; medir tensión real (P0-4).
4. P0-3 (piso de ruido) con bench: medir cargas de 0.3–2 A contra patrón.
5. P1-7 (sacar el `ESP.restart()`), con test en bench de 10 sesiones seguidas.
6. P0-2 (TLS + firma OTA) → entra en REQ012 y en la evaluación de Arduino-como-componente-IDF (0008).
