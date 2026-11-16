# 0012. Caja compacta 110 × 110 según el plano de referencia

- Status: accepted (JB, 2026-11-16)
- Date: 2026-11-16
- Deciders: JB
- Supersedes: 0011 en el formato y la disposición (0011 sigue vigente en "caja propia, CAD como código, impresa en ASA")
- Requirements: REQ005, REQ006, REQ007, REQ014, REQ016

## Contexto y problema

La primera caja propia (0011) medía 130 × 190 × 70 con la PCB al lado de la toma y el botón de
emergencia en el frente; impresa pesaba ~367 g y dejaba a rev B en 728 g, sobre el presupuesto de 650 g.
JB envió un plano de referencia de una caja estanca de 110 × 110 × 82 (+ tapa de 40), con toma IRAM 2071
en pozo de 70 × 70, bisagra arriba, clip abajo, ojales a 70 × 55 y knockouts Ø20.

## Opciones consideradas

1. Seguir con la caja de 130 × 190 (0011)
2. **Rehacer la caja al formato del plano** y resolver lo que el plano no tiene (botones, traba, PCB)
3. Comprar una caja comercial de ese formato y adaptar interiores

## Decisión

**Opción 2.** Resoluciones que el plano no trae:
- **PCB detrás de la toma**, paralela a la pared: es la única forma de que entre en 110 × 110.
- **Botones en los laterales** (JB, 2026-11-16): pulsador RGB a la izquierda, botón de emergencia compacto
  Ø16 a la derecha, en la posición de los knockouts.
- **Traba sobre el clip**: solenoide interno con pistón hacia abajo que traba el brazo del clip.
- **Bisagra integrada** al marco y a la tapa (sin pieza de bisagra aparte).

## Consecuencias

- Buenas: caja de ~271 g (rev B queda en 630 g, dentro del presupuesto), ~USD 6 de filamento, 5 piezas
  impresas, formato de producto reconocible. Los 20 tests de `mechanical/tests/` pasan.
- Malas: la PCB queda muy restringida en altura bajo la toma (17 mm) — los componentes altos de red
  tienen que ir a la banda inferior y a los costados (`hw/mainboard-revB/keepouts.md`). El knockout
  trasero queda tapado por la PCB. El botón de emergencia pasa de Ø22 a Ø16 compacto.
- Pendiente: medir la toma IRAM 2071 real, el botón Ø16 y el solenoide (CONFIRM en params.py).
