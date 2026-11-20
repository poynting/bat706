"""Variant: Daly 4S 12 V 20 A LiFePO4 BMS (15 A model is the same box) (34 x 59 x 9 mm, potted, flying leads) instead of the 60 x 120 x 10 board.

The published design (case.py) is left untouched. Base, spacer, Powerpole clamp and nut plugs are reused as they
are; only the lid gains four corner caps that locate and press down the smaller board. Everything else on the lid
(beams, Powerpole cradle, zig-zags, lead holes, vents, the old BMS corner pads) is unchanged, so the caps could
even be printed separately and glued into an already-printed lid.

Board: label up, leads toward the BACK, balance socket on the FRONT edge. Seen from above, that puts P- (black)
on the C4 side and B- (blue) on the C1 side, so neither lead crosses the board: P- runs over C4 to the black
output lead, B- over C1 to the C1- lead, both behind the middle beam. Held on the spacer with 1 mm double-sided
foam tape; the caps keep it there with the lid on.

Run: python cad/variant_daly.py -> checks, cad/out_daly/{lid_daly.stl,.step, daly_caps_only.stl, preview_daly.png,
     layout_daly.png} (viewer: viewer/build_viewer.py)
"""
import math, os
import cadquery as cq
import case as C
import render as R

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out_daly")

# ---------------------------------------------------------------- board (from the listing photo; measure yours)
D_W, D_L, D_T = 34.0, 59.0, 9.0
TAPE_T = 1.0                                   # double-sided foam tape under the board
D_Y0 = -24.0                                   # back (lead) edge; front (socket) edge at D_Y0 + D_L
D_X0, D_X1 = -D_W / 2, D_W / 2
D_Y1 = D_Y0 + D_L
D_Z0 = C.Z_BMS_BOT + TAPE_T
D_Z1 = D_Z0 + D_T
# flying leads at the back edge (x from the board centre, label up, leads toward -Y), measured off the photo
LEAD_P_X, LEAD_B_X, LEAD_NTC_X = 12.3, -11.0, -4.7
LEAD_P_D, LEAD_B_D, LEAD_NTC_D = 3.6, 3.6, 1.8     # silicone 14 AWG-ish; NTC thin
# balance socket on the front edge, toward the C1 side
SOCK_X0, SOCK_X1 = -9.0, -1.0
PLUG_KEEP = (-13.0, 3.0)                       # mating plug + latch footprint along X

# ---------------------------------------------------------------- corner caps (hang from the lid)
CAP_CLR = 0.5                                  # board edge -> cap wall
CAP_WALL = 2.0
CAP_PAD = 5.0                                  # square pressing pad over each corner
CAP_PRELOAD = 0.3                              # pad face below the board top: compresses the tape a little
CAP_DROP = 3.0                                 # walls reach this far down the board sides
CAP_SIDE_LEN = 9.0                             # side wall length along Y from the corner
CAP_LEAD_IN = 0.8                              # 45-degree lead-in on the walls' inner bottom edge
# end-wall legs along X from each corner, kept clear of the leads (back) and the balance plug (front)
CAP_END_LEG = {(1, -1): (LEAD_P_X + LEAD_P_D / 2 + 1.0, D_X1),     # back, C4 side: outboard of P-
               (-1, -1): (D_X0, LEAD_B_X - LEAD_B_D / 2 - 1.0),    # back, C1 side: outboard of B-
               (1, 1): (PLUG_KEEP[1] + 1.0, D_X1),                 # front, C4 side
               (-1, 1): (D_X0, PLUG_KEEP[0] - 1.0)}                # front, C1 side


