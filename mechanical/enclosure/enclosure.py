"""OCPP Socket enclosure as code (build123d).

Parts (all printable in FDM without supports, in the orientation given by PRINT_ORIENTATION):
    base            rear shell, wall-mounted; PCB standoffs, gasket groove, M20 gland, PB1 hole
    cover           front cover with the socket well, e-stop hole, screw counterbores
    lid             hinged smoked hood over the socket, cable notch, lock catch, magnet pocket
    hinge_bracket   x2 (same STL printed twice), carries the outer knuckles
    lock_housing    bump below the well with the solenoid and the Hall sensor (plunger exits downward)
    socket_insert   adapter plate for the chosen socket, screwed from inside (decision 0010)

Run `python enclosure.py` to export STL (print-oriented) and STEP (assembly) into ./out/.
Geometry is defined in params.py; tests are in mechanical/tests/test_enclosure.py.
"""
from __future__ import annotations

import math
import pathlib

from build123d import (
    Align, Axis, Box, Compound, Cone, Cylinder, Location, Part, Plane, Polygon, Pos,
    RectangleRounded, Text, export_step, export_stl, extrude,
)

import params as P

OUT = pathlib.Path(__file__).parent / "out"
MIN = (Align.MIN, Align.MIN, Align.MIN)


# ── helpers ──────────────────────────────────────────────────────────────────
def rr(w, h, r, z0, d, cx=P.W / 2, cy=P.H / 2, taper=0.0) -> Part:
    """Rounded-rectangle prism: footprint w x h centred at (cx, cy), from z0 up by d."""
    r = max(min(r, min(w, h) / 2 - 0.01), 0.3)
    face = Plane.XY.offset(z0) * Pos(cx, cy) * RectangleRounded(w, h, r)
    return extrude(face, amount=d, taper=taper)


def box(x0, x1, y0, y1, z0, z1) -> Part:
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN)


def cyl_z(cx, cy, z0, z1, d) -> Part:
    return Pos(cx, cy, z0) * Cylinder(d / 2, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))


