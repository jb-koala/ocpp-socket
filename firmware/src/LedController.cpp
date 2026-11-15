#include "LedController.h"

LedController::LedController(int pin, int numPixels)
    : _pixels(numPixels, pin, NEO_GRB + NEO_KHZ800), _currentState(LED_NO_WIFI),
      _lastToggle(0), _blinkOn(true) {}

void LedController::begin() {
  _pixels.begin();
  _pixels.setBrightness(60);
  update();
}

void LedController::setState(LedState state) {
  if (_currentState != state) {
    _currentState = state;
    _blinkOn = true;
    _lastToggle = millis();
  }
}

void LedController::_setColor(uint8_t r, uint8_t g, uint8_t b) {
  _pixels.setPixelColor(0, _pixels.Color(r, g, b));
  _pixels.show();
}

void LedController::_blink(uint8_t r, uint8_t g, uint8_t b,
                           unsigned long intervalMs) {
  if (millis() - _lastToggle >= intervalMs) {
    _blinkOn = !_blinkOn;
    _lastToggle = millis();
  }
  _blinkOn ? _setColor(r, g, b) : _setColor(0, 0, 0);
}

void LedController::update() {
  switch (_currentState) {
  case LED_NO_WIFI:
    _setColor(255, 0, 0); // Rojo fijo
    break;

  case LED_AP_MODE:
    _blink(255, 255, 255, 500); // Blanco, parpadeo lento 0.5s
    break;

  case LED_WIFI_NO_OCPP:
    _blink(255, 100, 0, 250); // Naranja parpadeando - Feedback claro
    break;

  case LED_READY:
    _setColor(0, 160, 0); // Verde natural (Equilibrado)
    break;

  case LED_CHARGING:
    _setColor(0, 80, 255); // Azul carga
    break;

  case LED_ERROR:
    _blink(200, 0, 0, 200); // Rojo parpadeo (Error/Reset)
    break;
  }
}
