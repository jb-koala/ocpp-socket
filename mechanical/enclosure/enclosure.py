"""OCPP Socket enclosure v2 as code (build123d) — compact 110 x 110 box (decision 0012).

Parts (FDM, no supports, in the orientation given by PRINT_ORIENTATION):
    base           rear shell: PCB standoffs, gasket groove, wall slots, Ø20 knockouts, side holes for the
                   RGB button (left) and the emergency stop (right), clip pivot lugs, solenoid cradle
    cover          front frame: socket well (45° funnel), drain/cable channel, centre hinge knuckle
    lid            full-face smoked hood, two outer knuckles, cable notch
    clip           bottom latch: two arms (cable between them), hook over the lid; locked by the solenoid
    socket_insert  adapter plate for the IRAM 2071 socket, screwed from inside (decision 0010)

`python enclosure.py` exports print-oriented STL and an assembly STEP into ./out/.
Geometry lives in params.py; checks in mechanical/tests/test_enclosure.py.
"""
from __future__ import annotations

import math
import pathlib

from build123d import (
    Align, Axis, Box, Compound, Cylinder, Location, Part, Plane, Polygon, Pos,
    RectangleRounded, Text, export_step, export_stl, extrude, offset,
)

import params as P

OUT = pathlib.Path(__file__).parent / "out"
MIN = (Align.MIN, Align.MIN, Align.MIN)


# ── helpers ──────────────────────────────────────────────────────────────────
def rr(w, h, r, z0, d, cx=P.W / 2, cy=P.H / 2, taper=0.0) -> Part:
    r = max(min(r, min(w, h) / 2 - 0.01), 0.3)
    face = Plane.XY.offset(z0) * Pos(cx, cy) * RectangleRounded(w, h, r)
    return extrude(face, amount=d, taper=taper)


def box(x0, x1, y0, y1, z0, z1) -> Part:
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN)


def cyl_z(cx, cy, z0, z1, d) -> Part:
    return Pos(cx, cy, z0) * Cylinder(d / 2, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))


def axis_plane(axis: str, origin) -> Plane:
    """Local Z along `axis`, local Y towards +Z (print 'up' for the base)."""
    if axis == "X":
        return Plane(origin=origin, x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    if axis == "Y":
        return Plane(origin=origin, x_dir=(-1, 0, 0), z_dir=(0, 1, 0))
    raise ValueError(axis)


def cyl_axis(axis, origin, length, d) -> Part:
    return axis_plane(axis, origin) * Cylinder(d / 2, length, align=(Align.CENTER, Align.CENTER, Align.MIN))


def teardrop(axis, origin, length, d) -> Part:
    r = d / 2
    s = r / math.sqrt(2)
    tri = Polygon((-s, s), (s, s), (0, r * math.sqrt(2)), align=None)
    return cyl_axis(axis, origin, length, d) + axis_plane(axis, origin) * extrude(tri, amount=length)


def yz_prism(points, x0, x1) -> Part:
    """Extrude a polygon given in (y, z) along X from x0 to x1 (vertex order does not matter)."""
    area2 = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(points, points[1:] + points[:1]))
    if area2 < 0:  # clockwise polygons would extrude towards -X
        points = list(reversed(points))
    poly = Polygon(*points, align=None)
    return Plane(origin=(x0, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0)) * extrude(poly, amount=x1 - x0)


def slot_z(cx, cy, length, width, along, z0, z1) -> Part:
    """Stadium-shaped hole along Z; `along` is 'X' or 'Y' (direction of the long axis)."""
    half = (length - width) / 2
    dx, dy = (half, 0) if along == "X" else (0, half)
    s = cyl_z(cx - dx, cy - dy, z0, z1, width) + cyl_z(cx + dx, cy + dy, z0, z1, width)
    if along == "X":
        s += box(cx - half, cx + half, cy - width / 2, cy + width / 2, z0, z1)
    else:
        s += box(cx - width / 2, cx + width / 2, cy - half, cy + half, z0, z1)
    return s


