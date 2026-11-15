#pragma once
#include <Arduino.h>

// ─────────────────────────────────────────────────────────────────────────────
// RelayController — control del relé de 220V
// GPIO HIGH = relé cerrado = 220V habilitado al socket
// GPIO LOW  = relé abierto = 220V cortado (estado por defecto / seguro)
// ─────────────────────────────────────────────────────────────────────────────
class RelayController {
public:
  explicit RelayController(int pin);

  void begin();
  void enable();  // Cierra relé → 220V al socket
  void disable(); // Abre relé  → 220V cortado (SAFE state)
  bool isEnabled() const;

private:
  int _pin;
  bool _enabled;
};
