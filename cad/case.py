"""
bat706: 4S LiFePO4 pack (4 x 33.5 x 136.25 mm cells) + 60 x 120 x 10 mm BMS in a 3D-printed case
for the Icom IC-706MKII.

BMS centred over C2/C3 on a printed spacer; lid beams (rib + ridge + rib) clamp C1 and C4 and run
wall to wall, held by 3 side screws per long wall.

Parts (print orientation):
  base.stl         - tub: cradles, end stops + floor spars, corner bosses, 6 teardrop side-screw holes,
                     Powerpole notch (front-right corner) open at the rim, with a lead-in
  spacer.stl       - cell-shaped insulator over C2/C3 carrying the BMS (flat face on bed)
  lid.stl          - lid: 3 beam stations. Each = rib (BMS side fence on the spacer + saddle on C1/C4 +
                     wall-end block with a side nut slot) + ridge across the BMS. Corner pads on the BMS,
                     recessed Powerpole cradle + backstop, lead holes + snap-in zig-zags, vents
                     (outer face on bed)
  pp_clamp.stl     - Powerpole clamp bar (screws up into the lid from below)
  nut_plug_x6.stl  - glue-in plugs closing the side nut slots

Coordinate system (installed): X across the cells (C1 at -X), Y along the cells (+Y = FRONT, the
Powerpole end), Z up from the base's bed face.

Run:  python case.py   -> STL + STEP into ./out
"""
import os
import cadquery as cq

# ---------------------------------------------------------------- cells, BMS, Powerpoles (measured / datasheet)
CELL_D = 33.5                                  # cell diameter (measured)
CELL_L = 136.25                                # cell body length, excluding tabs (measured)
TAB_W, TAB_T = 20.0, 2.0                       # copper tab width and height above the cell end
CELL_CLR_D = 0.6                               # diametral clearance in the base cradles
CELL_GAP = 1.0                                 # gap between neighbouring cells
N_CELLS = 4
BMS_W, BMS_L, BMS_T = 60.0, 120.0, 10.0
BMS_CLR = 0.6                                  # clearance between the BMS and the lid rib fences
PP_SQ = 7.9                                    # Powerpole housing cross-section (each)
PP_L = 24.6                                    # housing length
PP_N = 2
PP_CLR = 0.25                                  # per side, wall notch and cradle

# ---------------------------------------------------------------- shell
WALL = 2.4                                     # side/end wall thickness
FLOOR = 2.0
SADDLE = 1.0                                   # material under each cell at the lowest point of a cradle
LID_T = 2.0
R_VERT = 6.0                                   # vertical-corner fillet radius (outside)
CHAMFER_BED = 1.2                              # 45-degree chamfer on bed-facing edges
INSERT_D = 4.2                                 # M3 heat-set insert hole
BOSS_D = 9.0                                   # corner boss

# ---------------------------------------------------------------- cell stack
PITCH = CELL_D + CELL_GAP
IN_W = N_CELLS * PITCH + 1.0                   # interior width
OUT_W = IN_W + 2 * WALL
Z_CELL_BOT = FLOOR + SADDLE
Z_CELL_CTR = Z_CELL_BOT + CELL_D / 2
Z_CELL_TOP = Z_CELL_BOT + CELL_D
cell_x = [-IN_W / 2 + 0.5 + PITCH / 2 + i * PITCH for i in range(N_CELLS)]
SEAT_GAP = 0.5                                 # cell surface -> spacer / lid-rib seat; filled with 1 mm foam tape
SPACER_CREST = 1.5                             # spacer thickness over the top of C2/C3
R_SEAT = CELL_D / 2 + SEAT_GAP
Z_BMS_BOT = Z_CELL_TOP + SEAT_GAP + SPACER_CREST
Z_BMS_TOP = Z_BMS_BOT + BMS_T
SADDLE_YS = tuple(s * 0.33 * (CELL_L + 1.0) for s in (-1, 0, 1))   # base saddles + lid beam stations (+-45.29)


def rounded_box(w, l, h, r):
    return cq.Workplane("XY").sketch().rect(w, l).vertices().fillet(r).finalize().extrude(h)


def cells_cut(r=R_SEAT):
    """The four cells as solids of radius r, for cutting seats."""
    c = None
    for x in cell_x:
        s = cq.Workplane("XZ").center(x, Z_CELL_CTR).circle(r).extrude(CELL_L, both=True)
        c = s if c is None else c.union(s)
    return c


def to_print_spacer(s):                        # flat (BMS) face on the bed
    return s.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, Z_BMS_BOT))


# Lid stiffening: at each saddle station an internal 3 mm ridge crosses over the BMS, joining the
# C1 rib, ridge and C4 rib into one wall-to-wall beam (side-screwed at both ends). Internal rather
# than on top because the lid prints outer-face-down; same stiffness, same height cost.
BMS_TOP_CLR = 1.0                              # BMS components -> ridge underside
RIDGE_H = 3.0
H_BASE = Z_BMS_TOP + BMS_TOP_CLR + RIDGE_H     # rim height == lid underside
RIB_T = 4.0                                  # rib / ridge thickness (Y)
WIRE_CH = (4.5, 4.0)                           # wire channel through each rib over the C1/C2 and C3/C4
                                               # valleys: half-width beyond the valley line, height above seat

