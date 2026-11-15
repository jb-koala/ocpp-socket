"""Etapa 5: toda parte del BOM tiene los campos que necesitan los presupuestos y el pedido.

`order_code: TBD` se tolera solo mientras la placa no tenga esquemático en hw/.
"""
import re

REQUIRED = ["ref", "part", "qty", "supplier", "order_code", "mass", "cost", "power_idle"]
JLC_CODE = re.compile(r"^C\d+$")


def test_parts_have_required_fields(boms):
    for board, bom in boms.items():
        for part in bom["parts"]:
            missing = [k for k in REQUIRED if k not in part]
            assert not missing, f"{board} {part.get('ref')}: faltan {missing}"
            assert part["qty"] >= 1


def test_refs_are_unique(boms):
    for board, bom in boms.items():
        refs = [p["ref"] for p in bom["parts"]]
        assert len(refs) == len(set(refs)), f"{board}: refs duplicados"


def test_quantities_have_units(ureg, boms):
    for board, bom in boms.items():
        for part in bom["parts"]:
            assert ureg(part["mass"]).check("[mass]"), f"{board} {part['ref']}: mass sin unidad de masa"
            assert ureg(part["cost"]).check("[currency]"), f"{board} {part['ref']}: cost sin moneda"
            assert ureg(part["power_idle"]).check("[power]"), f"{board} {part['ref']}: power_idle sin unidad de potencia"


def test_order_codes_once_schematic_exists(boms, hw_has_schematic):
    for board, bom in boms.items():
        if not hw_has_schematic.get(board, False):
            continue  # todavía no hay esquemático: TBD permitido
        for part in bom["parts"]:
            code = str(part["order_code"])
            if part["supplier"] == "JLCPCB":
                assert JLC_CODE.match(code), f"{board} {part['ref']}: código JLCPCB inválido '{code}'"
            else:
                assert code not in ("TBD", ""), f"{board} {part['ref']}: falta order_code"
