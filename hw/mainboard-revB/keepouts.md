# Keep-outs que la caja v2 (110 × 110) le impone a la PCB rev B

Generados desde `mechanical/enclosure/params.py` (`PCB_ZONES`). Los tests de `mechanical/tests/`
verifican que nada de la caja, la toma, los botones ni la traba pise estas envolventes.

**La PCB va paralela a la pared, detrás de la toma** (en 110 × 110 no entra al lado). Componentes hacia
el frente. Origen: esquina inferior izquierda de la placa vista desde el frente.

```
 y=80 ┌──────────────────────────────────────────────────────────────────┐ ○
      │ ○      ≤45        │                                │     ≤45      │
      │                   │                                │              │
 y=50 │┌────────┐         │     BAJO EL CUERPO DE LA TOMA  │   ┌─────────┐│
      ││ RGB    │  ≤45    │          ≤ 17 mm               │≤45│ EMERG.  ││
      ││ ≤17    │         │       (x 24–76, y 24–80)       │   │ ≤15     ││
 y=30 │└────────┘         │                                │   └─────────┘│
 y=24 │                   └────────────────────────────────┘              │
      │   ≤45            TB1 aquí (x≈50, borde inferior)       ≤45         │
      │                         ┌──────────┐                               │
      │ ○                       │ cuna sol.│≤33                          ○ │
 y=0  └─────────────────────────┴──────────┴───────────────────────────────┘
      x=0              x=24     x=51   x=72  x=76                     x=100
```

| Zona | Rectángulo (x, y en mm de la placa) | Altura máx. sobre la placa | Qué hay arriba |
|---|---|---|---|
| General | toda la placa | **45 mm** | Bloque del pozo y placa de la toma |
| Toma | x 24–76, y 24–80 | **17 mm** | Cuerpo de la toma IRAM 2071 (Ø44 × 28 asumido, 4 mm de holgura) |
| RGB | x 0–20, y 30–50 | **17 mm** | Cuerpo del pulsador, pared izquierda |
| Emergencia | x 72–100, y 28–52 | **15 mm** | Bloque de contactos Ø20 × 28, pared derecha |
| Traba | x 51–72, y 0–11 | **33 mm** | Cuña de la cuna del solenoide |

| Otra restricción | Valor | Por qué |
|---|---|---|
| Tamaño | 100 × 80 × 1.6, centrada en X, borde inferior a 15 mm del piso | Entra con 2.5 mm a las paredes, libre de los tornillos de esquina |
| Agujeros | 4 × Ø3.2 a 4 mm de cada esquina, sin cobre en Ø8 | Standoffs de 6 mm con insertos M3 |
| Cara inferior | Nada más alto que 2 mm debajo de la placa en los 4 ojales (x 15/85 ± 5, y 12.5/67.5 ± 5) | Cabezas de los tornillos a pared |
| TB1 (red) | Borde inferior, centrado | El prensacable entra por el knockout inferior, en el centro |
| Knockout trasero | Bloqueado | Para usarlo hace falta un recorte Ø26 en el centro de la placa (choca con la zona de la toma: no recomendado en rev B) |

## Consecuencia para el layout (para Gabriel)

Los componentes altos de rev B (K1 ≈ 25 mm, PS1 HLK-10M12 ≈ 21.5 mm, T1/TR1 ≈ 20 mm, C4) **no entran
bajo la toma** (17 mm). Tienen que ir en la banda inferior (y 0–24, salvo la cuna) o en las columnas
laterales (x 0–24 y x 76–100, fuera de las zonas del RGB y de la emergencia). Es ajustado: si no entra,
las palancas en orden son (1) medir la toma real (si su cuerpo es más corto, la zona sube),
(2) una fuente más baja, (3) PCB en dos pisos (red abajo, control arriba en el hueco del pozo).
