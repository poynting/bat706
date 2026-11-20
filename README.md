# bat706: 4S LiFePO4 battery pack for the Icom IC-706MKII

A portable 13.x V supply for an Icom IC-706MKII:
- **Cells:** 4 × 3.2 V 15 Ah LiFePO4 laser-welded cylindrical cells in 4S (Ø33.5 × 136.25 mm, with 20 × 8 × 2 mm copper solder tabs).
- **BMS:** a 3S–20S 30 A balancing BMS (60 × 120 × 10 mm), or a Daly 4S 20 A (34 × 59 × 9 mm): see [Build options](#build-options).
- **Output:** an Anderson Powerpole pair.
- **Rating:** **12.8 V nominal, 14.6 V full, 15 Ah, ~192 Wh.**

The case is **143.8 W × 157.9 L × 54.5 H mm** (50.2 mm high for the low-profile Daly option), inside the radio's own 167 × 200 × 58 mm footprint. It's 3D-printed without supports.

![Exploded assembly](cad/out/preview_assembly.png)

## Build options

Three ways to build it, all with the same cells, footprint, Powerpoles and lead routing through the lid. Pick one in the [3D viewer](https://poynting.github.io/bat706/); its Downloads list switches to that option's STLs.

| | **60 × 120 BMS** (the main design) | **Daly 20 A** | **Daly 20 A, low profile** |
|---|---|---|---|
| BMS | 3S–20S 30 A, 60 × 120 × 10, two boards | Daly 4S 12 V 20 A LiFePO4, 34 × 59 × 9, potted, flying leads | same Daly |
| Size | 143.8 × 157.9 × **54.5** mm | 143.8 × 157.9 × **54.5** mm | 143.8 × 157.9 × **50.2** mm |
| BMS mounting | 4 × M3×5 through the spacer | 1 mm double-sided foam tape; 4 lid corner caps | 1 mm double-sided foam tape; the lid presses on it |
| Print | `cad/out/`: base, spacer, lid, pp_clamp, nut_plug ×6 | as the main design, but `cad/out_daly/lid_daly.stl` for the lid | `cad/out_daly_low/`: base, lid, pp_clamp, nut_plug ×6; spacer from `cad/out/` |
| Script | `cad/case.py` | `cad/variant_daly.py` | `cad/variant_daly_low.py` |

The rest of this README describes the main design; the two Daly sections below cover what differs. Parts lists for each option are in [BOM.md](BOM.md#build-options).

### Daly 20 A (same base, new lid)

![Daly layout](cad/out_daly/layout_daly.png)

- **Reuses the printed base, spacer, clamp and nut plugs.** Only the lid changes: the published lid plus 4 corner caps that press the board onto its tape (0.3 mm) and hold it in X and Y. Already printed the main lid? Print `cad/out_daly/daly_caps_only.stl` and glue the caps in instead (positions in `layout_daly.png`).
- **Board:** lengthwise over C2/C3, label up, leads toward the **back**, balance socket on the **front** edge. The old BMS screw pockets in the spacer stay empty.
- **Leads:** P− (black) runs over C4 to the black output lead, B− (blue) over C1 to the C1− lead, both behind the middle beam (32 mm further back than in the main design, so leave those leads longer). Trim the Daly's 130 mm leads to length. Tape the NTC to a cell.
- **Current:** the 20 A model is the one to use. The 15 A model is the same box, but the IC-706MKII draws about 20 A at 100 W TX.
- **Checks:** `python cad/variant_daly.py`: all collision checks zero except the intended cap preload.

### Daly 20 A, low profile (4.3 mm lower)

![Daly low-profile layout](cad/out_daly_low/layout.png)
![Daly low-profile sections](cad/out_daly_low/cross_section.png)

- **Board crosswise** between the middle and back lid beams, so no lid ridge passes over it: the lid's underside presses directly on the board (0.3 mm into the tape) and the rim drops from 52.5 to 48.2 mm. Label up, leads toward **C4**, balance socket toward **C1**. The middle beam's ridge stops the board's front edge; short lid walls at both ends hold it in X.
- **Leads:** P− (black) goes straight out over C4 to the black output lead, at the same joint as the main design. B− (blue) leaves the same end, loops back over C4 (about 7 mm bend radius) and runs to C1 in the lane between the board and the back beam (1.6 mm either side), then to the C1− lead.
- **Reprint:** base, lid, Powerpole clamp (its underside is hollowed to clear C4; full thickness at the screws) and the nut plugs (now 3.2 mm tall). The spacer is the main design's, unchanged.
- **Tighter than the main design:** side screws pass 0.2 mm under the lid's lip, the clamp is 0.5 mm off C4, and the end foam blocks are about 23 mm tall instead of 27.
- **Checks:** `python cad/variant_daly_low.py` re-runs the main design's full check suite at the new height (screws, nuts, cells, clamp, leads) plus the Daly's own: 72 checks, all zero. Fastener engagement is the same as the main design.

## 3D viewer

**<https://poynting.github.io/bat706/>**

It shows the printed parts with the dummy cells, BMS, Powerpoles, leads, screws, nuts and foam, so you can check fit as well as look at the parts. The viewer offers:
- **Build option:** switch between the three [build options](#build-options); the link remembers the choice (`#Daly%20low`).
- **Parts:** toggle each part, solo it, or show only the printed parts.
- **Explode:** a slider that spreads the assembly apart.
- **Section cut:** slice along X, Y or Z.
- **Views:** iso, top, front, side and under.
- **X-ray lid:** see inside with the lid on.
- **Flip lid:** turn the lid (with the Powerpoles, clamp, leads and nuts it carries) underside-up, as it lies on the bench.
- **Free rotate:** tumble freely in any direction (trackball) instead of keeping Z up.
- **Live dimensions:** the size of whatever is visible.
- **Downloads:** every printable STL for the selected option, and the [printable BOM](https://poynting.github.io/bat706/bom.html).

The same page is in the repo as [`viewer/index.html`](viewer/index.html). It's self-contained, but it needs internet once to load three.js. GitHub Actions (`.github/workflows/pages.yml`) republishes it on every push to `main`, together with the STLs from `cad/out/`, `cad/out_daly/` and `cad/out_daly_low/` and a page rendered from `BOM.md`. CI only copies the viewer and STLs, so rebuild them locally before you push (see [Regenerating](#regenerating)).

## Schematic

![Schematic](schematic/schematic.png)

- **Connections:** charger and radio both connect to the Powerpoles (common-port BMS).
- **Switching:** the BMS switches the negative side, so never connect a load between P+ and B−.
- **Balance plug:** fit it last, after checking the voltage steps on its pins: 0, 3.2, 6.4, 9.6, 12.8 V.

## Layout

![Top-view layout](schematic/layout.png)

The cells alternate direction. Seen from the **front** (Powerpole end), the ends are C1 −, C2 +, C3 −, C4 +. Pack B− is C1− and pack B+ is C4+, both at the front. The series links are:
- **Back:** C1+→C2− and C3+→C4−.
- **Front:** C2+→C3−.

## Design

![Printable parts](cad/out/preview_parts.png)

![Cross-section through the middle beam](cad/out/cross_section.png)

### Cells and BMS
- **Base:** a tub with three cradle saddles under the cells.
- **Spacer:** a printed block shaped to the tops of C2 and C3. It carries the BMS, centred across the case.
- **BMS position:** the BMS sits 3 mm from the spacer's **back** end. Its balance connector is on the front edge, so this leaves room at the Powerpole end for the plug and leads.
- **BMS mounting:**
  - **Boards:** the BMS is two boards on corner standoffs, heat-sink board toward the lid.
  - **Screws:** the lower board's own corner screws come out. 4 × M3×5 ISO 7380 button heads replace them, going up through counterbored pockets in the spacer and the lower board into the standoff threads.
  - **Pockets:** each is deep enough for the head to clear the cell's curved top.
  - **Location:** the screws locate the BMS, so the lid needs no fences around it.
- **Cell clamping:**
  - **Seats:** every seat sits 0.5 mm off the cell, with 1 mm foam tape in the gap. That covers the base saddles, the spacer and the lid ribs.
  - **Lid pressure:** the lid's 4 corner pads sit over the BMS standoffs and press the BMS onto the spacer, and the spacer onto C2/C3. The lid ribs press C1 and C4.
- **Cell ends:**
  - **Bottom third:** a rigid 2.4 mm base end stop, braced by 2 mm floor spars to the end wall, with a 2–3 mm closed-cell foam pad on its face (1.5 mm gap).
  - **Middle third:** fully open for the tabs and the 12 AWG links.
  - **Top third:** a closed-cell foam block you cut to fit, pressed in by the lid.
  - **Bays:** 5 mm at the front and 4 mm at the back. That's enough because the string is wired on the bench before it goes in.

### Lid
- **Beams:** three wall-to-wall beams at the saddle stations. Each beam is three pieces joined into one:
  - a rib clamping C1;
  - a 3 mm ridge crossing over the BMS;
  - a rib clamping C4.

  The ribs also act as the BMS side fences. The ridges are inside the lid rather than on top, because the lid prints outer face down. Each beam end takes a side screw.
- **Valley channels:** each rib has a slot over the C1/C2 and C3/C4 valleys. These are free for balance leads.
- **Vents:** slots over the BMS.

### Powerpoles
- **Placement:** a red/black pair in the front-right corner, hanging in a lid cradle. Red is inboard ("red right, tongue top" seen from the mating face) and black is toward the wall.
- **Recessed:** the mating face sits 0.5 mm inside the front wall's outer face, so nothing sticks out to be knocked off. The mating plug goes into the wall notch, which has a 0.6 mm 45° lead-in.
- **Backstop:** a solid backstop fills the space from the housings to the front beam and takes the push when you plug in. Its underside stays 0.5 mm clear of the clamp bar, so the bar always clamps the housings.
- **Clamp bar:** a printed bar under the housings screws up into the lid, with the screws hidden.

### Wiring through the lid

![Lid underside lead routing](cad/out/lid_routing.png)

This is the lid as it lies upside down on the bench. There's a printable PDF to mark up: `cad/out/lid_routing.pdf`.

- **Black output (outboard, over C4):**
  - **Out of the lid:** straight back from its Powerpole through a 4.6 mm teardrop hole in the backstop and front beam.
  - **Zig-zag:** a snap-in zig-zag channel takes it to a hole in the middle beam, then it goes on to BMS P−.
- **Red output (inboard):**
  - **Out of the lid:** straight back through its own hole in the backstop and front beam.
  - **U-turn:** it makes a free U-turn (about 8 mm radius) in the pocket behind the front beam.
  - **Return hole:** it comes back forward at lid level through a second hole in the front beam.
  - **Between the post and the pad:** it runs between the clamp-bar post and the BMS's front corner pad, with 0.38 mm each side.
  - **On the BMS edge:** for about 10 mm it lies on the BMS's top edge, in the 4 mm gap under the lid. It touches with no clearance.
  - **To C4+:** past the BMS's front edge it goes down into the front bay, then through an inline single Powerpole and a 30 A ATM mini fuse to C4+.
- **C1− to BMS B− (over C1):** the black run mirrored, with the second inline single Powerpole.
- **Zig-zag channel:**
  - **Size:** 4.4 mm wide and 4.6 mm deep, with a 3.4 mm snap lip and a 45° lead-in. A 4 mm jacket presses past the lip and sits fully inside.
  - **Shape:** one bump at 12 mm centreline radius, so the lead bends at no less than 8 mm (2× OD). It wraps 160° and comes out on the line it went in.
  - **Direction:** it swings toward the wall, leaving the inboard side of the pocket free for the red U-turn.
- **Inline Powerpoles:** the lid unplugs from the pack, so it lifts off without unsoldering.

### Parting line
The base rim is square, so base and lid meet flush with no groove to trap dirt. The vertical corners have R6 fillets. Edges that face the bed are 45° chamfers.

![Flush parting line](cad/out/seam.png)

### Fasteners: M3, countersunk (ISO 10642) wherever a head shows

| Where | Qty | Screw | Captured by |
|---|---|---|---|
| Long side walls into the lid beam ends | 6 | M3×10 | M3 nut dropped into a slot from the lid top, closed with a glue-in printed plug |
| Lid corners | 4 | M3×10 | heat-set insert in the base corner boss (the lid pad sits on the lowered boss) |
| Powerpole clamp bar, from below | 2 | M3×10 | heat-set insert in a lid boss (hidden) |
| BMS to spacer, from the cell side | 4 | M3×5 **button head** (ISO 7380) | the BMS's own heat-sink-side standoffs (3.5 mm thread) |

Each side-screw countersink is backed by a 1.2 mm pad inside the wall. Each lid beam end has a groove, open at the bottom, that clears that pad, so the lid drops straight in.

![Fastener sections](cad/out/fastener_sections.png)

![Cell-end detail](cad/out/end_detail.png)

### Checks
`python cad/render.py` runs 61 collision checks, all zero:
- the printed parts against each other;
- the dummy cells, tabs, BMS, balance plug and Powerpoles;
- the 4 mm leads in both zig-zags and the red's U-turn and return run;
- a 12 AWG wire through the C3/C4 valley channel, and the series links;
- every screw shank and head, the nuts, the plugs and the foam pads, including the BMS screw heads against the cells.

It also reports:
- the red lead's contact with the BMS top edge, on its own line;
- how much thread each screw has in its nut or insert;
- the size of each end foam block.

## Print

- **Material: PETG or ASA, not PLA.** The BMS FETs and 30 A wiring warm the box, and PLA creeps at about 55 °C.
- **Nozzle and layers:** 0.4 mm nozzle at 0.2 mm layers, or 0.6 mm at 0.3 mm. Walls and plates are sized in line-width multiples for both: 2.4 mm walls and stop plates, 2 mm spars and floor.
- **Orientation:** every STL in `cad/out/` is exported in print orientation, and none needs supports.
  - `base`: open side up.
  - `spacer`: flat face down.
  - `lid`: outer face down. The rib holes are teardrops and the zig-zag lips are 45° slopes, so both print without support.
  - `pp_clamp`: countersinks up.
  - `nut_plug_x6`: print six, on their side.
- **Not done yet:** fillets on the internal joints (rib-to-lid, rib-to-ridge, spars, bosses), to spread the stress at the current 90° corners.

## BOM

The full bill of materials, as a printable checklist, is in **[BOM.md](BOM.md)** ([printable web page](https://poynting.github.io/bat706/bom.html)): printed parts, fasteners (also listed per part), foam, electrical parts and tools.

In short: 12 × M3×10 countersunk (ISO 10642), 4 × M3×5 button head (ISO 7380), 6 × M3 nuts (ISO 4032), 6 × M3 heat-set inserts (4.2 mm hole), 3 Powerpole pairs, a 30 A ATM fuse and holder, 12 AWG and 22 AWG silicone wire, and closed-cell foam.

## Build order

1. **Check the cells.** They should be within about 0.05 V of each other; top-balance them in parallel if not.
2. **Wire the string on the bench, not in the case.**
   - **Layout:** lay the cells out as in the layout drawing above.
   - **Series links:** solder them flat on the tabs, about 5 s per joint with plenty of flux. Check the voltage after each one, then Kapton every joint.
   - **Main leads:** black from C1− and red from C4+, each ending in one half of an inline single Powerpole.
   - **Balance leads:** B0 = C1−, B1 = C1+/C2−, B2 = C2+/C3−, B3 = C3+/C4−, B4 = C4+.
3. **Prepare the printed parts:**
   - **Inserts:** melt the 4 heat-set inserts into the base corner bosses and the 2 into the lid's Powerpole bosses.
   - **Foam:** stick 1 mm foam tape on the base saddles, the spacer underside and the lid rib seats, and the 2–3 mm pads on the 8 base-stop faces.
4. **Mount the BMS on the spacer:** remove the lower board's 4 corner screws and fit 4 × M3×5 button heads up through the spacer pockets into the standoffs.
5. **Lower the string into the base,** front (Powerpole end) at the front, and set the spacer and BMS on C2/C3.
6. **Lid sub-assembly,** with the lid upside down:
   - **Thread the leads before crimping:** feed the 2 output leads through the backstop and front-beam holes, then crimp the contacts. The contacts won't pass the 4.6 mm holes.
   - **Seat the Powerpoles** in the cradle against the backstop.
   - **Black:** press it into the zig-zag until it snaps past the lip, then out through the middle-beam hole.
   - **Red:** U-turn it and feed it forward through its return hole, between the clamp-bar post and the BMS corner pad.
   - **Cell side:** do the same as black on the C1 side, with the lead from BMS B−.
   - **Clamp bar:** screw it on from below (2 × M3×10).
7. **Connect everything:**
   - BMS P− to the black output lead.
   - Red output lead through the fuse to its inline Powerpole, mated to the C4+ lead.
   - BMS B− lead (C1 side) to its inline Powerpole, mated to the C1− lead.
   - Check every balance-plug pin voltage, then plug the balance lead in **last**. On a smart BMS, set LiFePO4 / 4S.
8. **Fit the end foam blocks** above the wiring, close the lid, and fit the 4 corner screws.
9. **Fit the side screws:** drop the 6 nuts into the lid slots, fit the 6 side screws, then glue the plugs in flush.
10. **Fit the fuse** and check the voltage and polarity at the Powerpoles.

## Regenerating

Requires Python 3.10+. Set up a venv once (it's gitignored):

```
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python cad/case.py              # STL/STEP -> cad/out/
python cad/render.py            # collision checks, previews, cross-section
python cad/details.py           # fastener / cell-end / seam sections
python cad/lid_drawing.py       # lid underside routing drawing (png + pdf, for markup)
python schematic/schematic.py   # schematic.svg/.png
python schematic/layout.py      # layout.png
python cad/variant_daly.py      # Daly option: checks, cad/out_daly/
python cad/variant_daly_low.py  # Daly low-profile option: full checks at its height, cad/out_daly_low/
python viewer/build_viewer.py   # viewer/index.html, all three options (published to GitHub Pages on push)
python viewer/build_bom.py      # viewer/bom.html from BOM.md (CI also renders it on push)
```

All dimensions live in `cad/case.py`. The variants build on it: `case.load_variant(name, H_BASE=..., ...)` re-runs it as a separate copy with a few values changed, so every derived dimension follows. Coordinates: X across the cells (C1 at −X), Y along them (+Y = front, the Powerpole end), Z up from the base's bed face.

## Notes

- **Charging:** CC/CV at 14.2–14.6 V, ideally ≤ 7.5 A (0.5 C).
- **Load:** the IC-706MKII draws about 20 A at 100 W TX. The 12 AWG wiring, 30 A fuse and 30 A BMS all cover that.
- **Cell cans:** if a cell's can is tied to a terminal (measure can-to-tab), keep its shrink-wrap intact. The cells sit 1 mm apart.
