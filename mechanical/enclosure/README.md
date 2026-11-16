# Caja del OCPP Socket v2 — 110 × 110 (CAD como código)

Caja compacta según el plano de referencia de JB (decisión [0012](../../decisions/0012-caja-compacta-110.md)):
cuerpo 110 × 110 × 82, tapa ahumada de 40 mm (122 en total), toma IRAM 2071 en un pozo de 70 × 70,
bisagra arriba, clip abajo, ojales a 70 × 55, knockouts Ø20, paredes de 2.5 mm.
Pulsador RGB en el lateral izquierdo y botón de emergencia compacto Ø16 en el derecho.

Todo sale de `params.py` (medidas: **DRAWING** = del plano, **CONFIRM** = de una pieza real a medir) y
`enclosure.py` (geometría, build123d). `mechanical/tests/test_enclosure.py` verifica 20 reglas físicas.

| Cerrada | Tapa y clip abiertos, con ficha | Despiece | Corte |
|---|---|---|---|
| ![](renders/01_cerrada.png) | ![](renders/02_tapa_abierta_con_ficha.png) | ![](renders/03_explosion.png) | ![](renders/04_corte.png) |

```bash
pip install build123d trimesh matplotlib pyyaml pytest
make mech        # STL orientados para imprimir + STEP del conjunto en out/, renders en renders/
make mech-test   # 20 chequeos
```

## Cómo está armada

```
 pared │ base (70) ──────────────────────────┤ marco (12) │ tapa (40)
       │ PCB 100×80 paralela a la pared      │ pozo 70×70 │ hood ahumado, bisagra arriba
       │ (zonas de altura según lo que tiene  │ toma IRAM  │
       │  encima: ver keepouts de rev B)      │ 2071       │
       │ RGB ◄ lateral izq.   lateral der. ► emergencia Ø16
       │ prensacable M20 abajo · solenoide en su cuna abajo, pistón hacia abajo → clip
```

- **PCB detrás de la toma**: en 110 × 110 no entra al lado. La placa queda a 6 mm de la pared; arriba
  tiene el cuerpo de la toma (zona baja de 17 mm) y alrededor hasta 45 mm.
- **Clip**: pivota bajo la base, sus dos brazos corren bajo la tapa y el gancho abraza el borde
  inferior del frente de la tapa. El cable de la ficha baja por la muesca de la tapa y pasa entre los brazos.
- **Traba (REQ006)**: el solenoide está adentro, en una cuna sobre el piso de la base; el pistón sale
  hacia abajo (no entra agua) y entra en el brazo derecho del clip. Clip trabado = tapa trabada.
  Sensor Hall + imán en el clip para saber si está cerrado.
- **Canal de desagüe**: del fondo del pozo al borde inferior, con paredes a 45° (el agua sale por abajo).

## Piezas e impresión (FDM, sin soportes)

| Pieza | Orientación | Cama (mm) | Notas |
|---|---|---|---|
| `base` | fondo abajo (sobre las patitas) | 110 × 120 × 72 | Agujeros laterales y del pistón en gota; orejas del clip y cuna con caras a 45° |
| `cover` (marco) | frente abajo | 110 × 118 × 19 | Pozo en embudo, canal a 45°; el nudillo central de la bisagra apoya en la cama |
| `lid` | frente abajo | 110 × 118 × 47 | Escuadras a 45° bajo los nudillos; logo grabado |
| `clip` | brazos abajo | 30 × 66 × 19 | |
| `socket_insert` | plana | 78 × 78 × 3 | Adaptador de la toma (decisión 0010), se atornilla desde adentro |

ASA para exterior; PETG translúcido para la tapa si se quiere el efecto ahumado.
Boquilla 0.4, capa 0.2, 5 perímetros, 30 % gyroid. **Masa ≈ 271 g, filamento ≈ USD 6.**

## Tornillería y sellos (BOM: `BOX-HW`)

| Ítem | Cant. | Dónde |
|---|---|---|
| Inserto termofijado M3 (Ø4.0 × 6) | 12 | 4 esquinas de la base, 4 standoffs PCB, 4 postes del pozo |
| M3 × 10 cabeza cilíndrica | 4 | Marco → base, en contrafrente |
| M3 × 6 | 8 | PCB y placa de toma |
| Cordón EPDM/silicona Ø2.0 | ~400 mm | Ranura base/marco (25 % de compresión) |
| Pasador acero Ø3 | 2 | Bisagra (~50 mm) y pivote del clip (~42 mm) |
| Imán Ø6 × 3 + sensor Hall | 1 | Clip / cuna del solenoide |
| Prensacable M20 | 1 | Knockout inferior (entrada de red) |
| Tornillos a pared, cabeza tanque ≤ 3.5 mm | 4 | Ojales; las cabezas quedan debajo de la PCB |

## Armado

1. Insertos en base y postes del pozo. Solenoide en su cuna.
2. Base a la pared (4 tornillos por los ojales), prensacable abajo.
3. PCB en los standoffs; cableado: red a TB1, faston a la toma, RGB, emergencia, solenoide, Hall.
4. Toma en la placa adaptadora → placa contra el pozo desde adentro.
5. Cordón en la ranura, marco con 4 × M3. Tapa con su pasador; clip con el suyo.

## A confirmar con piezas reales (CONFIRM)

Toma IRAM 2071 (recorte de la placa, cuerpo Ø44 × 28 asumido), botón de emergencia Ø16 (bloque Ø20 × 28),
pulsador QN12 (cuerpo Ø16 × 20), solenoide (12 × 16 × 11, carrera 4), ficha del cargador (Ø42 × 45), insertos y cordón.
Si una pieza real es más grande, el test correspondiente falla y dice dónde.

## Limitaciones conocidas

- **Knockout trasero bloqueado por la PCB**: está, como en el plano, pero con rev B la entrada de red es por
  abajo. Usarlo exige un recorte Ø26 en el centro de la PCB (ver keepouts).
- El plano muestra el clip; la geometría del clip es una interpretación (brazos + gancho), no una copia de la vista de detalle.
- Ensayos pendientes sobre la caja impresa: IP (IEC 60529), hilo incandescente, UV (docs/003).
