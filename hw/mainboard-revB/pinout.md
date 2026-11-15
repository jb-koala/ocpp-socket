# Pinout rev B — ESP32-S3-WROOM-1-N16R8

Fuente de verdad para `firmware/src/board/board_fluxio_revb.h`. Reglas que lo guían:

- **ADC1 solamente** (GPIO1–10) para lo analógico; ADC2 se pelea con el Wi-Fi.
- **Strapping pins** sin carga externa que cambie el nivel en el boot: GPIO0 (BOOT, pull-up), GPIO3,
  GPIO45, GPIO46 quedan sin uso. GPIO19/20 reservados a USB.
- **GPIO26–37 no se usan**: internos a flash/PSRAM octal en el N16R8.
- Donde el devkit de campo usaba un pin para la misma función, se mantiene (GPIO4 botón, GPIO5 relé).
- Todo lo que sale de la placa (expansión, debug) con R serie 33 Ω para ESD/EMI.

| GPIO | Función | Dir | Bloque | Notas |
|---|---|---|---|---|
| 0 | BOOT | in | MCU | Pulsador a GND, pull-up 10 k. Strapping |
| 1 | NTC_SOCKET (ADC1_CH0) | ain | Temperatura | NTC sobre bornes de la toma, REQ003 |
| 2 | NTC_RELAY (ADC1_CH1) | ain | Temperatura | NTC junto a K1 |
| 3 | — | | | Strapping (JTAG), libre |
| 4 | BTN_USER | in | UI | PB1 switch, pull-down 10 k, HIGH = pulsado (igual que devkit) |
| 5 | RELAY_EN | out | Potencia | Driver Q1 → K1. Pull-down 10 k: abierto en boot (igual que devkit) |
| 6 | LOCK_DRV | out | Traba | MOSFET Q5 → solenoide. Pull-down 10 k |
| 7 | LOCK_SENSE | in | Traba | Microswitch de posición, pull-up |
| 8 | EXP_SDA | io | Expansión | I2C0 |
| 9 | EXP_SCL | out | Expansión | I2C0 |
| 10 | EXP_CS | out | Expansión | SPI CS |
| 11 | EXP_MOSI | out | Expansión | SPI (FSPI) |
| 12 | EXP_SCK | out | Expansión | SPI |
| 13 | EXP_MISO | in | Expansión | SPI |
| 14 | EXP_IRQ | in | Expansión | GPIO libre para el módulo (LoRa DIO0, RFID IRQ) |
| 15 | EXP_TX | out | Expansión | UART2 TX |
| 16 | EXP_RX | in | Expansión | UART2 RX |
| 17 | METER_TX | out | Medición | UART1 TX → ATM90E26 RX |
| 18 | METER_RX | in | Medición | UART1 RX ← ATM90E26 TX |
| 19 | USB_D− | io | MCU | USB-C |
| 20 | USB_D+ | io | MCU | USB-C |
| 21 | PWR_FAIL | in | Traba | Detector de caída del riel de 12 V (activo bajo) |
| 38 | LED_R | out | UI | PWM → Q → LED rojo de PB1 |
| 39 | LED_G | out | UI | PWM → Q → LED verde |
| 40 | LED_B | out | UI | PWM → Q → LED azul |
| 41 | BUZZER | out | UI | Q → BZ1 |
| 42 | ESTOP_SENSE | in | Potencia | Estado del botón de emergencia (solo lectura; el corte es por hardware) |
| 43 | TX0 | out | Debug | Header J-DBG + test point |
| 44 | RX0 | in | Debug | Header J-DBG + test point |
| 45 | — | | | Strapping (VDD_SPI), libre |
| 46 | — | | | Strapping (ROM log), libre |
| 47 | EXP_RST | out | Expansión | Reset del módulo |
| 48 | — | | | Libre (en devkit era el NeoPixel; rev B usa PB1 RGB) |
| EN | CHIP_EN | in | MCU | Pulsador a GND + RC 10 k / 1 µF |

## Header de expansión J-EXP (2×8, 2.54 mm)

```
  1  3V3 (fusible 500 mA)   2  12V
  3  GND                    4  GND
  5  EXP_SCK   (12)         6  EXP_MOSI  (11)
  7  EXP_MISO  (13)         8  EXP_CS    (10)
  9  EXP_SDA   (8)         10  EXP_SCL   (9)
 11  EXP_TX    (15)        12  EXP_RX    (16)
 13  EXP_IRQ   (14)        14  EXP_RST   (47)
 15  GND                   16  NC (reservado)
```

Módulos previstos sobre este header: SD (SPI), RFID RC522 (SPI + IRQ + RST), LoRa SX1276 (SPI + IRQ + RST,
alimentado desde 12V con su propio regulador o desde 3V3 si consume < 150 mA), segundo ESP32 (UART).

## Conectores de campo

| Ref | Tipo | Pines | A qué va |
|---|---|---|---|
| TB1 | Bornera 3P 9.5 mm | L, N, PE | Entrada de red |
| J-SKT | Faston 6.3 mm ×3 | L (vía K1), N, PE | Toma SKT1 |
| J-ESTOP | Bornera 2P 5.08 mm | 12V_COIL_IN, 12V_COIL_OUT | Botón de emergencia NC en serie con la bobina |
| J-NTC | JST-XH 2P | NTC, GND | Sensor sobre los bornes de la toma |
| J-LOCK | JST-XH 3P | SOL+, SOL−, SENSE | Solenoide + microswitch |
| J-PB | JST-XH 5P | SW, R, G, B, COM | Pulsador RGB en la tapa |
| J-DBG | Header 1×4 | 3V3, GND, TX0, RX0 | Debug |
| J-USB | USB-C | — | Flash / logs |
| J-EXP | 2×8 | ver arriba | Expansión |

## ATM90E26 — conexiones fijas

| Pin ATM90E26 | Conexión |
|---|---|
| I1P / I1N | Secundario de T1 (ZMCT102) con burden 24 Ω, filtro RC 1 k / 33 nF |
| V1P / V1N | Secundario de TR1 (ZMPT101L) con burden 100 Ω, filtro RC 1 k / 33 nF |
| I2P / I2N | A GND vía 1 k (canal de corriente 2 no usado; o segundo CT en neutro para detección de fuga diferencial en rev C) |
| MMD0 / MMD1 | Según modo UART (ver datasheet) — con jumper de 0 Ω para poder pasar a SPI |
| UART RX / TX | GPIO17 / GPIO18 |
| ZX, CF1, CF2 | Test points (pulsos de energía: sirven para calibrar con un contador de referencia) |
| IRQ, WarnOut | Test points |
| XIN / XOUT | Cristal 16.384 MHz + 2 × 22 pF |
| DVDD / AVDD | 3V3 con 100 nF + 10 µF cada uno |
