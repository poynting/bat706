"""
Variant B: BMS carried by the lid, lid clamps the cells. Compare with case.py (variant A).

Parts (print orientation):
  base_b.stl    - tub: cradles, end-stop ribs, corner bosses, Powerpole notch open at the rim
  spacer_b.stl  - cell-shaped insulator: underside nests on C1/C2, flat top carries the BMS;
                  sits between the end-stop ribs (prints flat face down, troughs up)
  lid_b.stl     - lid with saddle ribs clamping C3/C4, BMS fences + corner pads (BMS -> spacer
                  -> C1/C2), Powerpole cradle, vents (prints outer face down)

Stack above the cells: 0.5 mm seat gap (1 mm foam tape) + 1.5 mm spacer + BMS + 1 mm + lid.
All cell / wall / bay parameters are imported from case.py so the two variants compare like-for-like.
"""
import os
import cadquery as cq
import case as A
from case import (CELL_D, CELL_L, BMS_W, BMS_L, BMS_T, BMS_CLR, WALL, FLOOR, RIB_T, LID_T, R_VERT, R_TOP,
                  CHAMFER_BED, INSERT_D, INSERT_DEPTH, SCREW_D, SCREW_HEAD_D, BOSS_D, PP_SQ, PP_L, PP_N,
                  PP_CLR, PP_PROUD, PP_X, IN_W, IN_L, OUT_W, OUT_L, Y_OFF, FRONT_IN, CELL_ZONE,
                  Z_CELL_CTR, Z_CELL_TOP, cell_x, Y_RIB_F, boss_xy, rounded_box)

SEAT_GAP = 0.5          # cell surface -> spacer / lid-rib seat; filled with 1 mm foam tape
SPACER_CREST = 1.5      # spacer thickness over the top of C1/C2
BMS_PAD = 1.0           # lid underside -> BMS top (corner pads bridge it)
BMS_FROM_FRONT = 3.0

R_SEAT = CELL_D / 2 + SEAT_GAP
Z_BMS_BOT = Z_CELL_TOP + SEAT_GAP + SPACER_CREST
Z_BMS_TOP = Z_BMS_BOT + BMS_T
H_BASE = Z_BMS_TOP + BMS_PAD
Z_RIB_TOP = Z_CELL_TOP                         # base end-stop ribs
SADDLE_YS = (-CELL_ZONE * 0.33, 0.0, CELL_ZONE * 0.33)

SP_X0, SP_X1 = -IN_W / 2 + 0.4, -0.5           # spacer spans C1 + C2
SP_L = CELL_ZONE - 0.6                         # nests between the end-stop ribs
BMS_X0 = -IN_W / 2 + 2.6
BMS_Y1 = SP_L / 2 - BMS_FROM_FRONT             # BMS front edge (+Y = front)
BMS_CX, BMS_CY = BMS_X0 + BMS_W / 2, BMS_Y1 - BMS_L / 2
PP_W = PP_N * PP_SQ + 2 * PP_CLR
PP_Y0 = FRONT_IN + WALL + PP_PROUD - PP_L      # housing rear face
PP_Z0 = H_BASE - PP_SQ                         # housings hang from the lid underside


def cells_cut(r=R_SEAT):
    c = None
    for x in cell_x:
        s = cq.Workplane("XZ").center(x, Z_CELL_CTR).circle(r).extrude(CELL_L, both=True)
        c = s if c is None else c.union(s)
    return c


def outer_shell(h):
    b = rounded_box(OUT_W, OUT_L, h, R_VERT).translate((0, Y_OFF, 0))
    return b.faces("<Z").edges().chamfer(CHAMFER_BED).faces(">Z").edges().fillet(R_TOP * 0.6)


# ---------------------------------------------------------------- base
def make_base():
    body = outer_shell(H_BASE)
    body = body.cut(rounded_box(IN_W, IN_L, H_BASE, R_VERT - WALL).translate((0, Y_OFF, FLOOR)))
    sad_h = Z_CELL_CTR - 6.0
    for y in SADDLE_YS:
        s = cq.Workplane("XY").box(IN_W, 5.0, sad_h, centered=(True, True, False)).translate((0, y, 0))
        body = body.union(s.cut(cells_cut(CELL_D / 2 + A.CELL_CLR_D / 2)))
    for sy in (-1, 1):
        rib = cq.Workplane("XY").box(IN_W, RIB_T, Z_RIB_TOP, centered=(True, True, False)) \
            .translate((0, sy * Y_RIB_F, 0))
        for x in cell_x:
            nw = A.TAB_W + 4
            zb, zt = Z_CELL_CTR - nw / 2, Z_RIB_TOP + 1
            rib = rib.cut(cq.Workplane("XZ").center(x, (zb + zt) / 2).slot2D(zt - zb, nw, angle=90)
                          .extrude(RIB_T, both=True).translate((0, sy * Y_RIB_F, 0)))
        body = body.union(rib)
    for x, y in boss_xy:
        body = body.union(cq.Workplane("XY").circle(BOSS_D / 2).extrude(H_BASE - FLOOR).translate((x, y, FLOOR)))
        body = body.cut(cq.Workplane("XY").circle(INSERT_D / 2).extrude(INSERT_DEPTH + 1)
                        .translate((x, y, H_BASE - INSERT_DEPTH)))
    # Powerpole notch, open at the rim: the lid lowers the housings into it
    body = body.cut(cq.Workplane("XY").box(PP_W, WALL * 4, PP_SQ + PP_CLR + 1, centered=(True, True, False))
                    .translate((PP_X, FRONT_IN + WALL / 2, PP_Z0 - PP_CLR)))
    return body


