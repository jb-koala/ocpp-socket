"""Parameters of the OCPP Socket enclosure (all values in mm unless noted).

Frame (wall-mounted orientation):
    X = width (left -> right), Y = height (bottom -> top), Z = depth (0 at the wall, + outward).

Every number that comes from a real part is marked CONFIRM: it is a reasonable default taken from
datasheets of typical parts, and has to be checked against the part actually bought before printing
the final version. Changing a value here and re-running `make mech` rebuilds everything and re-runs
the interference tests.
"""
import math

# ── Overall box ───────────────────────────────────────────────────────────────
W = 130.0            # outer width
H = 190.0            # outer height
D_BASE = 40.0        # depth of the rear shell (base)
D_COVER = 30.0       # depth of the front cover
D = D_BASE + D_COVER # total depth (wall to front face)
R_CORNER = 8.0       # outer radius of the vertical edges

T_WALL = 2.5         # side walls (FDM: 5-6 perimeters with a 0.45 mm nozzle; typical for injection too)
T_BACK = 3.0         # base back plate (takes the wall-mount screws)
T_FRONT = 3.0        # cover front plate

# ── Base/cover joint: rim flange + gasket groove on the base, flat face on the cover ──
RIM_W = 6.0          # width of the mating rim (wall + inward flange)
RIM_H = 6.0          # height of the rim flange on the base (and 4 on the cover)
RIM_H_COVER = 4.0
CHAMFER_45 = RIM_W - T_WALL   # 45° chamfer under the flange so it prints without supports
GASKET_CORD_D = 2.4  # EPDM/silicone cord. CONFIRM with the cord bought
GROOVE_W = 2.8
GROOVE_D = 1.8       # compression = (2.4-1.8)/2.4 = 25 %; fill = cord area / groove area ≈ 90 %

# ── Cover screws (M4 into heat-set inserts in the base) ───────────────────────
SCREW_INSET = 10.5   # boss centre from the outer edges (keeps the screws inside the gasket)
BOSS_D = 10.0
M4_INSERT_HOLE = 5.6 # M4 heat-set insert, CONFIRM with insert datasheet
M4_INSERT_DEPTH = 9.0
M4_CLEAR = 4.5
M4_CBORE_D = 8.5
COVER_BOSS_SOLID = 6.0  # material left under the screw head in the cover boss

# ── PCB (hw/mainboard-revB) ───────────────────────────────────────────────────
PCB_W = 100.0
PCB_H = 80.0
PCB_T = 1.6
PCB_X0 = (W - PCB_W) / 2      # 15.0
PCB_Y0 = 17.0
PCB_HOLE_INSET = 4.0          # mounting holes Ø3.2 at 4 mm from each corner -> hw keep-out
STANDOFF_H = 6.0
STANDOFF_D = 8.0
M3_INSERT_HOLE = 4.0          # short M3 heat-set insert, CONFIRM
M3_INSERT_DEPTH = 5.5
PCB_Z0 = T_BACK + STANDOFF_H  # bottom face of the PCB
# Component height zones on the PCB (these become keep-outs in hw/mainboard-revB/keepouts.md)
TALL_ZONE_X = (0.0, 65.0)     # PCB-local X range where tall parts go (TB1, PS1, K1, T1, TR1, L1, C4)
TALL_H = 32.0                 # max height above the board in the tall zone (HLK-10M12 ≈ 21.5, K1 ≈ 25)
LOW_H = 12.0                  # max height above the board everywhere else (WROOM, ATM90E26, USB-C, buck)

# ── Socket well (front, upper zone) ───────────────────────────────────────────
WELL_W = 72.0
WELL_H = 78.0
WELL_DEPTH = 20.0             # socket face plane at z = D - WELL_DEPTH
WELL_STRAIGHT = 9.0           # straight part, then a 45° funnel down to the opening (prints face-down)
WELL_WALL = 2.5
WELL_OPEN_W = 50.0            # opening in the floor where the socket face shows
WELL_OPEN_H = 56.0
WELL_FLOOR_T = 3.0
WELL_CX = W / 2
WELL_CY = 124.0               # chosen so the socket body clears the PCB by ≥ 4 mm
WELL_R_OPEN = 2.0             # corner radius of the floor opening; the funnel grows it by 11
HOUSING_FLANGE = 5.0          # lock housing flange margin (sides only: the well opening is just above)
HOUSING_FLANGE_Y0 = 4.0       # flange starts this far above the housing bottom (clears the lid's inner corner radius)
HOUSING_FLANGE_T = 2.0
assert abs((WELL_W - WELL_OPEN_W) / 2 - (WELL_DEPTH - WELL_STRAIGHT)) < 1e-6, "funnel must be 45°"
assert abs((WELL_H - WELL_OPEN_H) / 2 - (WELL_DEPTH - WELL_STRAIGHT)) < 1e-6, "funnel must be 45°"

