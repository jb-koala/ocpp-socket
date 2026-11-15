// Custom mainboard FLUXIO-PCB-01 (hw/mainboard-revA): ZMCT102 + ZMPT101L, 12 V relay with
// transistor driver, RGB pushbutton, buzzer, no OLED.
// PINOUT NOT CONFIRMED YET — see hw/mainboard-revA/pinout.md. Fill in and remove the #error.
#pragma once

#define BOARD_NAME            "fluxio-pcb01"

#error "FLUXIO-PCB-01 pinout not defined yet: fill hw/mainboard-revA/pinout.md and this header"

#define PIN_BOTON             -1   // PB1 RGB pushbutton (switch)
#define PIN_LED_R             -1   // PB1 RGB pushbutton (LED)
#define PIN_LED_G             -1
#define PIN_LED_B             -1
#define PIN_RELAY             -1   // K1 via Qx driver
#define PIN_BOOT              0
#define PIN_RESET_EXT         -1
#define PIN_BUZZER            -1   // BZ1
#define PIN_CT                -1   // T1 ZMCT102 (current), ADC1 only
#define PIN_VT                -1   // TR1 ZMPT101L (voltage), ADC1 only
#define PIN_I2C_SDA           -1   // P6 expansion header
#define PIN_I2C_SCL           -1

#define BOARD_HAS_OLED        0
#define BOARD_HAS_NEOPIXEL    0
#define BOARD_HAS_VOLTAGE_SENSE 1
