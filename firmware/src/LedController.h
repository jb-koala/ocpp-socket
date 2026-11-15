#pragma once
#include <Adafruit_NeoPixel.h>

// ─────────────────────────────────────────────────────────────────────────────
// LedState — todos los estados posibles del sistema
// ─────────────────────────────────────────────────────────────────────────────
enum LedState {
  LED_NO_WIFI,      // 🔴 Rojo fijo     — Sin conexión WiFi
  LED_AP_MODE,      // ⚪ Blanco blink  — Modo configuración (AP)
  LED_WIFI_NO_OCPP, // 🟠 Naranja blink — WiFi OK pero sin OCPP
  LED_READY,        // 🟢 Verde fijo    — Listo para cargar
  LED_CHARGING,     // 🔵 Azul fijo     — Carga activa
  LED_ERROR         // 🟡 Amarillo blink — Error o alerta
};

// ─────────────────────────────────────────────────────────────────────────────
// LedController — maneja el NeoPixel de forma no bloqueante
// ─────────────────────────────────────────────────────────────────────────────
class LedController {
public:
  LedController(int pin, int numPixels = 1);

  void begin();
  void setState(LedState state);
  LedState getState() const { return _currentState; }

  // Llamar en cada iteración del loop() — maneja parpadeos con millis()
  void update();

private:
  Adafruit_NeoPixel _pixels;
  LedState _currentState;
  unsigned long _lastToggle;
  bool _blinkOn;

  void _setColor(uint8_t r, uint8_t g, uint8_t b);
  void _blink(uint8_t r, uint8_t g, uint8_t b, unsigned long intervalMs);
};
