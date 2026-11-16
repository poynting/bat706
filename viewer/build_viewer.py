"""Build viewer/index.html: a self-contained three.js viewer of the case, cells, BMS, wiring and fasteners.
Meshes are tessellated from the CadQuery models in INSTALLED position and embedded (base64), so the page
works when opened straight from disk. Run: python viewer/build_viewer.py"""
import base64, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cad"))
import cadquery as cq  # noqa: E402
import case as C  # noqa: E402
import render as R  # noqa: E402


def pack(shape, tol=0.08):
    vs, fs = shape.val().tessellate(tol, 0.15)
    p = np.array([(v.x, v.y, v.z) for v in vs], dtype="<f4")
    i = np.array(fs, dtype="<u4").ravel()
    return {"p": base64.b64encode(p.tobytes()).decode(), "i": base64.b64encode(i.tobytes()).decode(), "n": len(fs)}


def item(name, shape, color, explode=0.0, opacity=1.0, kind="part"):
    print("  ", name)
    return {"name": name, "color": color, "explode": explode, "opacity": opacity, "kind": kind, **pack(shape)}


C_BASE, C_PLATE, C_LID, C_CELL, C_TAB, C_BMS, C_PP = "#b8c2cc", "#e6dcae", "#9fb3c8", "#3a6ea5", "#d08a3a", "#2e8b57", "#c0392b"

c_cells, c_tabs, c_bms, c_plug, c_pp, c_screws, c_clamp_screws, c_wire, c_nuts, c_cnuts, c_links, c_plugs, c_pads, c_bscrews = R.dummies()
C_items = [item("base", C.make_base(), C_BASE), item("spacer", C.make_spacer_installed(), C_PLATE, 25),
           item("lid", C.make_lid_installed(), C_LID, 80), item("Powerpole clamp", C.make_pp_clamp_installed(), "#e0a040", 60)]
C_items += [item(f"cell C{k + 1}", c, C_CELL, 0, 1, "dummy") for k, c in enumerate(c_cells)]
C_items += [item(f"tab {k}", t, C_TAB, 0, 1, "dummy") for k, t in enumerate(c_tabs)]
C_items += [item("BMS (dummy)", c_bms, C_BMS, 50, 1, "dummy"), item("balance plug", c_plug, "#222222", 50, 1, "dummy"),
            item("Powerpoles", c_pp, C_PP, 80, 1, "dummy"), item("12 AWG in the C3/C4 valley channel (clearance dummy)", c_wire, "#ff5a4a", 0, 1, "dummy")]
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
_cb, _cl, _cc = C.make_base(), C.make_lid_installed(), C.make_pp_clamp_installed()
C_items += [item("end foam blocks (cut to fit)", C.end_foam_volume(1, _cb, _cl, [_cc, c_pp]).union(C.end_foam_volume(-1, _cb, _cl, [_cc, c_pp])),
                 "#3d3d3d", 80, 0.55, "dummy")]
_ld = R.leads()
C_items += [item("output lead black (zig-zag)", _ld[0], "#262626", 80, 1, "dummy"),
            item("output lead red (U-turn, back at lid level)", _ld[1], "#ff5a4a", 80, 1, "dummy"),
            item("C1- -> BMS B- lead (zig-zag)", _ld[2], "#555555", 80, 1, "dummy")]
C_items += [item("csk screws: 6 side + 4 lid (M3x10)", side, "#555555", 80, 1, "dummy"), item("csk clamp screws (2x M3x10, from below)", cl, "#555555", 60, 1, "dummy")]

data = {"bat706": {"title": f"{C.OUT_W:.1f} × {C.OUT_L:.1f} × {C.H_BASE + C.LID_T:.1f} mm: BMS centred, wall-to-wall lid beams", "items": C_items}}

html = open(os.path.join(HERE, "template.html")).read().replace("/*__DATA__*/null", json.dumps(data))
open(os.path.join(HERE, "index.html"), "w").write(html)
print("wrote", os.path.join(HERE, "index.html"), f"{os.path.getsize(os.path.join(HERE, 'index.html')) / 1e6:.1f} MB")
