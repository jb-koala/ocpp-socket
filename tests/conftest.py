from pathlib import Path

import pytest
import yaml
from pint import UnitRegistry

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def ureg():
    u = UnitRegistry()
    u.define("USD = [currency]")
    return u


@pytest.fixture(scope="session")
def budgets():
    with open(ROOT / "reqs" / "budgets.yml", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def boms():
    out = {}
    for p in sorted((ROOT / "bom").glob("*.yml")):
        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        out[data["board"]] = data
    return out


@pytest.fixture(scope="session")
def hw_has_schematic():
    return {d.name: any(d.glob("*.kicad_sch")) for d in (ROOT / "hw").iterdir() if d.is_dir()}