def make_cap(sx, sy):
    """One corner cap (installed coords): pad on the board top + L of walls round the corner."""
    xc, yc = (D_X1 if sx > 0 else D_X0), (D_Y1 if sy > 0 else D_Y0)
    z_pad = D_Z1 - CAP_PRELOAD
    z_wall = D_Z1 - CAP_DROP
    top = C.H_BASE + 0.01
    pad = cq.Workplane("XY").box(CAP_PAD, CAP_PAD, top - z_pad, centered=False) \
        .translate((xc - (CAP_PAD if sx > 0 else 0), yc - (CAP_PAD if sy > 0 else 0), z_pad))
    # side wall (along Y), outside the board's X edge
    wx0 = xc + CAP_CLR if sx > 0 else xc - CAP_CLR - CAP_WALL
    wy0 = yc - CAP_SIDE_LEN if sy > 0 else yc - CAP_CLR - CAP_WALL
    wy1 = yc + CAP_CLR + CAP_WALL if sy > 0 else yc + CAP_SIDE_LEN
    side = cq.Workplane("XY").box(CAP_WALL, wy1 - wy0, top - z_wall, centered=False).translate((wx0, wy0, z_wall))
    # end wall (along X), outside the board's Y edge, only over the allowed leg
    lx0, lx1 = CAP_END_LEG[(sx, sy)]
    lx0, lx1 = (lx0, xc + CAP_CLR + CAP_WALL) if sx > 0 else (xc - CAP_CLR - CAP_WALL, lx1)
    ey0 = yc + CAP_CLR if sy > 0 else yc - CAP_CLR - CAP_WALL
    end = cq.Workplane("XY").box(lx1 - lx0, CAP_WALL, top - z_wall, centered=False).translate((lx0, ey0, z_wall))
    # bridge from the walls in to the pad, at pad level (one solid, braced corner)
    web = cq.Workplane("XY").box(abs(wx0 + (0 if sx > 0 else CAP_WALL) - (xc - (CAP_PAD if sx > 0 else -CAP_PAD))) + 0.02,
                                 CAP_PAD, top - z_pad, centered=False)
    web = web.translate((min(xc - CAP_PAD, wx0) if sx > 0 else wx0, yc - (CAP_PAD if sy > 0 else 0), z_pad))
    cap = pad.union(side).union(end).union(web)
    # 45-degree lead-in on the inner bottom edges of the walls: the board is pushed home as the lid closes
    for ax_, pos, sgn in (("x", xc + sx * CAP_CLR, sx), ("y", yc + sy * CAP_CLR, sy)):
        k = CAP_LEAD_IN
        if ax_ == "x":
            prism = cq.Workplane("YZ").polyline([(0, 0), (0, k), (sgn * k, 0)]).close().extrude(200, both=True)
            prism = prism.rotate((0, 0, 0), (0, 1, 0), 0)
            tri = cq.Workplane("XZ").polyline([(pos, z_wall - 0.01), (pos + sgn * k, z_wall - 0.01), (pos, z_wall + k)]).close() \
                .extrude(100, both=True)
        else:
            tri = cq.Workplane("YZ").polyline([(pos, z_wall - 0.01), (pos + sgn * k, z_wall - 0.01), (pos, z_wall + k)]).close() \
                .extrude(100, both=True)
        cap = cap.cut(tri)
    return cap


def make_caps():
    caps = None
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = make_cap(sx, sy)
            caps = c if caps is None else caps.union(c)
    return caps


def make_lid_daly():
    return C.make_lid_installed().union(make_caps())