def axis_plane(axis: str, origin) -> Plane:
    """Plane whose local Z runs along `axis` and whose local Y points to +Z (print 'up')."""
    if axis == "X":
        return Plane(origin=origin, x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    if axis == "Y":
        return Plane(origin=origin, x_dir=(-1, 0, 0), z_dir=(0, 1, 0))
    raise ValueError(axis)


def cyl_axis(axis, origin, length, d) -> Part:
    return axis_plane(axis, origin) * Cylinder(d / 2, length, align=(Align.CENTER, Align.CENTER, Align.MIN))


def teardrop(axis, origin, length, d) -> Part:
    """Horizontal hole with a 45° roof so it prints without sagging (tip towards +Z)."""
    r = d / 2
    s = r / math.sqrt(2)
    tri = Polygon((-s, s), (s, s), (0, r * math.sqrt(2)), align=None)
    return cyl_axis(axis, origin, length, d) + axis_plane(axis, origin) * extrude(tri, amount=length)


def corners(inset):
    return [(inset, inset), (P.W - inset, inset), (inset, P.H - inset), (P.W - inset, P.H - inset)]


def pcb_holes():
    i = P.PCB_HOLE_INSET
    return [(P.PCB_X0 + x, P.PCB_Y0 + y) for x in (i, P.PCB_W - i) for y in (i, P.PCB_H - i)]


def insert_screws():
    return [(P.WELL_CX + sx * P.INSERT_SCREW_DX, P.WELL_CY + sy * P.INSERT_SCREW_DY)
            for sx in (-1, 1) for sy in (-1, 1)]


def housing_screws():
    x_off = P.BUMP_W / 2 + P.HOUSING_FLANGE / 2
    y_mid = P.BUMP_Y0 + P.BUMP_H / 2
    return [(P.BUMP_CX - x_off, y_mid), (P.BUMP_CX + x_off, y_mid)]


def bracket_screws():
    return [(P.W / 2 - P.BRACKET_SCREW_X, P.HINGE_Y), (P.W / 2 + P.BRACKET_SCREW_X, P.HINGE_Y)]


# ── base ─────────────────────────────────────────────────────────────────────
def make_base() -> Part:
    t, R = P.T_WALL, P.R_CORNER
    z_ch = P.D_BASE - P.RIM_H - P.CHAMFER_45
    part = rr(P.W, P.H, R, 0, P.D_BASE)
    part -= rr(P.W - 2 * t, P.H - 2 * t, R - t, P.T_BACK, z_ch - P.T_BACK)
    part -= rr(P.W - 2 * t, P.H - 2 * t, R - t, z_ch, P.CHAMFER_45, taper=45)  # inward 45°: no supports
    part -= rr(P.W - 2 * P.RIM_W, P.H - 2 * P.RIM_W, R - P.RIM_W, P.D_BASE - P.RIM_H, P.RIM_H + 1)

    # gasket groove centred on the rim
    o = P.RIM_W / 2 - P.GROOVE_W / 2
    i = P.RIM_W / 2 + P.GROOVE_W / 2
    z_g = P.D_BASE - P.GROOVE_D
    part -= rr(P.W - 2 * o, P.H - 2 * o, R - o, z_g, P.GROOVE_D + 1) - rr(P.W - 2 * i, P.H - 2 * i, R - i, z_g, P.GROOVE_D + 1)

    # cover screw bosses (M4 heat-set inserts), inside the gasket
    for x, y in corners(P.SCREW_INSET):
        part += cyl_z(x, y, P.T_BACK, P.D_BASE, P.BOSS_D)
        part -= cyl_z(x, y, P.D_BASE - P.M4_INSERT_DEPTH, P.D_BASE + 1, P.M4_INSERT_HOLE)

    # PCB standoffs (M3 heat-set inserts)
    for x, y in pcb_holes():
        part += cyl_z(x, y, P.T_BACK - 0.1, P.PCB_Z0, P.STANDOFF_D)
        part -= cyl_z(x, y, P.PCB_Z0 - P.M3_INSERT_DEPTH, P.PCB_Z0 + 1, P.M3_INSERT_HOLE)

    # wall-mount holes, countersunk from inside
    h_csk = (P.MOUNT_CSK_D - P.MOUNT_HOLE_D) / 2
    for x, y in P.MOUNT_HOLES:
        part -= cyl_z(x, y, -1, P.T_BACK + 1, P.MOUNT_HOLE_D)
        part -= Pos(x, y, P.T_BACK - h_csk) * Cone(P.MOUNT_HOLE_D / 2, P.MOUNT_CSK_D / 2, h_csk + 0.01,
                                                     align=(Align.CENTER, Align.CENTER, Align.MIN))

    # M20 gland in the bottom wall (under TB1) and PB1 on the left wall: teardrops (horizontal holes)
    part -= teardrop("Y", (P.GLAND_X, -1, P.GLAND_Z), P.RIM_W + 2, P.GLAND_HOLE_D)
    part -= teardrop("X", (-1, P.PB1_Y, P.PB1_Z), P.RIM_W + 2, P.PB1_HOLE_D)
    return part


# ── cover ────────────────────────────────────────────────────────────────────
def well_cavity() -> Part:
    grow = P.WELL_DEPTH - P.WELL_STRAIGHT
    r_top = P.WELL_R_OPEN + grow
    cav = rr(P.WELL_W, P.WELL_H, r_top, P.D - P.WELL_STRAIGHT, P.WELL_STRAIGHT + 1, P.WELL_CX, P.WELL_CY)
    cav += rr(P.WELL_OPEN_W, P.WELL_OPEN_H, P.WELL_R_OPEN, P.D - P.WELL_DEPTH, grow, P.WELL_CX, P.WELL_CY, taper=-45)
    cav += rr(P.WELL_OPEN_W, P.WELL_OPEN_H, P.WELL_R_OPEN, P.D - P.WELL_DEPTH - P.WELL_FLOOR_T - 1,
              P.WELL_FLOOR_T + 2, P.WELL_CX, P.WELL_CY)
    return cav


def well_block_z0() -> float:
    return P.D - P.WELL_DEPTH - P.WELL_FLOOR_T


def well_block_size():
    e = P.WELL_BLOCK_EXTRA
    return P.WELL_W + 2 * P.WELL_WALL + 2 * e, P.WELL_H + 2 * P.WELL_WALL + 2 * e


def well_block() -> Part:
    gw, gh = well_block_size()
    return rr(gw, gh, 2.0, well_block_z0(), P.D - well_block_z0(), P.WELL_CX, P.WELL_CY)


def well_pocket() -> Part:
    gw, gh = well_block_size()
    z0 = well_block_z0()
    z_face = P.D - P.WELL_DEPTH               # socket face plane (end of the floor)
    z_str = P.D - P.WELL_STRAIGHT             # start of the straight section
    off = P.WELL_SHELL * math.sqrt(2)         # horizontal offset of a 45° shell
    ow, oh = P.WELL_OPEN_W + 2 * off, P.WELL_OPEN_H + 2 * off
    pocket = rr(gw - 2 * P.WELL_WALL, gh - 2 * P.WELL_WALL, 1.0, z0 - 1, z_str - z0 + 1, P.WELL_CX, P.WELL_CY)
    keep = rr(ow, oh, P.WELL_R_OPEN + off, z0 - 2, z_face - z0 + 2, P.WELL_CX, P.WELL_CY)
    keep += rr(ow, oh, P.WELL_R_OPEN + off, z_face, z_str - z_face + 0.01, P.WELL_CX, P.WELL_CY, taper=-45)
    for x, y in insert_screws():
        keep += cyl_z(x, y, z0 - 2, z_str + 0.01, P.WELL_POST_D)
    return pocket - keep


def make_cover() -> Part:
    t, R, z0 = P.T_WALL, P.R_CORNER, P.D_BASE
    part = rr(P.W, P.H, R, z0, P.D_COVER)
    part -= rr(P.W - 2 * P.RIM_W, P.H - 2 * P.RIM_W, R - P.RIM_W, z0 - 1, P.RIM_H_COVER + 1)
    part -= rr(P.W - 2 * P.RIM_W, P.H - 2 * P.RIM_W, R - P.RIM_W, z0 + P.RIM_H_COVER, P.CHAMFER_45, taper=-45)
    z_main = z0 + P.RIM_H_COVER + P.CHAMFER_45
    part -= rr(P.W - 2 * t, P.H - 2 * t, R - t, z_main, P.D - P.T_FRONT - z_main)

    # screw bosses, clearance + counterbore from the front
    for x, y in corners(P.SCREW_INSET):
        part += cyl_z(x, y, z0, P.D, P.BOSS_D)
        part -= cyl_z(x, y, z0 - 1, P.D + 1, P.M4_CLEAR)
        part -= cyl_z(x, y, z0 + P.COVER_BOSS_SOLID, P.D + 1, P.M4_CBORE_D)

    # socket well: block, stepped funnel (straight + 45°), floor opening; the block is hollowed from
    # the back (open pocket, prints face-down) leaving a 2.5 mm funnel shell, a seal ring for the
    # insert plate, and four corner posts that take the insert screws
    part += well_block()
    part -= well_cavity()
    part -= well_pocket()
    for x, y in insert_screws():
        part -= cyl_z(x, y, well_block_z0() - 1, well_block_z0() + P.M3_INSERT_DEPTH, P.M3_INSERT_HOLE)

    # emergency stop
    part -= cyl_z(P.ESTOP_X, P.ESTOP_Y, P.D - P.T_FRONT - 1, P.D + 1, P.ESTOP_HOLE_D)

    # window behind the lock housing + pads with M3 inserts for the housing and the hinge brackets
    hw = P.BUMP_W / 2 - P.BUMP_WALL
    part -= box(P.BUMP_CX - hw, P.BUMP_CX + hw, P.BUMP_Y0 + P.BUMP_WALL, P.BUMP_Y0 + P.BUMP_H - P.BUMP_WALL,
                P.D - P.T_FRONT - 1, P.D + 1)
    for x, y in housing_screws() + bracket_screws():
        part += cyl_z(x, y, P.D - P.T_FRONT - 6, P.D - P.T_FRONT, 8.0)
        part -= cyl_z(x, y, P.D - P.M3_INSERT_DEPTH - 0.5, P.D + 1, P.M3_INSERT_HOLE)
    return part


# ── lid ──────────────────────────────────────────────────────────────────────
def make_lid(engrave: bool = True) -> Part:
    cx = P.W / 2
    h = P.LID_Y1 - P.LID_Y0
    cy = P.LID_Y0 + h / 2
    z0 = P.D + P.LID_GAP
    part = rr(P.LID_W, h, 6.0, z0, P.LID_DEPTH - P.LID_GAP, cx, cy)
    part -= rr(P.LID_W - 2 * P.LID_WALL, h - 2 * P.LID_WALL, 6.0 - P.LID_WALL, z0 - 1,
               P.LID_DEPTH - P.LID_GAP - P.LID_FRONT_T + 1, cx, cy)

    # cable notch in the bottom wall (keeps a front lip)
    part -= box(cx - P.CABLE_NOTCH_W / 2, cx + P.CABLE_NOTCH_W / 2, P.LID_Y0 - 1, P.LID_Y0 + P.LID_WALL + 1,
                z0 - 1, P.D + P.LID_DEPTH - 4)

    # lock catch: pad under the bottom wall, plunger hole, magnet pocket
    zc = P.D + 5.5
    part += box(P.BUMP_CX - 10, P.BUMP_CX + 10, P.LID_Y0 - P.LID_PAD_T, P.LID_Y0 + 0.01, z0, P.D + 14)
    part -= cyl_axis("Y", (P.BUMP_CX, P.LID_Y0 - P.LID_PAD_T - 1, zc), P.LID_WALL + P.LID_PAD_T + 2,
                     P.PLUNGER_HOLE_D + 0.8)
    mz = P.D + 11.0
    part -= cyl_axis("Y", (P.BUMP_CX, P.LID_Y0 + P.LID_WALL - P.MAGNET[1] - 0.2, mz), P.MAGNET[1] + 1,
                     P.MAGNET[0] + 0.2)

    # hinge knuckle + web + 45° gusset (so the lid prints front-down without supports)
    L = P.LID_KNUCKLE_L
    part += cyl_axis("X", (cx - L / 2, P.HINGE_Y, P.HINGE_Z), L, P.KNUCKLE_OD)
    part += box(cx - L / 2, cx + L / 2, P.LID_Y1 - P.LID_WALL, P.HINGE_Y, z0, P.HINGE_Z + 3)
    reach = P.HINGE_Y + P.KNUCKLE_OD / 2 - P.LID_Y1
    gus = Polygon((P.LID_Y1, P.HINGE_Z + P.KNUCKLE_OD / 2),
                  (P.LID_Y1 + reach, P.HINGE_Z + P.KNUCKLE_OD / 2),
                  (P.LID_Y1, P.HINGE_Z + P.KNUCKLE_OD / 2 + reach), align=None)
    part += Plane(origin=(cx - L / 2, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0)) * extrude(gus, amount=L)
    part -= cyl_axis("X", (cx - L / 2 - 1, P.HINGE_Y, P.HINGE_Z), L + 2, P.PIN_HOLE_LID)

    if engrave:
        try:
            txt = Plane.XY.offset(P.D + P.LID_DEPTH - 0.6) * Pos(cx, cy - 10) * Text("FLUXIO", font_size=12)
            part -= extrude(txt, amount=1)
        except Exception:  # no fonts in some CI images: the lid is still valid without the logo
            pass
    return part


# ── small parts ──────────────────────────────────────────────────────────────
def make_hinge_bracket(side: int = 1) -> Part:
    """Right bracket for side=+1; the left one is the same part rotated 180° about Z."""
    cx = P.W / 2
    x_in = P.LID_KNUCKLE_L / 2 + P.KNUCKLE_GAP
    px, py, pz = P.BRACKET_PLATE
    part = box(cx + x_in, cx + x_in + px, P.HINGE_Y - py / 2, P.HINGE_Y + py / 2, P.D, P.D + pz)
    part += cyl_axis("X", (cx + x_in, P.HINGE_Y, P.HINGE_Z), P.BRACKET_KNUCKLE_L, P.KNUCKLE_OD)
    part -= cyl_axis("X", (cx + x_in - 1, P.HINGE_Y, P.HINGE_Z), P.BRACKET_KNUCKLE_L + 2, P.PIN_HOLE_BRACKET)
    part -= cyl_z(cx + P.BRACKET_SCREW_X, P.HINGE_Y, P.D - 1, P.D + pz + 1, 3.4)
    if side < 0:
        part = part.rotate(Axis((cx, P.HINGE_Y, 0), (0, 0, 1)), 180)
    return part


def make_lock_housing() -> Part:
    cx = P.BUMP_CX
    w2, f = P.BUMP_W / 2, P.HOUSING_FLANGE
    y0, y1 = P.BUMP_Y0, P.BUMP_Y0 + P.BUMP_H
    part = box(cx - w2, cx + w2, y0, y1, P.D, P.D + P.BUMP_DEPTH)
    part += box(cx - w2 - f, cx + w2 + f, y0 + P.HOUSING_FLANGE_Y0, y1, P.D, P.D + P.HOUSING_FLANGE_T)
    i = P.BUMP_WALL
    part -= box(cx - w2 + i, cx + w2 - i, y0 + i, y1 - i, P.D - 1, P.D + P.BUMP_DEPTH - i)
    part -= cyl_axis("Y", (cx, y0 - 1, P.D + 5.5), i + 2, P.PLUNGER_HOLE_D)
    for x, y in housing_screws():
        part -= cyl_z(x, y, P.D - 1, P.D + P.HOUSING_FLANGE_T + 1, 3.4)
    return part


def make_socket_insert() -> Part:
    z1 = well_block_z0()
    part = rr(P.INSERT_W, P.INSERT_H, 4.0, z1 - P.INSERT_T, P.INSERT_T, P.WELL_CX, P.WELL_CY)
    part -= box(P.WELL_CX - P.INSERT_CUT_W / 2, P.WELL_CX + P.INSERT_CUT_W / 2,
                P.WELL_CY - P.INSERT_CUT_H / 2, P.WELL_CY + P.INSERT_CUT_H / 2, z1 - P.INSERT_T - 1, z1 + 1)
    for x, y in insert_screws():
        part -= cyl_z(x, y, z1 - P.INSERT_T - 1, z1 + 1, 3.4)
    return part


# ── reference envelopes (not printed): used by the tests and the renders ─────
# `m` grows the envelope by a clearance margin (XY and towards +Z where it makes sense).
def pcb_board(m: float = 0.0) -> Part:
    return box(P.PCB_X0 - m, P.PCB_X0 + P.PCB_W + m, P.PCB_Y0 - m, P.PCB_Y0 + P.PCB_H + m,
               P.PCB_Z0, P.PCB_Z0 + P.PCB_T)


def pcb_tall_zone(m: float = 0.0) -> Part:
    z = P.PCB_Z0 + P.PCB_T
    return box(P.PCB_X0 + P.TALL_ZONE_X[0] - m, P.PCB_X0 + P.TALL_ZONE_X[1] + m,
               P.PCB_Y0 - m, P.PCB_Y0 + P.PCB_H + m, z, z + P.TALL_H + m)


def pcb_low_zone(m: float = 0.0) -> Part:
    z = P.PCB_Z0 + P.PCB_T
    return box(P.PCB_X0 + P.TALL_ZONE_X[1] - m, P.PCB_X0 + P.PCB_W + m,
               P.PCB_Y0 - m, P.PCB_Y0 + P.PCB_H + m, z, z + P.LOW_H + m)


def pcb_all(m: float = 0.0) -> Part:
    return pcb_board(m) + pcb_tall_zone(m) + pcb_low_zone(m)


def socket_body(m: float = 0.0) -> Part:
    z1 = well_block_z0() - P.INSERT_T
    return cyl_z(P.WELL_CX, P.WELL_CY, z1 - P.SOCKET_BODY_DEPTH - m, z1, P.SOCKET_BODY_D + 2 * m)


def plug(m: float = 0.0) -> Part:
    z0 = P.D - P.WELL_DEPTH
    return cyl_z(P.WELL_CX, P.WELL_CY, z0 + 0.01, z0 + P.PLUG_LEN + m, P.PLUG_D + 2 * m)


def estop_body(m: float = 0.0) -> Part:
    z1 = P.D - P.T_FRONT
    return cyl_z(P.ESTOP_X, P.ESTOP_Y, z1 - P.ESTOP_DEPTH - m, z1 - 0.01, P.ESTOP_BODY_D + 2 * m)


def estop_head() -> Part:
    return cyl_z(P.ESTOP_X, P.ESTOP_Y, P.D + 0.01, P.D + 28, P.ESTOP_HEAD_D)


def pb1_body(m: float = 0.0) -> Part:
    return cyl_axis("X", (P.T_WALL + 0.01, P.PB1_Y, P.PB1_Z), P.PB1_DEPTH + m, P.PB1_BODY_D + 2 * m)


def solenoid_y0() -> float:
    return P.BUMP_Y0 + P.BUMP_WALL + P.SOLENOID_STROKE + 0.5


def solenoid() -> Part:
    sx, sy, sz = P.SOLENOID
    y0 = solenoid_y0()
    zc = P.D + 5.5
    return box(P.BUMP_CX - sx / 2, P.BUMP_CX + sx / 2, y0, y0 + sy, zc - sz / 2, zc + sz / 2)


def plunger_tip_y(extended: bool) -> float:
    return solenoid_y0() - P.PLUNGER_PROTRUSION - (P.SOLENOID_STROKE if extended else 0.0)


def mount_screw_heads() -> Part:
    out = None
    for x, y in P.MOUNT_HOLES:
        c = cyl_z(x, y, P.T_BACK, P.T_BACK + 4.0, P.MOUNT_CSK_D)
        out = c if out is None else out + c
    return out


def gland_nut() -> Part:
    return cyl_axis("Y", (P.GLAND_X, P.T_WALL + 0.01, P.GLAND_Z), 6.0, P.GLAND_NUT_D)


# ── assembly / export ────────────────────────────────────────────────────────
def lid_at(angle_deg: float = 0.0) -> Part:
    lid = make_lid()
    if angle_deg:
        lid = lid.rotate(Axis((0, P.HINGE_Y, P.HINGE_Z), (1, 0, 0)), -angle_deg)
    return lid


def printed_parts() -> dict[str, Part]:
    return {
        "base": make_base(),
        "cover": make_cover(),
        "lid": make_lid(),
        "hinge_bracket": make_hinge_bracket(1),
        "lock_housing": make_lock_housing(),
        "socket_insert": make_socket_insert(),
    }


PRINT_COUNT = {"base": 1, "cover": 1, "lid": 1, "hinge_bracket": 2, "lock_housing": 1, "socket_insert": 1}
# How each part lies on the bed: rotation about X (degrees) before dropping it to z = 0.
PRINT_ORIENTATION = {"base": 0, "cover": 180, "lid": 180, "hinge_bracket": 0, "lock_housing": 0, "socket_insert": 0}


def print_oriented(name: str, part: Part) -> Part:
    p = part.rotate(Axis.X, PRINT_ORIENTATION[name]) if PRINT_ORIENTATION[name] else part
    bb = p.bounding_box()
    return p.moved(Location((-bb.min.X, -bb.min.Y, -bb.min.Z)))


def export_all(out: pathlib.Path = OUT) -> dict[str, Part]:
    out.mkdir(parents=True, exist_ok=True)
    parts = printed_parts()
    for name, part in parts.items():
        export_stl(print_oriented(name, part), str(out / f"{name}.stl"), tolerance=0.02, angular_tolerance=0.15)
    assembly = Compound([*parts.values(), make_hinge_bracket(-1)])
    export_step(assembly, str(out / "ocpp_socket_enclosure_assembly.step"))
    return parts


if __name__ == "__main__":
    for name, part in export_all().items():
        bb = print_oriented(name, part).bounding_box()
        print(f"{name:14s} vol={part.volume / 1000:7.1f} cm³  bed={bb.size.X:6.1f} x {bb.size.Y:6.1f} x {bb.size.Z:5.1f}  valid={part.is_valid}")
