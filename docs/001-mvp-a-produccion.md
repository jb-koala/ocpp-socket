# De MVP a producto escalable

Estado al 2026-11-15. Fuentes: deck Hangar 19 v2.0, BOM FLUXIO-PCB-01, layout de la PCB,
y lo que ya corre en campo (4 meses en Hubeleon, ~340 kWh, 26 sesiones).

## Qué hay hoy (MVP, rev A = FLUXIO-PCB-01)

| Bloque | Como está | Veredicto para producción |
|---|---|---|
| MCU | ESP32-S3-DEVKITC-1 sobre headers | **Cambiar** → módulo WROOM-1 soldado ([0005](../decisions/0005-modulo-wroom-en-placa-en-vez-de-devkit.md)) |
| Fuente | HLK-10M12 (12 V) → 7805 lineal + disipador → LDO del devkit | **Cambiar** → buck 12 V → 3.3 V ([0007](../decisions/0007-alimentacion-buck-en-vez-de-7805.md)) |
| Potencia | Relé SFK112DM 20 A, bobina 12 V; fusible 0.5 A, varistor S07K275, filtro CM 2×10 mH, X1/Y1 | **Mantener.** Sirve para variante 20 A |
| Medición | ZMPT101L + ZMCT102 → ADC, 2-3 % | **Cambiar** → IC dedicado clase 1 ([0006](../decisions/0006-medicion-clase-1-con-ic-dedicado.md)) |
| Entrada | Bornera 3P 9.5 mm con tapa, faston 6.3 mm a la toma | Mantener; revisar creepage en pre-compliance |
| UI | Pulsador RGB QN12, LEDs, buzzer | Mantener |
| Expansión | P6 header 10 pines | Mantener; **documentar pinout** en `hw/mainboard-revA/pinout.md` |
| Traba de tapa | Fuera de la placa; servo hoy | Rev B: solenoide + supercap + sensor ([0004](../decisions/0004-traba-de-tapa-solenoide-supercap.md)) |
| Temperatura en contactos | No existe | **Agregar** en rev B (REQ003/REQ004, Gate 1) |
| Botón de emergencia | No existe | **Agregar** en rev B, en serie con el relé (REQ005, Gate 1) |
| Caja | GENROD IP65 115×165×65 PVC | OK para piloto; tooling propio recién a 1.000+ u |
| Montaje | Mezcla THT (7805, relé, bornera, transformadores) + SMD 1206 | Pasar todo lo posible a SMD para armado en JLCPCB; dejar THT solo donde no hay alternativa (relé, bornera, X/Y) |

## Números

- BOM rev A: **~USD 26 (China) / ~USD 59 (local)** por placa con caja y toma, sin traba ni armado.
  El deck dice "componentes incl. PCB: 100-150". Hay que reconciliar: o el deck cuenta otras cosas
  (traba, cableado, importación, impuestos) o está desactualizado. Esto importa para el margen a USD 300.
- Consumo en reposo estimado: 1.85 W (0.7 W es el 7805). Presupuesto: 2.5 W.
- Masa con caja: ~500 g. Presupuesto: 650 g (margen para traba y supercap).

## Qué significa "escalable" acá

1. **Que cualquiera pueda fabricar la placa sin Gabriel al lado.** → esquemático y layout en KiCad en
   `hw/`, con ERC/DRC a cero y `fab/kibot.yaml` generando gerbers + BOM + posiciones. Hoy el diseño está
   en otra herramienta: el primer trabajo es portarlo (o rehacerlo como rev B directamente en KiCad).
2. **Que cada unidad sea idéntica y trazable.** → número de serie en silkscreen (ya está) + credenciales
   por dispositivo grabadas en efuse en la línea + registro de qué firmware salió en qué unidad.
3. **Que se pueda probar cada unidad en minutos.** → fixture de fin de línea (EOL): pogo pins sobre
   test points, script que flashea, lee el commit, verifica Wi-Fi, mide tensión/corriente contra
   referencia y cierra/abre el relé. `bench/` es el embrión de eso.
4. **Que el firmware se pueda actualizar sin miedo.** → OTA firmada, rollback, y la escalera de tests
   (laptop → devkit → bench) corriendo en CI antes de cada release.
5. **Que pase una auditoría.** → pre-compliance antes de IRAM: creepage/clearance, ensayo térmico a
   10 A continuos, EMC. Lo que falle vuelve como requerimiento.

## Plan por Gate (del deck) traducido a trabajo en este repo

### Gate 1 · meses 0-3 · design freeze

| # | Trabajo | Dónde queda | Chequeo |
|---|---|---|---|
| 1 | Portar el firmware actual a este repo; separar lógica pura (`lib/`) de hardware (`src/`) | `firmware/` | `make fw-test` en CI |
| 2 | Esquemático rev A en KiCad tal cual está (as-built), con códigos LCSC | `hw/mainboard-revA/` | `make hw-check` |
| 3 | Decidir 0004-0007 (traba, módulo, medición, fuente) | `decisions/` | — |
| 4 | Rev B en KiCad: WROOM + buck + IC medición + NTC + e-stop + driver de traba | `hw/mainboard-revB/` | ERC/DRC = 0, `pytest` presupuestos |
| 5 | Firmware: guarda de temperatura (`session_guard`, ya existe), sensor de traba, e-stop, driver del IC de medición | `firmware/lib`, `firmware/src` | tests nativos + bench |
| 6 | Seguridad: TLS + credenciales por dispositivo, OTA firmada, secure boot | `firmware/`, `docs/` | bench: imagen sin firmar rechazada |
| 7 | Modo flota offline: lista RFID + log en SD por el puerto de expansión | `firmware/`, `hw/expansion-rfid-sd/` | bench sin Wi-Fi |
| 8 | 5 placas rev B armadas en JLCPCB; bench térmico 10 A continuos; pre-compliance | `bench/`, `data/runs/`, `versions/` | reporte en `versions/hw-mainboard-revB.md` |
| 9 | Matriz de prueba cargadores Mode 2 × vehículos | `docs/`, `data/` | tabla con resultado por combinación |

**Salida del Gate:** rev B pasa pre-compliance; todos los chequeos del repo en verde.

### Gate 2 · meses 3-6 · piloto certificado

- 50 unidades: BOM congelada, `fab/` genera el pedido, fixture EOL en `bench/eol/`.
- Certificación presentada a IRAM (CB) + ENACOM del módulo.
- 5-10 unidades en IPT (Líbano) y primeros hosts en Buenos Aires, todas reportando a `data/`.

### Gate 3 · meses 6-9 · lanzamiento

- Primeras 500: cotización a 1.000 u (hoy "pending" en el deck) con la BOM de rev B.
- Tooling de caja solo si el volumen lo justifica.

## Primer sprint sugerido (2 semanas)

1. Subir el código actual del ESP32 a `firmware/` sin modificar (commit "as-is").
2. Subir esquemático y layout actuales (el formato que sea) a `hw/mainboard-revA/source-original/`,
   y empezar el port a KiCad.
3. Resolver las decisiones 0005/0006/0007 con Gabriel: son las tres que definen rev B.
4. Reconciliar el costo de componentes del deck (100-150) con la BOM (26/59).
