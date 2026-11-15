# 0008. Mantener Arduino + MicroOcpp, compilado con PlatformIO

- Status: accepted
- Date: 2026-11-15
- Deciders: JB
- Requirements: REQ001, REQ002
- Aclara: 0001 (que asumía ESP-IDF puro en sus consecuencias)

## Contexto y problema

El firmware que corre en campo (v1.0.23, 4 meses en Hubeleon) está escrito con el framework Arduino
para ESP32-S3 y usa MicroOcpp (1.6-J, UpdateFirmware, MeterValues). El esqueleto inicial del repo
asumía ESP-IDF puro. Migrar a ESP-IDF implicaría reescribir OCPP, OTA, portal cautivo y NVS: meses de
trabajo sin valor para el usuario y con riesgo de regresión sobre algo que funciona.

## Opciones consideradas

1. Migrar todo a ESP-IDF puro
2. Mantener Arduino + MicroOcpp, compilar con PlatformIO (reproducible, CI, tests nativos)
3. Arduino como componente de ESP-IDF (híbrido: secure boot, flash encryption e IDF completo, y las libs Arduino siguen)

## Decisión

**Opción 2 ahora**, con la puerta abierta a la 3 cuando toque endurecer seguridad (REQ012: secure
boot, flash encryption, OTA firmada). MicroOcpp es Arduino-first y está probado en campo.

## Consecuencias

- `firmware/platformio.ini`: `framework = arduino`, partición `default_8MB` (dos slots OTA).
- La lógica nueva (guardas, máquina de estados) va a `lib/` sin dependencias de Arduino para
  correr en laptop; el `.ino` queda como orquestador y se va adelgazando de a un módulo por vez
  (lección L-005: nada de refactors big-bang).
- Secure boot y flash encryption se evalúan con la opción 3 en Gate 1.