def corners(inset):
    return [(inset, inset), (P.W - inset, inset), (inset, P.H - inset), (P.W - inset, P.H - inset)]


def pcb_holes():
    i = P.PCB_HOLE_INSET
    return [(P.PCB_X0 + x, P.PCB_Y0 + y) for x in (i, P.PCB_W - i) for y in (i, P.PCB_H - i)]


def insert_screws():
    return [(P.WELL_CX + sx * P.INSERT_SCREW_DX, P.WELL_CY + sy * P.INSERT_SCREW_DY)
            for sx in (-1, 1) for sy in (-1, 1)]


def mount_slots():
    x0, x1 = P.W / 2 - P.MOUNT_DX / 2, P.W / 2 + P.MOUNT_DX / 2
    y0, y1 = P.H / 2 - P.MOUNT_DY / 2, P.H / 2 + P.MOUNT_DY / 2
    return [(x0, y1, "Y"), (x1, y1, "Y"), (x0, y0, "X"), (x1, y0, "X")]


def clip_x():
    return P.W / 2 - P.CLIP_W / 2, P.W / 2 + P.CLIP_W / 2


# ── base ─────────────────────────────────────────────────────────────────────
def make_base() -> Part:
    t, R = P.T_WALL, P.R_CORNER
    z_ch = P.D_BASE - P.RIM_H - P.CHAMFER_45
    part = rr(P.W, P.H, R, 0, P.D_BASE)
    part -= rr(P.W - 2 * t, P.H - 2 * t, R - t, P.T_BACK, z_ch - P.T_BACK)
    part -= rr(P.W - 2 * t, P.H - 2 * t, R - t, z_ch, P.CHAMFER_45, taper=45)
    part -= rr(P.W - 2 * P.RIM_W, P.H - 2 * P.RIM_W, R - P.RIM_W, P.D_BASE - P.RIM_H, P.RIM_H + 1)

    o, i = P.RIM_W / 2 - P.GROOVE_W / 2, P.RIM_W / 2 + P.GROOVE_W / 2
    z_g = P.D_BASE - P.GROOVE_D
    part -= rr(P.W - 2 * o, P.H - 2 * o, R - o, z_g, P.GROOVE_D + 1) - rr(P.W - 2 * i, P.H - 2 * i, R - i, z_g, P.GROOVE_D + 1)

    for x, y in corners(P.SCREW_INSET):
        part += cyl_z(x, y, P.T_BACK, P.D_BASE, P.BOSS_D)
        part -= cyl_z(x, y, P.D_BASE - P.M3_INSERT_DEPTH, P.D_BASE + 1, P.M3_INSERT_HOLE)

    for x, y in pcb_holes():
        part += cyl_z(x, y, P.T_BACK - 0.1, P.PCB_Z0, P.STANDOFF_D)
        part -= cyl_z(x, y, P.PCB_Z0 - P.M3_INSERT_DEPTH + 0.5, P.PCB_Z0 + 1, P.M3_INSERT_HOLE)

    # feet on the back
    i_f = P.FEET_INSET
    for x, y in corners(i_f):
        part += cyl_z(x, y, -P.FEET[1], 0.01, P.FEET[0])

    # wall-mount slots (as drawn: top ones vertical, bottom ones horizontal)
    for x, y, along in mount_slots():
        part -= slot_z(x, y, P.MOUNT_SLOT[0], P.MOUNT_SLOT[1], along, -P.FEET[1] - 1, P.T_BACK + 1)

    # Ø20 knockouts: annular groove from inside, thin skin to punch out
    kr, g, skin = P.KNOCKOUT_D / 2, P.KNOCKOUT_GROOVE, P.KNOCKOUT_SKIN
    rx, ry = P.REAR_KO
    part -= cyl_z(rx, ry, skin, P.T_BACK + 1, 2 * kr + 2 * g) - cyl_z(rx, ry, skin - 1, P.T_BACK + 2, 2 * kr)
    ko = (cyl_axis("Y", (P.BOTTOM_KO_X, skin, P.BOTTOM_KO_Z), P.T_WALL - skin + 0.5, 2 * kr + 2 * g)
          - cyl_axis("Y", (P.BOTTOM_KO_X, skin - 1, P.BOTTOM_KO_Z), P.T_WALL + 2, 2 * kr))
    part -= ko

    # side holes: RGB button (left), emergency stop (right)
    part -= teardrop("X", (-1, P.SIDE_Y, P.SIDE_Z), t + 2, P.PB1_HOLE_D)
    part -= teardrop("X", (P.W - t - 1, P.SIDE_Y, P.SIDE_Z), t + 2, P.ESTOP_HOLE_D)

    # clip pivot lugs under the bottom face; 45° underside so they print without supports
    py, pz = P.CLIP_PIVOT
    depth = -py + 4.5
    lug = [(0.0, P.D_BASE - depth - 6.0 - 0.01), (-depth, P.D_BASE - 6.0), (-depth, P.D_BASE), (0.0, P.D_BASE)]
    cx0, cx1 = clip_x()
    for a, b in ((cx0 - P.CLEAR_MOVING - P.CLIP_LUG_T, cx0 - P.CLEAR_MOVING),
                 (cx1 + P.CLEAR_MOVING, cx1 + P.CLEAR_MOVING + P.CLIP_LUG_T)):
        part += yz_prism(lug, a, b)
    part -= cyl_axis("X", (cx0 - P.CLIP_LUG_T - 2, py, pz), P.CLIP_W + 2 * P.CLIP_LUG_T + 4, P.PIN_HOLE_FRAME)

    # solenoid cradle on the bottom wall, open towards the front, 45° wedge underneath
    sx, sy, sz = P.SOLENOID
    w = P.CRADLE_WALL
    cx = P.SOLENOID_X
    y_top = P.SOLENOID_Y0 + sy + w
    z_bot = P.SOLENOID_Z - sz / 2 - w
    part += box(cx - sx / 2 - w, cx + sx / 2 + w, P.T_WALL - 0.01, y_top, z_bot, P.D_BASE)
    part += yz_prism([(P.T_WALL - 0.01, z_bot - (y_top - P.T_WALL)), (y_top, z_bot + 0.01), (P.T_WALL - 0.01, z_bot + 0.01)],
                     cx - sx / 2 - w, cx + sx / 2 + w)
    part -= box(cx - sx / 2 - 0.2, cx + sx / 2 + 0.2, P.SOLENOID_Y0, P.SOLENOID_Y0 + sy + 0.2,
                P.SOLENOID_Z - sz / 2 - 0.2, P.D_BASE + 1)
    part -= teardrop("Y", (cx, -1, P.SOLENOID_Z), P.SOLENOID_Y0 + 1.01, P.PLUNGER_HOLE_D)
    return part


