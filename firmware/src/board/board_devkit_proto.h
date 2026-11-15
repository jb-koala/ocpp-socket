// Prototype on ESP32-S3-DEVKITC-1 N16R8 with external modules (the unit running in the field).
// Source: firmware/legacy/MATERIALES-prototipo-devkit.md and the original .ino pin constants.
#pragma once

#define BOARD_NAME            "devkit-proto"

#define PIN_BOTON             4    // touch sensor, INPUT_PULLDOWN, HIGH = pressed
#define PIN_LED               48   // on-board WS2812 NeoPixel
#define PIN_RELAY             5    // 5 V relay module, HIGH = closed (220 V to socket)
#define PIN_BOOT              0    // on-board BOOT button, INPUT_PULLUP, LOW = pressed
#define PIN_RESET_EXT         7    // external reset button, INPUT_PULLUP

#define PIN_SCT               6    // SCT-013-030 clamp on ADC1_CH5 (never ADC2: Wi-Fi interference)

#define PIN_I2C_SDA           8    // SSD1306 128x32 OLED
#define PIN_I2C_SCL           9

#define BOARD_HAS_OLED        1
#define BOARD_HAS_NEOPIXEL    1
#define BOARD_HAS_VOLTAGE_SENSE 0  // no voltage transformer: firmware assumes 220 V
