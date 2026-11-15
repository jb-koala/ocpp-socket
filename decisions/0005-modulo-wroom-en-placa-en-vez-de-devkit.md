# 0005. Reemplazar el DevKitC por un módulo ESP32-S3-WROOM-1 soldado en la placa

- Status: proposed
- Date: 2026-11-15
- Deciders: JB, Gabriel
- Requirements: REQ009, REQ012, REQ014

## Contexto y problema

El MVP usa un ESP32-S3-DEVKITC-1 (USD 9.6-13.5, el ítem más caro de la BOM después de la toma)
montado sobre headers. Para producción eso implica: costo, altura, un conector mecánico más que puede
fallar, y un segundo LDO (el del devkit) en la cadena 12 V → 5 V → 3.3 V. Además ENACOM homologa
el módulo de radio: conviene uno con certificación modular (WROOM-1 la tiene; el devkit no es un módulo).

## Opciones consideradas

1. Mantener el DevKitC (cero rediseño)
2. ESP32-S3-WROOM-1 (N8R2 o N16R8) soldado en la placa + conector USB-C para flash/logs
3. ESP32-S3 chip desnudo con antena en PCB (requiere certificación de radio propia)

## Decisión

Pendiente. Propuesta: **opción 2** en rev B. Ahorro estimado USD 6-10 por unidad, menos piezas, y
camino de homologación más corto.

## Consecuencias

- Hay que rediseñar la zona de U2 en `hw/mainboard-revB`, agregar USB-C + circuito de auto-reset,
  y un buck 12 V → 3.3 V (ver 0007). Flash y provisioning pasan a hacerse por USB-C o pogo pins.
