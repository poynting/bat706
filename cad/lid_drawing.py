"""Simple line drawing of the lid underside for marking up by hand.
Viewed as the lid lies on the bench upside down (print orientation): +X right, FRONT (Powerpole end) at the bottom.
Run: python cad/lid_drawing.py -> cad/out/lid_routing.png (+ .pdf)"""
import os
import math
import tempfile
import cadquery as cq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import trimesh
import case as C

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def mesh(w):
    f = tempfile.mktemp(suffix=".stl")
    cq.exporters.export(w, f, tolerance=0.05)
    m = trimesh.load(f)
    os.remove(f)
    return m


def outline(ax, m, z, **kw):
    s = m.section(plane_origin=(0, 0, z), plane_normal=(0, 0, 1))
    if s is None:
        return
    for e in s.discrete:
        ax.plot(e[:, 0], -e[:, 1], **kw)


lid = mesh(C.make_lid_installed())
fig, ax = plt.subplots(figsize=(11, 12), dpi=130)
outline(ax, lid, C.H_BASE + 0.05, color="k", lw=1.2)              # lid edge
outline(ax, lid, C.H_BASE - 0.3, color="k", lw=0.8)               # everything hanging from the plate
outline(ax, lid, C.LEAD_Z + 0.2, color="0.45", lw=0.6)            # channel + holes at the lead axis
# BMS and cells, dashed / dotted, for reference
bx0, by1 = C.BMS_X0, C.BMS_Y1
ax.plot([bx0, bx0 + C.BMS_W, bx0 + C.BMS_W, bx0, bx0], [-by1, -by1, -(by1 - C.BMS_L), -(by1 - C.BMS_L), -by1], "g--", lw=1)
ax.text(0, -C.BMS_CY, "BMS\n(on spacer, below)", ha="center", va="center", color="g", fontsize=10, bbox=dict(fc="white", ec="none", alpha=0.9))
for k, x in enumerate(C.cell_x):
    for sx in (-1, 1):
        ax.plot([x + sx * C.CELL_D / 2] * 2, [-C.CELL_L / 2, C.CELL_L / 2], ":", color="#3a6ea5", lw=0.7)
    ax.text(x, C.CELL_L / 2 - 4, f"C{k + 1}", ha="center", color="#3a6ea5", fontsize=10)
# Powerpoles
px0, px1 = C.PP_X - C.PP_N * C.PP_SQ / 2, C.PP_X + C.PP_N * C.PP_SQ / 2
for i, col in enumerate(("#c0392b", "#222")):
    x0 = px0 + i * C.PP_SQ
    ax.add_patch(plt.Rectangle((x0, -(C.PP_Y0 + C.PP_L)), C.PP_SQ, C.PP_L, fill=False, ec=col, lw=1.6, hatch="//"))
ax.text(C.PP_X, -(C.PP_Y0 + C.PP_L) - 6, "Powerpoles (red inboard, black outboard)", ha="center", fontsize=9)
# lead routes
x_red, x_blk = C.lead_xs()
y0, y1 = C.zz_span()
path = C.zz_path(y0, y1).val()
zz = [path.positionAt(t / 200) for t in range(201)]
y_out = C.SADDLE_YS[1] - C.RIB_T / 2 - 8
for sx, lab in ((1, "black: PP -> BMS P-"), (-1, "C1- -> BMS B-")):
    xs = [sx * x_blk] * 2 + [sx * p.x for p in zz] + [sx * x_blk]
    ys = [C.PP_Y0 if sx > 0 else C.SADDLE_YS[2] + 8, y0] + [p.y for p in zz] + [y_out]
    ax.plot(xs, [-y for y in ys], color="k", lw=2.4)
    ax.annotate(lab, (sx * x_blk, -y_out), (sx * 40, -y_out + 12), ha="center", fontsize=9, arrowprops=dict(arrowstyle="->"),
                bbox=dict(fc="white", ec="none", alpha=0.9))
# red: back through the front rib, U-turn, forward at lid level between the clamp boss and the BMS corner pad
ya = y0 - 3
xr = C.red_return_x()
rad = (x_red - xr) / 2
xc = (x_red + xr) / 2
arc = [(xc + rad * math.cos(t), ya - rad * math.sin(t)) for t in [i / 40 * math.pi for i in range(41)]]
xs = [x_red, x_red] + [p[0] for p in arc] + [xr, xr]
ys = [C.PP_Y0, ya] + [p[1] for p in arc] + [ya, C.FRONT_IN - 2]
ax.plot(xs, [-y for y in ys], color="#c0392b", lw=2.4)
ax.annotate("red: U-turn, back through its own front-rib hole,\nbetween clamp post and BMS corner pad -> C4+",
            (xr, -(ya - rad)), (xr - 32, -(ya - rad) + 4), ha="center", fontsize=9, color="#c0392b",
            bbox=dict(fc="white", ec="none", alpha=0.9), arrowprops=dict(arrowstyle="->", color="#c0392b"))
ax.add_patch(plt.Rectangle((C.BMS_CX - 8, -(C.BMS_Y1 + 8)), 16, 8, fill=False, ec="g", lw=1, ls="--"))
ax.text(C.BMS_CX, -(C.BMS_Y1 + 4), "balance plug", ha="center", va="center", color="g", fontsize=8)
for y, lab in ((C.SADDLE_YS[2], "front rib"), (C.SADDLE_YS[1], "middle rib"), (C.SADDLE_YS[0], "back rib")):
    ax.text(-C.OUT_W / 2 - 3, -y, lab, ha="right", va="center", fontsize=9)
ax.text(0, -(C.FRONT_IN + C.WALL) - 8, "FRONT (Powerpole end)", ha="center", fontsize=11, weight="bold")
ax.text(0, (C.BACK_IN + C.WALL) + 5, "BACK", ha="center", fontsize=11, weight="bold")
ax.set_aspect("equal")
ax.set_xlim(-C.OUT_W / 2 - 25, C.OUT_W / 2 + 5)
ax.set_ylim(-(C.FRONT_IN + C.WALL) - 14, C.BACK_IN + C.WALL + 10)
ax.set_xticks(range(-70, 71, 10)); ax.set_yticks(range(-80, 81, 10)); ax.grid(alpha=0.15)
ax.set_title("Lid underside as it lies on the bench (upside down), front at the bottom - mark up freely", fontsize=11)
plt.tight_layout()
for ext in ("png", "pdf"):
    plt.savefig(os.path.join(OUT, f"lid_routing.{ext}"))
print("wrote lid_routing.png/.pdf")
