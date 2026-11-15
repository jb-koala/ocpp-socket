# firmware/

ESP32-S3 con **framework Arduino + MicroOcpp** (decisions/0008), compilado con PlatformIO.
Es el firmware que corre en campo desde ago-2026 (v1.0.23), importado tal cual el 2026-11-15
desde el proyecto Arduino IDE `occp-socket-charger` (ver `docs/002-auditoria-firmware.md`).

```
src/                 firmware de campo. El .ino lo compila PlatformIO directamente.
  occp-socket-charger.ino   orquestador: setup/loop, OCPP, medición SCT, OTA, dashboard, OLED
  WiFiProvisioning.*        portal cautivo + NVS (credenciales, URL OCPP, calibración)
  LedController.*           NeoPixel por estados (no usado aún por el .ino)
  RelayController.*         relé (no usado aún por el .ino)
  Version.h                 FIRMWARE_VERSION
lib/session_guard/   lógica pura nueva (guarda de temperatura, REQ004). sg_limits.h se GENERA desde reqs/budgets.yml
test/                tests Unity de lib/. Corren en laptop (env native)
docs/                sensado de corriente, OLED, guía de flasheo inicial, lecciones aprendidas
legacy/              BOM del prototipo en devkit y log de referencia de una carga OK
scripts/             git_version.py (commit en el build), gen_limits.py (umbrales desde budgets.yml)
```

## Secretos

No hay credenciales en el código. La clave del OTA HTTP local se pasa por `platformio.local.ini`
(no versionado, ver `.example`). Sin ella, el endpoint `/update` del puerto 8266 queda deshabilitado;
el OTA por OCPP (`UpdateFirmware`) no depende de esa clave.

## Escalera de tests

1. `pio test -e native` — laptop, solo `lib/`. Corre en CI.
2. `pio run -e esp32s3` — build completo (sin flashear). Corre en CI.
3. `pio test -e esp32s3` — devkit por USB, sin potencia conectada.
4. `make bench-test` — placa real en bench, con pytest-embedded esperando `READY`.

## Flashear

`pio run -e esp32s3 -t upload` y `arduino-cli upload` están **bloqueados por el hook** de
`.claude/settings.json`. Los corre una persona con `OCPP_ALLOW_FLASH=1`, con el bench sin tensión
de red. Primer flash por USB; después OTA (docs/guia_flasheo_inicial.md).
