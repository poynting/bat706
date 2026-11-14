"""Build viewer/index.html: a self-contained three.js viewer for variants A and B.
Meshes are tessellated from the CadQuery models in INSTALLED position and embedded (base64), so the page
works when opened straight from disk. Run: python viewer/build_viewer.py"""
import base64, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cad"))
import cadquery as cq  # noqa: E402
import case as A  # noqa: E402
import case_b as B  # noqa: E402
import render as RA  # noqa: E402
import render_b as RB  # noqa: E402
import case_c as CC  # noqa: E402
import render_c as RC  # noqa: E402


def pack(shape, tol=0.08):
    vs, fs = shape.val().tessellate(tol, 0.15)
    p = np.array([(v.x, v.y, v.z) for v in vs], dtype="<f4")
    i = np.array(fs, dtype="<u4").ravel()
    return {"p": base64.b64encode(p.tobytes()).decode(), "i": base64.b64encode(i.tobytes()).decode(), "n": len(fs)}


def item(name, shape, color, explode=0.0, opacity=1.0, kind="part"):
    print("  ", name)
    return {"name": name, "color": color, "explode": explode, "opacity": opacity, "kind": kind, **pack(shape)}


C_BASE, C_PLATE, C_LID, C_CELL, C_TAB, C_BMS, C_PP = "#b8c2cc", "#e6dcae", "#9fb3c8", "#3a6ea5", "#d08a3a", "#2e8b57", "#c0392b"

print("variant A")
a_cells, a_bms, a_plug, a_pp = RA.dummies()
a_lid = A.make_lid().rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, A.H_BASE + A.LID_T))
A_items = [item("base", A.make_base(), C_BASE), item("tray (cell clamp)", A.make_tray().translate((0, 0, A.Z_TRAY)), C_PLATE, 30),
           item("lid", a_lid, C_LID, 80)]
for k, c in enumerate(a_cells):
    if isinstance(c, tuple):
        A_items.append(item(f"tab {k}", c[1], C_TAB, 0, 1, "dummy"))
    else:
        A_items.append(item(f"cell C{len([x for x in a_cells[:k] if not isinstance(x, tuple)]) + 1}", c, C_CELL, 0, 1, "dummy"))
A_items += [item("BMS (dummy)", a_bms, C_BMS, 50, 1, "dummy"), item("balance plug", a_plug, "#222222", 50, 1, "dummy"),
            item("Powerpoles", a_pp, C_PP, 50, 1, "dummy")]

print("variant B")
b_cells, b_tabs, b_bms, b_plug, b_pp = RB.dummies_b()
B_items = [item("base", B.make_base(), C_BASE), item("spacer", B.make_spacer_installed(), C_PLATE, 25),
           item("lid", B.make_lid_installed(), C_LID, 80)]
B_items += [item(f"cell C{k + 1}", c, C_CELL, 0, 1, "dummy") for k, c in enumerate(b_cells)]
B_items += [item(f"tab {k}", t, C_TAB, 0, 1, "dummy") for k, t in enumerate(b_tabs)]
B_items += [item("BMS (dummy)", b_bms, C_BMS, 50, 1, "dummy"), item("balance plug", b_plug, "#222222", 50, 1, "dummy"),
            item("Powerpoles", b_pp, C_PP, 80, 1, "dummy")]

print("variant C")
c_cells, c_tabs, c_bms, c_plug, c_pp, c_screws, c_clamp_screws, c_wire, c_nuts, c_cnuts, c_links, c_plugs, c_pads, c_bscrews = RC.dummies_c()
C_items = [item("base", CC.make_base(), C_BASE), item("spacer", CC.make_spacer_installed(), C_PLATE, 25),
           item("lid", CC.make_lid_installed(), C_LID, 80), item("Powerpole clamp", CC.make_pp_clamp_installed(), "#e0a040", 60)]
C_items += [item(f"cell C{k + 1}", c, C_CELL, 0, 1, "dummy") for k, c in enumerate(c_cells)]
C_items += [item(f"tab {k}", t, C_TAB, 0, 1, "dummy") for k, t in enumerate(c_tabs)]
C_items += [item("BMS (dummy)", c_bms, C_BMS, 50, 1, "dummy"), item("balance plug", c_plug, "#222222", 50, 1, "dummy"),
            item("Powerpoles", c_pp, C_PP, 80, 1, "dummy"), item("B+ wire (12 AWG)", c_wire, "#ff5a4a", 0, 1, "dummy")]
side = c_screws[0][0]
for s_, h_ in c_screws:
    side = side.union(s_).union(h_)
cl = c_clamp_screws[0][0]
for s_, h_ in c_clamp_screws:
    cl = cl.union(s_).union(h_)
def fuse(shapes):
    u = shapes[0]
    for x in shapes[1:]:
        u = u.union(x)
    return u
C_items += [item("nut plugs (glue in, x6)", fuse(c_plugs), "#7f8fa0", 80), item("M3 nuts (6, side)", fuse(c_nuts), "#c8c8c8", 80, 1, "dummy"),
            item("12 AWG series links", fuse(c_links), "#303030", 0, 1, "dummy"),
            item("base-stop foam pads", fuse(c_pads), "#2b2b2b", 0, 1, "dummy"),
            item("BMS screws (4x M3x5 button head)", fuse([s.union(h) for s, h in c_bscrews]), "#555555", 25, 1, "dummy")]
_cb, _cl, _cc = CC.make_base(), CC.make_lid_installed(), CC.make_pp_clamp_installed()
C_items += [item("end foam blocks (cut to fit)", CC.end_foam_volume(1, _cb, _cl, [_cc, c_pp]).union(CC.end_foam_volume(-1, _cb, _cl, [_cc, c_pp])),
                 "#3d3d3d", 80, 0.55, "dummy")]
_ld = RC.leads_c()
C_items += [item("output lead black (zig-zag)", _ld[0], "#262626", 80, 1, "dummy"),
            item("output lead red (U-turn to valley)", _ld[1], "#ff5a4a", 80, 1, "dummy"),
            item("C1- -> BMS B- lead (zig-zag)", _ld[2], "#555555", 80, 1, "dummy")]
C_items += [item("csk screws: 6 side + 4 lid (M3x10)", side, "#555555", 80, 1, "dummy"), item("csk clamp screws (2x M3x10, from below)", cl, "#555555", 60, 1, "dummy")]

data = {"A": {"title": f"A: tray clamp, {A.OUT_W:.1f} × {A.OUT_L:.1f} × {A.H_BASE + A.LID_T:.1f} mm", "items": A_items},
        "B": {"title": f"B: lid carries BMS, {A.OUT_W:.1f} × {A.OUT_L:.1f} × {B.H_BASE + A.LID_T:.1f} mm", "items": B_items},
        "C": {"title": f"C: BMS centred, wall-to-wall beams, {A.OUT_W:.1f} × {CC.OUT_L:.1f} × {CC.H_BASE + A.LID_T:.1f} mm", "items": C_items}}

html = open(os.path.join(HERE, "template.html")).read().replace("/*__DATA__*/null", json.dumps(data))
open(os.path.join(HERE, "index.html"), "w").write(html)
print("wrote", os.path.join(HERE, "index.html"), f"{os.path.getsize(os.path.join(HERE, 'index.html')) / 1e6:.1f} MB")