# ---- length budget. Cells are wired on the bench before they go in, so the
# bays only hold finished wiring: tab (2) + 12 AWG link (4.5) beyond the cell end, with foam behind the stops.
END_FOAM_GAP = 1.5                             # cell end -> stop face: 2-3 mm closed-cell EVA/neoprene pad,
                                               # compressed ~30-40%; stops/spars/webs limit travel if it bottoms
END_STOP_T = 2.4                               # end-stop plate (base rib + lid tabs), 6 lines @0.4 / 4 @0.6
BAY_F, BAY_B = 5.0, 4.0                        # wiring bays beyond the stop plates
CELL_ZONE = CELL_L + 2 * END_FOAM_GAP
Y_STOP = CELL_ZONE / 2                         # cell-side face of the end stops
IN_L = BAY_F + BAY_B + 2 * END_STOP_T + CELL_ZONE
OUT_L = IN_L + 2 * WALL
Y_OFF = (BAY_F - BAY_B) / 2
FRONT_IN = Y_OFF + IN_L / 2
BACK_IN = IN_L / 2 - Y_OFF                     # |y| of the back wall's inside face
boss_xy = [(sx * (IN_W / 2 - BOSS_D / 2 + 1.5), Y_OFF + sy * (IN_L / 2 - BOSS_D / 2 + 1.5))
           for sx in (-1, 1) for sy in (-1, 1)]

BMS_FROM_BACK = 3.0                            # BMS pushed to the BACK end of the spacer: its balance connector is on
                                               # the front edge, which keeps the front (Powerpole) end uncrowded
BMS_PAD_IN = 5.0                               # lid corner pads: centre this far in from the BMS edges = over the
                                               # standoffs (holes 50 x 110 on a 60 x 120 board)
# BMS mounting: two boards on corner standoffs (heat-sink board toward the lid); the lower PCB is flat and
# sits directly on the spacer. Its corner screws are replaced by M3 x 5 ISO 7380 button heads from the cell
# side: spacer -> lower PCB -> standoff thread (3.5 mm deep). The holes land over C2/C3's curved shoulders,
# so each head sits in a counterbored pocket deep enough to clear the cell + seat gap under its full width.
BMS_HOLE_DX, BMS_HOLE_DY = 50.0, 110.0          # hole centre-to-centre (measured), pattern centred on the board
BMS_PCB_T = 1.6
BMS_THREAD_DEPTH = 3.5
BMS_HEAD_D, BMS_HEAD_K = 5.7, 1.65             # ISO 7380 M3 button head
BMS_POCKET_D = 6.3
BMS_SCREW_L = 5.0                              # under-head length
SP_X1 = BMS_W / 2 + 1.0                        # spacer: C2 + C3 under the BMS, stops short of the
                                               # C1/C2 and C3/C4 valleys so wires can run in them
SP_X0 = -SP_X1
SP_L = CELL_ZONE - 0.6
BMS_X0 = -BMS_W / 2
BMS_Y1 = -SP_L / 2 + BMS_FROM_BACK + BMS_L
BMS_CX, BMS_CY = 0.0, BMS_Y1 - BMS_L / 2
FENCE_X = BMS_W / 2 + BMS_CLR / 2              # inner face of the rib fences

# Powerpoles: front-right corner, next to the corner screw, RECESSED: the mating face sits just inside the
# front wall's outer face, so nothing stands proud to be knocked off. The mating plug enters the wall notch.
PP_X = 50.0
PP_W = PP_N * PP_SQ + 2 * PP_CLR
PP_RECESS = 0.5                                # mating face -> outer face of the front wall
PP_Y0 = FRONT_IN + WALL - PP_RECESS - PP_L     # housing rear face
PP_NOTCH_LEAD = 0.6                            # 45-degree lead-in round the notch at the outer face

# Output leads (2 x 12 AWG, 4 mm jacket) leave the housings straight back, through a solid backstop + the front
# rib, through a snap-in zig-zag in the pocket over C4, then through the middle rib to the solder joints
# beyond it. The zig-zag is one bump (turn ZZ_TH, 2 ZZ_TH back, ZZ_TH again): it exits on the entry line.
LEAD_D = 4.0                                   # jacket OD
LEAD_HOLE_D = 4.6                              # rib holes (teardrop, point toward the cells = up in print)
LEAD_DX = PP_SQ                                # lead spacing = housing pitch
ZZ_R = 12.0                                    # centreline bend radius -> 8 mm (2 x OD) inner, 16 mm outer lead
ZZ_TH = 40.0                                   # degrees; total wrap 4 x 40 = 160 deg per lead
ZZ_SIDE = 1                                    # bump swings toward the wall, leaving the inboard side of the
                                               # pocket free for the red lead's U-turn
