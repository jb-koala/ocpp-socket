#include "RelayController.h"

RelayController::RelayController(int pin) : _pin(pin), _enabled(false) {}

void RelayController::begin() {
  pinMode(_pin, OUTPUT);
  digitalWrite(_pin, LOW); // Safe default: relay OFF
  _enabled = false;
  Serial.printf("[RELAY] Inicializado en GPIO %d\n", _pin);
}

void RelayController::enable() {
  if (!_enabled) {
    digitalWrite(_pin, HIGH);
    _enabled = true;
    Serial.println("[RELAY] ON — 220V habilitado al socket");
  }
}

void RelayController::disable() {
  if (_enabled) {
    digitalWrite(_pin, LOW);
    _enabled = false;
    Serial.println("[RELAY] OFF — 220V cortado del socket");
  }
}

bool RelayController::isEnabled() const { return _enabled; }
