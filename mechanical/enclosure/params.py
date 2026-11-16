"""Parameters of the OCPP Socket enclosure, v2 — compact 110 x 110 box after JB's reference drawing
(decision 0012). All values in mm unless noted.

Frame (wall-mounted orientation):
    X = width (left -> right), Y = height (bottom -> top), Z = depth (0 at the wall, + outward).

Values taken from the reference drawing are marked DRAWING. Values that come from a real part are
marked CONFIRM: check them against the part actually bought before printing the final version.
"""
import math

# ── Overall box (DRAWING: 110 x 110, body 82, lid 40, total 122, walls 2.0–2.5) ──
W = 110.0
H = 110.0
D_BASE = 70.0        # rear shell
D_COVER = 12.0       # front frame (the gasket line of the drawing sits here)
D = D_BASE + D_COVER # 82: front face of the frame
R_CORNER = 8.0
T_WALL = 2.5
T_BACK = 2.5
T_FRONT = 2.5
FEET = (8.0, 2.0)    # Ø x height, 4 feet on the back (DRAWING: small feet under the box)
FEET_INSET = 13.0

# ── Base/frame joint ──────────────────────────────────────────────────────────
RIM_W = 5.0
RIM_H = 5.0
RIM_H_COVER = 3.0
CHAMFER_45 = RIM_W - T_WALL
GASKET_CORD_D = 2.0  # CONFIRM with the cord bought
GROOVE_W = 2.3
GROOVE_D = 1.5       # compression 25 %, fill ≈ 91 %

# ── Frame screws: M3 into heat-set inserts in the base (DRAWING: 4 corner screws) ──
SCREW_INSET = 8.2
BOSS_D = 7.0
M3_INSERT_HOLE = 4.0 # CONFIRM with insert datasheet
M3_INSERT_DEPTH = 6.0
M3_CLEAR = 3.4
M3_CBORE_D = 6.5
COVER_BOSS_SOLID = 4.0

# ── Wall mounting (DRAWING: slots 70 mm apart horizontally, 55 mm vertically) ──
MOUNT_DX = 70.0
MOUNT_DY = 55.0
MOUNT_SLOT = (10.0, 5.0)  # long x wide; top slots vertical, bottom slots horizontal (as drawn)
MOUNT_HEAD = (9.0, 3.5)   # pan head Ø x height, sits on the inner back face under the PCB
KNOCKOUT_D = 20.0         # DRAWING: Ø20 knockouts
KNOCKOUT_SKIN = 0.8       # thin skin left to punch out
KNOCKOUT_GROOVE = 1.2
REAR_KO = (W / 2, H / 2)  # DRAWING: rear knockout in the centre (blocked by the PCB: see keepouts)
BOTTOM_KO_X = W / 2       # mains entry (M20 gland) in the bottom wall
BOTTOM_KO_Z = 30.0
GLAND_NUT_D = 26.0

# ── Side controls (JB 2026-11-16: in the side knockout positions) ─────────────
SIDE_Y = H / 2
SIDE_Z = 38.0
PB1_HOLE_D = 12.2         # QN12-L1-RGB, LEFT side
PB1_BODY_D = 16.0         # CONFIRM
PB1_DEPTH = 20.0          # CONFIRM
ESTOP_HOLE_D = 16.2       # compact Ø16 emergency stop, RIGHT side
ESTOP_HEAD_D = 30.0       # CONFIRM
ESTOP_BODY_D = 20.0       # CONFIRM
ESTOP_DEPTH = 28.0        # CONFIRM: behind the panel, with the NC contact block

# ── PCB rev B, now behind the socket, parallel to the wall ────────────────────
PCB_W = 100.0
PCB_H = 80.0
PCB_T = 1.6
PCB_X0 = (W - PCB_W) / 2  # 5
PCB_Y0 = 15.0
PCB_HOLE_INSET = 4.0
STANDOFF_H = 6.0
STANDOFF_D = 8.0
PCB_Z0 = T_BACK + STANDOFF_H
GENERAL_H = 45.0          # max component height where nothing is above (under the well block)
# Height-limited zones, PCB-local coordinates (x0, x1, y0, y1, max height). Derived from what is above;
# the tests check them against the real geometry and hw/mainboard-revB/keepouts.md documents them.
PCB_ZONES = {
    "socket": (24.0, 76.0, 24.0, 80.0, 17.0),   # under the socket body
    "pb1": (0.0, 20.0, 30.0, 50.0, 17.0),       # under the RGB button (left wall)
    "estop": (72.0, 100.0, 28.0, 52.0, 15.0),   # under the emergency stop (right wall)
    "lock": (51.0, 72.0, 0.0, 11.0, 33.0),      # under the solenoid cradle
}

