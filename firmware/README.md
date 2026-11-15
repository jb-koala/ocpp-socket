# firmware/

ESP-IDF vía PlatformIO, target ESP32-S3 (decisions/0001).

```
lib/session_guard/   lógica pura (sin ESP-IDF): guarda de temperatura (REQ004). limits.h se GENERA desde reqs/budgets.yml
src/                 todo lo que toca hardware: main.c, drivers, Wi-Fi, OCPP transport
test/                tests Unity. Corren en laptop (env native) y en placa (env esp32s3)
scripts/             git_version.py (commit en el build), gen_limits.py (umbrales desde budgets.yml)
```

## Escalera de tests (no se saltan escalones)

1. `pio test -e native` — laptop, solo `lib/`. Corre en CI.
2. `pio test -e esp32s3` — devkit ESP32-S3 por USB, sin potencia conectada.
3. `make bench-test` — placa real en bench (`bench/`), con pytest-embedded esperando `READY`.

## Flashear

`pio run -e esp32s3 -t upload` está **bloqueado por el hook** de `.claude/settings.json`.
Lo corre una persona, con `OCPP_ALLOW_FLASH=1`, después de verificar que el bench está sin tensión de red.