# ---------------------------------------------------------------- spacer (modelled installed, exported flipped)
def make_spacer_installed():
    z_lo = Z_CELL_TOP - 9.0
    sp = cq.Workplane("XY").box(SP_X1 - SP_X0, SP_L, Z_BMS_BOT - z_lo, centered=(False, True, False)) \
        .translate((SP_X0, 0, z_lo))
    sp = sp.edges("|Y").edges(">Z").fillet(1.0)
    sp = sp.cut(cells_cut())
    # no fences on top: the flat face must go on the bed. The lid's fences + pads locate the BMS.
    return sp


# ---------------------------------------------------------------- lid (modelled installed, exported flipped)
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

    # saddle ribs clamping C3/C4 (spacer + BMS clamp C1/C2)
    for y in SADDLE_YS:
        rib = cq.Workplane("XY").box(IN_W / 2 - 2.4 - 0.5, 4.0, H_BASE - (Z_CELL_CTR + 6), centered=(False, True, False)) \
            .translate((0.5, y, Z_CELL_CTR + 6))
        lid = lid.union(rib.cut(cells_cut()))

    # BMS: corner pads press it onto the spacer; L-fences on the open (+X) side and the ends locate it
    for sx in (0, 1):
        for sy in (0, 1):
            kx = BMS_X0 + 4 + sx * (BMS_W - 8)
            ky = BMS_Y1 - 4 - sy * (BMS_L - 8)
            lid = lid.union(cq.Workplane("XY").rect(5, 5).extrude(BMS_PAD).edges("|Z").fillet(1.5)
                            .translate((kx, ky, Z_BMS_TOP)))
    fd, ft, arm = BMS_PAD + 4.0, 1.4, 10.0
    for sy in (-1, 1):
        cx = BMS_CX + (BMS_W + BMS_CLR) / 2 + ft / 2
        cy = BMS_CY + sy * ((BMS_L + BMS_CLR) / 2 + ft / 2)
        lid = lid.union(cq.Workplane("XY").box(ft, arm, fd, centered=(True, True, False))
                        .translate((cx, cy - sy * (arm / 2 - ft / 2), H_BASE - fd)))
        lid = lid.union(cq.Workplane("XY").box(arm + 12, ft, fd, centered=(True, True, False))
                        .translate((cx - (arm + 12) / 2 + ft / 2, cy, H_BASE - fd)))

    # Powerpole cradle hanging from the lid: side walls, rear stop with wire slots
    cw = 1.6
    for sx in (-1, 1):
        lid = lid.union(cq.Workplane("XY").box(cw, FRONT_IN - 0.4 - (PP_Y0 - 2), PP_SQ, centered=(True, False, False))
                        .translate((PP_X + sx * (PP_W / 2 + cw / 2), PP_Y0 - 2, PP_Z0)))
    stop = cq.Workplane("XY").box(PP_W + 2 * cw, 2.0, PP_SQ, centered=(True, False, False)) \
        .translate((PP_X, PP_Y0 - 2, PP_Z0))
    for i in range(PP_N):
        cx = PP_X - PP_W / 2 + PP_CLR + PP_SQ * (i + 0.5)
        stop = stop.cut(cq.Workplane("XZ").center(cx, PP_Z0 + PP_SQ / 2 - 1).slot2D(PP_SQ + 2, 4.8, angle=90)
                        .extrude(5, both=True).translate((0, PP_Y0 - 1, 0)))
    lid = lid.union(stop)

    # through-cuts: screw holes + counterbores, vents over BMS, zip-tie slots beside the Powerpole cradle
    for x, y in boss_xy:
        lid = lid.cut(cq.Workplane("XY").circle(SCREW_D / 2).extrude(LID_T + 2).translate((x, y, H_BASE - 1)))
        lid = lid.cut(cq.Workplane("XY").circle(SCREW_HEAD_D / 2).extrude(2).translate((x, y, H_BASE + LID_T - 1.2)))
    for i in range(-4, 5):
        lid = lid.cut(cq.Workplane("XY").center(BMS_CX, BMS_CY + i * 11).slot2D(BMS_W - 16, 3.0)
                      .extrude(LID_T + 2).translate((0, 0, H_BASE - 1)))
    for sx in (-1, 1):
        lid = lid.cut(cq.Workplane("XY").center(PP_X + sx * (PP_W / 2 + cw + 1.6), PP_Y0 + PP_L * 0.45)
                      .rect(2.0, 5.0).extrude(LID_T + 2).translate((0, 0, H_BASE - 1)))
    return lid


def to_print_lid(s):     # flip about X so the outer face lands on the bed at Z=0
    return s.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, H_BASE + LID_T))


def to_print_spacer(s):  # flat (BMS) face on the bed
    return s.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, Z_BMS_BOT))


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_b")
    os.makedirs(out, exist_ok=True)
    parts = {"base_b": make_base(), "spacer_b": to_print_spacer(make_spacer_installed()),
             "lid_b": to_print_lid(make_lid_installed())}
    for name, p in parts.items():
        cq.exporters.export(p, os.path.join(out, f"{name}.stl"), tolerance=0.05, angularTolerance=0.1)
        cq.exporters.export(p, os.path.join(out, f"{name}.step"))
        bb = p.val().BoundingBox()
        print(f"{name:8s} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f} mm  valid={p.val().isValid()}")
    print(f"outside {OUT_W:.1f} x {OUT_L:.1f} x {H_BASE + LID_T:.1f}  (variant A: {OUT_W:.1f} x {OUT_L:.1f} x "
          f"{A.H_BASE + A.LID_T:.1f})")
