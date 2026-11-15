# Changelog

Formato: fecha, área, qué cambió. Lo más nuevo arriba.

## 2026-11-15

- repo: estructura inicial siguiendo el flujo "AI como ingeniero de hardware"
  (docs → requerimientos → hw → BOM → fab → firmware → bench → logs). Ver README.md.
- reqs: primeros requerimientos (REQ001–REQ008) y presupuestos de masa/potencia/costo.
- decisions: 0001 ESP32-S3, 0002 OCPP 1.6, 0003 corte por temperatura, 0004 traba de tapa (propuesta).
- firmware: esqueleto PlatformIO con env `native` (tests Unity) y `esp32s3` (ESP-IDF).
  `session_guard` (guarda de temperatura) con tests en laptop.
- tests: `test_budgets.py` y `test_bom.py` fallan si se supera un presupuesto o falta un código.

## 2026-11-15 (2)

- bom: BOM real del MVP FLUXIO-PCB-01 transcripta de la planilla (precios China y local).
- reqs: ajustes a la realidad (10 A, 100-240 V, traba con sensor, medición clase 1, TLS/OTA firmada, certificación).
- decisions: 0005 WROOM en placa, 0006 IC de medición, 0007 buck en vez de 7805 (todas propuestas).
- docs: 001-mvp-a-produccion.md con el plan por Gates.

## 2026-11-15 (3)

- fw: importado el firmware de campo v1.0.23 (Arduino + MicroOcpp) a `firmware/src/` tal cual,
  salvo dos credenciales embebidas que se eliminaron (red de laboratorio y clave OTA → `platformio.local.ini`).
- fw: `platformio.ini` pasa a `framework = arduino` con `default_8MB`; se elimina el esqueleto ESP-IDF.
- decisions: 0008 mantener Arduino + MicroOcpp sobre PlatformIO (aclara 0001).
- docs: 002-auditoria-firmware.md con hallazgos P0/P1/P2 y el desfasaje firmware ↔ PCB.
- hook: también bloquea `arduino-cli upload`.

## 2026-11-15 (6) — branch docs/certificacion

- docs: 003-certificacion-y-precompliance.md. La Res. 169/2018 que asumía el deck está derogada:
  rige la Res. SIyC 16/2025 (acepta certificados CB, vigencia 2 años) y para radio la Res. ENACOM 57/2026.
  Clasificación del producto, 14 ensayos de pre-compliance con criterio y equipo, registros posteriores.
- reqs: REQ014 actualizado; REQ015 calentamiento ≤ 45 K; REQ016 aislación reforzada (3 kV, 6.4 mm).
- decisions: 0010 tomacorriente IRAM 2071 vs universal (propuesta).
