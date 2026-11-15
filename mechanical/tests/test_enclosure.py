"""Etapa 2 (mecánica): chequeos de la caja como código.

Cada test construye la geometría desde mechanical/enclosure/params.py y verifica una regla física:
interferencias, holguras, junta, recorrido de la traba, cama de impresión y masa contra la BOM.
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

EPS = 1e-3  # mm³: below this an intersection is numerical noise (touching faces)


def overlap(a, b) -> float:
    inter = a & b
    return inter.volume if inter is not None else 0.0


@pytest.fixture(scope="module")
def parts():
    return E.printed_parts()


@pytest.fixture(scope="module")
def brackets():
    return E.make_hinge_bracket(1) + E.make_hinge_bracket(-1)


# ── piezas válidas e imprimibles ──────────────────────────────────────────────
def test_parts_are_valid_single_solids(parts):
    for name, part in parts.items():
        assert part.is_valid, f"{name}: sólido inválido"
        assert len(part.solids()) == 1, f"{name}: {len(part.solids())} sólidos (debería ser 1)"


def test_parts_fit_print_bed(parts):
    bx, by, bz = P.BED
    for name, part in parts.items():
        s = E.print_oriented(name, part).bounding_box().size
        fits = (s.X <= bx and s.Y <= by) or (s.Y <= bx and s.X <= by)
        assert fits and s.Z <= bz, f"{name}: {s.X:.0f}x{s.Y:.0f}x{s.Z:.0f} no entra en la cama {P.BED}"


def test_print_orientation_is_flat_on_bed(parts):
    """La cara que va a la cama tiene que ser plana: nada sobresale por debajo de z=0 tras orientar."""
    for name, part in parts.items():
        bb = E.print_oriented(name, part).bounding_box()
        assert abs(bb.min.Z) < 1e-6, name


def test_minimum_walls():
    assert P.T_WALL >= 2.5 and P.T_FRONT >= 2.5 and P.T_BACK >= 2.5
    assert P.LID_WALL >= 2.0 and P.WELL_SHELL >= 2.5


# ── estanqueidad ──────────────────────────────────────────────────────────────
def test_gasket_compression_and_fill():
    assert 0.20 <= P.gasket_compression() <= 0.30, f"compresión {P.gasket_compression():.0%}"
    assert 0.75 <= P.gasket_fill() <= 0.95, f"llenado de ranura {P.gasket_fill():.0%}"


def test_cover_screws_inside_gasket():
    groove_inner_edge = P.RIM_W / 2 + P.GROOVE_W / 2
    boss_outer_edge = P.SCREW_INSET - P.BOSS_D / 2
    assert boss_outer_edge - groove_inner_edge >= 1.0, "los tornillos de la tapa tienen que quedar dentro de la junta"


# ── electrónica adentro ───────────────────────────────────────────────────────
def test_pcb_and_components_clear_the_enclosure(parts):
    # la placa apoya en los standoffs por una cara (volumen de contacto cero); el margen va solo en XY
    # para la placa y en XY + arriba para los componentes
    pcb = E.pcb_all(P.CLEAR_PCB)
    for name in ("base", "cover"):
        v = overlap(pcb, parts[name])
        assert v < EPS, f"PCB + componentes (con {P.CLEAR_PCB} mm) tocan {name}: {v:.1f} mm³"


def test_socket_body_clears_pcb_and_enclosure(parts):
    body = E.socket_body()
    assert overlap(E.socket_body(P.CLEAR_SOCKET_PCB), E.pcb_all()) < EPS, "cuerpo de la toma muy cerca de la PCB"
    for name in ("base", "cover", "socket_insert"):
        assert overlap(body, parts[name]) < EPS, f"cuerpo de la toma choca con {name}"


def test_estop_clears_pcb_and_base(parts):
    assert overlap(E.estop_body(P.CLEAR_PCB), E.pcb_all()) < EPS, \
        "el bloque de contactos del botón de emergencia pisa la zona de componentes: revisar keep-out"
    assert overlap(E.estop_body(), parts["base"]) < EPS


def test_pb1_clears_everything(parts):
    body = E.pb1_body(1.0)
    for name in ("cover",):
        assert overlap(body, parts[name]) < EPS, f"PB1 choca con {name}"
    assert overlap(body, E.socket_body()) < EPS
    assert overlap(E.pb1_body(), parts["base"]) < EPS


def test_mounting_screws_and_gland_clear_the_pcb(parts):
    assert overlap(E.mount_screw_heads(), E.pcb_all(1.0)) < EPS
    assert overlap(E.mount_screw_heads(), E.socket_body()) < EPS
    assert overlap(E.gland_nut(), E.pcb_all(1.0)) < EPS, "la tuerca del prensacable pisa la PCB"


# ── tapa, bisagra y traba ─────────────────────────────────────────────────────
def test_lid_closed_does_not_collide(parts, brackets):
    lid = parts["lid"]
    for name, other in (("cover", parts["cover"]), ("lock_housing", parts["lock_housing"]),
                        ("hinge_brackets", brackets), ("estop_head", E.estop_head())):
        assert overlap(lid, other) < EPS, f"tapa cerrada choca con {name}"


def test_lid_clears_plug_in_use(parts):
    assert overlap(E.plug(), parts["cover"]) < EPS, "la ficha enchufada no entra en el pozo"
    assert overlap(E.plug(P.CLEAR_PLUG_LID), parts["lid"]) < EPS, f"la tapa no cierra con la ficha (holgura {P.CLEAR_PLUG_LID} mm)"


def test_cable_notch_fits_cable():
    assert P.CABLE_NOTCH_W >= P.CABLE_D + 2


@pytest.mark.parametrize("angle", P.LID_OPEN_ANGLES)
def test_lid_swings_open(parts, brackets, angle):
    lid = E.lid_at(angle)
    for name, other in (("cover", parts["cover"]), ("hinge_brackets", brackets),
                        ("lock_housing", parts["lock_housing"])):
        assert overlap(lid, other) < EPS, f"la tapa choca con {name} al abrir {angle}°"


def test_knuckle_gap():
    assert P.KNUCKLE_GAP >= P.CLEAR_MOVING
    assert P.PIN_HOLE_LID - P.PIN_D >= 0.2, "el pasador tiene que girar libre en la tapa"


def test_solenoid_fits_in_housing(parts):
    sol = E.solenoid()
    assert overlap(sol, parts["lock_housing"]) < EPS
    assert overlap(sol, parts["cover"]) < EPS


def test_lock_housing_clear_of_well(parts):
    assert overlap(parts["lock_housing"], E.well_cavity()) < EPS, "la caja de la traba invade el pozo de la toma"
    top = P.BUMP_Y0 + P.BUMP_H
    assert top <= P.WELL_CY - P.WELL_H / 2 - 1.0, "la caja de la traba tiene que quedar debajo del pozo"


def test_plunger_locks_and_releases():
    lid_catch_top = P.LID_Y0 + P.LID_WALL
    assert E.plunger_tip_y(False) >= P.BUMP_Y0, "retraído, el pistón no puede sobresalir de la caja de la traba"
    assert E.plunger_tip_y(False) <= P.BUMP_Y0 + P.BUMP_WALL, "retraído, el pistón tiene que quedar dentro de su guía"
    assert E.plunger_tip_y(True) <= lid_catch_top - P.PLUNGER_ENGAGE, \
        f"extendido, el pistón entra menos de {P.PLUNGER_ENGAGE} mm en la tapa"


# ── masa contra la BOM ────────────────────────────────────────────────────────
def printed_mass_g(parts) -> float:
    total = 0.0
    for name, part in parts.items():
        v, a = part.volume, part.area
        solid_skin = min(v, a * 1.2)  # ~1.2 mm de piel maciza por cara (perímetros + capas sup/inf)
        total += P.DENSITY_ASA * (solid_skin + 0.30 * (v - solid_skin)) * E.PRINT_COUNT[name]
    return total


def test_bom_reserves_the_enclosure_mass(parts):
    bom = yaml.safe_load((ROOT / "bom" / "mainboard-revB.yml").read_text(encoding="utf-8"))
    box = next(p for p in bom["parts"] if p["ref"] == "BOX")
    reserved = float(str(box["mass"]).split()[0])
    m = printed_mass_g(parts)
    assert reserved >= m, f"la BOM reserva {reserved:.0f} g para la caja, la caja impresa pesa ~{m:.0f} g"
