"""Top-view physical layout of variant C (the build design). Run: python schematic/layout.py -> layout.png"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cad"))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import case as A
import case_c as C

fig, ax = plt.subplots(figsize=(9, 10.5), dpi=120)
ax.add_patch(FancyBboxPatch((-A.OUT_W / 2, C.Y_OFF - C.OUT_L / 2), A.OUT_W, C.OUT_L,
                            boxstyle=f"round,pad=0,rounding_size={A.R_VERT}", fc="#eceff1", ec="k", lw=1.5))
ax.add_patch(FancyBboxPatch((-A.IN_W / 2, C.Y_OFF - C.IN_L / 2), A.IN_W, C.IN_L, boxstyle="round,pad=0,rounding_size=3",
                            fc="white", ec="#888"))
for sy in (-1, 1):   # base end stops (bottom third) + spars
    y0 = C.Y_STOP if sy > 0 else -C.Y_STOP - C.END_STOP_T
    ax.add_patch(Rectangle((-A.IN_W / 2, y0), A.IN_W, C.END_STOP_T, fc="#b0bec5"))
    y_wall = C.FRONT_IN if sy > 0 else -C.BACK_IN
    for xc in A.cell_x:
        for xw in (xc - C.END_STOP_W / 2, xc + C.END_STOP_W / 2 - C.END_WEB_T):
            ax.add_patch(Rectangle((xw, min(y0, y_wall)), C.END_WEB_T, abs(y_wall - y0), fc="#b0bec5"))
front_sign = ["−", "+", "−", "+"]
for i, x in enumerate(A.cell_x):
    ax.add_patch(Rectangle((x - A.CELL_D / 2, -A.CELL_L / 2), A.CELL_D, A.CELL_L, fc="#5b8cc0", ec="k"))
    f, b = front_sign[i], ("+" if front_sign[i] == "−" else "−")
    ax.text(x, A.CELL_L / 2 - 10, f, ha="center", va="center", fontsize=22, color="w", weight="bold")
    ax.text(x, -A.CELL_L / 2 + 10, b, ha="center", va="center", fontsize=22, color="w", weight="bold")
    ax.text(x, -20, f"C{i + 1}", ha="center", va="center", fontsize=16, color="w", weight="bold", rotation=90)
    for sy in (-1, 1):
        ax.add_patch(Rectangle((x - A.TAB_W / 2, sy * (A.CELL_L / 2 + 1) - 1), A.TAB_W, 2, fc="#d08a3a", zorder=4))
X = A.cell_x
yF, yB = A.CELL_L / 2 + 4.3, -A.CELL_L / 2 - 4.3
kw = dict(lw=5, solid_capstyle="round", zorder=5, color="#333")
ax.plot([X[0], X[1]], [yB, yB], **kw); ax.text((X[0] + X[1]) / 2, yB - 9, "C1+→C2−", ha="center", fontsize=9)
ax.plot([X[2], X[3]], [yB, yB], **kw); ax.text((X[2] + X[3]) / 2, yB - 9, "C3+→C4−", ha="center", fontsize=9)
ax.plot([X[1], X[2]], [yF, yF], **kw); ax.text((X[1] + X[2]) / 2, yF + 12, "C2+→C3−", ha="center", fontsize=9)
# BMS centred on the spacer over C2/C3
ax.add_patch(Rectangle((C.BMS_X0, C.BMS_Y1 - A.BMS_L), A.BMS_W, A.BMS_L, fc=(0.18, 0.55, 0.34, 0.25), ec="#2e7d32", lw=2, ls="--", zorder=6))
ax.text(0, C.BMS_CY + 25, "BMS on spacer\n(over C2/C3)", ha="center", color="#1b5e20", fontsize=10, weight="bold", zorder=7)
ax.add_patch(Rectangle((-8, C.BMS_Y1 - A.BMS_L - 7), 16, 7, fc="k", zorder=7))
ax.text(0, C.BMS_Y1 - A.BMS_L - 12, "balance plug", ha="center", fontsize=8, zorder=7)
# lid beams (3 stations, wall to wall) + side screws
for y in C.SADDLE_YS:
    ax.add_patch(Rectangle((-A.IN_W / 2, y - C.RIB_T_C / 2), A.IN_W, C.RIB_T_C, fc=(0.4, 0.45, 0.55, 0.35), ec="none", zorder=6))
    for sx in (-1, 1):
        ax.plot([sx * (A.IN_W / 2 + A.WALL / 2)], [y], marker="o", ms=7, color="#222", zorder=8)
ax.text(-A.OUT_W / 2 - 2, C.SADDLE_YS[2] + 4, "lid beam +\nside screw", fontsize=7, ha="right")
# B+ run in the C3/C4 valley, fuse pocket over C4
ax.plot([A.PITCH, A.PITCH], [-A.CELL_L / 2 + 5, A.CELL_L / 2 - 2], color="#c0392b", lw=3, ls="--", zorder=7)
ax.text(A.PITCH + 2, -40, "B+ run\n(C3/C4 valley)", color="#c0392b", fontsize=8, zorder=8)
ax.add_patch(Rectangle((A.cell_x[3] - 6, 4), 12, 36, fc=(0.9, 0.6, 0.2, 0.5), ec="#c47a10", zorder=7))
ax.text(A.cell_x[3], 22, "30 A\nATM\nfuse", ha="center", va="center", fontsize=8, zorder=8)
# Powerpoles front-right ("red right, tongue top" seen from outside -> red is the -X housing)
y0 = C.PP_Y0
for i, (col, lbl) in enumerate((("#c0392b", "P+"), ("#222", "P−"))):
    x0 = C.PP_X - A.PP_SQ * A.PP_N / 2 + i * A.PP_SQ
    ax.add_patch(Rectangle((x0, y0), A.PP_SQ, A.PP_L, fc=col, ec="k", alpha=0.9, zorder=9))
    ax.text(x0 + A.PP_SQ / 2, y0 + 5, lbl, color="w", ha="center", fontsize=8, weight="bold", zorder=10)
ax.text(C.PP_X, C.FRONT_IN + A.WALL + 8, "Powerpoles  FRONT", ha="center", fontsize=10, weight="bold")
ax.text(0, -C.BACK_IN - A.WALL - 8, "BACK", ha="center", fontsize=10, weight="bold")
for x, y in C.boss_xy:
    ax.add_patch(plt.Circle((x, y), A.BOSS_D / 2, fc="#90a4ae", ec="k", zorder=6))
ax.set_xlim(-A.OUT_W / 2 - 22, A.OUT_W / 2 + 6); ax.set_ylim(C.Y_OFF - C.OUT_L / 2 - 14, C.Y_OFF + C.OUT_L / 2 + 14)
ax.set_aspect("equal"); ax.axis("off")
ax.set_title(f"Variant C top view, lid off  ({A.OUT_W:.1f} × {C.OUT_L:.1f} mm outside)")
plt.tight_layout(); plt.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "layout.png"))
