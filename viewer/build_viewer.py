"""Build viewer/index.html: a self-contained three.js viewer of the case, cells, BMS, wiring and fasteners, with
the three build options (60 x 120 BMS, Daly 20 A, Daly 20 A low profile) selectable in one page.
Meshes are tessellated from the CadQuery models in INSTALLED position and embedded (base64). A mesh that is the
same in several options (cells, spacer, Powerpoles, ...) is stored once. The page works opened straight from disk.
Run: python viewer/build_viewer.py"""
import base64, hashlib, json, os, sys
from functools import reduce
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cad"))
import cadquery as cq  # noqa: E402,F401
import case as C  # noqa: E402
import render as R  # noqa: E402
import variant_daly as VD  # noqa: E402
import variant_daly_low as VL  # noqa: E402

MESHES = {}
# items carried in the lid: they turn over with it when the viewer's "flip lid" is on
LID_GROUP = ("lid", "Powerpole clamp", "Powerpoles", "nut plugs", "M3 nuts", "output lead", "C1- -> BMS", "csk screws", "csk clamp")


def pack(shape, tol=0.08):
    vs, fs = shape.val().tessellate(tol, 0.15)
    p = np.array([(v.x, v.y, v.z) for v in vs], dtype="<f4").tobytes()
    i = np.array(fs, dtype="<u4").ravel().tobytes()
    key = hashlib.sha1(p + i).hexdigest()[:16]
    MESHES.setdefault(key, {"p": base64.b64encode(p).decode(), "i": base64.b64encode(i).decode(), "n": len(fs)})
    return key


def item(name, shape, color, explode=0.0, opacity=1.0, kind="part"):
    print("  ", name)
    return {"name": name, "color": color, "explode": explode, "opacity": opacity, "kind": kind,
            "lidgroup": name.startswith(LID_GROUP), "m": pack(shape)}


fuse = lambda shapes: reduce(lambda a, b: a.union(b), shapes)
C_BASE, C_PLATE, C_LID, C_CELL, C_TAB, C_PP = "#b8c2cc", "#e6dcae", "#9fb3c8", "#3a6ea5", "#d08a3a", "#c0392b"


def assembly(Cm, Rm, base, spacer, lid, clamp, bms_items, lid_name="lid", base_name="base", clamp_name="Powerpole clamp"):
    """Everything common to the three options, around the option's own printed parts and BMS items."""
    cells, tabs, _bms, _plug, pp, screws, clamp_screws, wire, nuts, _cn, links, plugs, pads, _bs = Rm.dummies()
    out = [item(base_name, base, C_BASE), item("spacer", spacer, C_PLATE, 25), item(lid_name, lid, C_LID, 80),
           item(clamp_name, clamp, "#e0a040", 60)]
    out += [item(f"cell C{k + 1}", c, C_CELL, 0, 1, "dummy") for k, c in enumerate(cells)]
    out += [item(f"tab {k}", t, C_TAB, 0, 1, "dummy") for k, t in enumerate(tabs)]
    out += bms_items
    out += [item("Powerpoles", pp, C_PP, 80, 1, "dummy"),
            item("12 AWG in the C3/C4 valley channel (clearance dummy)", wire, "#ff5a4a", 0, 1, "dummy"),
            item("nut plugs (glue in, x6)", fuse(plugs), "#7f8fa0", 80), item("M3 nuts (6, side)", fuse(nuts), "#c8c8c8", 80, 1, "dummy"),
            item("12 AWG series links", fuse(links), "#303030", 0, 1, "dummy"),
            item("base-stop foam pads", fuse(pads), "#2b2b2b", 0, 1, "dummy")]
    out += [item("end foam blocks (cut to fit)", Cm.end_foam_volume(1, base, lid, [clamp, pp]).union(
        Cm.end_foam_volume(-1, base, lid, [clamp, pp])), "#3d3d3d", 80, 0.55, "dummy")]
    ld = Rm.leads()
    out += [item("output lead black (zig-zag)", ld[0], "#262626", 80, 1, "dummy"),
            item("output lead red (U-turn, back at lid level)", ld[1], "#ff5a4a", 80, 1, "dummy"),
            item("C1- -> BMS B- lead (zig-zag)", ld[2], "#555555", 80, 1, "dummy")]
    out += [item("csk screws: 6 side + 4 lid (M3x10)", fuse([s.union(h) for s, h in screws]), "#555555", 80, 1, "dummy"),
            item("csk clamp screws (2x M3x10, from below)", fuse([s.union(h) for s, h in clamp_screws]), "#555555", 60, 1, "dummy")]
    return out


def dl(directory, file, qty, note=""):
    return {"dir": directory, "file": file, "qty": qty, "note": note}


# ---------------------------------------------------------------- 1. published design: 60 x 120 BMS
print("60 x 120 BMS")
base, spacer, clamp = C.make_base(), C.make_spacer_installed(), C.make_pp_clamp_installed()
dm = R.dummies()
bms, plug, bscrews = dm[2], dm[3], dm[-1]
main_items = assembly(C, R, base, spacer, C.make_lid_installed(), clamp, [
    item("BMS (dummy)", bms, "#2e8b57", 50, 1, "dummy"), item("balance plug", plug, "#222222", 50, 1, "dummy"),
    item("BMS screws (4x M3x5 button head)", fuse([s.union(h) for s, h in bscrews]), "#555555", 25, 1, "dummy")])
