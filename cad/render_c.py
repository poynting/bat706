"""Variant C: interference + side-screw alignment checks, previews, and an A/B/C section comparison."""
import os
import cadquery as cq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import case as A
import case_b as B
import case_c as C
import render as RA
import render_b as RB

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_c")


def dummies_c():
    cells = [cq.Workplane("XZ").circle(A.CELL_D / 2).extrude(A.CELL_L / 2, both=True).translate((x, 0, A.Z_CELL_CTR))
             for x in A.cell_x]
    tabs = [cq.Workplane("XY").box(A.TAB_W, A.TAB_T, 8).translate((x, sy * (A.CELL_L / 2 + A.TAB_T / 2), A.Z_CELL_CTR))
            for x in A.cell_x for sy in (-1, 1)]
    bms = cq.Workplane("XY").box(A.BMS_W, A.BMS_L, A.BMS_T, centered=(False, False, False)).translate(
        (C.BMS_X0, C.BMS_Y1 - A.BMS_L, C.Z_BMS_BOT))
    plug = cq.Workplane("XY").box(16, 8, 6).translate((C.BMS_CX, C.BMS_Y1 + 4, C.Z_BMS_BOT + 4))   # balance plug, front edge
    pp = cq.Workplane("XY").box(A.PP_N * A.PP_SQ, A.PP_L, A.PP_SQ, centered=(True, False, False)).translate(
        (C.PP_X, C.PP_Y0, C.PP_Z0))
    def csk_screw(pt, d, length):
        """ISO 10642 M3: head top flush with the surface at pt, axis d (into the part), total length incl. head."""
        d = cq.Vector(*d).normalized(); p = cq.Vector(*pt)
        head = cq.Workplane("XY").add(cq.Solid.makeCone(3.36, 1.5, 1.86, p, d))
        shank = cq.Workplane("XY").add(cq.Solid.makeCylinder(1.5, length - 1.86, p + d * 1.86, d))
        return shank, head
    # side screws M3 x 10, lid corner screws M3 x 10 (countersunk, flush)
    screws = [csk_screw((sx * (A.IN_W / 2 + A.WALL), y, C.SIDE_Z), (-sx, 0, 0), 10.0) for sx, y in C.SIDE_SCREWS]
    corner_screws = [csk_screw((x, y, C.H_BASE + A.LID_T), (0, 0, -1), 10.0) for x, y in C.boss_xy]
    # Powerpole clamp screws (M3 x 8, upward through the bar into the lid bosses)
    # Powerpole clamp: M3 x 10 countersunk UP from under the bar, into heat-set inserts in the lid bosses
    clamp_screws = [csk_screw((bx, C.PP_CLAMP_Y, C.PP_Z0 - C.PP_CLAMP_T), (0, 0, 1), 10.0) for bx in C.pp_clamp_boss_x()]
    # M3 nuts (AF 5.5, t 2.4): side nuts stand in their slots (flats facing +-Y), clamp nuts in the bar pockets
    nuts = []
    for sx, y in C.SIDE_SCREWS:
        n0, n1 = C.side_nut_x(sx)
        xc = (n0 + n1) / 2
        nut = cq.Workplane("YZ").polygon(6, C.NUT_AF / 0.8660254).extrude(C.NUT_T).rotate((0, 0, 0), (1, 0, 0), 30) \
            .translate((xc - C.NUT_T / 2, y, C.SIDE_Z))
        nuts.append(nut)
    clamp_nuts = []
    # 12 AWG silicone (4.5 mm) B+ run along the C3/C4 valley, full cell length
    wire = cq.Workplane("XZ").center(A.PITCH, 31.0).circle(2.25).extrude(A.CELL_L / 2, both=True)
    # 12 AWG series links running straight across in the tab plane (back: C1-C2, C3-C4; front: C2-C3)
    links = []
    for sy, (i, j) in ((-1, (0, 1)), (-1, (2, 3)), (1, (1, 2))):
        xa, xb = A.cell_x[i], A.cell_x[j]
        links.append(cq.Workplane("YZ").center(sy * (A.CELL_L / 2 + 2.25 + 0.1), A.Z_CELL_CTR).circle(2.25)
                     .extrude(xb - xa).translate((xa, 0, 0)))
    plugs = [C.make_nut_plug_installed(sx, y) for sx, y in C.SIDE_SCREWS]
    # closed-cell foam pads on the base stop faces (compressed into the 1.5 mm gap), bottom third
    pads = []
    for sy in (-1, 1):
        for xc in A.cell_x:
            for z0, z1 in ((A.Z_CELL_BOT + 1.5, C.END_STOP_BOT_Z),):   # base-stop pads; top is the foam block
                p = cq.Workplane("XY").box(C.END_STOP_W - 1, C.END_FOAM_GAP - 0.02, z1 - z0, centered=(True, False, False)) \
                    .translate((xc, A.CELL_L / 2 + 0.01, z0))
                pads.append(p if sy > 0 else p.mirror("XZ"))
    # BMS mounting: M3 x 5 ISO 7380 button heads up through the spacer + lower PCB into the standoff threads
    bms_screws = []
    for x, y in C.bms_hole_xy():
        zb = C.bms_screw_head_z(x)
        head = cq.Workplane("XY").circle(C.BMS_HEAD_D / 2).extrude(C.BMS_HEAD_K).translate((x, y, zb))
        shank = cq.Workplane("XY").circle(1.5).extrude(C.BMS_SCREW_L).translate((x, y, zb + C.BMS_HEAD_K))
        bms_screws.append((shank, head))
    return cells, tabs, bms, plug, pp, screws + corner_screws, clamp_screws, wire, nuts, clamp_nuts, links, plugs, pads, bms_screws


