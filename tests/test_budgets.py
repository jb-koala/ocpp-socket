"""Etapa 1: los presupuestos de reqs/budgets.yml son límites duros.

Suma masa, costo y consumo en reposo de bom/<board>.yml y falla si alguno supera el
presupuesto. Sumar magnitudes de unidades distintas (watts + newtons) también falla,
gracias a pint.
"""
import pytest

FIELDS = {
    "mass": "mass",
    "bom_cost": "cost",
    "idle_power": "power_idle",
}


def _total(ureg, bom, field):
    total = None
    for part in bom["parts"]:
        q = ureg(part[field]) * part["qty"]
        total = q if total is None else total + q
    return total


@pytest.mark.parametrize("budget_key,bom_field", FIELDS.items())
def test_board_within_budget(ureg, budgets, boms, budget_key, bom_field):
    for board, limits in budgets.items():
        if board == "safety":
            continue
        assert board in boms, f"no hay bom/{board}.yml para el presupuesto {board}"
        limit = ureg(limits[budget_key])
        total = _total(ureg, boms[board], bom_field)
        assert total.check(limit.dimensionality), (
            f"{board}.{bom_field}: unidades incompatibles {total.units} vs {limit.units}"
        )
        assert total <= limit, (
            f"{board}: {budget_key} = {total:~P} supera el presupuesto {limit:~P}"
        )


def test_safety_thresholds_are_consistent(ureg, budgets):
    s = budgets["safety"]
    cutoff = ureg(s["temp_cutoff"])
    resume = ureg(s["temp_resume"])
    assert resume < cutoff, "temp_resume debe ser menor que temp_cutoff (histéresis)"
    assert ureg(s["temp_hold"]).check("[time]")
    assert ureg(s["temp_cooldown"]).check("[time]")
    assert ureg(s["max_current"]).check("[current]")
