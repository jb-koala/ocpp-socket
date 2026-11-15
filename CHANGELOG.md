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

## 2026-11-15 (5) — branch hw/revb-diseno

- decisions: 0005, 0006, 0007 aceptadas por JB; 0009 topología de medición aislada (ATM90E26 + CT/VT).
- hw: `mainboard-revB/README.md` diseño por bloques (10 bloques, qué se conserva de rev A y qué cambia),
  `pinout.md` asignación completa de GPIO del WROOM-1 y conectores, `jlcpcb.kicad_dru` con la barrera de 6.4 mm.
- bom: `mainboard-revB.yml` estimada (~USD 25 China, ~565 g, ~1.2 W en reposo).
- reqs: entrada `mainboard-revB` en `budgets.yml` (650 g, 1.5 W, 40 USD), aprobada por JB.

## 2026-11-15 (7) — branch mech/caja

- mech: caja propia como código (build123d) según el boceto: base, frente con pozo de toma en embudo,
  tapa con bisagra que cierra con la ficha, 2 bisagras, caja de traba (solenoide + Hall, pistón hacia
  abajo), placa adaptadora de toma. Imprimible en FDM sin soportes; STL orientados + STEP.
- mech: 22 tests (interferencias con PCB/toma/ficha/botones, apertura de la tapa a 30/60/95°, junta 25 %,
  recorrido de la traba, cama de impresión, masa vs BOM). Renders en `mechanical/enclosure/renders/`.
- hw: `mainboard-revB/keepouts.md` — zona alta (x 0–65, ≤ 32 mm) / zona baja (x 65–100, ≤ 12 mm), TB1, antena.
- bom: rev B con la caja impresa (370 g, USD 8.1) + tornillería (43 g, USD 2). Total 728 g / USD 33.5.
- decisions: 0011 caja propia impresa en ASA.
- **tests/test_budgets.py falla en masa (728 g > 650 g): decisión pendiente de JB.**