ZZ_W, ZZ_H = 4.4, 4.6                          # channel width; floor -> lip (wire 4.0 sits fully in, 0.6 spare)
ZZ_MOUTH = 3.4                                 # snap lip opening (0.3 mm/side interference on the jacket)
ZZ_LIP_LAND = 0.4
ZZ_WALL = 2.0                                  # outer channel walls (inner wall between leads = 7.9 - 4.4 = 3.5)
PP_Z0 = H_BASE - PP_SQ
LEAD_Z = PP_Z0 + PP_SQ / 2                     # lead axis = housing axis

# side screws
SIDE_Z = 43.5                                  # screw axis height (above C1/C4, below the lid lip)
SIDE_HOLE_D = 3.5                              # clearance in the base wall (print tolerance)

# All fasteners: ISO 10642 countersunk M3 (head dk 6.72 max, k 1.86), 90-degree seats
CSK_D = 6.9                                    # countersink diameter at the surface (head sits ~0.3 below flush)
CSK_HOLE_D = 3.4
LID_PAD = 1.5                                  # lid pads drop into the corner bosses -> 3.5 mm under each csk head
CORNER_INSERT_DEPTH = 8.0                      # M3 x 10 lid screws
WALL_PAD = 1.2                                 # inside pad behind each side-screw csk -> 3.6 mm wall there
WALL_PAD_W = 12.0
SIDE_BLOCK = (10.0, 10.0)                      # rib wall-end block: X depth, Y width
# cell end stops: bottom third from the base, top third from the lid, middle third open for wiring
END_STOP_BOT_Z = Z_CELL_BOT + CELL_D / 3     # base end-stop rib top
END_STOP_TOP_Z = Z_CELL_TOP - CELL_D / 3       # top of the open wiring band; foam fills above this
END_STOP_W = 16.0                              # lid tab width per cell (gaps over the valleys for wires)
END_WEB_T = 2.0                                # two edge webs per tab, reaching back to the end wall
END_WEB_GAP = 0.3                              # web -> base end wall (slide fit; load goes into the wall)
END_WEB_LEAD = 4.0                             # 45-degree lead-in on the web's lower outer corner

def end_foam_volume(sy, base, lid, others=()):
    """Space for the closed-cell foam block at one end: cell-end face -> end wall, top of the wiring band
    -> lid underside, full width, minus everything printed or fitted there. Cut foam to this shape."""
    y_wall = FRONT_IN if sy > 0 else BACK_IN
    blk = cq.Workplane("XY").box(IN_W, y_wall - CELL_L / 2, H_BASE - END_STOP_TOP_Z, centered=(True, False, False)) \
        .translate((0, CELL_L / 2, END_STOP_TOP_Z))
    if sy < 0:
        blk = blk.mirror("XZ")
    blk = blk.cut(base).cut(lid)
    for o in others:
        blk = blk.cut(o)
    return blk


# glue-in plugs closing the side nut slots flush with the lid top
NUT_PLUG_CLR = 0.15


# capture: side screws -> M3 nuts dropped into slots from the lid top (glue-in plugs above);
# Powerpole clamp + corners -> M3 heat-set inserts
NUT_AF, NUT_T = 5.5, 2.4                       # ISO 4032 M3 nut: across flats, thickness
NUT_SLOT_W, NUT_SLOT_T = 5.7, 2.6              # side nut slot (flats against the slot sides: can't spin)
NUT_SETBACK = 2.0                              # material between the rib-end face and the nut
SIDE_CLEAR_DEPTH = 8.0                         # clearance bore in the rib-end block (screw tip room)
PP_INSERT_DEPTH = 7.0                          # Powerpole boss: blind heat-set insert from below
PP_CLAMP_T = 4.5                               # Powerpole clamp bar thickness (holds a 2.4 mm nut pocket)
PP_CLAMP_W = 8.0                               # along Y
PP_BOSS_D = 8.0
PP_BOSS_OFF = 4.0                              # boss centre offset beyond the cradle wall
PP_CLAMP_Y = PP_Y0 + 5.0                       # clamp under the housings' rear half (over the cells)
SIDE_SCREWS = [(sx, y) for sx in (-1, 1) for y in SADDLE_YS]


def csk(point, direction, d_top=CSK_D, d_hole=CSK_HOLE_D):
    """90-degree countersink cone: point = surface centre, direction = into the material."""
    d = cq.Vector(*direction).normalized()
    r1 = d_top / 2 + 0.5
    start = cq.Vector(*point) - d * 0.5
    return cq.Workplane("XY").add(cq.Solid.makeCone(r1, d_hole / 2, r1 - d_hole / 2, start, d))


def teardrop_x(x0, y, z, r, length):
    """Cylinder along X with a 45-degree roof (prints without support in an upright wall)."""
    k = r / 2 ** 0.5
    cyl = cq.Workplane("YZ").center(y, z).circle(r).extrude(length).translate((x0, 0, 0))
    roof = cq.Workplane("YZ").polyline([(y - k, z + k), (y, z + r * 2 ** 0.5), (y + k, z + k), (y, z)]).close() \
        .extrude(length).translate((x0, 0, 0))
    return cyl.union(roof)