# ── cover (front frame) ──────────────────────────────────────────────────────
def well_block_z0() -> float:
    return P.D - P.WELL_DEPTH - P.WELL_FLOOR_T


def well_block_size():
    e = P.WELL_BLOCK_EXTRA
    return P.WELL_W + 2 * P.WELL_WALL + 2 * e, P.WELL_H + 2 * P.WELL_WALL + 2 * e


def well_block() -> Part:
    gw, gh = well_block_size()
    return rr(gw, gh, 2.0, well_block_z0(), P.D - well_block_z0(), P.WELL_CX, P.WELL_CY)


def well_cavity() -> Part:
    grow = P.WELL_DEPTH - P.WELL_STRAIGHT
    cav = rr(P.WELL_W, P.WELL_H, P.WELL_R_OPEN + grow, P.D - P.WELL_STRAIGHT, P.WELL_STRAIGHT + 1, P.WELL_CX, P.WELL_CY)
    cav += rr(P.WELL_OPEN_W, P.WELL_OPEN_H, P.WELL_R_OPEN, P.D - P.WELL_DEPTH, grow, P.WELL_CX, P.WELL_CY, taper=-45)
    cav += rr(P.WELL_OPEN_W, P.WELL_OPEN_H, P.WELL_R_OPEN, well_block_z0() - 1, P.WELL_FLOOR_T + 2, P.WELL_CX, P.WELL_CY)
    return cav


