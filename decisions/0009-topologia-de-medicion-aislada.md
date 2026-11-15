# 0009. Medición con ATM90E26 alimentado por transformadores de corriente y tensión (lado SELV aislado)

- Status: accepted
- Date: 2026-11-15
- Deciders: JB
- Requirements: REQ011, REQ012, REQ014
- Relacionada: 0006

## Contexto y problema

0006 decidió usar un IC de medición. Queda definir **dónde está la referencia de masa**. Los diseños
de referencia de estos ICs (ATM90E26, BL0940, HLW8032) miden con shunt y divisor resistivo, lo que
deja al IC —y a todo lo que hable con él— referido a la red. Un socket con USB-C para flasheo, un
puerto de expansión y un instalador tocando headers no puede tener la masa del MCU a 220 V.

## Opciones consideradas

1. IC referido a red (shunt + divisor) + aislador digital (ISO7721 o similar) en la UART hacia el MCU
2. IC en el lado SELV, alimentado por **transformador de corriente (ZMCT102) y de tensión (ZMPT101L)**:
   la aislación la dan los transformadores, el IC comparte masa con el MCU
3. Dos placas: medición en una placa "caliente", control en otra

## Decisión

**Opción 2.** Rev A ya tiene los dos transformadores y funcionan; a precio China cuestan centavos
(el ZMPT101L es caro solo en el mercado local). El IC ve señales de pocos cientos de mV, igual que
con un shunt, y no hay ningún nodo de la red del lado del MCU. Es también la historia más simple
para el ensayo de rigidez dieléctrica en pre-compliance.

IC: **ATM90E26** (SPI o UART, clase 0.5S capaz, bien documentado, cristal de 16.384 MHz).
Alternativa de segundo proveedor: **BL0940** (UART, sin cristal, sensor de temperatura interno).
El footprint y las entradas analógicas no son compatibles entre sí: se elige uno por revisión.

## Consecuencias

- La exactitud final depende de la linealidad de los transformadores, no solo del IC. Se verifica
  en bench contra patrón clase 0.5 en 5 puntos (0.3, 1, 2, 5, 10 A) antes de aceptar REQ011.
- El ZMPT101L es un transformador de corriente usado como de tensión: necesita resistencia serie
  en el primario (R4/R5 de rev A, 2 × 56 kΩ metal film) y burden en el secundario. Se conserva.
- El ADC del ESP32 queda libre; solo se usa para el NTC.