def teardrop_y(x, z, r, y0, y1):
    """Cylinder along Y with a 45-degree point toward -Z (installed) = up when the lid prints outer face down."""
    k = r / 2 ** 0.5
    cyl = cq.Workplane("XZ").center(x, z).circle(r).extrude(-(y1 - y0)).translate((0, y0, 0))
    roof = cq.Workplane("XZ").polyline([(x - k, z - k), (x, z - r * 2 ** 0.5), (x + k, z - k), (x, z)]).close() \
        .extrude(-(y1 - y0)).translate((0, y0, 0))
    return cyl.union(roof)


def lead_xs():
    """(red, black) lead x. Red is inboard ("red right" seen from the mating face): it U-turns in the pocket
    behind the front rib and runs forward along the C3/C4 valley to C4+. Black is outboard and runs through the
    zig-zag and the middle rib to the BMS."""
    return (PP_X - LEAD_DX / 2, PP_X + LEAD_DX / 2)


def zz_x():
    return lead_xs()[1]


def red_return_x():
    """Red lead's forward run after the U-turn: centred between the inboard clamp boss and the front-right BMS
    corner pad, at lid level."""
    pad_edge = BMS_X0 + BMS_W - BMS_PAD_IN + 2.5
    boss_edge = pp_clamp_boss_x()[0] - PP_BOSS_D / 2
    return (pad_edge + boss_edge) / 2




def zz_span():
    """(y_start, y_end) of the zig-zag block: front rib's cell-side face -> middle rib's front face."""
    return SADDLE_YS[2] - RIB_T / 2, SADDLE_YS[1] + RIB_T / 2


def zz_path(y_start, y_end, z=0.0):
    """Zig-zag centreline in plan, heading -Y from (zz_x(), y_start): straight, arc +th, arc -2th, arc +th,
    straight, ending at (PP_X, y_end). Arcs are tangent-continuous at radius ZZ_R."""
    import math
    th = math.radians(ZZ_TH)
    arcs_len = 4 * ZZ_R * math.sin(th)
    lead = ((y_start - y_end) - arcs_len) / 2
    assert lead > 1.0, "zig-zag does not fit between the ribs"
    x, y, hd = zz_x(), y_start, -math.pi / 2
    w = cq.Workplane("XY").workplane(offset=z).moveTo(x, y)
    y -= lead
    w = w.lineTo(x, y)
    for turn in (ZZ_SIDE * th, -ZZ_SIDE * 2 * th, ZZ_SIDE * th):     # heading -Y, CCW (+) turns toward +X
        s = 1 if turn > 0 else -1                                   # +1 = CCW
        cx, cy = x - s * ZZ_R * math.sin(hd), y + s * ZZ_R * math.cos(hd)
        a0 = math.atan2(y - cy, x - cx)
        am, a1 = a0 + turn / 2, a0 + turn
        w = w.threePointArc((cx + ZZ_R * math.cos(am), cy + ZZ_R * math.sin(am)),
                            (cx + ZZ_R * math.cos(a1), cy + ZZ_R * math.sin(a1)))
        x, y, hd = cx + ZZ_R * math.cos(a1), cy + ZZ_R * math.sin(a1), hd + turn
    return w.lineTo(zz_x(), y_end).wire()


def zz_sweep(profile_pts_list, y_start, y_end):
    """Sweep closed XZ profiles (x, z installed, drawn at y_start) along the zig-zag (path is planar, so the
    profile's Z stays vertical; an off-centre profile point traces the exact parallel offset curve)."""
    path = zz_path(y_start, y_end)
    out = None
    for pts in profile_pts_list:
        prof = cq.Workplane("XZ", origin=(0, y_start, 0)).polyline(pts).close()
        sol = prof.sweep(path, isFrenet=False)    # corrected Frenet: profile stays upright through the S
        out = sol if out is None else out.union(sol)
    return out


def zz_channel_profile(xc):
    """Channel void across one lead: floor at the lid side, snap lip + 45-degree lead-in at the mouth."""
    zf = LEAD_Z + LEAD_HOLE_D / 2                 # floor (flush with the top of the rib holes)
    z1 = zf - ZZ_H                                 # start of the lip
    hw, hm = ZZ_W / 2, ZZ_MOUTH / 2
    z2 = z1 - (hw - hm)                            # 45-degree lip underside (prints: overhang toward the floor)
    z3 = z2 - ZZ_LIP_LAND
    z4 = z3 - (hw + 0.3 - hm)                      # 45-degree lead-in
    half = [(hw, zf + 0.01), (hw, z1), (hm, z2), (hm, z3), (hw + 0.3, z4 - 0.01)]
    return [(xc + u, zz) for u, zz in half] + [(xc - u, zz) for u, zz in reversed(half)]


def zz_block_z0():
    return zz_channel_profile(0)[4][1] + 0.01


