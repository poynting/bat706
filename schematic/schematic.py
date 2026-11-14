"""4S LiFePO4 pack + common-port BMS schematic (hand-laid SVG).
Run: python schematic.py  -> schematic.svg (+ schematic.png if cairosvg is installed)"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1150, 820
o = []
add = o.append
RED, BLK, GRY, GRN = "#c0392b", "#111", "#666", "#2e7d32"


def line(pts, w=2, c=BLK, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<polyline points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="none" stroke="{c}" '
        f'stroke-width="{w}" stroke-linejoin="round"{d}/>')


def text(x, y, s, size=14, c=BLK, anchor="start", weight="normal"):
    for i, ln in enumerate(s.split("\n")):
        add(f'<text x="{x}" y="{y + i * (size + 3)}" font-size="{size}" fill="{c}" text-anchor="{anchor}" '
            f'font-weight="{weight}" font-family="DejaVu Sans, Arial">{ln}</text>')


def dot(x, y, r=4.5, open_=False):
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{"white" if open_ else BLK}" stroke="{BLK}" stroke-width="2"/>')


add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
add(f'<rect width="{W}" height="{H}" fill="white"/>')
text(W / 2, 34, "4S LiFePO4 pack — 12.8 V nominal / 14.6 V full — 15 Ah (192 Wh)", 20, anchor="middle", weight="bold")

# ---------------- cell stack -----------------------------------------------------------
CX = 300
node_y = [620, 500, 380, 260, 140]           # B0 (pack −) ... B4 (pack +)
joints = ["C1 −  (FRONT bay)", "C1+ → C2−  (BACK bay)", "C2+ → C3−  (FRONT bay)",
          "C3+ → C4−  (BACK bay)", "C4 +  (FRONT bay)"]
for i in range(4):
    yb, yt = node_y[i], node_y[i + 1]
    yc = (yb + yt) / 2
    line([(CX, yt), (CX, yc - 7)], 4)
    line([(CX - 26, yc - 7), (CX + 26, yc - 7)], 3)          # long plate = +
    line([(CX - 14, yc + 7), (CX + 14, yc + 7)], 6)          # short plate = −
    line([(CX, yc + 7), (CX, yb)], 4)
    text(CX + 34, yc - 12, "+", 14, GRY)
    text(CX + 34, yc + 2, f"C{i + 1}", 16, weight="bold")
    text(CX + 34, yc + 19, "3.2 V 15 Ah", 12, GRY)
for i, y in enumerate(node_y):
    dot(CX, y)
    text(CX - 14, y + 5, joints[i], 13, GRY, anchor="end")
text(CX - 14, node_y[0] + 24, "12 AWG series links", 12, GRY, anchor="end")

# ---------------- BMS ---------------------------------------------------------------------
BX0, BX1, BY0, BY1 = 560, 820, 110, 660
add(f'<rect x="{BX0}" y="{BY0}" width="{BX1 - BX0}" height="{BY1 - BY0}" rx="10" fill="#eef6ee" '
    f'stroke="{GRN}" stroke-width="2.5"/>')
text((BX0 + BX1) / 2, 330, "BMS\n3S–20S, 30 A\ncommon port\n\nconfigure:\nLiFePO4, 4S", 15, GRN,
     anchor="middle", weight="bold")
# balance connector block on left edge
add(f'<rect x="{BX0 - 6}" y="{node_y[4] - 22}" width="34" height="{node_y[0] - node_y[4] + 44}" '
    f'fill="white" stroke="{BLK}" stroke-width="1.5"/>')
text(BX0 + 11, node_y[4] - 30, "balance plug", 11, GRY, anchor="middle")
for i, y in enumerate(node_y):
    line([(CX, y), (BX0 - 6, y)], 2, RED if i else BLK)
    text(BX0 + 11, y + 5, f"B{i}", 12, anchor="middle", weight="bold")
text((CX + BX0) / 2, node_y[4] - 8, "balance harness, 22 AWG", 12, RED, anchor="middle")
volts = ["0 V", "3.2 V", "6.4 V", "9.6 V", "12.8 V"]
for y, v in zip(node_y, volts):
    text(BX0 - 14, y - 6, v, 11, GRY, anchor="end")

# main pads on the bottom edge
BMX, PMX = 620, 760
for x, lbl in ((BMX, "B−"), (PMX, "P− / C−")):
    add(f'<rect x="{x - 14}" y="{BY1 - 4}" width="28" height="10" fill="{BLK}"/>')
    text(x, BY1 - 12, lbl, 13, anchor="middle", weight="bold")

# B− path (thick)
line([(CX, node_y[0]), (CX, 720), (BMX, 720), (BMX, BY1 + 6)], 6)
text((CX + BMX) / 2, 740, "12 AWG  pack B− → BMS B−", 12, anchor="middle")
# P− out
line([(PMX, BY1 + 6), (PMX, 760), (1000, 760)], 6)
dot(1000, 760, 7, open_=True)
text(1014, 755, "P−  black 12 AWG\nPowerpole (front)", 13)

# B+ → fuse → P+
line([(CX, node_y[4]), (CX, 70), (880, 70)], 6)
add(f'<rect x="880" y="58" width="70" height="24" rx="4" fill="white" stroke="{BLK}" stroke-width="2.5"/>')
line([(880, 70), (950, 70)], 1.5)
text(915, 50, "F1  30 A", 13, anchor="middle", weight="bold")
text(915, 100, "in-line ATM mini fuse,\nin the pocket over C4", 11, GRY, anchor="middle")
line([(950, 70), (1000, 70)], 6)
dot(1000, 70, 7, open_=True)
text(1014, 66, "P+  red 12 AWG\nPowerpole (front)", 13)

# NTC
line([(BX1, 560), (900, 560)], 2, dash="6,4")
text(906, 556, "NTC probe (if fitted):\ntape to C2/C3 body", 12, GRY)

# load / charger
add(f'<rect x="1000" y="300" width="130" height="200" rx="8" fill="#f6f6f6" stroke="{GRY}" stroke-dasharray="5,4"/>')
text(1065, 390, "Radio (load)\nand charger\nboth on P+/P−", 13, GRY, anchor="middle")
line([(1000, 77), (1000, 300)], 1.5, GRY, "4,4")
line([(1000, 500), (1000, 753)], 1.5, GRY, "4,4")

text(40, 790, "Charge CC/CV 14.2–14.6 V, ≤ 7.5 A typ. (0.5 C).  BMS switches the negative side: never connect a load "
     "between P+ and B− (that bypasses protection).", 12, GRY)
text(40, 808, "Fit balance plug LAST, after measuring the voltage steps above on the plug pins.  Unused balance "
     "wires on a 3S–20S harness: follow the BMS manual (do not leave bare ends loose).", 12, GRY)
add("</svg>")

svg = "\n".join(o)
open(os.path.join(HERE, "schematic.svg"), "w").write(svg)
try:
    import cairosvg
    cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(HERE, "schematic.png"), output_width=1600)
except ImportError:
    pass
