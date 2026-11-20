"""Variant: Daly 4S 20 A BMS (34 x 59 x 9 mm), LOW PROFILE. Revision of variant_daly.py, which stays as it is.

The board lies CROSSWISE between the middle and back lid beams, so no lid ridge passes over it and the lid's
underside presses straight on its top. That drops the rim from 52.5 to 48.2 mm (case 54.5 -> 50.2 mm tall).
Same footprint: width and length are set by the cells.

  - board: label up, leads toward C4 (+X), balance socket toward C1 (-X), on 1 mm double-sided foam tape
    on the unchanged spacer; its front edge sits 0.5 mm behind the middle beam's ridge, which locates it
  - lid: pressed onto the board (0.3 mm into the tape); short end walls between the leads and beside the
    balance plug locate it in X. No old BMS corner pads.
  - P- (black) goes straight out over C4 to the black output lead (joint where the published design has it)
  - B- (blue) leaves the same end, loops back over C4 (7 mm bend radius) and runs to C1 in the lane between
    the board and the back beam
  - Powerpole clamp: its underside is hollowed to follow C4 (full 4.5 mm at the screw bosses)
  - reprint: base, lid, Powerpole clamp, nut plugs. The spacer is the published one, unchanged.

Run: python cad/variant_daly_low.py -> full check suite + Daly checks, cad/out_daly_low/* (viewer: viewer/build_viewer.py)
"""
import math, os
import cadquery as cq
import case as C0

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out_daly_low")

# ---------------------------------------------------------------- board (34 x 59 x 9; positions off the photo)
D_LONG, D_SHORT, D_T = 59.0, 34.0, 9.0
TAPE_T = 1.0
PRELOAD = 0.3                                  # lid underside below the free board top: compresses the tape
H_BASE = C0.Z_BMS_BOT + TAPE_T + D_T - PRELOAD

V = C0.load_variant("case_daly_low", H_BASE=H_BASE, LID_BMS_PADS=False, PP_CLAMP_CELL_RELIEF=True)

