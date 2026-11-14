"""Variant C detail sections for the README: fasteners, cell ends (stops / foam / wiring band), parting line.
Run: python cad/details_c.py -> cad/out_c/{fastener_sections_c,end_detail_c,seam_c}.png"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import case as A
import case_c as C
import render_b as RB
import render_c as RC

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_c")
base, lid, clamp = C.make_base(), C.make_lid_installed(), C.make_pp_clamp_installed()
cells, tabs, bms, plug, pp, screws, cscrews, wire, nuts, cnuts, links, plugs, pads, bms_screws = RC.dummies_c()
foam = [C.end_foam_volume(sy, base, lid, [clamp, pp]) for sy in (1, -1)]


def draw(ax, parts, org, nrm, axes):
    for shp, col in parts:
        RB.section(ax, shp, org, nrm, col, axes)
    ax.set_aspect("equal"); ax.grid(alpha=0.3)


# fasteners
fig, axs = plt.subplots(1, 3, figsize=(18, 6), dpi=110)
draw(axs[0], [(base, "#b9bec4"), (lid, "#9aa7b4"), (cells[3], "#3a6ea5")] + [(n, "#c8c8c8") for n in nuts] +
     [(p, "#7f8fa0") for p in plugs] + [(s, "#333") for s, h in screws] + [(h, "#111") for s, h in screws], (0, 0.01, 0), (0, 1, 0), (0, 2))
axs[0].set_xlim(52, 76); axs[0].set_ylim(30, 56); axs[0].set_title("side screw (y=0): csk in wall + pad, nut in lid slot, glue-in plug")
x, y = C.boss_xy[3]
draw(axs[1], [(base, "#b9bec4"), (lid, "#9aa7b4")] + [(s, "#333") for s, h in screws] + [(h, "#111") for s, h in screws], (x, 0, 0), (1, 0, 0), (1, 2))
axs[1].set_xlim(y - 14, y + 8); axs[1].set_ylim(34, 56); axs[1].set_title("lid corner screw: lid pad on lowered boss, heat-set insert")
draw(axs[2], [(lid, "#9aa7b4"), (clamp, "#e0a040"), (pp, "#c0392b")] + [(s, "#333") for s, h in cscrews] + [(h, "#111") for s, h in cscrews],
     (0, C.PP_CLAMP_Y, 0), (0, 1, 0), (0, 2))
axs[2].set_xlim(28, 72); axs[2].set_ylim(36, 56); axs[2].set_title("Powerpole clamp: csk from below into heat-set inserts")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "fastener_sections_c.png"))

# cell ends: section along C1 axis + through a spar
fig, axs = plt.subplots(1, 2, figsize=(16, 6), dpi=110)
xs = A.cell_x[0] - C.END_STOP_W / 2 + C.END_WEB_T / 2
common = [(base, "#b9bec4"), (lid, "#9aa7b4"), (clamp, "#e0a040"), (pp, "#c0392b")] + [(c, "#3a6ea5") for c in cells] + \
         [(t, "#d08a3a") for t in tabs] + [(l, "#303030") for l in links] + [(p, "#2b2b2b") for p in pads] + [(f, "#6b6b6b") for f in foam]
for ax, xx, ttl in ((axs[0], A.cell_x[0], "cell ends along C1 axis"), (axs[1], xs, f"through a base spar (x={xs:.1f})")):
    draw(ax, common, (xx, 0, 0), (1, 0, 0), (1, 2))
    ax.set_ylim(0, 56); ax.set_title(ttl + "\nbase stop + pad / open wiring band / foam block", fontsize=10)
    ax.axhspan(C.END_STOP_BOT_Z, C.END_STOP_TOP_Z, color="#2e8b57", alpha=0.08)
axs[0].set_xlim(-C.BACK_IN - 4, -C.BACK_IN + 22); axs[1].set_xlim(C.FRONT_IN - 22, C.FRONT_IN + 4)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "end_detail_c.png"))

# parting line
fig, axs = plt.subplots(1, 2, figsize=(12, 5), dpi=110)
for ax, (org, nrm, axes, xl, ttl) in zip(axs, [((0, 20, 0), (0, 1, 0), (0, 2), (A.OUT_W / 2 - 8, A.OUT_W / 2 + 2), "long side"),
                                             ((0, 0, 0), (1, 0, 0), (1, 2), (C.FRONT_IN + A.WALL - 8, C.FRONT_IN + A.WALL + 2), "front")]):
    draw(ax, [(base, "#b9bec4"), (lid, "#9aa7b4")], org, nrm, axes)
    ax.set_xlim(*xl); ax.set_ylim(C.H_BASE - 6, C.H_BASE + A.LID_T + 1); ax.set_title("flush parting line, " + ttl)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "seam_c.png"))
print("wrote fastener_sections_c.png, end_detail_c.png, seam_c.png")
