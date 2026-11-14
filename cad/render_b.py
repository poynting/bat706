"""Variant B previews, sections, interference check, and an A-vs-B comparison figure."""
import os
import numpy as np
import cadquery as cq
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import case as A
import case_b as B
import render as R

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_b")


def dummies_b():
    cells = [cq.Workplane("XZ").circle(A.CELL_D / 2).extrude(A.CELL_L / 2, both=True).translate((x, 0, A.Z_CELL_CTR))
             for x in A.cell_x]
    tabs = [cq.Workplane("XY").box(A.TAB_W, A.TAB_T, 8).translate((x, sy * (A.CELL_L / 2 + A.TAB_T / 2), A.Z_CELL_CTR))
            for x in A.cell_x for sy in (-1, 1)]
    bms = cq.Workplane("XY").box(A.BMS_W, A.BMS_L, A.BMS_T, centered=(False, False, False)).translate(
        (B.BMS_X0, B.BMS_Y1 - A.BMS_L, B.Z_BMS_BOT))
    plug = cq.Workplane("XY").box(16, 8, 6).translate((B.BMS_CX, B.BMS_Y1 - A.BMS_L - 4, B.Z_BMS_BOT + 4))
    pp = cq.Workplane("XY").box(A.PP_N * A.PP_SQ, A.PP_L, A.PP_SQ, centered=(True, False, False)).translate(
        (A.PP_X, B.PP_Y0, B.PP_Z0))
    return cells, tabs, bms, plug, pp


def section(ax, shape, origin, normal, color, axes):
    vs, fs = shape.val().tessellate(0.1, 0.2)
    s = trimesh.Trimesh([(p.x, p.y, p.z) for p in vs], fs).section(plane_origin=origin, plane_normal=normal)
    if s is not None:
        for poly in s.discrete:
            ax.fill(poly[:, axes[0]], poly[:, axes[1]], color=color, alpha=0.85, lw=0.6, ec="k")