def well_pocket() -> Part:
    gw, gh = well_block_size()
    z0 = well_block_z0()
    z_face = P.D - P.WELL_DEPTH
    z_str = P.D - P.WELL_STRAIGHT
    off = P.WELL_SHELL * math.sqrt(2)
    ow, oh = P.WELL_OPEN_W + 2 * off, P.WELL_OPEN_H + 2 * off
    pocket = rr(gw - 2 * P.WELL_WALL, gh - 2 * P.WELL_WALL, 1.0, z0 - 1, z_str - z0 + 1, P.WELL_CX, P.WELL_CY)
    keep = rr(ow, oh, P.WELL_R_OPEN + off, z0 - 2, z_face - z0 + 2, P.WELL_CX, P.WELL_CY)
    keep += rr(ow, oh, P.WELL_R_OPEN + off, z_face, z_str - z_face + 0.01, P.WELL_CX, P.WELL_CY, taper=-45)
    for x, y in insert_screws():
        keep += cyl_z(x, y, z0 - 2, z_str + 0.01, P.WELL_POST_D)
    return pocket - keep


def channel_outline(grow: float = 0.0):
    y_top = P.WELL_CY - P.WELL_H / 2 + P.WELL_STRAIGHT  # overlaps the bottom of the well
    cx = P.W / 2
    pts = [(cx - P.CHANNEL_W_BOTTOM / 2, -2.0), (cx + P.CHANNEL_W_BOTTOM / 2, -2.0),
           (cx + P.CHANNEL_W_TOP / 2, y_top), (cx - P.CHANNEL_W_TOP / 2, y_top)]
    face = Polygon(*pts, align=None)
    return offset(face, amount=grow) if grow else face


def channel_cavity() -> Part:
    z_bot = P.D - P.CHANNEL_DEPTH
    inner = Plane.XY.offset(z_bot) * offset(channel_outline(), amount=-P.CHANNEL_DEPTH)
    return extrude(inner, amount=P.CHANNEL_DEPTH + 1, taper=-45)


def channel_block() -> Part:
    face = Plane.XY.offset(P.CHANNEL_BLOCK_Z0) * channel_outline(grow=P.WELL_WALL)
    blk = extrude(face, amount=P.D - P.CHANNEL_BLOCK_Z0)
    return blk & box(0, P.W, 0, P.H, 0, P.D + 1)


