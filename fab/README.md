# fab/ — archivos de fabricación

`kibot.yaml` genera gerbers, taladros, BOM para JLCPCB, archivo de posiciones y PDF del
esquemático. El preflight corre ERC + DRC y **falla si una parte no tiene código LCSC**.

```bash
pip install kibot
make fab BOARD=mainboard-revA     # salida en fab/out/<board>/ (ignorado por git)
```

El carrito en JLCPCB lo arma el agente a partir de estos archivos; el pago lo hace una persona.