def make_zz_relief():
    """Solid block (installed coords) hanging from the lid with the black lead's snap-in channel cut in."""
    y0, y1 = zz_span()
    hw, xc = ZZ_W / 2 + ZZ_WALL, zz_x()
    z0 = zz_block_z0()
    blk = zz_sweep([[(xc - hw, z0), (xc + hw, z0), (xc + hw, H_BASE + 0.01), (xc - hw, H_BASE + 0.01)]], y0 + 0.01, y1 - 0.01)
    ch = zz_sweep([zz_channel_profile(xc)], y0 + 0.2, y1 - 0.2)
    return blk.cut(ch)


def pp_clamp_boss_x():
    return (PP_X - PP_W / 2 - 1.6 - PP_BOSS_OFF, PP_X + PP_W / 2 + 1.6 + PP_BOSS_OFF)


def side_nut_x(sx):
    """(x_near, x_far) of the side nut slot, measured from the rib-end entry face."""
    face = IN_W / 2 - 0.3 - WALL_PAD - 0.3
    a, b = face - NUT_SETBACK - NUT_SLOT_T, face - NUT_SETBACK
    return (a, b) if sx > 0 else (-b, -a)


def to_print_lid(s):     # flip about X so the outer face lands on the bed at Z=0
    return s.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, H_BASE + LID_T))


# ---------------------------------------------------------------- Powerpole clamp bar (installed coords)
def make_pp_clamp_installed():
    x0, x1 = pp_clamp_boss_x()
    bar = cq.Workplane("XY").box(x1 - x0 + 2 * PP_BOSS_OFF, PP_CLAMP_W, PP_CLAMP_T, centered=(True, True, False)) \
        .edges("|Z").fillet(2.0).translate(((x0 + x1) / 2, PP_CLAMP_Y, PP_Z0 - PP_CLAMP_T))
    for bx in (x0, x1):
        bar = bar.cut(cq.Workplane("XY").circle(CSK_HOLE_D / 2).extrude(PP_CLAMP_T * 3, both=True)
                      .translate((bx, PP_CLAMP_Y, PP_Z0)))
        bar = bar.cut(csk((bx, PP_CLAMP_Y, PP_Z0 - PP_CLAMP_T), (0, 0, 1)))   # heads hidden under the bar
    return bar


# ---------------------------------------------------------------- side nut-slot plug (glue in, flush)
def nut_plug_z0():
    return SIDE_Z + NUT_AF / 2 / 0.8660254 + 0.3      # just above the nut's top corner


def make_nut_plug_installed(sx=1, y=0.0):
    n0, n1 = side_nut_x(sx)
    z0, z1 = nut_plug_z0(), H_BASE + LID_T
    p = cq.Workplane("XY").box(n1 - n0 - 2 * NUT_PLUG_CLR, NUT_SLOT_W - 2 * NUT_PLUG_CLR, z1 - z0, centered=(True, True, False)) \
        .translate(((n0 + n1) / 2, y, z0))
    return p.faces(">Z").edges().chamfer(0.3)


# ---------------------------------------------------------------- base
def outer_shell_c(h):
    """Base shell: vertical-corner fillets + bed chamfer, but a SQUARE rim so base and lid meet
    flush with no V-groove at the parting line to collect dirt."""
    b = rounded_box(OUT_W, OUT_L, h, R_VERT).translate((0, Y_OFF, 0))
    return b.faces("<Z").edges().chamfer(CHAMFER_BED)


