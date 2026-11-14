"""
4S LiFePO4 (4x 33.5 x 136.25 mm laser-welded cells) + 60x120x10 BMS enclosure.

Three printed parts, each modelled in its print orientation:
  base.stl  - open-top tub with cell cradles, end-stop ribs and wiring bays (prints open side up)
  tray.stl  - cell clamp plate, screwed to 3 posts in the base (M3 inserts) over foam strips;
              insulates the BMS from the cells and locates it (prints flat)
  lid.stl   - screw-down lid with locating lip and BMS keeper posts (prints outer face down)

Coordinate system (base): X = across the cells (cell 1 at -X), Y = along the cells
(+Y = FRONT, where the pack leads exit), Z = up.

Run:  python case.py   -> writes STL + STEP into ./out
"""
import os
import cadquery as cq

# ---------------------------------------------------------------- parameters
CELL_D = 33.5           # cell diameter (measured)
CELL_L = 136.25         # cell body length, excluding tabs (measured)
TAB_W, TAB_T = 20.0, 2.0  # copper tab width and height above cell end
CELL_CLR_D = 0.6        # diametral clearance in cradles
CELL_CLR_L = 1.0        # total axial clearance between end-stop ribs
CELL_GAP = 1.0          # gap between neighbouring cells
N_CELLS = 4

BMS_W, BMS_L, BMS_T = 60.0, 120.0, 10.0
BMS_CLR = 0.6           # clearance around BMS in its locating fence
BMS_FROM_FRONT = 3.0    # BMS pushed toward the FRONT end, connector end faces back

WALL = 2.4              # side/end wall thickness
FLOOR = 2.0             # floor thickness
SADDLE = 1.0            # material under the cell at the lowest point of a cradle
BAY_F = 10.0            # front wiring bay: C2+/C3- link, B-/B+ leads, 90deg bend into lead exits
BAY_B = 8.0             # back wiring bay: two flat 12 AWG links + balance taps only
RIB_T = TAB_T           # end-stop rib: tab sits flush with its outer face
TRAY_T = 2.0
TRAY_GAP = 1.0          # cell top -> tray underside; filled by 1.5 mm adhesive foam strips (~33% squeeze)
CLAMP_POST_D = 9.0      # tray clamp posts (M3 heat-set insert in top)
TOP_CLR = 2.5           # space above the BMS components for wires
LID_T = 2.0

R_VERT = 6.0            # vertical-corner fillet radius (outside)
R_TOP = 2.5             # fillet on up-facing outer edges
CHAMFER_BED = 1.2       # 45 deg chamfer on bed-facing edges (printable "fillet")

INSERT_D = 4.2          # M3 heat-set insert hole (e.g. M3x5.7 insert)
INSERT_DEPTH = 7.0
SCREW_D = 3.4
SCREW_HEAD_D = 6.2
BOSS_D = 9.0

# Anderson Powerpole PP15/30/45 bonded pair (red P+, black P-) in the FRONT wall at tray level
PP_SQ = 7.9             # housing cross-section (each), mm
PP_L = 24.6             # housing length
PP_N = 2
PP_CLR = 0.25           # per side, wall cut-out and cradle
PP_PROUD = 4.0          # mating face stands this far proud of the front wall
PP_X = 10.0             # pair centre (clear of the BMS, which ends at x ~ -8)

# ---------------------------------------------------------------- derived
PITCH = CELL_D + CELL_GAP
IN_W = N_CELLS * PITCH + 1.0                       # interior width
CELL_ZONE = CELL_L + CELL_CLR_L                    # between end-stop ribs
IN_L = BAY_F + BAY_B + 2 * RIB_T + CELL_ZONE       # interior length
Y_OFF = (BAY_F - BAY_B) / 2                        # box centre vs cell-zone centre (cells stay at Y=0)
FRONT_IN = Y_OFF + IN_L / 2                        # Y of the front wall's inside face
OUT_W, OUT_L = IN_W + 2 * WALL, IN_L + 2 * WALL

Z_CELL_BOT = FLOOR + SADDLE
Z_CELL_CTR = Z_CELL_BOT + CELL_D / 2
Z_CELL_TOP = Z_CELL_BOT + CELL_D
Z_TRAY = Z_CELL_TOP + TRAY_GAP                     # tray underside: rests on ribs + clamp posts
Z_BMS_TOP = Z_TRAY + TRAY_T + BMS_T
H_BASE = Z_BMS_TOP + TOP_CLR                       # rim height == lid underside

