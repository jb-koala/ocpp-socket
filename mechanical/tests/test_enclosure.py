"""Etapa 2 (mecánica): chequeos de la caja v2 (110 × 110, decisión 0012) como código.

Cada test construye la geometría desde mechanical/enclosure/params.py y verifica una regla física.
Si uno falla, el arreglo va a params.py o al diseño (con decisión en decisions/), no al test.
"""
import pathlib
import sys

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "mechanical" / "enclosure"))

import enclosure as E  # noqa: E402
import params as P  # noqa: E402

EPS = 1e-3  # mm³: por debajo es ruido numérico (caras que se tocan)


def overlap(a, b) -> float:
    inter = a & b
    return inter.volume if inter is not None else 0.0


@pytest.fixture(scope="module")
def parts():
    return E.printed_parts()


# ── el plano de referencia ────────────────────────────────────────────────────
def test_outline_matches_reference_drawing(parts):
    body = (parts["base"] + parts["cover"]).bounding_box()
    assert body.size.X == pytest.approx(110, abs=0.5), "frente de 110 mm (plano)"
    assert P.W == 110 and P.H == 110, "110 × 110 (plano); bisagra y orejas del clip sobresalen aparte"
    assert P.D == pytest.approx(82, abs=0.5), "cuerpo 82 mm (plano)"
    assert P.D + P.LID_DEPTH == pytest.approx(122, abs=0.5), "total 122 mm con la tapa (plano)"
    assert P.MOUNT_DX == 70 and P.MOUNT_DY == 55 and P.KNOCKOUT_D == 20
    assert 2.0 <= P.T_WALL <= 2.5, "espesor de pared 2.0–2.5 mm (plano)"


# ── piezas válidas e imprimibles ──────────────────────────────────────────────
def test_parts_are_valid_single_solids(parts):
    for name, part in parts.items():
        assert part.is_valid, f"{name}: sólido inválido"
        assert len(part.solids()) == 1, f"{name}: {len(part.solids())} sólidos"


def test_parts_fit_print_bed(parts):
    bx, by, bz = P.BED
    for name, part in parts.items():
        s = E.print_oriented(name, part).bounding_box().size
        assert ((s.X <= bx and s.Y <= by) or (s.Y <= bx and s.X <= by)) and s.Z <= bz, f"{name} no entra en la cama"


# ── estanqueidad ──────────────────────────────────────────────────────────────
def test_gasket_compression_and_fill():
    assert 0.20 <= P.gasket_compression() <= 0.30
    assert 0.75 <= P.gasket_fill() <= 0.95


def test_frame_screws_inside_gasket():
    assert (P.SCREW_INSET - P.BOSS_D / 2) - (P.RIM_W / 2 + P.GROOVE_W / 2) >= 1.0


# ── electrónica adentro ───────────────────────────────────────────────────────
def test_pcb_and_components_clear_the_enclosure(parts):
    pcb = E.pcb_all(P.CLEAR_PCB)
    for name in ("base", "cover"):
        v = overlap(pcb, parts[name])
        assert v < EPS, f"PCB + componentes (holgura {P.CLEAR_PCB} mm) tocan {name}: {v:.1f} mm³"


def test_socket_body_clears_pcb_and_enclosure(parts):
    assert overlap(E.socket_body(P.CLEAR_SOCKET_PCB), E.pcb_all()) < EPS, \
        "el cuerpo de la toma pisa la zona de componentes de la PCB: revisar PCB_ZONES['socket']"
    for name in ("base", "cover", "socket_insert"):
        assert overlap(E.socket_body(), parts[name]) < EPS, f"cuerpo de la toma choca con {name}"


def test_side_buttons_clear_everything(parts):
    for label, body in (("botón de emergencia", E.estop_body(P.CLEAR_PCB)), ("pulsador RGB", E.pb1_body(P.CLEAR_PCB))):
        assert overlap(body, E.pcb_all()) < EPS, f"{label}: pisa la zona de componentes"
        assert overlap(body, E.socket_body()) < EPS, f"{label}: choca con el cuerpo de la toma"
        assert overlap(body, parts["cover"]) < EPS, f"{label}: choca con el frente"
    assert overlap(E.estop_body(), parts["base"]) < EPS
    assert overlap(E.pb1_body(), parts["base"]) < EPS


