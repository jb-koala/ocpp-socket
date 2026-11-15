# OCPP Socket

Toma de carga para vehículos eléctricos con lógica OCPP 1.6 a bordo (ESP32-S3), OTA remota,
sensado de temperatura con corte de sesión, y puerto de expansión (SD / RFID offline / LoRa).

Este README es el **índice**: dice dónde está cada cosa para que una persona o un agente de IA
sepan dónde mirar. Las reglas de trabajo para el agente están en [CLAUDE.md](CLAUDE.md).

## Mapa del repo

| Carpeta / archivo | Qué contiene | Etapa |
|---|---|---|
| [`docs/`](docs/) | Arquitectura (LikeC4), glosario, notas de diseño | 0 |
| [`reqs/`](reqs/) | Requerimientos en [Doorstop](https://doorstop.readthedocs.io) (un YAML por requerimiento) | 1 |
| [`reqs/budgets.yml`](reqs/budgets.yml) | Presupuestos de masa, potencia y costo, con unidades ([pint](https://pint.readthedocs.io)) | 1 |
| [`decisions/`](decisions/) | Decisiones de diseño en formato [MADR](https://adr.github.io/madr/). Una decisión = un archivo. Nunca se edita, se supersede | 1 |
| [`hw/`](hw/) | Electrónica en KiCad 10 (texto plano). Una carpeta por placa y revisión | 3 |
| [`bom/`](bom/) | Lista de materiales con códigos de pedido, masa, potencia y costo por parte | 5 |
| [`fab/`](fab/) | Configuración de KiBot para generar gerbers, BOM y posiciones desde un YAML | 6 |
| [`firmware/`](firmware/) | Firmware ESP-IDF (PlatformIO). Lógica pura en `lib/`, testeable en laptop | 7 |
| [`bench/`](bench/) | Tests en hardware real (pytest-embedded), scripts de flash y de bench | 8 |
| [`data/`](data/) | Corridas registradas (MCAP). No se commitean los archivos grandes | 9 |
| [`tests/`](tests/) | Tests de proyecto (pytest): presupuestos, requerimientos, consistencia | 1, 5 |
| [`versions/`](versions/) | Notas de cada revisión de hardware y de cada release de firmware | — |
| [`CHANGELOG.md`](CHANGELOG.md) | Qué cambió y cuándo | — |

## Cómo verificar el repo

```bash
make check          # pytest (presupuestos + requerimientos) + tests nativos de firmware
make fw-test        # solo tests nativos del firmware (no necesita placa)
make hw-check       # ERC + DRC de todas las placas en hw/ (necesita KiCad 10 instalado)
```

Cada etapa tiene un chequeo determinístico que **falla** si algo está mal. Un cambio que hace fallar
un chequeo no se mergea, se corrige o se cambia el requerimiento (y queda registrado).

## Estado

Ver [`versions/`](versions/) para el estado de cada revisión y [`CHANGELOG.md`](CHANGELOG.md)
para el historial.
