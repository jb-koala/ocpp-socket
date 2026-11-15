# 0011. Caja propia diseñada como código, impresa en ASA para el piloto

- Status: accepted (JB, 2026-11-15)
- Date: 2026-11-15
- Deciders: JB
- Requirements: REQ005, REQ006, REQ007, REQ013, REQ014, REQ016

## Contexto y problema

Rev A usa una caja GENROD IP65 115 × 165 × 65 comprada, con agujeros hechos a mano. El boceto del
producto muestra otra cosa: tapa con bisagra que cierra con la ficha enchufada, toma empotrada,
pulsador lateral, y la traba de tapa integrada. Para el piloto de 50 unidades hace falta una caja
repetible; la matricería de inyección recién se justifica a 1.000+ unidades (deck, Gate 3).

## Opciones consideradas

1. Seguir con la GENROD + piezas interiores impresas (frente de toma, traba, porta-PCB)
2. **Caja propia, CAD como código (build123d), impresa en FDM para el piloto**, diseñada con reglas que
   después sirven para inyección (paredes uniformes de 2.5 mm, embudos y chaflanes a 45°)
3. Caja propia mecanizada / termoformada

## Decisión

**Opción 2.** Impresión propia en ASA, sin soportes. Medidas en `mechanical/enclosure/params.py`,
22 chequeos automáticos en `mechanical/tests/`. Objetivo IP54 con tapa cerrada y ficha enchufada
(junta de cordón al 25 % de compresión, prensacable M20, botones IP65, pistón de la traba saliendo
hacia abajo).

## Consecuencias

- Buenas: la traba, la tapa, la placa de toma y los keep-outs de la PCB salen del mismo modelo; cambiar la
  toma o el botón de emergencia es cambiar un número y volver a correr los tests. El STEP sirve para
  cotizar inyección cuando toque.
- Malas: **masa ~367 g** contra ~250 g de la GENROD; rev B pasa a 728 g contra un presupuesto de 650 g
  (decisión pendiente de JB). Costo de filamento ~USD 8 por caja + ~USD 2 de tornillería; tiempo de
  impresión ~12–15 h por caja en FDM.
- La caja impresa necesita sus propios ensayos (IP, hilo incandescente 850 °C, UV): ver docs/003.
- La GENROD queda como plan B si la impresión no pasa los ensayos del piloto.
