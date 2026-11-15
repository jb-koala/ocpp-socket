# 0010. Tomacorriente: IRAM 2071 en lugar de toma universal

- Status: proposed
- Date: 2026-11-15
- Deciders: JB, Gabriel
- Requirements: REQ010, REQ014

## Contexto y problema

Rev A usa una toma IP "universal" de 10 A (acepta varias geometrías de ficha). Para un producto de
instalación fija en Argentina, la reglamentación de instalaciones (AEA 90364) y las normas de
producto esperan tomacorrientes IRAM 2071 (10 A / 20 A). La Res. 16/2025 flexibilizó la geometría de
las fichas de los aparatos, no de los tomacorrientes. Una toma universal puede ser lo único que
trabe la certificación. Además, las tomas universales suelen tener peor presión de contacto, lo que
va directo contra el riesgo #1 (calentamiento a 10 A continuos).

## Opciones consideradas

1. Mantener la toma universal (máxima compatibilidad con cargadores importados con ficha Schuko)
2. **IRAM 2071 10 A** (certificada, S-mark), con adaptador/cable Mode 2 con ficha IRAM 2073
3. IRAM 2071 20 A para la variante de 20 A, misma caja
4. Toma Schuko (CEE 7/3) certificada bajo IEC 60884 para mercados de exportación (Líbano usa Schuko)

## Decisión

Pendiente. Propuesta: **opción 2 para Argentina** y **opción 4 como variante de exportación**, con el
mismo PCB y una ventana de caja distinta. La toma se compra ya certificada (S-mark / CB) para que
el ensayo del conjunto no tenga que re-ensayar la toma.

## Consecuencias

- Los cargadores Mode 2 con ficha Schuko necesitan ficha IRAM 2073 o cable con ficha local; esto va
  en la matriz de prueba cargador × vehículo (Gate 1).
- BOM: SKT1 cambia; el costo sube pero la toma viene con certificado propio.