def leads_c():
    """Dummy 4 mm leads: [black output, red output, C1- -> BMS B-].
    Black: housing rear -> backstop + front rib -> zig-zag -> middle rib -> 6 mm beyond.
    Red: housing rear -> backstop + front rib -> U-turn -> forward at lid level between the clamp boss and the BMS
    corner pad, through its own front-rib hole, toward the front bay.
    C1 side: the black run mirrored, entering the front rib from 5 mm in front of it."""
    import math
    r = C.LEAD_D / 2
    y0, y1 = C.zz_span()
    y_out = C.SADDLE_YS[1] - C.RIB_T_C / 2 - 6
    z = C.LEAD_Z + 0.2                              # pushed up toward the channel floor
    x_red, x_blk = C.lead_xs()
    ring = lambda x: [(x + r * math.cos(t / 16 * 2 * math.pi), z + r * math.sin(t / 16 * 2 * math.pi)) for t in range(16)]
    straight = lambda x, ya, yb: cq.Workplane("XZ").center(x, z).circle(r).extrude(-(ya - yb)).translate((0, yb, 0))   # XZ extrudes along -Y; negative = +Y from yb
    black = straight(x_blk, C.PP_Y0, y0).union(C.zz_sweep([ring(x_blk)], y0 + 0.01, y1 - 0.01)).union(straight(x_blk, y1, y_out))
    # red: out of the front rib, 3 mm straight, U-turn to the return line, then forward at lid level between the
    # clamp boss and the BMS corner pad, through its own front-rib hole, to just past the BMS front edge
    ya = y0 - 3.0
    xr, zr = C.red_return_x(), C.H_BASE - r
    A_, B_ = cq.Vector(x_red, ya, C.LEAD_Z), cq.Vector(xr, ya, zr)
    rad = (A_ - B_).Length / 2
    apex = (A_ + B_) * 0.5 - cq.Vector(0, rad, 0)
    loop = cq.Workplane("XY").add(cq.Wire.assembleEdges([cq.Edge.makeThreePointArc(A_, apex, B_)]))
    prof = cq.Workplane("XZ", origin=(0, ya, 0)).center(x_red, C.LEAD_Z).circle(r)
    red = cq.Workplane("XZ").center(x_red, C.LEAD_Z).circle(r).extrude(-(C.PP_Y0 - ya)).translate((0, ya, 0)) \
        .union(prof.sweep(loop, isFrenet=True)) \
        .union(cq.Workplane("XZ").center(xr, zr).circle(r).extrude(-(C.PP_Y0 + 8 - ya)).translate((0, ya, 0)))
    y_in = C.SADDLE_YS[2] + C.RIB_T_C / 2 + 5
    c1 = black.cut(cq.Workplane("XY").box(200, 200, 200).translate((0, y_in + 100, 0))).mirror("YZ")
    return [black, red, c1]