# Socket insert plate: screwed from INSIDE against the back of the well block (decision 0010 pending)
INSERT_W = 80.0
INSERT_H = 86.0
INSERT_T = 3.0
INSERT_CUT_W = 45.0           # CONFIRM: cutout for the chosen socket (IRAM 2071 or Schuko panel insert)
INSERT_CUT_H = 45.0
INSERT_SCREW_DX = 35.5        # M3 screws at (±DX, ±DY) from the well centre, in posts outside the funnel
INSERT_SCREW_DY = 38.5
WELL_BLOCK_EXTRA = 2.0        # block grows by this per side so the corner posts fit
WELL_POST_D = 7.0
WELL_SHELL = 2.5              # wall thickness of the hollowed funnel (normal to the 45° face)
SOCKET_BODY_D = 44.0          # CONFIRM: envelope of the socket body behind its face
SOCKET_BODY_DEPTH = 34.0
# Plug in use (CONFIRM with the Mode 2 chargers of the test matrix)
PLUG_D = 42.0
PLUG_LEN = 45.0               # protrusion from the socket face
CABLE_D = 12.0

# ── Lid lock bump (below the well): solenoid + Hall sensor, plunger exits downward ──
BUMP_W = 24.0
BUMP_H = 30.0                 # fits the solenoid + stroke with 1.5 mm to spare
BUMP_DEPTH = 14.0
BUMP_WALL = 2.0
BUMP_CX = W / 2 + 22.0        # off-centre: the cable notch is at the centre
BUMP_Y0 = 52.5                # bottom of the bump (just above the lid's bottom wall)
PLUNGER_HOLE_D = 4.6
SOLENOID = (12.0, 20.0, 11.0) # X, Y, Z body of a mini push-pull 12 V solenoid. CONFIRM (e.g. JF-0420B)
SOLENOID_PLUNGER_D = 4.0
SOLENOID_STROKE = 4.0
PLUNGER_PROTRUSION = 4.8      # plunger beyond the body when RETRACTED (CONFIRM; cut the plunger to length)
PLUNGER_ENGAGE = 2.0          # minimum engagement into the lid catch when extended
MAGNET = (6.0, 3.0)           # Ø x thick neodymium disc in the lid, sensed by a Hall switch in the bump

# ── Lid (hood over the well, hinged at the top) ───────────────────────────────
LID_CLEAR = 2.0               # side clearance between the hood and the well block / bump
LID_WALL = 2.2
LID_FRONT_T = 2.5
LID_GAP = 0.5                 # gap between the hood's back edge and the cover front face
LID_DEPTH = 34.0
LID_Y0 = BUMP_Y0 - LID_WALL - 0.3
LID_Y1 = 166.0                # top of the hood (below the hinge brackets)
LID_PAD_T = 1.8               # local pad under the lid bottom wall for the magnet pocket
CABLE_NOTCH_W = 16.0
HINGE_Y = 171.0
HINGE_Z = D + 5.0
KNUCKLE_OD = 8.0
PIN_D = 3.0                   # Ø3 steel rod or M3 screw
PIN_HOLE_LID = 3.25
PIN_HOLE_BRACKET = 2.95       # slight press fit
LID_KNUCKLE_L = 50.0
BRACKET_KNUCKLE_L = 14.0
BRACKET_PLATE = (22.6, 9.0, 3.0)  # per side: X from the lid knuckle end outward, Y, Z
BRACKET_SCREW_X = 44.0        # from the centre line
KNUCKLE_GAP = 0.4
LID_W = (WELL_W + 2 * WELL_WALL) + 2 * LID_CLEAR + 2 * LID_WALL

# ── Front controls ────────────────────────────────────────────────────────────
ESTOP_HOLE_D = 22.3           # standard 22 mm emergency stop
ESTOP_HEAD_D = 40.0
ESTOP_BODY_D = 32.0           # contact block envelope. CONFIRM
ESTOP_DEPTH = 40.0            # behind the front panel. CONFIRM
ESTOP_X = W - 30.0
ESTOP_Y = 26.0
PB1_HOLE_D = 12.2             # QN12-L1-RGB on the LEFT side wall (as in the sketch)
PB1_BODY_D = 16.0
PB1_DEPTH = 20.0
PB1_Y = 135.0
PB1_Z = 22.0                  # in the base wall, below the rim flange

# ── Base: wall mounting and cable entry ───────────────────────────────────────
MOUNT_HOLES = [(25.0, 10.0), (W - 25.0, 10.0), (25.0, H - 25.0), (W - 25.0, H - 25.0)]
MOUNT_HOLE_D = 5.0
MOUNT_CSK_D = 10.0
GLAND_HOLE_D = 20.5           # M20 cable gland, cable Ø6-12 mm
GLAND_X = 40.0                # under TB1 (left part of the PCB)
GLAND_Z = T_BACK + 15.0
GLAND_NUT_D = 26.0

# ── Printing / material ───────────────────────────────────────────────────────
BED = (220.0, 220.0, 250.0)   # printer build volume, CONFIRM with your printer
DENSITY_ASA = 1.07e-3         # g/mm³
PRINT_FILL_FACTOR = 0.85      # 6 perimeters + 30 % infill on 3 mm walls ≈ 85 % of solid
FILAMENT_USD_PER_KG = 22.0

# ── Minimum clearances checked by the tests ───────────────────────────────────
CLEAR_PCB = 2.0
CLEAR_SOCKET_PCB = 4.0
CLEAR_PLUG_LID = 3.0
CLEAR_MOVING = 0.4
LID_OPEN_ANGLES = (30.0, 60.0, 95.0)  # the lid must swing through these without hitting anything


def gasket_compression() -> float:
    return (GASKET_CORD_D - GROOVE_D) / GASKET_CORD_D


def gasket_fill() -> float:
    return (math.pi * (GASKET_CORD_D / 2) ** 2) / (GROOVE_W * GROOVE_D)
