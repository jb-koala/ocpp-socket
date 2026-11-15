#pragma once
#include <Arduino.h>
#include <DNSServer.h>
#include <Preferences.h>
#include <WebServer.h>
#include <WiFi.h>

// ─────────────────────────────────────────────────────────────────────────────
// WiFiProvisioning
//
// Flujo:
//   1. hasCredentials() → false  → startAPMode()
//   2. handleAPLoop() en loop()  → cuando usuario guarda, retorna true
//   3. Llamar ESP.restart() después de que retorne true
//
// Persistencia: Preferences (NVS) — sobrevive reboots y flashes OTA
// ─────────────────────────────────────────────────────────────────────────────
class WiFiProvisioning {
public:
  WiFiProvisioning();

  // ── NVS Credential Helpers ────────────────────────────────────────────────
  bool hasCredentials();
  String getSSID();
  String getPassword();
  String getOcppUrl();
  String getChargePointId();
  float  getSctCalibration();
  bool   getAutocutEnabled();

  void saveCredentials(const String &ssid, const String &password,
                       const String &ocppUrl, const String &cpId,
                       float sctCalibration, bool autocutEnabled);
  void clearCredentials(); // Factory reset

  // ── AP / Captive Portal ───────────────────────────────────────────────────
  void startAPMode();

  // Llamar en loop() cuando isAPMode() == true.
  // Retorna true si acaban de guardarse credenciales → reiniciar
  bool handleAPLoop();

  bool isAPMode() const { return _apMode; }

private:
  Preferences _prefs;
  WebServer _server;
  DNSServer _dns;
  bool _apMode;
  bool _credentialsSaved;

  // Configuración del AP
  static constexpr const char *AP_SSID = "Fluxio-Setup";
  static constexpr const char *AP_PASSWORD = ""; // Red abierta
  static constexpr const char *NVS_NS = "fluxio";

  // Defaults
  static constexpr const char *DEFAULT_OCPP_URL = "ws://72.60.9.174:8080/ws";
  static constexpr const char *DEFAULT_CP_ID = "OCPP-SOCKET-01";
  static constexpr float DEFAULT_SCT_CAL = 47.2f;
  static constexpr bool  DEFAULT_AUTOCUT  = true;

  void _setupRoutes();
  void _handleRoot();
  void _handleSave();
  void _handleCaptiveRedirect();
};