def make_base():
    body = outer_shell_c(H_BASE)
    body = body.cut(rounded_box(IN_W, IN_L, H_BASE, R_VERT - WALL).translate((0, Y_OFF, FLOOR)))
    for y in SADDLE_YS:
        s = cq.Workplane("XY").box(IN_W, 5.0, Z_CELL_CTR - 6.0, centered=(True, True, False)).translate((0, y, 0))
        body = body.union(s.cut(cells_cut(CELL_D / 2 + CELL_CLR_D / 2)))
    # end stops, bottom third only: the middle third stays open for tabs + 12 AWG links,
    # the lid (and the Powerpole clamp at C4-front) provides the top third
    # 2.4 mm rib (cell-side face unchanged, thickened into the bay) + floor spars to the end wall,
    # in the same X planes as the lid's end-stop webs: cell thrust goes into the end wall in compression
    y_in = Y_STOP
    for sy in (-1, 1):
        y_wall = FRONT_IN if sy > 0 else BACK_IN
        rib = cq.Workplane("XY").box(IN_W, END_STOP_T, END_STOP_BOT_Z, centered=(True, False, False)).translate((0, y_in, 0))
        for xc in cell_x:
            for xw in (xc - END_STOP_W / 2, xc + END_STOP_W / 2 - END_WEB_T):
                rib = rib.union(cq.Workplane("XY").box(END_WEB_T, y_wall + 0.2 - (y_in + END_STOP_T - 0.01), END_STOP_BOT_Z,
                                                       centered=(False, False, False)).translate((xw, y_in + END_STOP_T - 0.01, 0)))
        body = body.union(rib if sy > 0 else rib.mirror("XZ"))
    for x, y in boss_xy:
        top = H_BASE - LID_PAD                   # lid pad drops into the pocket above the boss
        body = body.union(cq.Workplane("XY").circle(BOSS_D / 2).extrude(top - FLOOR).translate((x, y, FLOOR)))
        body = body.cut(cq.Workplane("XY").circle(INSERT_D / 2).extrude(CORNER_INSERT_DEPTH + 1)
                        .translate((x, y, top - CORNER_INSERT_DEPTH)))
    for sx, y in SIDE_SCREWS:
        # inside pad behind the countersink, 45-degree underside so it prints in the upright wall
        z0, z1 = SIDE_Z - 6.0, H_BASE - 3.5
        prof = [(0, z0), (WALL_PAD, z0 + WALL_PAD), (WALL_PAD, z1), (0, z1)]
        pad = cq.Workplane("XZ").polyline([(IN_W / 2 + 0.01 - px, pz) for px, pz in prof]).close() \
            .extrude(WALL_PAD_W / 2, both=True).translate((0, y, 0))
        if sx < 0:
            pad = pad.mirror("YZ")
        body = body.union(pad)
        x0 = IN_W / 2 - WALL_PAD - 1 if sx > 0 else -IN_W / 2 - WALL - 1
        body = body.cut(teardrop_x(x0, y, SIDE_Z, SIDE_HOLE_D / 2, WALL + WALL_PAD + 2))
        body = body.cut(csk((sx * (IN_W / 2 + WALL), y, SIDE_Z), (-sx, 0, 0)))
    body = body.cut(cq.Workplane("XY").box(PP_W, WALL * 4, PP_SQ + PP_CLR + 1, centered=(True, True, False))
                    .translate((PP_X, FRONT_IN + WALL / 2, PP_Z0 - PP_CLR)))
    # lead-in for the mating plug: 45-degree chamfer on the notch's sides and floor at the outer face
    yo = FRONT_IN + WALL
    body = body.edges(cq.selectors.BoxSelector((PP_X - PP_W / 2 - 0.5, yo - 0.1, PP_Z0 - PP_CLR - 0.5),
                                               (PP_X + PP_W / 2 + 0.5, yo + 0.1, H_BASE - 0.5))).chamfer(PP_NOTCH_LEAD)
    return body


# ---------------------------------------------------------------- spacer (installed coords)
def bms_hole_xy():
    xs = (BMS_CX - BMS_HOLE_DX / 2, BMS_CX + BMS_HOLE_DX / 2)
    ys = (BMS_CY - BMS_HOLE_DY / 2, BMS_CY + BMS_HOLE_DY / 2)
    return [(x, y) for x in xs for y in ys]


def cell_top_z(x):
    """Highest cell-surface Z at plan position x."""
    dx = min(abs(x - c) for c in cell_x)
    return Z_CELL_CTR + (max(CELL_D ** 2 / 4 - dx ** 2, 0)) ** 0.5


def bms_screw_head_z(x):
    """Underside of the button head: clears the cell (+ seat gap) across the whole pocket width."""
    r = BMS_POCKET_D / 2
    return max(cell_top_z(x + t * r) for t in (-1, -0.5, 0, 0.5, 1)) + SEAT_GAP


def make_spacer_installed():
    z_lo = Z_CELL_TOP - 9.0
    z_top = Z_BMS_BOT
    sp = cq.Workplane("XY").box(SP_X1 - SP_X0, SP_L, z_top - z_lo, centered=(True, True, False)) \
        .translate((0, 0, z_lo))
    # bed-side (BMS face) long edges: 45 deg chamfer, not a fillet, so the first layers have no overhang.
    # 1.0 mm = the spacer margin outside the BMS, so the board keeps full support.
    sp = sp.edges("|Y").edges(">Z").chamfer(1.0)
    sp = sp.cut(cells_cut())
    for x, y in bms_hole_xy():
        zh = bms_screw_head_z(x)
        sp = sp.cut(cq.Workplane("XY").circle(CSK_HOLE_D / 2).extrude(20).translate((x, y, zh - 5)))
        # counterbored pocket from the curved cell side up to the head's bearing face
        sp = sp.cut(cq.Workplane("XY").circle(BMS_POCKET_D / 2).extrude(BMS_HEAD_K + 6.0).translate((x, y, zh - 6.0)))
    return sp