if __name__ == "__main__":
    base, spacer, lid = B.make_base(), B.make_spacer_installed(), B.make_lid_installed()
    cells, tabs, bms, plug, pp = dummies_b()

    vol = lambda a, b: a.intersect(b).val().Volume()
    checks = {
        "cells vs base": sum(vol(base, c) for c in cells + tabs),
        "cells vs spacer": sum(vol(spacer, c) for c in cells + tabs),
        "cells vs lid": sum(vol(lid, c) for c in cells + tabs),
        "spacer vs base": vol(spacer, base), "spacer vs lid": vol(spacer, lid),
        "BMS vs spacer": vol(bms, spacer), "BMS vs lid": vol(bms, lid), "BMS vs base": vol(bms, base),
        "PP vs base": vol(pp, base), "PP vs lid": vol(pp, lid), "PP vs BMS": vol(pp, bms),
        "lid vs base": vol(lid, base),
    }
    for k, v in checks.items():
        print(f"interference {k:16s}: {v:8.3f} mm^3")
    # contact check: lid pads should just touch the BMS, lid ribs/spacer should sit 0.5 mm off the cells
    print(f"gap lid->BMS {bms.val().distance(lid.val()):.2f}  spacer->C1 {cells[0].val().distance(spacer.val()):.2f}"
          f"  lid->C4 {cells[3].val().distance(lid.val()):.2f}  spacer->BMS {bms.val().distance(spacer.val()):.2f}")

    # ---- previews
    fig = plt.figure(figsize=(14, 7), dpi=110)
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    R.draw(ax, base, "#c9cdd2")
    for c in cells: R.draw(ax, c, "#3a6ea5")
    for t in tabs: R.draw(ax, t, "#d08a3a")
    R.draw(ax, spacer.translate((0, 0, 22)), "#e8e2c8")
    R.draw(ax, bms.translate((0, 0, 40)), "#2e8b57")
    R.draw(ax, plug.translate((0, 0, 40)), "#222222")
    R.draw(ax, pp.translate((0, 0, 62)), "#c0392b")
    R.draw(ax, lid.translate((0, 0, 62)), "#c9cdd2", 0.8)
    R.finish(ax, ((-80, 80), (-100, 100), (0, 140)))
    ax.set_title("Variant B exploded: spacer, BMS, lid (BMS + Powerpoles ride in the lid)")
    ax = fig.add_subplot(1, 2, 2, projection="3d")
    R.draw(ax, lid.rotate((0, 0, 0), (1, 0, 0), 180), "#9db4c8")
    R.draw(ax, pp.rotate((0, 0, 0), (1, 0, 0), 180), "#c0392b")
    R.finish(ax, ((-80, 80), (-100, 100), (-60, -40)), elev=50, azim=-60)
    ax.set_title("Lid underside: C3/C4 saddle ribs, BMS pads + fences, Powerpole cradle")
    plt.tight_layout(); plt.savefig(os.path.join(OUT, "preview_assembly_b.png"))

    fig = plt.figure(figsize=(15, 5), dpi=110)
    for i, (name, part, lim2, el, az) in enumerate([
            ("base_b (print as shown)", base, ((-80, 80), (-100, 100), (0, 55)), 40, -60),
            ("spacer_b (flat face on bed)", B.to_print_spacer(spacer), ((-75, 10), (-75, 75), (0, 15)), 45, -60),
            ("lid_b (outer face on bed)", B.to_print_lid(lid), ((-80, 80), (-100, 100), (0, 30)), 45, -60)]):
        ax = fig.add_subplot(1, 3, i + 1, projection="3d")
        R.draw(ax, part, "#9db4c8"); R.finish(ax, lim2, el, az); ax.set_title(name)
    plt.tight_layout(); plt.savefig(os.path.join(OUT, "preview_parts_b.png"))

    # ---- A vs B cross-sections at the same scale (across the cells, through the middle saddle)
    a_tray = A.make_tray().translate((0, 0, A.Z_TRAY))
    a_lid = A.make_lid().rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, A.H_BASE + A.LID_T))
    a_cells, a_bms, a_plug, a_pp = R.dummies()
    a_parts = [(A.make_base(), "#b9bec4"), (a_tray, "#e3d9a8"), (a_lid, "#9aa7b4"), (a_bms, "#2e8b57"), (a_pp, "#c0392b")]
    a_parts += [(c, "#3a6ea5") for c in a_cells if not isinstance(c, tuple)]
    b_parts = [(base, "#b9bec4"), (spacer, "#e3d9a8"), (lid, "#9aa7b4"), (bms, "#2e8b57"), (pp, "#c0392b")]
    b_parts += [(c, "#3a6ea5") for c in cells]

    fig, axs = plt.subplots(2, 2, figsize=(16, 10), dpi=110)
    for col, (title, parts, h) in enumerate([
            (f"A (current): tray clamp, {A.H_BASE + A.LID_T:.1f} mm tall", a_parts, A.H_BASE + A.LID_T),
            (f"B (lid carries BMS): {B.H_BASE + A.LID_T:.1f} mm tall", b_parts, B.H_BASE + A.LID_T)]):
        for row, (org, nrm, axes, sub) in enumerate([
                ((0, 0.5, 0), (0, 1, 0), (0, 2), "across cells, mid-length"),
                ((A.PP_X + 2, 0, 0), (1, 0, 0), (1, 2), "along x=12 (Powerpoles at right)")]):
            ax = axs[row, col]
            for shp, c in parts:
                section(ax, shp, org, nrm, c, axes)
            ax.axhline(h, color="r", lw=0.8, ls="--"); ax.axhline(58, color="k", lw=0.8, ls=":")
            ax.text(ax.get_xlim()[0] if False else -84, 58.6, "IC-706MKII height 58", fontsize=8)
            ax.set_aspect("equal"); ax.set_ylim(-2, 62); ax.grid(alpha=0.25)
            ax.set_title(f"{title}\n{sub}" if row == 0 else sub)
    plt.tight_layout(); plt.savefig(os.path.join(OUT, "compare_A_vs_B.png"))
