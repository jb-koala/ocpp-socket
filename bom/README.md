# bom/ — lista de materiales

Un YAML por placa y revisión. Es la fuente de verdad para masa, costo y consumo en reposo:
`tests/test_budgets.py` suma estos campos y falla si superan `reqs/budgets.yml`.

Cuando el esquemático en `hw/` esté cerrado, los códigos de pedido viven **en el esquemático**
(campo `LCSC` de cada símbolo) y KiBot genera el BOM para pedir. Este YAML queda como la vista
"de producto" (masa, costo, consumo), y `tests/test_bom.py` verifica que ambos coincidan.

`order_code: TBD` está permitido solo mientras `hw/` no tenga esquemático; después el test lo rechaza.