cell_x = [-IN_W / 2 + 0.5 + PITCH / 2 + i * PITCH for i in range(N_CELLS)]
Y_RIB_F = CELL_ZONE / 2 + RIB_T / 2                # rib centre lines
# tray clamp posts (x, y): front bay between C1/C2 and C3/C4 tabs, back bay between C2/C3 tabs
clamp_xy = [(-PITCH, Y_RIB_F + RIB_T / 2 + CLAMP_POST_D / 2 - 0.5),
            (PITCH, Y_RIB_F + RIB_T / 2 + CLAMP_POST_D / 2 - 0.5),
            (0.0, -(Y_RIB_F + RIB_T / 2 + CLAMP_POST_D / 2 - 0.5))]
boss_xy = [(sx * (IN_W / 2 - BOSS_D / 2 + 1.5), Y_OFF + sy * (IN_L / 2 - BOSS_D / 2 + 1.5))
           for sx in (-1, 1) for sy in (-1, 1)]


def rounded_box(w, l, h, r):
    return cq.Workplane("XY").sketch().rect(w, l).vertices().fillet(r).finalize().extrude(h)


# ---------------------------------------------------------------- base
def make_base():
    body = rounded_box(OUT_W, OUT_L, H_BASE, R_VERT).translate((0, Y_OFF, 0))
    body = body.faces("<Z").edges().chamfer(CHAMFER_BED)
    body = body.faces(">Z").edges().fillet(R_TOP * 0.6)  # soften rim
    cavity = rounded_box(IN_W, IN_L, H_BASE, R_VERT - WALL).translate((0, Y_OFF, FLOOR))
    body = body.cut(cavity)

    # cradle saddles: 3 transverse ribs with half-round seats
    sad_h = Z_CELL_CTR - 6.0
    for y in (-CELL_ZONE * 0.33, 0, CELL_ZONE * 0.33):
        s = cq.Workplane("XY").box(IN_W, 5.0, sad_h, centered=(True, True, False)).translate((0, y, 0))
        for x in cell_x:
            s = s.cut(cq.Workplane("XZ").center(x, Z_CELL_CTR)
                      .circle((CELL_D + CELL_CLR_D) / 2).extrude(5, both=True).translate((0, y, 0)))
        body = body.union(s)

    # end-stop ribs up to tray height, open-top U-notch per cell for tab + wire
    for sy in (-1, 1):
        rib = cq.Workplane("XY").box(IN_W, RIB_T, Z_TRAY, centered=(True, True, False)) \
            .translate((0, sy * Y_RIB_F, 0))
        for x in cell_x:
            notch_w = TAB_W + 4
            zb, zt = Z_CELL_CTR - notch_w / 2, Z_TRAY + 1   # round bottom centred on cell axis
            slot = (cq.Workplane("XZ").center(x, (zb + zt) / 2)
                    .slot2D(zt - zb, notch_w, angle=90)
                    .extrude(RIB_T, both=True).translate((0, sy * Y_RIB_F, 0)))
            rib = rib.cut(slot)
        body = body.union(rib)

    # tray clamp posts: stand on the floor, fused to the end-stop rib, insert in the top
    for x, y in clamp_xy:
        body = body.union(cq.Workplane("XY").circle(CLAMP_POST_D / 2).extrude(Z_TRAY - FLOOR)
                          .translate((x, y, FLOOR)))
        body = body.cut(cq.Workplane("XY").circle(INSERT_D / 2).extrude(INSERT_DEPTH + 1)
                        .translate((x, y, Z_TRAY - INSERT_DEPTH)))

    # corner bosses for M3 heat-set inserts (lid screws)
    for x, y in boss_xy:
        b = cq.Workplane("XY").circle(BOSS_D / 2).extrude(H_BASE - FLOOR).translate((x, y, FLOOR))
        body = body.union(b)
        body = body.cut(cq.Workplane("XY").circle(INSERT_D / 2).extrude(INSERT_DEPTH + 1)
                        .translate((x, y, H_BASE - INSERT_DEPTH)))   # overshoot: no coplanar faces

    # Powerpole cut-out in the front wall; bottom edge = tray top so the housings sit on the tray tongue
    pp_w, pp_h = PP_N * PP_SQ + 2 * PP_CLR, PP_SQ + 2 * PP_CLR
    body = body.cut(cq.Workplane("XY").box(pp_w, WALL * 4, pp_h, centered=(True, True, False))
                    .translate((PP_X, FRONT_IN + WALL / 2, Z_TRAY + TRAY_T - PP_CLR)))
    return body