# ---------------------------------------------------------------- lid (installed coords)
def make_lid_installed():
    plate = rounded_box(OUT_W, OUT_L, LID_T, R_VERT).translate((0, Y_OFF, H_BASE))
    lid = plate.faces(">Z").edges().chamfer(CHAMFER_BED)
    lip_h, lip_t, gap = 3.0, 1.6, 0.35
    lip = rounded_box(IN_W - 2 * gap, IN_L - 2 * gap, lip_h, R_VERT - WALL - gap) \
        .cut(rounded_box(IN_W - 2 * gap - 2 * lip_t, IN_L - 2 * gap - 2 * lip_t, lip_h,
                         max(R_VERT - WALL - gap - lip_t, 0.5))).translate((0, Y_OFF, H_BASE - lip_h))
    for x, y in boss_xy:
        lip = lip.cut(cq.Workplane("XY").circle(BOSS_D / 2 + 1.5).extrude(lip_h).translate((x, y, H_BASE - lip_h)))
    lip = lip.cut(cq.Workplane("XY").box(PP_W + 4, 10, lip_h, centered=(True, True, False))
                  .translate((PP_X, FRONT_IN, H_BASE - lip_h)))
    lid = lid.union(lip)

    x_wall = IN_W / 2 - 0.3
    for sx in (-1, 1):
        for y in SADDLE_YS:
            # fence: beside the BMS edge, bottom rests on the spacer top
            fence = cq.Workplane("XY").box(SP_X1 + 0.4 - FENCE_X, RIB_T, H_BASE - Z_BMS_BOT, centered=(False, True, False)) \
                .translate((FENCE_X, y, Z_BMS_BOT))
            # saddle: from the spacer edge to the wall, seats on C1 / C4 (0.5 mm foam gap)
            sad = cq.Workplane("XY").box(x_wall - (SP_X1 + 0.4), RIB_T, H_BASE - (Z_CELL_CTR + 6), centered=(False, True, False)) \
                .translate((SP_X1 + 0.4, y, Z_CELL_CTR + 6))
            bw, bd = SIDE_BLOCK
            blk = cq.Workplane("XY").box(bw, bd, H_BASE - 34.0, centered=(False, True, False)) \
                .translate((x_wall - bw, y, 34.0))
            rib = fence.union(sad).union(blk.edges("|Z").fillet(1.5))
            # vertical groove clearing the base wall pad (open at the bottom so the lid drops straight in)
            rib = rib.cut(cq.Workplane("XY").box(WALL_PAD + 0.3 + 0.1, WALL_PAD_W + 1.0, H_BASE - 3.0 - 34.0 + 0.2, centered=(False, True, False))
                          .translate((x_wall - WALL_PAD - 0.3, y, 33.9)))
            # wire channel where the rib dips into the C3/C4 valley (B+ / fuse run)
            hw, hh = WIRE_CH
            rib = rib.cut(cq.Workplane("XY").box(PITCH + hw - (SP_X1 + 0.4), RIB_T * 3, Z_CELL_TOP + hh, centered=(False, True, False))
                          .translate((SP_X1 + 0.4, y, 0)))
            if sx < 0:
                rib = rib.mirror("YZ")
            rib = rib.cut(cells_cut())
            # sideways heat-set insert from the wall face
            face = x_wall - WALL_PAD - 0.3              # groove floor = screw entry face
            bore = cq.Workplane("YZ").center(y, SIDE_Z).circle(CSK_HOLE_D / 2).extrude(SIDE_CLEAR_DEPTH + 0.5)
            bore = bore.translate((face - SIDE_CLEAR_DEPTH, 0, 0)) if sx > 0 else bore.translate((-face - 0.5, 0, 0))
            n0, n1 = side_nut_x(sx)
            z_floor = SIDE_Z - NUT_AF / 2 / 0.8660254 - 0.1   # nut rests on a corner; centre on the screw axis
            slot = cq.Workplane("XY").box(n1 - n0, NUT_SLOT_W, H_BASE + LID_T + 1 - z_floor, centered=(False, True, False)) \
                .translate((n0, y, z_floor))
            lid = lid.union(rib).cut(bore).cut(slot)

    # no lid end tabs: the space above the wiring band at each end is filled with closed-cell foam
    # (see end_foam_volume) which holds the top of the cell ends and keeps the wiring in place

    # stiffening ridges across the BMS, continuous with the ribs either side
    for y in SADDLE_YS:
        lid = lid.union(cq.Workplane("XY").box(2 * FENCE_X + 0.2, RIB_T, RIDGE_H + 0.01, centered=(True, True, False))
                        .translate((0, y, H_BASE - RIDGE_H)))

    # BMS: corner pads press it onto the spacer
    for sx in (0, 1):
        for sy in (0, 1):
            kx = BMS_X0 + BMS_PAD_IN + sx * (BMS_W - 2 * BMS_PAD_IN)
            ky = BMS_Y1 - BMS_PAD_IN - sy * (BMS_L - 2 * BMS_PAD_IN)
            lid = lid.union(cq.Workplane("XY").rect(5, 5).extrude(H_BASE - Z_BMS_TOP).edges("|Z").fillet(1.5)
                            .translate((kx, ky, Z_BMS_TOP)))
    # (no BMS end fences: the four M3 screws through the spacer locate the board; the 1.4 mm fences broke off)

    # Powerpole cradle
    cw = 1.6
    for sx in (-1, 1):
        lid = lid.union(cq.Workplane("XY").box(cw, FRONT_IN - 0.4 - (PP_Y0 - 1), PP_SQ, centered=(True, False, False))
                        .translate((PP_X + sx * (PP_W / 2 + cw / 2), PP_Y0 - 1, PP_Z0)))
    # solid backstop from the housings' rear face to the front rib: takes the mating push. Its underside
    # stays 0.5 mm above the clamp bar so the bar always clamps the housings, not the backstop.
    y_rib_f = SADDLE_YS[2] + RIB_T / 2 - 0.01
    lid = lid.union(cq.Workplane("XY").box(PP_W + 2 * cw, PP_Y0 - y_rib_f, H_BASE - PP_Z0 - 0.5, centered=(True, False, False))
                    .translate((PP_X, y_rib_f, PP_Z0 + 0.5)))
    # snap-in zig-zag strain relief between the front and middle ribs, then the lead holes through
    # backstop + front rib and through the middle rib (teardrops: they run horizontally in the print)
    # Black: front rib -> zig-zag -> middle rib. Red: front rib only, then a free U-turn down into the C3/C4
    # valley and forward through the rib's valley slot. The black run is mirrored over C1 (-X) for the single
    # C1- -> BMS B- lead; that side has no backstop, so its front-rib hole only goes through the rib.
    y0, y1 = zz_span()
    x_red, x_blk = lead_xs()
    for sx in (1, -1):
        zz = make_zz_relief()
        lid = lid.union(zz if sx > 0 else zz.mirror("YZ"))
        y_far = PP_Y0 + 0.01 if sx > 0 else SADDLE_YS[2] + RIB_T / 2 + 0.5
        lid = lid.cut(teardrop_y(sx * x_blk, LEAD_Z, LEAD_HOLE_D / 2, y0 - 0.3, y_far))
        lid = lid.cut(teardrop_y(sx * x_blk, LEAD_Z, LEAD_HOLE_D / 2, SADDLE_YS[1] - RIB_T / 2 - 0.5, y1 + 0.3))
    lid = lid.cut(teardrop_y(x_red, LEAD_Z, LEAD_HOLE_D / 2, y0 - 0.3, PP_Y0 + 0.01))
    # red's return hole through the front rib (fence + ridge end), top flush with the lid underside
    lid = lid.cut(teardrop_y(red_return_x(), H_BASE - LEAD_HOLE_D / 2, LEAD_HOLE_D / 2, y0 - 0.3,
                             SADDLE_YS[2] + RIB_T / 2 + 0.3))

    # two bosses either side of the cradle; clamp screws come UP from under the bar into blind
    # M3 heat-set inserts (pressed in from below): the lid top stays clean
    for bx in pp_clamp_boss_x():
        lid = lid.union(cq.Workplane("XY").circle(PP_BOSS_D / 2).extrude(H_BASE - PP_Z0).translate((bx, PP_CLAMP_Y, PP_Z0)))
        lid = lid.cut(cq.Workplane("XY").circle(INSERT_D / 2).extrude(PP_INSERT_DEPTH + 0.5).translate((bx, PP_CLAMP_Y, PP_Z0 - 0.5)))

    # through-cuts
    inner = rounded_box(IN_W - 0.7, IN_L - 0.7, LID_PAD, R_VERT - WALL - 0.35).translate((0, Y_OFF, H_BASE - LID_PAD))
    for x, y in boss_xy:
        lid = lid.union(cq.Workplane("XY").circle(BOSS_D / 2 - 0.3).extrude(LID_PAD + 0.01)
                        .translate((x, y, H_BASE - LID_PAD)).intersect(inner))
    for x, y in boss_xy:
        lid = lid.cut(cq.Workplane("XY").circle(CSK_HOLE_D / 2).extrude(LID_T + LID_PAD + 2).translate((x, y, H_BASE - LID_PAD - 1)))
        lid = lid.cut(csk((x, y, H_BASE + LID_T), (0, 0, -1)))
    for i in range(-4, 5):
        if any(abs(BMS_CY + i * 11 - y) < RIB_T / 2 + 2.5 for y in SADDLE_YS):
            continue
        lid = lid.cut(cq.Workplane("XY").center(BMS_CX, BMS_CY + i * 11).slot2D(BMS_W - 16, 3.0)
                      .extrude(LID_T + 2).translate((0, 0, H_BASE - 1)))
    return lid


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out, exist_ok=True)
    parts = {"base": make_base(), "spacer": to_print_spacer(make_spacer_installed()),
             "lid": to_print_lid(make_lid_installed()),
             "nut_plug_x6": make_nut_plug_installed().rotate((0, 0, 0), (0, 1, 0), 90),   # print on its side, x6
             # printed nut-pockets-up
             "pp_clamp": make_pp_clamp_installed().rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, PP_Z0))}
    for name, p in parts.items():
        cq.exporters.export(p, os.path.join(out, f"{name}.stl"), tolerance=0.05, angularTolerance=0.1)
        cq.exporters.export(p, os.path.join(out, f"{name}.step"))
        bb = p.val().BoundingBox()
        print(f"{name:8s} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f} mm  valid={p.val().isValid()}  "
              f"solids={len(p.solids().vals())}")
    print(f"outside {OUT_W:.1f} x {OUT_L:.1f} x {H_BASE + LID_T:.1f}")
