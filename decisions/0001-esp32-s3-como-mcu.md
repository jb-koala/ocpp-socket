# 0001. Usar ESP32-S3 como microcontrolador principal

- Status: accepted
- Date: 2026-11-15
- Deciders: JB
- Requirements: REQ001, REQ002, REQ007

## Contexto y problema

El socket necesita Wi-Fi, TLS para WebSocket seguro, OTA con rollback y suficiente RAM para una
pila OCPP en JSON. Además queremos un puerto de expansión con SPI/I2C/UART libres.

## Opciones consideradas

1. ESP32 clásico (ya probado en los prototipos actuales)
2. ESP32-S3
3. ESP32-C6 (Wi-Fi 6, RISC-V)
4. STM32 + módulo Wi-Fi externo

## Decisión

Elegimos **ESP32-S3**: mantiene el ecosistema ESP-IDF ya conocido, tiene USB nativo (flash y logs
sin puente serie), más GPIO libres para el puerto de expansión y PSRAM opcional para TLS + JSON.

## Consecuencias

- Buenas: ESP-IDF trae MCP server oficial; OTA y particiones de rollback son estándar.
- Malas: hay que portar lo que esté hecho en ESP32 clásico (bajo riesgo, misma API).
- Qué hay que cambiar en el repo: `firmware/platformio.ini` env `esp32s3`; footprint del módulo en `hw/`.
