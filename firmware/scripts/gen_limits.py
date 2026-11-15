"""Genera lib/session_guard/limits.h desde reqs/budgets.yml (sección safety).

Los umbrales viven en un solo lugar (budgets.yml). El firmware no los redefine.
Uso: python firmware/scripts/gen_limits.py
"""
from pathlib import Path

import yaml
from pint import UnitRegistry

ROOT = Path(__file__).resolve().parents[2]
u = UnitRegistry()

s = yaml.safe_load((ROOT / "reqs" / "budgets.yml").read_text(encoding="utf-8"))["safety"]


def c(q):
    return u(q).to("degC").magnitude


def ms(q):
    return int(u(q).to("ms").magnitude)


out = f"""// GENERADO por firmware/scripts/gen_limits.py desde reqs/budgets.yml. NO EDITAR A MANO.
#pragma once
#define SG_TEMP_CUTOFF_C   {c(s['temp_cutoff']):.1f}f
#define SG_TEMP_RESUME_C   {c(s['temp_resume']):.1f}f
#define SG_TEMP_HOLD_MS    {ms(s['temp_hold'])}u
#define SG_TEMP_COOLDOWN_MS {ms(s['temp_cooldown'])}u
#define SG_MAX_CURRENT_A   {u(s['max_current']).to('A').magnitude:.1f}f
"""
(ROOT / "firmware" / "lib" / "session_guard" / "limits.h").write_text(out, encoding="utf-8")
print(out)