# ---------------------------------------------------------------- tray
TRAY_W = IN_W - 0.8
TRAY_L = CELL_ZONE + 2 * RIB_T - 0.6
BMS_X0 = -TRAY_W / 2 + 2.5                     # BMS justified to the cell-1 side
BMS_Y0 = TRAY_L / 2 - BMS_FROM_FRONT - BMS_L - BMS_CLR  # in tray coords, front = +Y


def make_tray():
    t = rounded_box(TRAY_W, TRAY_L, TRAY_T, 2.5)
    t = t.faces("<Z").edges().chamfer(0.4)
    bx = BMS_X0 + (BMS_W + BMS_CLR) / 2
    by = TRAY_L / 2 - BMS_FROM_FRONT - (BMS_L + BMS_CLR) / 2
    # L-shaped corner fences (3 mm tall) that locate the BMS without covering its edges
    fence_h, fence_t, arm = 3.0, 1.6, 12.0
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx = bx + sx * ((BMS_W + BMS_CLR) / 2 + fence_t / 2)
            cy = by + sy * ((BMS_L + BMS_CLR) / 2 + fence_t / 2)
            a = cq.Workplane("XY").box(fence_t, arm, fence_h, centered=(True, True, False)) \
                .translate((cx, cy - sy * arm / 2 + sy * fence_t / 2, TRAY_T))
            b = cq.Workplane("XY").box(arm, fence_t, fence_h, centered=(True, True, False)) \
                .translate((cx - sx * arm / 2 + sx * fence_t / 2, cy, TRAY_T))
            t = t.union(a).union(b)
    # Powerpole tongue: reaches across the front bay to the wall and merges with the front-right
    # clamp ear, so that ear's M3 screw stiffens it. Carries cradle, rear stop and zip-tie slots.
    pp_w = PP_N * PP_SQ + 2 * PP_CLR
    y_front = FRONT_IN - 0.4
    y_rear = FRONT_IN + WALL + PP_PROUD - PP_L               # housing rear face
    ear_x1 = clamp_xy[1][0] + (CLAMP_POST_D + 3) / 2
    tx0 = PP_X - pp_w / 2 - 6
    t = t.union(cq.Workplane("XY").center((tx0 + ear_x1) / 2, (TRAY_L / 2 - 4 + y_front) / 2)
                .rect(ear_x1 - tx0, y_front - (TRAY_L / 2 - 4)).extrude(TRAY_T).edges("|Z").fillet(2.0))
    cw, ch = 1.6, 5.5                                        # cradle wall thickness / height
    for sx in (-1, 1):
        t = t.union(cq.Workplane("XY").box(cw, y_front - (y_rear - 2), ch, centered=(True, False, False))
                    .translate((PP_X + sx * (pp_w / 2 + cw / 2), y_rear - 2, TRAY_T)))
    stop = cq.Workplane("XY").box(pp_w + 2 * cw, 2.0, ch, centered=(True, False, False)) \
        .translate((PP_X, y_rear - 2, TRAY_T))
    for i in range(PP_N):                                    # U-slots for the 12 AWG leads
        cx = PP_X - pp_w / 2 + PP_CLR + PP_SQ * (i + 0.5)
        stop = stop.cut(cq.Workplane("XZ").center(cx, TRAY_T + 1.2 + 3).slot2D(6, 4.8, angle=90)
                        .extrude(5, both=True).translate((0, y_rear - 1, 0)))
    t = t.union(stop)
    for sx in (-1, 1):                                       # zip-tie slots, over the bay (not the cells)
        t = t.cut(cq.Workplane("XY").center(PP_X + sx * (pp_w / 2 + cw + 2.0), (TRAY_L / 2 + y_front) / 2 + 1)
                  .rect(2.0, 5.0).extrude(TRAY_T * 3, both=True))

    # clamp ears reaching over the posts in the bays, with M3 clearance holes
    for x, y in clamp_xy:
        sy = 1 if y > 0 else -1
        y0 = sy * (TRAY_L / 2 - 3)                      # overlap into the plate
        y1 = y + sy * (CLAMP_POST_D / 2 + 0.5)
        y1 = min(y1, FRONT_IN - 0.4) if sy > 0 else max(y1, Y_OFF - IN_L / 2 + 0.4)  # stop short of end wall
        ear = (cq.Workplane("XY").center(x, (y0 + y1) / 2).rect(CLAMP_POST_D + 3, abs(y1 - y0))
               .extrude(TRAY_T).edges("|Z").fillet(2.0))
        t = t.union(ear)
        t = t.cut(cq.Workplane("XY").circle(SCREW_D / 2).extrude(TRAY_T * 3, both=True).translate((x, y, 0)))
    return t