def make_cover() -> Part:
    t, R, z0 = P.T_WALL, P.R_CORNER, P.D_BASE
    part = rr(P.W, P.H, R, z0, P.D_COVER)
    part -= rr(P.W - 2 * P.RIM_W, P.H - 2 * P.RIM_W, R - P.RIM_W, z0 - 1, P.RIM_H_COVER + 1)
    part -= rr(P.W - 2 * P.RIM_W, P.H - 2 * P.RIM_W, R - P.RIM_W, z0 + P.RIM_H_COVER, P.CHAMFER_45, taper=-45)
    z_main = z0 + P.RIM_H_COVER + P.CHAMFER_45
    part -= rr(P.W - 2 * t, P.H - 2 * t, R - t, z_main, P.D - P.T_FRONT - z_main)

    for x, y in corners(P.SCREW_INSET):
        part += cyl_z(x, y, z0, P.D, P.BOSS_D)
        part -= cyl_z(x, y, z0 - 1, P.D + 1, P.M3_CLEAR)
        part -= cyl_z(x, y, z0 + P.COVER_BOSS_SOLID, P.D + 1, P.M3_CBORE_D)

    part += well_block() + channel_block()
    part -= well_cavity()
    part -= well_pocket()
    part -= channel_cavity()
    for x, y in insert_screws():
        part -= cyl_z(x, y, well_block_z0() - 1, well_block_z0() + P.M3_INSERT_DEPTH - 0.5, P.M3_INSERT_HOLE)

    # centre hinge knuckle on the top face (touches the bed when the frame prints face-down)
    L = P.FRAME_KNUCKLE_L
    part += cyl_axis("X", (P.W / 2 - L / 2, P.HINGE_Y, P.HINGE_Z), L, P.KNUCKLE_OD)
    part += box(P.W / 2 - L / 2, P.W / 2 + L / 2, P.H - 1.0, P.HINGE_Y, P.HINGE_Z - P.KNUCKLE_OD / 2, P.D)
    part -= cyl_axis("X", (P.W / 2 - L / 2 - 1, P.HINGE_Y, P.HINGE_Z), L + 2, P.PIN_HOLE_FRAME)
    return part


# ── lid ──────────────────────────────────────────────────────────────────────
def lid_knuckle_ranges():
    a = P.FRAME_KNUCKLE_L / 2 + P.KNUCKLE_GAP
    return [(P.W / 2 - a - P.LID_KNUCKLE_L, P.W / 2 - a), (P.W / 2 + a, P.W / 2 + a + P.LID_KNUCKLE_L)]


def make_lid(engrave: bool = True) -> Part:
    z0 = P.D + P.LID_GAP
    part = rr(P.W, P.H, P.R_CORNER, z0, P.LID_DEPTH - P.LID_GAP)
    part -= rr(P.W - 2 * P.LID_WALL, P.H - 2 * P.LID_WALL, P.R_CORNER - P.LID_WALL, z0 - 1,
               P.LID_DEPTH - P.LID_GAP - P.LID_FRONT_T + 1)

    # cable notch at the bottom (the cable then passes between the clip arms)
    part -= box(P.W / 2 - P.CABLE_NOTCH_W / 2, P.W / 2 + P.CABLE_NOTCH_W / 2, -1, P.LID_WALL + 1,
                z0 - 1, P.D + P.LID_DEPTH - 4)

    # two outer knuckles on arms above the top face + 45° gussets (lid prints face-down)
    r = P.KNUCKLE_OD / 2
    reach = P.HINGE_Y + r - P.H
    zt = z0 + 2.5
    for x0, x1 in lid_knuckle_ranges():
        part += cyl_axis("X", (x0, P.HINGE_Y, P.HINGE_Z), x1 - x0, P.KNUCKLE_OD)
        part += box(x0, x1, P.H + P.CLEAR_MOVING, P.HINGE_Y, P.HINGE_Z, zt)  # web only in front of the axis
        part += box(x0, x1, P.H - P.LID_WALL, P.H + P.CLEAR_MOVING + 0.01, z0, zt)
        part += yz_prism([(P.H, zt - 0.01), (P.H + reach, zt - 0.01), (P.H, zt + reach)], x0, x1)
    part -= cyl_axis("X", (lid_knuckle_ranges()[0][0] - 1, P.HINGE_Y, P.HINGE_Z), P.W, P.PIN_HOLE_LID)

    if engrave:
        try:
            txt = Plane.XY.offset(P.D + P.LID_DEPTH - 0.6) * Pos(P.W / 2, P.H / 2 - 30) * Text("FLUXIO", font_size=10)
            part -= extrude(txt, amount=1)
        except Exception:
            pass
    return part


