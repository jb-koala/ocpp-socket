# hw/ — electrónica (KiCad 10)

Una carpeta por placa y revisión: `hw/<placa>-rev<X>/`. Dentro, el proyecto KiCad completo
(`.kicad_pro`, `.kicad_sch`, `.kicad_pcb`, librerías locales en `lib/`).

## Convenciones

- KiCad **10** (archivos de texto; se diffean bien en git).
- Cada símbolo con parte real lleva los campos `LCSC` (código JLCPCB), `MPN` y `Manufacturer`.
- Reglas de diseño del fabricante en `<placa>-rev<X>/jlcpcb.kicad_dru` (se versiona).
- Una revisión nueva es una carpeta nueva (copia + bump). La anterior no se toca.

## Chequeo

```bash
make hw-check      # kicad-cli sch erc + pcb drc con --exit-code-violations en todas las placas
```

Cero violaciones es la condición para generar archivos de fabricación (`fab/`).

## Autorouter

Freerouting corre local: `make hw-route BOARD=mainboard-revA` exporta DSN, rutea e importa SES.
El resultado siempre se revisa a mano antes del DRC.

## Estado de las placas

| Placa | Estado | Dónde |
|---|---|---|
| mainboard-revA (FLUXIO-PCB-01) | En campo. Solo PDF del layout y BOM; esquemático en formato original a recuperar | `mainboard-revA/` |
| mainboard-revB | Diseño por bloques y pinout definidos; esquemático KiCad por dibujar | `mainboard-revB/README.md`, `pinout.md`, `jlcpcb.kicad_dru` |

## Checklist de revisión de la barrera de aislación (antes de pedir rev B)

- [ ] Ningún nodo SELV a < 6.4 mm de L, N o cualquier nodo de red (DRC `isolation_barrier` a cero).
- [ ] Ranura fresada bajo PS1, T1, TR1 y K1; sin plano de cobre que la cruce.
- [ ] PE con pista ≥ 2 mm² equivalente y continuidad directa TB1 → SKT1.
- [ ] Componentes X/Y, varistor y fusible del lado de red, antes de cualquier otra cosa.
- [ ] El botón de emergencia corta la bobina de K1, no pasa por ningún GPIO.
- [ ] USB-C, header de expansión y debug: solo nodos SELV.