# ---------------------------------------------------------------- lid
def make_lid():
    # modelled print-orientation: outer face on Z=0, lip & posts grow +Z
    # lid coords = base coords mirrored in Y (lid is flipped about X to close): y_lid = -y_base
    lid = rounded_box(OUT_W, OUT_L, LID_T, R_VERT).translate((0, -Y_OFF, 0))
    lid = lid.faces("<Z").edges().chamfer(CHAMFER_BED)
    # locating lip that drops inside the base walls (notched around bosses)
    lip_h, lip_t, gap = 3.0, 1.6, 0.35
    lip = rounded_box(IN_W - 2 * gap, IN_L - 2 * gap, lip_h, R_VERT - WALL - gap) \
        .cut(rounded_box(IN_W - 2 * gap - 2 * lip_t, IN_L - 2 * gap - 2 * lip_t, lip_h,
                         max(R_VERT - WALL - gap - lip_t, 0.5))).translate((0, -Y_OFF, LID_T))
    for x, y in boss_xy:
        lip = lip.cut(cq.Workplane("XY").circle(BOSS_D / 2 + 1.5).extrude(lip_h).translate((x, -y, LID_T)))
    # BMS wire bundle clearance: notch the lip nowhere (all wiring is internal)
    lid = lid.union(lip)
    # screw holes with counterbores (counterbore on outer face = bed side, prints fine)
    for x, y in boss_xy:
        lid = lid.cut(cq.Workplane("XY").circle(SCREW_D / 2).extrude(LID_T + 1).translate((x, -y, -0.5)))
        lid = lid.cut(cq.Workplane("XY").circle(SCREW_HEAD_D / 2).extrude(1.2).translate((x, -y, -0.01)))
    # keeper posts: stop 1 mm above the BMS corners so it can't climb out of its fences
    for sx in (0, 1):
        for sy in (0, 1):
            kx = BMS_X0 + 4 + sx * (BMS_W - 8)
            ky = -(TRAY_L / 2 - BMS_FROM_FRONT - 4 - sy * (BMS_L - 8))
            klen = H_BASE - Z_BMS_TOP - 1.0
            lid = lid.union(cq.Workplane("XY").rect(5, 5).extrude(klen).edges("|Z").fillet(1.5)
                            .translate((kx, ky, LID_T)))
    # vent slots above the BMS (BMS sits at base -X, front-justified -> lid -X, -Y side)
    bms_cx = BMS_X0 + BMS_W / 2
    bms_cy = -(TRAY_L / 2 - BMS_FROM_FRONT - BMS_L / 2)
    for i in range(-4, 5):
        lid = lid.cut(cq.Workplane("XY").center(bms_cx, bms_cy + i * 11)
                      .slot2D(BMS_W - 16, 3.0).extrude(LID_T + 1).translate((0, 0, -0.5)))
    return lid


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out, exist_ok=True)
    parts = {"base": make_base(), "tray": make_tray(), "lid": make_lid()}
    for name, p in parts.items():
        cq.exporters.export(p, os.path.join(out, f"{name}.stl"), tolerance=0.05, angularTolerance=0.1)
        cq.exporters.export(p, os.path.join(out, f"{name}.step"))
        bb = p.val().BoundingBox()
        print(f"{name:5s} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f} mm  valid={p.val().isValid()}")
    print(f"outside {OUT_W:.1f} x {OUT_L:.1f} (IC-706MKII: 167 x 200), interior {IN_W:.1f} x {IN_L:.1f}, base height {H_BASE:.1f}, total closed height {H_BASE + LID_T:.1f}")
