# Pinout FLUXIO-PCB-01 (rev A) — A COMPLETAR

Fuente de verdad para `firmware/src/board/board_fluxio_pcb01.h`. Cuando se complete, actualizar
el header y sacar el `#error`.

| Función | Componente | GPIO ESP32-S3 | Notas |
|---|---|---|---|
| Relé (driver) | K1 vía Q? | | HIGH = cerrado |
| Corriente (CT) | T1 ZMCT102 → R?/C? | | Debe ser ADC1 (GPIO1–10) |
| Tensión (VT) | TR1 ZMPT101L → R4/R5 | | Debe ser ADC1 |
| Pulsador | PB1 (switch) | | |
| LED R / G / B | PB1 (LED RGB) vía Q? | / / | |
| Buzzer | BZ1 vía Q? | | |
| Reset externo | | | |
| Header P5 (6 pines) | | | ¿qué lleva cada pin? |
| Header P6 (10 pines) | | | expansión: 3V3, 5V, GND, SPI, I2C, UART? |
| Header P7 (2 pines) | | | |
| Fuente 12 V → 5 V | PS1 → U1 7805 | — | |