# ── Socket well (DRAWING: 70 x 70, IRAM 2071 socket) ──────────────────────────
WELL_W = 70.0
WELL_H = 70.0
WELL_DEPTH = 16.0         # socket face at z = D - WELL_DEPTH
WELL_STRAIGHT = 6.0
WELL_WALL = 2.5
WELL_OPEN_W = 50.0
WELL_OPEN_H = 50.0
WELL_R_OPEN = 2.0
WELL_FLOOR_T = 3.0
WELL_CX = W / 2
WELL_CY = 65.0            # leaves room below for the drain channel and the lid lock
WELL_BLOCK_EXTRA = 2.0
WELL_POST_D = 7.0
WELL_SHELL = 2.5
assert abs((WELL_W - WELL_OPEN_W) / 2 - (WELL_DEPTH - WELL_STRAIGHT)) < 1e-6, "funnel must be 45°"
assert abs((WELL_H - WELL_OPEN_H) / 2 - (WELL_DEPTH - WELL_STRAIGHT)) < 1e-6, "funnel must be 45°"

INSERT_W = 78.0           # socket adapter plate, screwed from inside (decision 0010)
INSERT_H = 78.0
INSERT_T = 3.0
INSERT_CUT_W = 45.0       # CONFIRM with the IRAM 2071 module
INSERT_CUT_H = 45.0
INSERT_SCREW_DX = 35.5
INSERT_SCREW_DY = 35.5
SOCKET_BODY_D = 44.0      # CONFIRM
SOCKET_BODY_DEPTH = 28.0  # CONFIRM
PLUG_D = 42.0             # CONFIRM with the Mode 2 chargers of the test matrix
PLUG_LEN = 45.0
CABLE_D = 12.0

# Drain / cable channel from the bottom of the well to the bottom edge (DRAWING: ribbed funnel)
CHANNEL_W_TOP = 40.0
CHANNEL_W_BOTTOM = 20.0
CHANNEL_DEPTH = 6.0       # 45° sides: prints face-down without supports
CHANNEL_BLOCK_Z0 = D - CHANNEL_DEPTH - 2.0

# ── Lid: full-face smoked hood (DRAWING: 40 deep, same outline as the body) ──
LID_DEPTH = 40.0
LID_GAP = 0.5
LID_WALL = 2.2
LID_FRONT_T = 2.5
CABLE_NOTCH_W = 17.0
HINGE_Y = H + 4.0         # axis just above the top face (knuckles clear it by 0.5)
HINGE_Z = D - 3.5         # behind the front face: the frame knuckle touches the bed when printed face-down
KNUCKLE_OD = 7.0
PIN_D = 3.0
PIN_HOLE_LID = 3.25
PIN_HOLE_FRAME = 2.95
FRAME_KNUCKLE_L = 18.0    # centre knuckle, part of the frame
LID_KNUCKLE_L = 12.0      # two outer knuckles, part of the lid
KNUCKLE_GAP = 0.4

# ── Clip (DRAWING: latch at the bottom) + solenoid lock ──────────────────────
CLIP_W = 30.0
CLIP_ARM_W = 6.5          # two arms; the cable passes between them
CLIP_ARM_T = 7.5
CLIP_ARM_GAP = 1.5        # gap between the arm and the box bottom
CLIP_PIVOT = (-5.0, 63.0) # (y, z) of the pin, under the base
CLIP_HOOK_UP = 10.0       # how far the hook rises over the lid's front-bottom edge
CLIP_HOOK_T = 3.0
CLIP_LUG_T = 3.6
SOLENOID = (12.0, 16.0, 11.0)   # X, Y, Z. CONFIRM (mini 12 V push-pull, ~15 mm frame)
SOLENOID_X = W / 2 + CLIP_W / 2 - CLIP_ARM_W / 2   # above the right clip arm
SOLENOID_Z = 67.5
SOLENOID_STROKE = 4.0
SOLENOID_Y0 = RIM_W + 1.5       # body bottom, above the base rim
PLUNGER_D = 4.0
PLUNGER_HOLE_D = 4.6
PLUNGER_ENGAGE = 2.0
CRADLE_WALL = 1.6

# ── Printing / material ───────────────────────────────────────────────────────
BED = (220.0, 220.0, 250.0)     # CONFIRM with your printer
DENSITY_ASA = 1.07e-3           # g/mm³
FILAMENT_USD_PER_KG = 22.0

# ── Minimum clearances checked by the tests ───────────────────────────────────
CLEAR_PCB = 2.0
CLEAR_SOCKET_PCB = 4.0
CLEAR_PLUG_LID = 3.0
CLEAR_MOVING = 0.4
LID_OPEN_ANGLES = (30.0, 60.0, 95.0)


def gasket_compression() -> float:
    return (GASKET_CORD_D - GROOVE_D) / GASKET_CORD_D


def gasket_fill() -> float:
    return (math.pi * (GASKET_CORD_D / 2) ** 2) / (GROOVE_W * GROOVE_D)


def plunger_retracted_y() -> float:
    """Plunger tip when retracted: flush with the outside of the bottom wall."""
    return 0.0


def plunger_extended_y() -> float:
    return plunger_retracted_y() - SOLENOID_STROKE