# ── clip + socket insert ─────────────────────────────────────────────────────
def make_clip() -> Part:
    x0, x1 = clip_x()
    py, pz = P.CLIP_PIVOT
    y_top = -P.CLIP_ARM_GAP
    y_bot = y_top - P.CLIP_ARM_T
    z_hook = P.D + P.LID_DEPTH + 0.3
    part = cyl_axis("X", (x0, py, pz), x1 - x0, 2 * (py - y_bot))  # tube bottom flush with the arms
    for a, b in ((x0, x0 + P.CLIP_ARM_W), (x1 - P.CLIP_ARM_W, x1)):
        part += box(a, b, y_bot, y_top, pz, z_hook)
    part += box(x0, x1, y_bot, P.CLIP_HOOK_UP, z_hook, z_hook + P.CLIP_HOOK_T)
    part -= cyl_axis("X", (x0 - 1, py, pz), x1 - x0 + 2, P.PIN_HOLE_LID)
    # catch for the solenoid plunger in the right arm
    part -= cyl_axis("Y", (P.SOLENOID_X, y_top - P.PLUNGER_ENGAGE - 1.5, P.SOLENOID_Z), P.PLUNGER_ENGAGE + 2.5,
                     P.PLUNGER_HOLE_D + 0.4)
    return part


def make_socket_insert() -> Part:
    z1 = well_block_z0()
    part = rr(P.INSERT_W, P.INSERT_H, 4.0, z1 - P.INSERT_T, P.INSERT_T, P.WELL_CX, P.WELL_CY)
    part -= box(P.WELL_CX - P.INSERT_CUT_W / 2, P.WELL_CX + P.INSERT_CUT_W / 2,
                P.WELL_CY - P.INSERT_CUT_H / 2, P.WELL_CY + P.INSERT_CUT_H / 2, z1 - P.INSERT_T - 1, z1 + 1)
    for x, y in insert_screws():
        part -= cyl_z(x, y, z1 - P.INSERT_T - 1, z1 + 1, 3.4)
    return part


# ── reference envelopes (not printed) ────────────────────────────────────────
def pcb_board(m: float = 0.0) -> Part:
    return box(P.PCB_X0 - m, P.PCB_X0 + P.PCB_W + m, P.PCB_Y0 - m, P.PCB_Y0 + P.PCB_H + m,
               P.PCB_Z0, P.PCB_Z0 + P.PCB_T)


def pcb_components(m: float = 0.0) -> Part:
    """General height everywhere, lowered in each PCB_ZONES rectangle. Margin m grows it."""
    zt = P.PCB_Z0 + P.PCB_T
    x0, y0 = P.PCB_X0, P.PCB_Y0
    env = box(x0 - m, x0 + P.PCB_W + m, y0 - m, y0 + P.PCB_H + m, zt, zt + P.GENERAL_H + m)
    for zx0, zx1, zy0, zy1, h in P.PCB_ZONES.values():
        a = x0 + (zx0 + m if zx0 > 0 else -m - 1)
        b = x0 + (zx1 - m if zx1 < P.PCB_W else P.PCB_W + m + 1)
        c = y0 + (zy0 + m if zy0 > 0 else -m - 1)
        d = y0 + (zy1 - m if zy1 < P.PCB_H else P.PCB_H + m + 1)
        env -= box(a, b, c, d, zt + h + m, zt + P.GENERAL_H + m + 1)
    return env


def pcb_all(m: float = 0.0) -> Part:
    return pcb_board(m) + pcb_components(m)


def socket_body(m: float = 0.0) -> Part:
    z1 = well_block_z0() - P.INSERT_T
    return cyl_z(P.WELL_CX, P.WELL_CY, z1 - P.SOCKET_BODY_DEPTH - m, z1 - 0.01, P.SOCKET_BODY_D + 2 * m)


def plug(m: float = 0.0) -> Part:
    z0 = P.D - P.WELL_DEPTH
    return cyl_z(P.WELL_CX, P.WELL_CY, z0 + 0.01, z0 + P.PLUG_LEN + m, P.PLUG_D + 2 * m)


