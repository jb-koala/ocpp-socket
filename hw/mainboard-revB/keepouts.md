# Keep-outs que la caja le impone a la PCB rev B

Generados desde `mechanical/enclosure/params.py`. Si cambian ahí, cambian acá (y los tests de
`mechanical/tests/` verifican que la caja y la PCB no se pisen).

Origen: esquina inferior izquierda de la PCB vista desde el frente (componentes hacia el usuario).

```
 y=80 ┌───────────────────────────────────────────────┬────────────────────┐
      │ ○                                              │ (antena WROOM aquí,│ ○
      │                                                │  borde superior    │
      │   ZONA ALTA  (x 0–65)                          │  derecho)          │
      │   ≤ 32 mm sobre la placa                       │                    │
      │   TB1 · F1 · VR1 · L1 · PS1 · K1 · T1 · TR1 · C4│  ZONA BAJA (x 65–100)
      │                                                │  ≤ 12 mm           │
      │                                                │  WROOM · ATM90E26  │
      │                                                │  buck · USB-C      │
      │   TB1 sobre el borde inferior, x≈25            │      ┌───────────┐ │
      │   (prensacable M20 debajo)                     │      │ E-STOP    │ │
      │ ○                                              │ ○    │ Ø32 bloque│ │
 y=0  └───────────────────────────────────────────────┴──────┴───────────┴─┘
      x=0                                            x=65                x=100
```

| Restricción | Valor | Por qué |
|---|---|---|
| Tamaño | 100 × 80 × 1.6 mm | Entra en la base con 2 mm de holgura a paredes y tornillos |
| Agujeros de fijación | 4 × Ø3.2 a 4 mm de cada esquina; sin cobre en Ø8 | Standoffs Ø8 con insertos M3 |
| Zona alta | x 0–65 mm: hasta **32 mm** sobre la placa | Debajo del frente libre; cuerpo de la toma arriba, fuera de la placa |
| Zona baja | x 65–100 mm: hasta **12 mm** | Arriba pasa el bloque de contactos del botón de emergencia (Ø32, centro en x≈85, y≈9) |
| TB1 (red) | Borde inferior, x ≈ 25 mm | El prensacable M20 entra por abajo en x = 40 de la caja (x = 25 de la placa) |
| Faston a la toma | Borde superior, zona alta | La toma está arriba de la placa, en el frente |
| Antena WROOM | Borde superior derecho, en el borde | Lejos de la red y del bloque del botón; la caja es plástica |
| J-ESTOP | Zona baja, cerca de la esquina inferior derecha, ≤ 12 mm de alto | Bornera 5.08 mm ≈ 10 mm |
| J-PB (pulsador RGB) | Borde superior izquierdo | El pulsador está en la pared lateral izquierda, a la altura de la toma |
| J-LOCK (traba) | Borde superior, a la derecha del centro | La caja de traba está en el frente, x ≈ 87 de la caja, sobre la placa |
| Barrera de aislación | La línea x ≈ 65 coincide con el límite zona alta / zona baja | La división natural red (izquierda) / SELV (derecha) cae justo ahí: 6.4 mm de creepage sobre esa línea |

Es una propuesta de partida: si a Gabriel la zona alta de 65 mm le queda chica para los componentes de
red, la palanca es mover el botón de emergencia (o ensanchar la caja: `W` en params.py) y volver a correr
`make mech-test`.
