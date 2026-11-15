// Mainboard rev B (hw/mainboard-revB). Source of truth: hw/mainboard-revB/pinout.md.
// Board not fabricated yet; this header lets the firmware compile against the rev B pin map.
#pragma once

#define BOARD_NAME            "fluxio-revb"

#define PIN_BOOT              0
#define PIN_NTC_SOCKET        1    // ADC1_CH0, NTC on socket terminals (REQ003)
#define PIN_NTC_RELAY         2    // ADC1_CH1, NTC next to K1
#define PIN_BOTON             4    // PB1 switch, INPUT_PULLDOWN, HIGH = pressed
#define PIN_RELAY             5    // Q1 -> K1, HIGH = closed
#define PIN_LOCK_DRV          6    // Q5 -> solenoid
#define PIN_LOCK_SENSE        7    // lid lock microswitch
#define PIN_EXP_SDA           8
#define PIN_EXP_SCL           9
#define PIN_EXP_CS            10
#define PIN_EXP_MOSI          11
#define PIN_EXP_SCK           12
#define PIN_EXP_MISO          13
#define PIN_EXP_IRQ           14
#define PIN_EXP_TX            15
#define PIN_EXP_RX            16
#define PIN_METER_TX          17   // UART1 -> ATM90E26
#define PIN_METER_RX          18
#define PIN_PWR_FAIL          21   // 12 V rail drop detector, active low
#define PIN_LED_R             38
#define PIN_LED_G             39
#define PIN_LED_B             40
#define PIN_BUZZER            41
#define PIN_ESTOP_SENSE       42   // read-only: the cut is in hardware (coil series)
#define PIN_EXP_RST           47

// Compatibility with the current .ino (devkit-era names). Remove as the .ino is refactored.
#define PIN_RESET_EXT         -1   // no external reset button on rev B: use PB1 long press
#define PIN_SCT               -1   // no clamp: current comes from the ATM90E26
#define PIN_LED               -1   // no NeoPixel
#define PIN_I2C_SDA           PIN_EXP_SDA
#define PIN_I2C_SCL           PIN_EXP_SCL

#define BOARD_HAS_OLED        0
#define BOARD_HAS_NEOPIXEL    0
#define BOARD_HAS_VOLTAGE_SENSE 1
#define BOARD_HAS_METER_IC    1