if __name__ == "__main__":
    base, spacer, lid = C.make_base(), C.make_spacer_installed(), C.make_lid_installed()
    cells, tabs, bms, plug, pp, screws, clamp_screws, wire, nuts, clamp_nuts, links, plugs, pads, bms_screws = dummies_c()
    clamp = C.make_pp_clamp_installed()
    leads = leads_c()
    vol = lambda a, b: a.intersect(b).val().Volume()
    checks = {
        "cells vs base": sum(vol(base, c) for c in cells + tabs),
        "cells vs spacer": sum(vol(spacer, c) for c in cells + tabs),
        "cells vs lid": sum(vol(lid, c) for c in cells + tabs),
        "spacer vs base": vol(spacer, base), "spacer vs lid": vol(spacer, lid),
        "BMS vs spacer": vol(bms, spacer), "BMS vs lid": vol(bms, lid), "BMS vs base": vol(bms, base),
        "plug vs lid": vol(plug, lid), "plug vs spacer": vol(plug, spacer),
        "PP vs base": vol(pp, base), "PP vs lid": vol(pp, lid), "PP vs BMS": vol(pp, bms),
        "lid vs base": vol(lid, base),
        "screw shanks vs base": sum(vol(s, base) for s, h in screws[:6]),
        "screw shanks vs lid": sum(vol(s, lid) for s, h in screws),
        "csk heads vs base": sum(vol(h, base) for s, h in screws),
        "csk heads vs lid": sum(vol(h, lid) for s, h in screws),
        "corner shanks vs base": sum(vol(s, base) for s, h in screws[6:]),
        "side screws vs cells": sum(vol(s, c) for s, h in screws for c in cells),
        "PP clamp vs lid": vol(clamp, lid), "PP clamp vs base": vol(clamp, base), "PP clamp vs cells": sum(vol(clamp, c) for c in cells),
        "PP clamp vs PP": vol(clamp, pp),
        "clamp screws vs lid": sum(vol(s, lid) for s, h in clamp_screws),
        "clamp shanks vs bar": sum(vol(s, clamp) for s, h in clamp_screws),
        "clamp csk heads vs bar": sum(vol(h, clamp) for s, h in clamp_screws),
        "clamp screws vs cells": sum(vol(s, c) for s, h in clamp_screws for c in cells),
        "side nuts vs lid": sum(vol(n, lid) for n in nuts),
        "nut plugs vs lid": sum(vol(p, lid) for p in plugs), "nut plugs vs nuts": sum(vol(p, n) for p in plugs for n in nuts),
        "links vs base": sum(vol(l, base) for l in links), "links vs lid": sum(vol(l, lid) for l in links),
        "links vs PP clamp": sum(vol(l, clamp) for l in links), "links vs cells": sum(vol(l, c) for l in links for c in cells),
        "tabs vs lid+clamp": sum(vol(t, lid) + vol(t, clamp) for t in tabs),
        "PP vs clamp": vol(pp, clamp), "wire vs clamp": vol(wire, clamp),
        "foam pads vs base": sum(vol(p, base) for p in pads), "foam pads vs lid": sum(vol(p, lid) for p in pads),
        "foam pads vs clamp": sum(vol(p, clamp) for p in pads), "foam pads vs cells": sum(vol(p, c) for p in pads for c in cells),
        "foam pads vs tabs": sum(vol(p, t) for p in pads for t in tabs),
        "BMS screws vs spacer": sum(vol(s, spacer) + vol(h, spacer) for s, h in bms_screws),
        "BMS screw heads vs cells": sum(vol(h, c) for s, h in bms_screws for c in cells),
 "links vs corner bosses/walls": sum(vol(l, base) for l in links),
        "clamp nuts vs bar": sum(vol(n, clamp) for n in clamp_nuts),
        "clamp scr heads vs cells": sum(vol(h, c) for s, h in clamp_screws for c in cells),
        "B+ wire vs lid": vol(wire, lid), "B+ wire vs spacer": vol(wire, spacer), "B+ wire vs base": vol(wire, base),
        "B+ wire vs cells": sum(vol(wire, c) for c in cells),
        "PP leads vs lid": sum(vol(l, lid) for l in leads), "PP leads vs cells": sum(vol(l, c) for l in leads for c in cells),
        "PP leads vs clamp": sum(vol(l, clamp) for l in leads), "black leads vs BMS": vol(leads[0], bms) + vol(leads[2], bms),
        "PP leads vs base": sum(vol(l, base) for l in leads), "black leads vs B+ wire": vol(leads[0], wire) + vol(leads[2], wire),
        "red lead vs balance plug": vol(leads[1], plug),
        "PP leads vs PP": sum(vol(l, pp) for l in leads), "PP leads vs clamp screws": sum(vol(l, s) + vol(l, h) for l in leads for s, h in clamp_screws),
    }
    for k, v in checks.items():
        print(f"interference {k:20s}: {v:8.3f} mm^3")
    for sy, nm in ((1, "FRONT"), (-1, "BACK")):
        f = C.end_foam_volume(sy, base, lid, [clamp, pp])
        bb = f.val().BoundingBox()
        print(f"end foam {nm}: {bb.xlen:.0f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm envelope, {f.val().Volume() / 1000:.1f} cm^3, "
              f"{len(f.solids().vals())} piece(s)")
    xr = C.red_return_x()
    print(f"red lead forward run: x={xr:.2f}, {xr - 2 - (C.BMS_X0 + A.BMS_W - C.BMS_PAD_IN + 2.5):.2f} mm to the BMS corner pad, "
          f"{C.pp_clamp_boss_x()[0] - C.PP_BOSS_D / 2 - (xr + 2):.2f} mm to the clamp boss; lies on the BMS top edge "
          f"({C.BMS_X0 + A.BMS_W - (xr - 2):.1f} mm of its width over the board, y {C.SADDLE_YS[2] - C.RIB_T_C / 2:.1f}.."
          f"{C.BMS_Y1:.1f}) in the {C.H_BASE - C.Z_BMS_TOP:.1f} mm BMS->lid gap: contact, no clearance")
    print(f"gaps: lid->BMS {bms.val().distance(lid.val()):.2f}  spacer->BMS {bms.val().distance(spacer.val()):.2f}  "
          f"spacer->C2 {cells[1].val().distance(spacer.val()):.2f}  lid->C1 {cells[0].val().distance(lid.val()):.2f}  "
          f"lid->C4 {cells[3].val().distance(lid.val()):.2f}  lid->spacer {spacer.val().distance(lid.val()):.2f}  "
          f"red->lid {leads[1].val().distance(lid.val()):.2f}  red->BMS {leads[1].val().distance(bms.val()):.2f}  "
          f"clamp->PP {clamp.val().distance(pp.val()):.2f}  clamp-head->C4 {min(h.val().distance(cells[3].val()) for s, h in clamp_screws):.2f}")
    # thread engagement: shank length through each nut / insert
    def engaged(shank, region):
        return shank.intersect(region).val().Volume() / (3.14159 * 1.5 ** 2)
    for (sx, y), (s, h), n in zip(C.SIDE_SCREWS, screws[:6], nuts):
        tip = s.val().BoundingBox()
        print(f"side screw x{'+' if sx > 0 else '-'} y={y:6.1f}: {engaged(s, n):.1f} of {C.NUT_T} mm nut engaged, "
              f"tip {abs((tip.xmin if sx > 0 else tip.xmax)) - abs(C.side_nut_x(sx)[0 if sx > 0 else 1]):+.1f} mm past nut")
    for (x, y), (s, h) in zip(C.boss_xy, screws[6:]):
        top = C.H_BASE - C.LID_PAD
        bore = cq.Workplane("XY").circle(A.INSERT_D / 2).extrude(C.CORNER_INSERT_DEPTH).translate((x, y, top - C.CORNER_INSERT_DEPTH))
        print(f"corner screw ({x:6.1f},{y:6.1f}): {engaged(s, bore):.1f} mm in insert bore")
    for bx, (s, h) in zip(C.pp_clamp_boss_x(), clamp_screws):
        bore = cq.Workplane("XY").circle(A.INSERT_D / 2).extrude(C.PP_INSERT_DEPTH).translate((bx, C.PP_CLAMP_Y, C.PP_Z0))
        tip = s.val().BoundingBox().zmax
        print(f"clamp screw x={bx:5.1f}: {engaged(s, bore):.1f} mm in insert bore, tip {C.PP_Z0 + C.PP_INSERT_DEPTH - tip:.1f} mm short of "
              f"bore bottom, {C.H_BASE + A.LID_T - tip:.1f} mm below lid top (hidden)")

    for (x, y), (s, h) in zip(C.bms_hole_xy(), bms_screws):
        tip = s.val().BoundingBox().zmax
        eng = tip - (C.Z_BMS_BOT + C.BMS_PCB_T)
        print(f"BMS screw ({x:5.1f},{y:6.1f}): {eng:.1f} of {C.BMS_THREAD_DEPTH} mm standoff thread, "
              f"head {min(h.val().distance(c.val()) for c in cells):.2f} mm off the nearest cell, "
              f"{C.Z_BMS_BOT - (C.bms_screw_head_z(x) + C.BMS_HEAD_K):.2f} mm of spacer between head and PCB")
    print(f"spacer crest over C2/C3: {C.Z_BMS_BOT - (A.Z_CELL_TOP + C.SEAT_GAP):.2f} mm")

    # ---- previews
    fig = plt.figure(figsize=(14, 7), dpi=110)
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    RA.draw(ax, base, "#c9cdd2")
    for c in cells: RA.draw(ax, c, "#3a6ea5")
    for l in links: RA.draw(ax, l, "#333333")
    for t in tabs: RA.draw(ax, t, "#d08a3a")
    RA.draw(ax, spacer.translate((0, 0, 22)), "#e8e2c8")
    RA.draw(ax, bms.translate((0, 0, 40)), "#2e8b57")
    RA.draw(ax, plug.translate((0, 0, 40)), "#222222")
    RA.draw(ax, pp.translate((0, 0, 62)), "#c0392b")
    RA.draw(ax, clamp.translate((0, 0, 45)), "#e0a040")
    RA.draw(ax, wire, "#c0392b")
    RA.draw(ax, lid.translate((0, 0, 62)), "#c9cdd2", 0.8)
    for s, h in screws:
        RA.draw(ax, s, "#444"); RA.draw(ax, h, "#444")
    RA.finish(ax, ((-80, 80), (-100, 100), (0, 140)))
    ax.set_title("Variant C exploded: centred BMS, side screws into lid ribs")
    ax = fig.add_subplot(1, 2, 2, projection="3d")
    RA.draw(ax, lid.rotate((0, 0, 0), (1, 0, 0), 180), "#9db4c8")
    RA.draw(ax, pp.rotate((0, 0, 0), (1, 0, 0), 180), "#c0392b")
    RA.draw(ax, clamp.rotate((0, 0, 0), (1, 0, 0), 180), "#e0a040")
    for l, col in zip(leads, ("#222222", "#c0392b", "#222222")):
        RA.draw(ax, l.rotate((0, 0, 0), (1, 0, 0), 180), col)
    RA.finish(ax, ((-80, 80), (-100, 100), (-60, -40)), elev=50, azim=-60)
    ax.set_title("Lid underside: beams, recessed PP cradle + clamp, zig-zag lead relief")
    plt.tight_layout(); plt.savefig(os.path.join(OUT, "preview_assembly_c.png"))

    fig = plt.figure(figsize=(20, 5), dpi=110)
    for i, (name, part, lim2, el, az) in enumerate([
            ("pp_clamp_c (nut pockets up)", clamp.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, C.PP_Z0)), ((25, 75), (-95, -40), (0, 10)), 45, -60),
            ("base_c (print as shown)", base, ((-80, 80), (-100, 100), (0, 55)), 30, -35),
            ("spacer_c (flat face on bed)", C.to_print_spacer(spacer), ((-45, 45), (-75, 75), (0, 15)), 45, -60),
            ("lid_c (outer face on bed)", C.to_print_lid(lid), ((-80, 80), (-100, 100), (0, 30)), 45, -60)]):
        ax = fig.add_subplot(1, 4, i + 1, projection="3d")
        RA.draw(ax, part, "#9db4c8"); RA.finish(ax, lim2, el, az); ax.set_title(name)
    plt.tight_layout(); plt.savefig(os.path.join(OUT, "preview_parts_c.png"))

    # ---- A / B / C sections across the cells through the middle rib station, same scale
    a_cells, a_bms, a_plug, a_pp = RA.dummies()
    a_parts = [(A.make_base(), "#b9bec4"), (A.make_tray().translate((0, 0, A.Z_TRAY)), "#e3d9a8"),
               (A.make_lid().rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, A.H_BASE + A.LID_T)), "#9aa7b4"),
               (a_bms, "#2e8b57")] + [(c, "#3a6ea5") for c in a_cells if not isinstance(c, tuple)]
    b_cells, _, b_bms, _, _ = RB.dummies_b()
    b_parts = [(B.make_base(), "#b9bec4"), (B.make_spacer_installed(), "#e3d9a8"), (B.make_lid_installed(), "#9aa7b4"),
               (b_bms, "#2e8b57")] + [(c, "#3a6ea5") for c in b_cells]
    c_parts = [(base, "#b9bec4"), (spacer, "#e3d9a8"), (lid, "#9aa7b4"), (bms, "#2e8b57")] + \
              [(c, "#3a6ea5") for c in cells] + [(s, "#333") for s, h in screws] + [(h, "#333") for s, h in screws] + [(wire, "#c0392b")]
    fig, axs = plt.subplots(3, 1, figsize=(10, 15), dpi=110)
    for ax, (title, parts) in zip(axs, [
            (f"A: tray clamp, 4 top + 3 tray screws, {A.H_BASE + A.LID_T:.1f} mm", a_parts),
            (f"B: lid carries BMS (BMS at wall), 4 top screws, {B.H_BASE + A.LID_T:.1f} mm", b_parts),
            (f"C: BMS centred, wall-to-wall beams, 4 top + 6 side screws, {C.H_BASE + A.LID_T:.1f} mm", c_parts)]):
        for shp, col in parts:
            RB.section(ax, shp, (0, 0.5, 0), (0, 1, 0), col, (0, 2))
        ax.axhline(58, color="k", lw=0.8, ls=":"); ax.text(-84, 58.8, "IC-706MKII height 58", fontsize=8)
        ax.set_aspect("equal"); ax.set_xlim(-85, 85); ax.set_ylim(-2, 62); ax.grid(alpha=0.25)
        ax.set_title(title + "  — section through the middle rib station")
    plt.tight_layout(); plt.savefig(os.path.join(OUT, "compare_A_B_C.png"))