std_dl = [dl("out", "base.stl", 1), dl("out", "spacer.stl", 1), dl("out", "lid.stl", 1), dl("out", "pp_clamp.stl", 1),
          dl("out", "nut_plug_x6.stl", 6)]

# ---------------------------------------------------------------- 2. Daly 20 A, same base: new lid only
print("Daly 20 A")
d_bms, d_tape, d_plug, d_leads, d_ntc = VD.daly_dummies()
main_lid = C.make_lid_installed()
daly_items = assembly(C, R, base, spacer, main_lid, clamp, [
    # the Daly lid = the published lid (shared mesh) + 4 corner caps: shown as two items, printed as one (lid_daly.stl)
    item("lid caps (Daly; printed with the lid as lid_daly.stl)", VD.make_caps(), "#7f9bb5", 80),
    item("Daly BMS 34x59x9 (dummy)", d_bms, "#d0402a", 50, 1, "dummy"), item("foam tape", d_tape, "#2b2b2b", 50, 1, "dummy"),
    item("balance plug", d_plug, "#eeeeee", 50, 1, "dummy"),
    item("Daly P- lead (black)", d_leads[0], "#262626", 50, 1, "dummy"), item("Daly B- lead (blue)", d_leads[1], "#2060d0", 50, 1, "dummy"),
    item("Daly NTC lead", d_ntc, "#777777", 50, 1, "dummy")])
daly_dl = [dl("out", "base.stl", 1), dl("out", "spacer.stl", 1), dl("out_daly", "lid_daly.stl", 1),
           dl("out", "pp_clamp.stl", 1), dl("out", "nut_plug_x6.stl", 6),
           dl("out_daly", "daly_caps_only.stl", 1, "only the 4 caps, to glue into an already-printed lid")]

# ---------------------------------------------------------------- 3. Daly 20 A, low profile
print("Daly 20 A low profile")
V = VL.V
l_base, l_spacer, l_clamp = V.make_base(), V.make_spacer_installed(), V.make_pp_clamp_installed()
l_bms, l_tape, l_plug, l_p, l_b, l_ntc, _th, _bx = VL.daly_dummies()
low_items = assembly(V, VL.R, l_base, l_spacer, VL.make_lid(), l_clamp, [
    item("Daly BMS 59x34x9 (dummy)", l_bms, "#d0402a", 50, 1, "dummy"), item("foam tape", l_tape, "#2b2b2b", 50, 1, "dummy"),
    item("balance plug", l_plug, "#eeeeee", 50, 1, "dummy"),
    item("Daly P- lead (black)", l_p, "#262626", 50, 1, "dummy"), item("Daly B- lead (blue)", l_b, "#2060d0", 50, 1, "dummy"),
    item("Daly NTC lead", l_ntc, "#777777", 50, 1, "dummy")],
    lid_name="lid (Daly low)", base_name="base (low)", clamp_name="Powerpole clamp (C4 relief)")
low_dl = [dl("out_daly_low", "base.stl", 1), dl("out", "spacer.stl", 1), dl("out_daly_low", "lid.stl", 1),
          dl("out_daly_low", "pp_clamp.stl", 1), dl("out_daly_low", "nut_plug_x6.stl", 6)]

size = lambda Cm: f"{Cm.OUT_W:.1f} × {Cm.OUT_L:.1f} × {Cm.H_BASE + Cm.LID_T:.1f} mm"
variants = {
    "60 × 120 BMS": {"title": f"{size(C)}: 60 × 120 BMS centred, wall-to-wall lid beams",
                     "note": "The original build: 30 A two-board BMS, screwed through the spacer.",
                     "items": main_items, "downloads": std_dl, "flip": {"y": C.Y_OFF, "z": C.H_BASE + C.LID_T / 2}},
    "Daly 20 A": {"title": f"{size(C)}: Daly 20 A, same base, new lid",
                  "note": "Daly 4S 20 A (34 × 59 × 9) taped to the same spacer. Only the lid changes: 4 corner caps.",
                  "items": daly_items, "downloads": daly_dl, "flip": {"y": C.Y_OFF, "z": C.H_BASE + C.LID_T / 2}},
    "Daly low": {"title": f"{size(V)}: Daly 20 A, low profile",
                 "note": f"Daly crosswise between two lid beams, the lid presses on it: {C.H_BASE + C.LID_T - V.H_BASE - V.LID_T:.1f} mm "
                         "lower. New base, lid, clamp and nut plugs; same spacer.",
                 "items": low_items, "downloads": low_dl, "flip": {"y": V.Y_OFF, "z": V.H_BASE + V.LID_T / 2}},
}
data = {"meshes": MESHES, "variants": variants}
print(f"{sum(len(v['items']) for v in variants.values())} items, {len(MESHES)} unique meshes")

html = open(os.path.join(HERE, "template.html")).read().replace("/*__DATA__*/null", json.dumps(data))
open(os.path.join(HERE, "index.html"), "w").write(html)
print("wrote", os.path.join(HERE, "index.html"), f"{os.path.getsize(os.path.join(HERE, 'index.html')) / 1e6:.1f} MB")
