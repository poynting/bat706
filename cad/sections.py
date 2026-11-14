"""Cross-section drawings of the closed assembly (reliable fit check + build reference)."""
import os, numpy as np, trimesh, cadquery as cq
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import case as C, render as R

def mesh(shape):
    vs, fs = shape.val().tessellate(0.1, 0.2)
    return trimesh.Trimesh([(p.x, p.y, p.z) for p in vs], fs)

def section(ax, shape, origin, normal, color, axes, hatch=None):
    s = mesh(shape).section(plane_origin=origin, plane_normal=normal)
    if s is None: return
    for poly in s.discrete:
        ax.fill(poly[:, axes[0]], poly[:, axes[1]], color=color, alpha=0.85, lw=0.6, ec="k")

base, tray, lid = C.make_base(), C.make_tray(), C.make_lid()
tray = tray.translate((0, 0, C.Z_TRAY))
lid = lid.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, C.H_BASE + C.LID_T))
cells, bms, plug, pp = R.dummies()
parts = [(base, "#b9bec4"), (tray, "#e3d9a8"), (lid, "#9aa7b4"), (bms, "#2e8b57"), (plug, "#222"), (pp, "#c0392b")]
parts += [(c[1], "#d08a3a") if isinstance(c, tuple) else (c, "#3a6ea5") for c in cells]

fig, axs = plt.subplots(3, 1, figsize=(11, 13), dpi=110)
for ax, (title, y_or_x, normal, axes) in zip(axs, [
        ("Section A-A: across cells at mid-length (looking from front)", (0, 0.5, 0), (0, 1, 0), (0, 2)),
        (f"Section B-B: along cell 1 axis (x={C.cell_x[0]:.1f}), front is right", (C.cell_x[0], 0, 0), (1, 0, 0), (1, 2)),
        (f"Section C-C: through Powerpoles (x={C.PP_X + 2:.0f}), front is right", (C.PP_X + 2, 0, 0), (1, 0, 0), (1, 2))]):
    for shp, col in parts:
        section(ax, shp, y_or_x, normal, col, axes)
    ax.set_aspect("equal"); ax.set_title(title); ax.grid(alpha=0.25)
    ax.set_xlabel("mm"); ax.set_ylabel("Z (mm)")
plt.tight_layout()
plt.savefig(os.path.join(C.__file__.rsplit("/", 1)[0], "out", "sections.png"))
