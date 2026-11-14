"""Render preview PNGs of the parts and an exploded assembly with dummy cells + BMS."""
import os
import numpy as np
import cadquery as cq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import case as C

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def tris(shape, tol=0.4, max_edge=5.0):
    """Tessellate, then split big faces into small triangles so matplotlib's per-polygon
    depth sort (painter's algorithm) doesn't draw far faces over near ones."""
    import trimesh
    vs, fs = shape.val().tessellate(tol, 0.5)
    v = np.array([(p.x, p.y, p.z) for p in vs])
    v, f = trimesh.remesh.subdivide_to_size(v, np.array(fs), max_edge=max_edge)
    return v[f]


_pending = {}


def draw(ax, shape, color, alpha=1.0, tol=0.4):
    """Queue a shape; flush(ax) adds everything as ONE collection so triangles from different
    parts are depth-sorted together (separate collections are sorted only as whole blocks)."""
    t = tris(shape, tol)
    n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    n /= np.linalg.norm(n, axis=1)[:, None] + 1e-9
    shade = 0.45 + 0.55 * np.clip(n @ np.array([0.3, -0.5, 0.8]), 0, 1)
    cols = np.clip(np.array(matplotlib.colors.to_rgb(color))[None, :] * shade[:, None], 0, 1)
    _pending.setdefault(id(ax), []).append((t, np.c_[cols, np.full(len(cols), alpha)]))


def flush(ax):
    items = _pending.pop(id(ax), [])
    ax.add_collection3d(Poly3DCollection(np.concatenate([t for t, _ in items]),
                                         facecolors=np.concatenate([c for _, c in items]), linewidths=0))


def finish(ax, lim, elev=28, azim=-55):
    flush(ax)
    (x0, x1), (y0, y1), (z0, z1) = lim
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_zlim(z0, z1)
    ax.set_box_aspect((x1 - x0, y1 - y0, z1 - z0))
    ax.view_init(elev, azim); ax.set_axis_off()


def dummies():
    cells = []
    for i, x in enumerate(C.cell_x):
        body = cq.Workplane("XZ").circle(C.CELL_D / 2).extrude(C.CELL_L / 2, both=True) \
            .translate((x, 0, C.Z_CELL_CTR))
        cells.append(body)
        for sy in (-1, 1):
            tab = cq.Workplane("XY").box(C.TAB_W, C.TAB_T, 8).translate(
                (x, sy * (C.CELL_L / 2 + C.TAB_T / 2), C.Z_CELL_CTR))
            cells.append(("tab", tab))
    bms = cq.Workplane("XY").box(C.BMS_W, C.BMS_L, C.BMS_T, centered=(False, False, False)).translate(
        (C.BMS_X0, C.TRAY_L / 2 - C.BMS_FROM_FRONT - C.BMS_L, C.Z_TRAY + C.TRAY_T))
    plug = cq.Workplane("XY").box(16, 8, 6).translate(
        (C.BMS_X0 + C.BMS_W / 2, C.TRAY_L / 2 - C.BMS_FROM_FRONT - C.BMS_L - 4, C.Z_TRAY + C.TRAY_T + 4))
    pp_w = C.PP_N * C.PP_SQ
    pp = cq.Workplane("XY").box(pp_w, C.PP_L, C.PP_SQ, centered=(True, False, False)).translate(
        (C.PP_X, C.FRONT_IN + C.WALL + C.PP_PROUD - C.PP_L, C.Z_TRAY + C.TRAY_T))
    return cells, bms, plug, pp


if __name__ == "__main__":
    base, tray, lid = C.make_base(), C.make_tray(), C.make_lid()
    cells, bms, plug, pp = dummies()
    lim = ((-80, 80), (-100, 100), (0, 150))

    fig = plt.figure(figsize=(14, 7), dpi=110)
    # exploded assembly
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    draw(ax, base, "#c9cdd2")
    for c in cells:
        if isinstance(c, tuple):
            draw(ax, c[1], "#d08a3a")
        else:
            draw(ax, c, "#3a6ea5")
    draw(ax, tray.translate((0, 0, C.Z_TRAY + 25)), "#e8e2c8")
    draw(ax, bms.translate((0, 0, 25)), "#2e8b57")
    draw(ax, plug.translate((0, 0, 25)), "#222222")
    draw(ax, pp.translate((0, 0, 25)), "#c0392b")
    lid_flip = lid.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, C.H_BASE + 75))
    draw(ax, lid_flip, "#c9cdd2", 0.8)
    finish(ax, lim)
    ax.set_title("Exploded assembly (Powerpoles exit the front wall)")

    # base with the cell string installed, tray off
    ax = fig.add_subplot(1, 2, 2, projection="3d")
    draw(ax, base, "#c9cdd2")
    for c in cells:
        draw(ax, c[1] if isinstance(c, tuple) else c, "#d08a3a" if isinstance(c, tuple) else "#3a6ea5")
    finish(ax, ((-80, 80), (-100, 100), (0, 60)), elev=50, azim=-120)
    ax.set_title("Cells in base (tray off): bays, clamp posts, bosses")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "preview_assembly.png"))

    fig = plt.figure(figsize=(15, 5), dpi=110)
    for i, (name, part, lim2, el, az) in enumerate([
            ("base (print as shown)", base, ((-80, 80), (-100, 100), (0, 60)), 40, -60),
            ("tray (print as shown)", tray, ((-75, 75), (-75, 75), (0, 10)), 50, -60),
            ("lid (print as shown, outer face on bed)", lid, ((-80, 80), (-100, 100), (0, 20)), 45, -60)]):
        ax = fig.add_subplot(1, 3, i + 1, projection="3d")
        draw(ax, part, "#9db4c8")
        finish(ax, lim2, el, az)
        ax.set_title(name)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "preview_parts.png"))

    # interference check: cells vs base, BMS vs lid
    asm_lid = lid.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, C.H_BASE + C.LID_T))
    checks = {
        "cells vs base": sum(base.intersect(c if not isinstance(c, tuple) else c[1]).val().Volume()
                             for c in cells),
        "cells vs tray": sum(tray.translate((0, 0, C.Z_TRAY)).intersect(c if not isinstance(c, tuple) else c[1])
                             .val().Volume() for c in cells),
        "tray vs base": tray.translate((0, 0, C.Z_TRAY)).intersect(base).val().Volume(),
        "BMS vs tray": bms.intersect(tray.translate((0, 0, C.Z_TRAY))).val().Volume(),
        "BMS vs lid": bms.intersect(asm_lid).val().Volume(),
        "PP vs base": pp.intersect(base).val().Volume(),
        "PP vs tray": pp.intersect(tray.translate((0, 0, C.Z_TRAY))).val().Volume(),
        "PP vs lid": pp.intersect(asm_lid).val().Volume(),
        "PP vs BMS": pp.intersect(bms).val().Volume(),
        "lid vs base": asm_lid.intersect(base).val().Volume(),
        "lid vs tray": asm_lid.intersect(tray.translate((0, 0, C.Z_TRAY))).val().Volume(),
    }
    for k, v in checks.items():
        print(f"interference {k:14s}: {v:8.3f} mm^3")
