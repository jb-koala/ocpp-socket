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