# ---------------------------------------------------------------- dummies
def daly_dummies():
    bms = cq.Workplane("XY").box(D_W, D_L, D_T, centered=False).translate((D_X0, D_Y0, D_Z0))
    tape = cq.Workplane("XY").box(D_W - 2, D_L - 2, TAPE_T, centered=False).translate((D_X0 + 1, D_Y0 + 1, C.Z_BMS_BOT))
    zc = D_Z0 + D_T / 2
    # balance plug: 8 mm deep, 14 x 6, in front of the socket
    plug = cq.Workplane("XY").box(PLUG_KEEP[1] - PLUG_KEEP[0] - 2, 8.0, 6.0, centered=(True, False, True)) \
        .translate(((PLUG_KEEP[0] + PLUG_KEEP[1]) / 2, D_Y1, zc))
    # P- and B-: straight back 4 mm, 90-degree bend (r 6), sideways over C4 / C1 to the output-lead line
    leads = []
    for x0, dia, sx in ((LEAD_P_X, LEAD_P_D, 1), (LEAD_B_X, LEAD_B_D, -1)):
        r, rb = dia / 2, 6.0
        ya = D_Y0 - 4.0
        x_end = sx * C.zz_x()
        s1 = cq.Workplane("XZ").center(x0, zc).circle(r).extrude(-4.0).translate((0, ya, 0))
        a = cq.Vector(x0, ya, zc)
        b = cq.Vector(x0 + sx * rb, ya - rb, zc)
        m = cq.Vector(x0 + sx * rb * (1 - math.cos(math.pi / 4)), ya - rb * math.sin(math.pi / 4), zc)
        path = cq.Workplane("XY").add(cq.Wire.assembleEdges([cq.Edge.makeThreePointArc(a, m, b)]))
        bend = cq.Workplane("XZ", origin=(0, ya, 0)).center(x0, zc).circle(r).sweep(path, isFrenet=True)
        run = cq.Workplane("YZ").center(ya - rb, zc).circle(r).extrude(x_end - b.x).translate((b.x, 0, 0))
        leads.append(s1.union(bend).union(run))
    ntc = cq.Workplane("XZ").center(LEAD_NTC_X, zc).circle(LEAD_NTC_D / 2).extrude(-10.0).translate((0, D_Y0 - 10.0, 0))
    return bms, tape, plug, leads, ntc


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    base, spacer, lid = C.make_base(), C.make_spacer_installed(), make_lid_daly()
    caps = make_caps()
    clamp = C.make_pp_clamp_installed()
    cells, tabs, _bms, _plug, pp, screws, clamp_screws, wire, nuts, _cn, links, plugs, pads, bms_screws = R.dummies()
    out_leads = R.leads()
    bms, tape, plug, dleads, ntc = daly_dummies()
    vol = lambda a, b: a.intersect(b).val().Volume()
    checks = {
        "Daly vs lid": vol(bms, lid), "Daly vs spacer": vol(bms, spacer), "Daly vs base": vol(bms, base),
        "Daly vs cells": sum(vol(bms, c) for c in cells),
        "tape vs spacer": vol(tape, spacer),
        "balance plug vs lid": vol(plug, lid), "balance plug vs spacer": vol(plug, spacer),
        "balance plug vs output leads": sum(vol(plug, l) for l in out_leads),
        "Daly leads vs lid": sum(vol(l, lid) for l in dleads), "Daly leads vs spacer": sum(vol(l, spacer) for l in dleads),
        "Daly leads vs cells": sum(vol(l, c) for l in dleads for c in cells),
        "Daly leads vs base": sum(vol(l, base) for l in dleads),
        "Daly leads vs side screws/nuts": sum(vol(l, s) + vol(l, h) for l in dleads for s, h in screws) + sum(vol(l, n) for l in dleads for n in nuts),
        "NTC lead vs lid": vol(ntc, lid), "NTC lead vs spacer": vol(ntc, spacer),
        "Daly vs output leads": sum(vol(bms, l) for l in out_leads),
        "Daly vs old BMS screw pockets": 0.0 if not C.bms_hole_xy() else sum(
            vol(bms, cq.Workplane("XY").circle(C.BMS_POCKET_D / 2).extrude(20).translate((x, y, C.Z_BMS_BOT - 10))) for x, y in C.bms_hole_xy()),
        "caps vs spacer": vol(caps, spacer), "caps vs cells": sum(vol(caps, c) for c in cells),
        "caps vs output leads": sum(vol(caps, l) for l in out_leads), "caps vs PP clamp": vol(caps, clamp),
        "caps vs balance plug": vol(caps, plug), "caps vs Daly leads": sum(vol(caps, l) for l in dleads) + vol(caps, ntc),
    }
    preload = vol(bms, caps)
    for k, v in checks.items():
        print(f"interference {k:32s}: {v:8.3f} mm^3")
    print(f"cap pads into the board top (intended {CAP_PRELOAD} mm tape preload): {preload:.1f} mm^3 "
          f"= 4 x {CAP_PAD:.0f} x {CAP_PAD:.0f} x {preload / (4 * CAP_PAD ** 2):.2f} mm")
    print(f"board {D_X0:.1f}..{D_X1:.1f} x {D_Y0:.1f}..{D_Y1:.1f} y, z {D_Z0:.1f}..{D_Z1:.1f}; "
          f"ridge underside {C.H_BASE - C.RIDGE_H:.1f} -> {C.H_BASE - C.RIDGE_H - D_Z1:.1f} mm over the board")
    sp_y0 = -C.SP_L / 2
    print(f"spacer behind the board: {D_Y0 - sp_y0:.1f} mm; in front (plug side): {sp_y0 + C.SP_L - D_Y1:.1f} mm; "
          f"plug front face y={D_Y1 + 8:.1f}, front beam at y={C.SADDLE_YS[2] - C.RIB_T / 2:.1f}")
    print(f"P- / B- leads cross C4 / C1 at y={D_Y0 - 10:.1f} (middle beam back face y={C.SADDLE_YS[1] - C.RIB_T / 2:.1f}, "
          f"back beam front face y={C.SADDLE_YS[0] + C.RIB_T / 2:.1f}), z={D_Z0 + D_T / 2:.1f}")

    cq.exporters.export(C.to_print_lid(lid), os.path.join(OUT, "lid_daly.stl"), tolerance=0.05, angularTolerance=0.1)
    cq.exporters.export(C.to_print_lid(lid), os.path.join(OUT, "lid_daly.step"))
    cq.exporters.export(C.to_print_lid(caps), os.path.join(OUT, "daly_caps_only.stl"), tolerance=0.05, angularTolerance=0.1)
    v = lid.val()
    print(f"lid_daly valid={v.isValid()} solids={len(lid.solids().vals())}")

    # ---- previews
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, FancyBboxPatch
    fig = plt.figure(figsize=(14, 7), dpi=110)
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    R.draw(ax, spacer, "#e8e2c8")
    for c in cells: R.draw(ax, c, "#3a6ea5")
    R.draw(ax, bms, "#d0402a"); R.draw(ax, plug, "#eeeeee")
    for l, col in zip(dleads, ("#222222", "#2060d0")): R.draw(ax, l, col)
    R.draw(ax, caps.translate((0, 0, 20)), "#9db4c8")
    R.finish(ax, ((-75, 75), (-80, 70), (0, 80)), elev=35, azim=-60)
    ax.set_title("Daly on the spacer (caps lifted 20 mm)")
    ax = fig.add_subplot(1, 2, 2, projection="3d")
    R.draw(ax, lid.rotate((0, 0, 0), (1, 0, 0), 180), "#9db4c8")
    R.finish(ax, ((-80, 80), (-100, 100), (-60, -40)), elev=50, azim=-60)
    ax.set_title("lid_daly underside: published lid + 4 corner caps")
    plt.tight_layout(); plt.savefig(os.path.join(OUT, "preview_daly.png"))

    # ---- plan view, lid off, with the lid's beams and caps dashed
    fig, ax = plt.subplots(figsize=(9, 10.5), dpi=120)
    ax.add_patch(FancyBboxPatch((-C.OUT_W / 2, C.Y_OFF - C.OUT_L / 2), C.OUT_W, C.OUT_L,
                                boxstyle=f"round,pad=0,rounding_size={C.R_VERT}", fc="#eceff1", ec="k", lw=1.5))
    for i, x in enumerate(C.cell_x):
        ax.add_patch(Rectangle((x - C.CELL_D / 2, -C.CELL_L / 2), C.CELL_D, C.CELL_L, fc="#5b8cc0", ec="k"))
        ax.text(x, -55, f"C{i + 1}", ha="center", va="center", fontsize=15, color="w", weight="bold", rotation=90)
    ax.add_patch(Rectangle((C.SP_X0, -C.SP_L / 2), C.SP_X1 - C.SP_X0, C.SP_L, fc="#e8e2c8", ec="#998", alpha=0.9))
    for x, y in C.bms_hole_xy():
        ax.add_patch(plt.Circle((x, y), C.BMS_POCKET_D / 2, fc="none", ec="#998", ls=":"))
    for y in C.SADDLE_YS:
        ax.add_patch(Rectangle((-C.IN_W / 2, y - C.RIB_T / 2), C.IN_W, C.RIB_T, fc=(0.4, 0.45, 0.55, 0.3), ec="#556", ls="--"))
    ax.add_patch(Rectangle((D_X0, D_Y0), D_W, D_L, fc="#d0402a", ec="k", lw=1.5, zorder=5))
    ax.text(0, D_Y0 + D_L / 2, f"Daly 4S 20 A\n{D_W:.0f} x {D_L:.0f} x {D_T:.0f}\nlabel up", ha="center", va="center",
            color="w", fontsize=9, weight="bold", zorder=6)
    ax.add_patch(Rectangle((PLUG_KEEP[0] + 1, D_Y1), PLUG_KEEP[1] - PLUG_KEEP[0] - 2, 8, fc="#f5f5f5", ec="k", zorder=6))
    ax.text((PLUG_KEEP[0] + PLUG_KEEP[1]) / 2, D_Y1 + 11, "balance plug", ha="center", fontsize=8, zorder=7)
    yl = D_Y0 - 10
    ax.plot([LEAD_P_X, LEAD_P_X, C.zz_x()], [D_Y0, yl, yl], color="#222", lw=4, solid_capstyle="round", zorder=6)
    ax.plot([LEAD_B_X, LEAD_B_X, -C.zz_x()], [D_Y0, yl, yl], color="#2060d0", lw=4, solid_capstyle="round", zorder=6)
    ax.plot([LEAD_NTC_X, LEAD_NTC_X], [D_Y0, D_Y0 - 10], color="#555", lw=1.5, zorder=6)
    ax.text(C.zz_x(), yl - 6, "P− joins the black\noutput lead", ha="center", fontsize=8, zorder=7,
            bbox=dict(fc="white", ec="none", alpha=0.85))
    ax.text(-C.zz_x(), yl - 6, "B− joins the\nC1− lead", ha="center", fontsize=8, zorder=7,
            bbox=dict(fc="white", ec="none", alpha=0.85))
    bb = caps.val().BoundingBox()
    for sx in (-1, 1):
        for sy in (-1, 1):
            b = make_cap(sx, sy).val().BoundingBox()
            ax.add_patch(Rectangle((b.xmin, b.ymin), b.xlen, b.ylen, fc="none", ec="#123", lw=1.2, ls="--", zorder=7))
    ax.text(D_X1 + 4, D_Y1 + 2, "lid corner caps\n(dashed)", fontsize=8, zorder=7)
    for i, (col, lbl) in enumerate((("#c0392b", "P+"), ("#222", "P−"))):
        x0 = C.PP_X - C.PP_SQ * C.PP_N / 2 + i * C.PP_SQ
        ax.add_patch(Rectangle((x0, C.PP_Y0), C.PP_SQ, C.PP_L, fc=col, ec="k", zorder=6))
    ax.text(C.PP_X, C.FRONT_IN + C.WALL + 6, "Powerpoles  FRONT", ha="center", fontsize=10, weight="bold")
    ax.text(0, -C.BACK_IN - C.WALL - 8, "BACK", ha="center", fontsize=10, weight="bold")
    ax.set_xlim(-C.OUT_W / 2 - 6, C.OUT_W / 2 + 6); ax.set_ylim(C.Y_OFF - C.OUT_L / 2 - 14, C.Y_OFF + C.OUT_L / 2 + 14)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("Daly variant: top view, lid off (old screw pockets dotted, unused)")
    plt.tight_layout(); plt.savefig(os.path.join(OUT, "layout_daly.png"))