def test_mounting_screws_and_gland_clear_the_pcb(parts):
    assert overlap(E.mount_screw_heads(), E.pcb_all()) < EPS, "las cabezas de los tornillos a pared tocan la PCB"
    assert overlap(E.gland_nut(), E.pcb_all(1.0)) < EPS, "la tuerca del prensacable pisa la PCB"


# ── tapa, bisagra, clip y traba ───────────────────────────────────────────────
def test_lid_closed_does_not_collide(parts):
    for name, other in (("cover", parts["cover"]), ("base", parts["base"]), ("clip", parts["clip"]),
                        ("emergencia", E.estop_head())):
        assert overlap(parts["lid"], other) < EPS, f"tapa cerrada choca con {name}"


def test_lid_clears_plug_in_use(parts):
    assert overlap(E.plug(), parts["cover"]) < EPS, "la ficha enchufada no entra en el pozo"
    assert overlap(E.plug(P.CLEAR_PLUG_LID), parts["lid"]) < EPS, "la tapa no cierra con la ficha enchufada"


@pytest.mark.parametrize("angle", P.LID_OPEN_ANGLES)
def test_lid_swings_open(parts, angle):
    lid = E.lid_at(angle)
    for name in ("cover", "base"):
        assert overlap(lid, parts[name]) < EPS, f"la tapa choca con {name} al abrir {angle}°"


def test_knuckles_and_pin():
    assert P.KNUCKLE_GAP >= P.CLEAR_MOVING
    assert P.PIN_HOLE_LID - P.PIN_D >= 0.2
    assert P.HINGE_Y - P.KNUCKLE_OD / 2 - P.H >= P.CLEAR_MOVING, "los nudillos rozan la cara superior"


def test_clip_closed_and_open(parts):
    clip = parts["clip"]
    for name in ("base", "cover"):
        assert overlap(clip, parts[name]) < EPS, f"el clip cerrado choca con {name}"
    # abierto 90° hacia abajo, para liberar la tapa
    assert overlap(E.clip_at(90), parts["base"]) < EPS
    assert overlap(E.clip_at(90), parts["lid"]) < EPS


def test_cable_passes_between_clip_arms():
    gap = P.CLIP_W - 2 * P.CLIP_ARM_W
    assert gap >= P.CABLE_D + 2, f"entre los brazos del clip quedan {gap} mm para un cable de {P.CABLE_D}"
    assert P.CABLE_NOTCH_W >= P.CABLE_D + 2


def test_solenoid_fits_its_cradle(parts):
    sol = E.solenoid()
    for name in ("base", "cover"):
        assert overlap(sol, parts[name]) < EPS, f"el solenoide choca con {name}"
    assert overlap(sol, E.pcb_all(P.CLEAR_PCB)) < EPS


def test_plunger_locks_and_releases():
    arm_top = -P.CLIP_ARM_GAP
    assert P.plunger_retracted_y() >= arm_top, "retraído, el pistón no puede tocar el clip"
    assert P.plunger_retracted_y() <= P.T_WALL, "retraído, el pistón tiene que quedar en su guía"
    assert P.plunger_extended_y() <= arm_top - P.PLUNGER_ENGAGE, "extendido, el pistón no traba el clip"


# ── masa contra la BOM ────────────────────────────────────────────────────────
def printed_mass_g(parts) -> float:
    total = 0.0
    for name, part in parts.items():
        v, a = part.volume, part.area
        skin = min(v, a * 1.2)
        total += P.DENSITY_ASA * (skin + 0.30 * (v - skin)) * E.PRINT_COUNT[name]
    return total


def test_bom_reserves_the_enclosure_mass(parts):
    bom = yaml.safe_load((ROOT / "bom" / "mainboard-revB.yml").read_text(encoding="utf-8"))
    box = next(p for p in bom["parts"] if p["ref"] == "BOX")
    reserved = float(str(box["mass"]).split()[0])
    m = printed_mass_g(parts)
    assert reserved >= m, f"la BOM reserva {reserved:.0f} g para la caja; la caja impresa pesa ~{m:.0f} g"