def _render_copy():
    """A private copy of render.py bound to the low-profile model (the shared `render` keeps the published one)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("render_daly_low", os.path.join(HERE, "render.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.C = V
    return mod


R = _render_copy()

D_X0, D_X1 = -D_LONG / 2, D_LONG / 2
D_Y1 = V.SADDLE_YS[1] - V.RIB_T / 2 - 0.5      # 0.5 mm behind the middle beam's ridge (the ridge locates it)
D_Y0 = D_Y1 - D_SHORT
D_Z0 = V.Z_BMS_BOT + TAPE_T
D_Z1 = D_Z0 + D_T
ZC = D_Z0 + D_T / 2                            # lead / socket axis height
# leads on the +X end, measured along the end from its +Y corner (label up, leads toward +X)
LEAD_P_Y, LEAD_B_Y, LEAD_NTC_Y = D_Y1 - 4.7, D_Y0 + 6.0, D_Y1 - 21.7
LEAD_D, NTC_D = 3.6, 1.8
# balance socket on the -X end, 18-26 mm from the +Y corner; mating plug + latch keep-out
SOCK_C = D_Y1 - 22.0
PLUG_KEEP = (SOCK_C - 8.0, SOCK_C + 8.0)
LANE_Y = (V.SADDLE_YS[0] + V.RIB_T / 2 + D_Y0) / 2   # B- run, between the board and the back beam
B_BEND_R = 7.0

# ---------------------------------------------------------------- end walls (hang from the lid)
WALL_CLR, WALL_T, WALL_DROP, WALL_LEAD_IN, WALL_MIN = 0.5, 2.0, 3.0, 0.8, 3.0


def free_spans(lo, hi, keepouts):
    spans, cur = [], lo
    for a, b in sorted(keepouts):
        if a > cur:
            spans.append((cur, min(a, hi)))
        cur = max(cur, b)
    if cur < hi:
        spans.append((cur, hi))
    return [(a, b) for a, b in spans if b - a >= WALL_MIN]


def wall_spans():
    k = LEAD_D / 2 + 1.0
    plus = free_spans(D_Y0, D_Y1, [(LEAD_P_Y - k, LEAD_P_Y + k), (LEAD_B_Y - k, LEAD_B_Y + k),
                                   (LEAD_NTC_Y - NTC_D / 2 - 1.0, LEAD_NTC_Y + NTC_D / 2 + 1.0)])
    minus = free_spans(D_Y0, D_Y1, [PLUG_KEEP])
    return {1: plus, -1: minus}


def make_walls():
    walls = None
    z0, z1 = D_Z1 - WALL_DROP, V.H_BASE + 0.01
    for sx, spans in wall_spans().items():
        xi = sx * (D_X1 + WALL_CLR)                 # inner face
        xo = xi + sx * WALL_T
        k = WALL_LEAD_IN
        prof = [(xi + sx * k, z0), (xo, z0), (xo, z1), (xi, z1), (xi, z0 + k)]   # 45-degree lead-in, inner bottom
        for a, b in spans:
            w = cq.Workplane("XZ").polyline(prof).close().extrude(-(b - a)).translate((0, a, 0))
            walls = w if walls is None else walls.union(w)
    return walls


def make_lid():
    return V.make_lid_installed().union(make_walls())


# ---------------------------------------------------------------- dummies
def planar_path(x, y, heading, segs, z):
    """segs: ('L', length) or ('A', signed turn deg, radius). Returns a wire in the plane z."""
    w = cq.Workplane("XY").workplane(offset=z).moveTo(x, y)
    for s in segs:
        if s[0] == "L":
            x, y = x + s[1] * math.cos(heading), y + s[1] * math.sin(heading)
            w = w.lineTo(x, y)
        else:
            turn, r = math.radians(s[1]), s[2]
            sgn = 1 if turn > 0 else -1
            cx, cy = x - sgn * r * math.sin(heading), y + sgn * r * math.cos(heading)
            a0 = math.atan2(y - cy, x - cx)
            am, a1 = a0 + turn / 2, a0 + turn
            x, y = cx + r * math.cos(a1), cy + r * math.sin(a1)
            w = w.threePointArc((cx + r * math.cos(am), cy + r * math.sin(am)), (x, y))
            heading += turn
    return w.wire(), (x, y)


def daly_dummies():
    bms = cq.Workplane("XY").box(D_LONG, D_SHORT, D_T, centered=False).translate((D_X0, D_Y0, D_Z0))
    tape = cq.Workplane("XY").box(D_LONG - 2, D_SHORT - 2, TAPE_T, centered=False).translate((D_X0 + 1, D_Y0 + 1, V.Z_BMS_BOT))
    plug = cq.Workplane("XY").box(8.0, PLUG_KEEP[1] - PLUG_KEEP[0] - 2, 6.0, centered=(False, True, True)) \
        .translate((D_X0 - 8.0, SOCK_C, ZC))
    r = LEAD_D / 2
    # P-: straight out over C3/C4 to just short of the black output lead's end (the joint)
    p_end = V.zz_x() - 4.0
    lead_p = cq.Workplane("YZ").center(LEAD_P_Y, ZC).circle(r).extrude(p_end - D_X1).translate((D_X1, 0, 0))
    # B-: 3 mm out, "light-bulb" loop (CCW th, CW 180+th, radius B_BEND_R) into the lane, then along it to C1
    th = math.degrees(math.acos((LEAD_B_Y - LANE_Y) / (2 * B_BEND_R)))
    b_end = -V.zz_x() + 4.0
    path, (xe, ye) = planar_path(D_X1, LEAD_B_Y, 0.0, [("L", 3.0), ("A", th, B_BEND_R), ("A", -(180 + th), B_BEND_R)], ZC)
    assert abs(ye - LANE_Y) < 0.05, ye
    loop = cq.Workplane("YZ", origin=(D_X1, 0, 0)).center(LEAD_B_Y, ZC).circle(r).sweep(cq.Workplane().add(path), isFrenet=False)
    run = cq.Workplane("YZ").center(LANE_Y, ZC).circle(r).extrude(xe - b_end).translate((b_end, 0, 0))
    lead_b = loop.union(run)
    ntc = cq.Workplane("YZ").center(LEAD_NTC_Y, ZC).circle(NTC_D / 2).extrude(10.0).translate((D_X1, 0, 0))
    bulb_max_x = cq.Workplane().add(path).val().BoundingBox().xmax + r
    return bms, tape, plug, lead_p, lead_b, ntc, th, bulb_max_x


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    base, spacer, lid, clamp = V.make_base(), V.make_spacer_installed(), make_lid(), V.make_pp_clamp_installed()
    sp0 = C0.make_spacer_installed()
    same_spacer = abs(sp0.val().Volume() - spacer.val().Volume()) < 1e-6 and abs(sp0.cut(spacer).val().Volume()) < 1e-6
    print(f"case {V.OUT_W:.1f} x {V.OUT_L:.1f} x {V.H_BASE + V.LID_T:.1f} mm (published {C0.H_BASE + C0.LID_T:.1f}); "
          f"spacer identical to the published one: {same_spacer}")
    print("---- published check suite at the new height (old 60 x 120 board checks dropped)")
    checks, dm, out_leads = R.run_checks(base, spacer, lid, clamp, with_bms=False)
    cells, tabs, _b, _p, pp, screws, clamp_screws, wire, nuts, _cn, links, plugs, pads, _bs = dm
    bad = {k: v for k, v in checks.items() if v > 1e-3}

    print("---- Daly")
    bms, tape, plug, lead_p, lead_b, ntc, th, bulb_x = daly_dummies()
    walls = make_walls()
    vol = lambda a, b: a.intersect(b).val().Volume()
    dchecks = {
        "Daly vs spacer": vol(bms, spacer), "Daly vs base": vol(bms, base), "Daly vs cells": sum(vol(bms, c) for c in cells),
        "Daly vs end walls": vol(bms, walls), "Daly vs output leads": sum(vol(bms, l) for l in out_leads),
        "tape vs spacer": vol(tape, spacer),
        "balance plug vs lid": vol(plug, lid), "balance plug vs spacer": vol(plug, spacer),
        "balance plug vs cells": sum(vol(plug, c) for c in cells),
        "P- vs lid": vol(lead_p, lid), "B- vs lid": vol(lead_b, lid), "NTC vs lid": vol(ntc, lid),
        "Daly leads vs spacer": vol(lead_p, spacer) + vol(lead_b, spacer),
        "Daly leads vs cells": sum(vol(l, c) for l in (lead_p, lead_b) for c in cells),
        "Daly leads vs base": vol(lead_p, base) + vol(lead_b, base),
        "Daly leads vs output leads": sum(vol(l, o) for l in (lead_p, lead_b) for o in out_leads),
        "Daly leads vs each other": vol(lead_p, lead_b),
        "Daly leads vs PP clamp": vol(lead_p, clamp) + vol(lead_b, clamp),
        "Daly leads vs side screws/nuts": sum(vol(l, s) + vol(l, h) for l in (lead_p, lead_b) for s, h in screws)
                                          + sum(vol(l, n) for l in (lead_p, lead_b) for n in nuts),
        "end walls vs spacer": vol(walls, spacer), "end walls vs cells": sum(vol(walls, c) for c in cells),
    }
    for k, v in dchecks.items():
        print(f"interference {k:32s}: {v:8.3f} mm^3")
    bad.update({k: v for k, v in dchecks.items() if v > 1e-3})
    press = vol(bms, lid)
    print(f"lid pressing the board top (intended {PRELOAD} mm): {press:.0f} mm^3 over the board's "
          f"{D_LONG * D_SHORT:.0f} mm^2 (less vent slots) = {press / (D_LONG * D_SHORT):.2f} mm average")
    print(f"board x {D_X0:.1f}..{D_X1:.1f}, y {D_Y0:.2f}..{D_Y1:.2f}, z {D_Z0:.1f}..{D_Z1:.1f}; "
          f"middle ridge face y={V.SADDLE_YS[1] - V.RIB_T / 2:.1f} (stop, {(V.SADDLE_YS[1] - V.RIB_T / 2) - D_Y1:.1f} mm), "
          f"ridge bottom z={V.H_BASE - V.RIDGE_H:.1f} overlaps the board edge by {D_Z1 - (V.H_BASE - V.RIDGE_H):.1f} mm")
    print(f"B- lane y={LANE_Y:.2f}: {D_Y0 - LANE_Y - LEAD_D / 2:.2f} mm to the board, "
          f"{LANE_Y - LEAD_D / 2 - (V.SADDLE_YS[0] + V.RIB_T / 2):.2f} mm to the back beam; loop {th:.1f} + {180 + th:.1f} deg "
          f"at r {B_BEND_R}, reaches x={bulb_x:.1f}")
    print(f"end walls: +X (lead end) spans {[(round(a, 1), round(b, 1)) for a, b in wall_spans()[1]]}, "
          f"-X (socket end) spans {[(round(a, 1), round(b, 1)) for a, b in wall_spans()[-1]]}")
    c4 = cells[3]
    print(f"PP clamp: {clamp.val().distance(c4.val()):.2f} mm to C4, thinnest {V.PP_Z0 - (V.Z_CELL_TOP + V.SEAT_GAP):.2f} mm "
          f"over C4's crest, {V.PP_CLAMP_T} mm at the screws")
    print(f"zig-zag block bottom z={V.zz_block_z0():.2f}, {V.zz_block_z0() - V.Z_CELL_TOP:.2f} mm over C1/C4 tops; "
          f"lid lip bottom z={V.H_BASE - 3:.1f} vs side screw top z={V.SIDE_Z + 1.5:.1f}")
    print(f"NON-ZERO: {bad}" if bad else f"all {len(checks) + len(dchecks)} interference checks zero")

    # ---- exports (spacer: use the published spacer.stl)
    parts = {"base": base, "lid": V.to_print_lid(lid),
             "pp_clamp": clamp.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, V.PP_Z0)),
             "nut_plug_x6": V.make_nut_plug_installed().rotate((0, 0, 0), (0, 1, 0), 90)}
    for name, p in parts.items():
        cq.exporters.export(p, os.path.join(OUT, f"{name}.stl"), tolerance=0.05, angularTolerance=0.1)
        cq.exporters.export(p, os.path.join(OUT, f"{name}.step"))
        bb = p.val().BoundingBox()
        print(f"{name:12s} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f} mm  valid={p.val().isValid()}  solids={len(p.solids().vals())}")

    # ---- pictures
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, FancyBboxPatch
    fig, ax = plt.subplots(figsize=(9, 10.5), dpi=120)
    ax.add_patch(FancyBboxPatch((-V.OUT_W / 2, V.Y_OFF - V.OUT_L / 2), V.OUT_W, V.OUT_L,
                                boxstyle=f"round,pad=0,rounding_size={V.R_VERT}", fc="#eceff1", ec="k", lw=1.5))
    for i, x in enumerate(V.cell_x):
        ax.add_patch(Rectangle((x - V.CELL_D / 2, -V.CELL_L / 2), V.CELL_D, V.CELL_L, fc="#5b8cc0", ec="k"))
        ax.text(x, 45, f"C{i + 1}", ha="center", va="center", fontsize=15, color="w", weight="bold", rotation=90)
    ax.add_patch(Rectangle((V.SP_X0, -V.SP_L / 2), V.SP_X1 - V.SP_X0, V.SP_L, fc="#e8e2c8", ec="#998", alpha=0.9))
    for y in V.SADDLE_YS:
        ax.add_patch(Rectangle((-V.IN_W / 2, y - V.RIB_T / 2), V.IN_W, V.RIB_T, fc=(0.4, 0.45, 0.55, 0.3), ec="#556", ls="--"))
    ax.text(-V.IN_W / 2 + 1, V.SADDLE_YS[1] + 3, "lid beams (dashed)", fontsize=7)
    ax.add_patch(Rectangle((D_X0, D_Y0), D_LONG, D_SHORT, fc="#d0402a", ec="k", lw=1.5, zorder=5))
    ax.text(0, (D_Y0 + D_Y1) / 2, f"Daly 4S 20 A\n{D_LONG:.0f} x {D_SHORT:.0f} x {D_T:.0f}, label up", ha="center", va="center",
            color="w", fontsize=9, weight="bold", zorder=6)
    ax.add_patch(Rectangle((D_X0 - 8, PLUG_KEEP[0] + 1), 8, PLUG_KEEP[1] - PLUG_KEEP[0] - 2, fc="#f5f5f5", ec="k", zorder=6))
    ax.text(D_X0 - 10, SOCK_C, "balance\nplug", ha="right", va="center", fontsize=8, zorder=7)
    for sh, col in ((lead_p, "#222222"), (lead_b, "#2060d0"), (ntc, "#666666")):
        R.section(ax, sh, (0, 0, ZC), (0, 0, 1), col, (0, 1))
    for sx, spans in wall_spans().items():
        for a, b in spans:
            x0 = sx * (D_X1 + WALL_CLR) if sx > 0 else -(D_X1 + WALL_CLR + WALL_T)
            ax.add_patch(Rectangle((x0, a), WALL_T, b - a, fc="none", ec="#123", lw=1.2, ls="--", zorder=7))
    ax.text(V.zz_x(), LEAD_P_Y + 6, "P− joins the black\noutput lead", ha="center", fontsize=8, zorder=8,
            bbox=dict(fc="white", ec="none", alpha=0.85))
    ax.text(-V.zz_x() + 6, LANE_Y - 9, "B− to the C1− lead", ha="center", fontsize=8, zorder=8,
            bbox=dict(fc="white", ec="none", alpha=0.85))
    for i, (col, lbl) in enumerate((("#c0392b", "P+"), ("#222", "P−"))):
        ax.add_patch(Rectangle((V.PP_X - V.PP_SQ * V.PP_N / 2 + i * V.PP_SQ, V.PP_Y0), V.PP_SQ, V.PP_L, fc=col, ec="k", zorder=6))
    ax.text(V.PP_X, V.FRONT_IN + V.WALL + 6, "Powerpoles  FRONT", ha="center", fontsize=10, weight="bold")
    ax.text(0, -V.BACK_IN - V.WALL - 8, "BACK", ha="center", fontsize=10, weight="bold")
    ax.set_xlim(-V.OUT_W / 2 - 6, V.OUT_W / 2 + 6); ax.set_ylim(V.Y_OFF - V.OUT_L / 2 - 14, V.Y_OFF + V.OUT_L / 2 + 14)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(f"Daly low profile: top view, lid off (lid end walls dashed)  {V.OUT_W:.1f} × {V.OUT_L:.1f} × "
                 f"{V.H_BASE + V.LID_T:.1f} mm")
    plt.tight_layout(); plt.savefig(os.path.join(OUT, "layout.png"))

    fig, axs = plt.subplots(1, 2, figsize=(16, 5), dpi=110)
    for ax, (y, ttl) in zip(axs, ((D_Y0 + D_SHORT / 2 + 3, "through the board"), (V.SADDLE_YS[1] + 0.5, "through the middle beam"))):
        for shp, col in [(base, "#b9bec4"), (spacer, "#e3d9a8"), (lid, "#9aa7b4"), (bms, "#d0402a"), (tape, "#333"), (clamp, "#e0a040")] + \
                [(c, "#3a6ea5") for c in cells] + [(s, "#333") for s, h in screws] + [(h, "#333") for s, h in screws] + \
                [(lead_p, "#222"), (lead_b, "#2060d0"), (pp, "#c0392b")]:
            R.section(ax, shp, (0, y, 0), (0, 1, 0), col, (0, 2))
        ax.axhline(58, color="k", lw=0.8, ls=":"); ax.text(-84, 58.8, "IC-706MKII height 58", fontsize=8)
        ax.axhline(C0.H_BASE + C0.LID_T, color="#a33", lw=0.8, ls="--")
        ax.text(40, C0.H_BASE + C0.LID_T + 0.8, f"published lid top {C0.H_BASE + C0.LID_T:.1f}", fontsize=8, color="#a33")
        ax.set_aspect("equal"); ax.set_xlim(-85, 85); ax.set_ylim(-2, 62); ax.grid(alpha=0.25); ax.set_title(f"section {ttl} (y={y:.1f})")
    plt.suptitle(f"Daly low profile: {V.OUT_W:.1f} × {V.OUT_L:.1f} × {V.H_BASE + V.LID_T:.1f} mm")
    plt.tight_layout(); plt.savefig(os.path.join(OUT, "cross_section.png"))