def estop_body(m: float = 0.0) -> Part:
    x = P.W - P.T_WALL - P.ESTOP_DEPTH - m
    return cyl_axis("X", (x, P.SIDE_Y, P.SIDE_Z), P.ESTOP_DEPTH + m - 0.01, P.ESTOP_BODY_D + 2 * m)


def estop_head() -> Part:
    return cyl_axis("X", (P.W + 0.01, P.SIDE_Y, P.SIDE_Z), 22.0, P.ESTOP_HEAD_D)


def pb1_body(m: float = 0.0) -> Part:
    return cyl_axis("X", (P.T_WALL + 0.01, P.SIDE_Y, P.SIDE_Z), P.PB1_DEPTH + m, P.PB1_BODY_D + 2 * m)


def pb1_head() -> Part:
    return cyl_axis("X", (-3.0, P.SIDE_Y, P.SIDE_Z), 3.0 - 0.01, 16.0)


def solenoid() -> Part:
    sx, sy, sz = P.SOLENOID
    return box(P.SOLENOID_X - sx / 2, P.SOLENOID_X + sx / 2, P.SOLENOID_Y0, P.SOLENOID_Y0 + sy,
               P.SOLENOID_Z - sz / 2, P.SOLENOID_Z + sz / 2)


def mount_screw_heads() -> Part:
    out = None
    for x, y, _ in mount_slots():
        c = cyl_z(x, y, P.T_BACK, P.T_BACK + P.MOUNT_HEAD[1], P.MOUNT_HEAD[0])
        out = c if out is None else out + c
    return out


def gland_nut() -> Part:
    return cyl_axis("Y", (P.BOTTOM_KO_X, P.T_WALL + 0.01, P.BOTTOM_KO_Z), 6.0, P.GLAND_NUT_D)


# ── assembly / export ────────────────────────────────────────────────────────
def lid_at(angle_deg: float = 0.0) -> Part:
    lid = make_lid()
    if angle_deg:
        lid = lid.rotate(Axis((0, P.HINGE_Y, P.HINGE_Z), (1, 0, 0)), -angle_deg)
    return lid


def clip_at(angle_deg: float = 0.0) -> Part:
    clip = make_clip()
    if angle_deg:
        py, pz = P.CLIP_PIVOT
        clip = clip.rotate(Axis((0, py, pz), (1, 0, 0)), angle_deg)  # positive: the hook swings down
    return clip


def printed_parts() -> dict[str, Part]:
    return {
        "base": make_base(),
        "cover": make_cover(),
        "lid": make_lid(),
        "clip": make_clip(),
        "socket_insert": make_socket_insert(),
    }


PRINT_COUNT = {"base": 1, "cover": 1, "lid": 1, "clip": 1, "socket_insert": 1}
PRINT_ORIENTATION = {"base": 0, "cover": 180, "lid": 180, "clip": 90, "socket_insert": 0}


def print_oriented(name: str, part: Part) -> Part:
    p = part.rotate(Axis.X, PRINT_ORIENTATION[name]) if PRINT_ORIENTATION[name] else part
    bb = p.bounding_box()
    return p.moved(Location((-bb.min.X, -bb.min.Y, -bb.min.Z)))


def export_all(out: pathlib.Path = OUT) -> dict[str, Part]:
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*"):
        old.unlink()
    parts = printed_parts()
    for name, part in parts.items():
        export_stl(print_oriented(name, part), str(out / f"{name}.stl"), tolerance=0.02, angular_tolerance=0.15)
    export_step(Compound(list(parts.values())), str(out / "ocpp_socket_enclosure_assembly.step"))
    return parts


if __name__ == "__main__":
    for name, part in export_all().items():
        bb = print_oriented(name, part).bounding_box()
        print(f"{name:14s} vol={part.volume / 1000:6.1f} cm³  bed={bb.size.X:6.1f} x {bb.size.Y:6.1f} x {bb.size.Z:5.1f}"
              f"  valid={part.is_valid}  solids={len(part.solids())}")
