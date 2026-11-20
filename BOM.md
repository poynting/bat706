# bat706 bill of materials

The checklist for building one pack. Tick the **Have** box as you collect each item. Dimensions come from `cad/case.py`; the design is described in the [README](README.md).

## 1. Printed parts

Print in PETG or ASA, not PLA. Every STL in [`cad/out/`](cad/out/) is already in print orientation and needs no supports.

| Have | Part | File | Qty | Print orientation |
|:---:|---|---|:---:|---|
| ☐ | Base (tub) | `base.stl` | 1 | open side up |
| ☐ | BMS spacer | `spacer.stl` | 1 | flat face down |
| ☐ | Lid | `lid.stl` | 1 | outer face down |
| ☐ | Powerpole clamp bar | `pp_clamp.stl` | 1 | countersinks up |
| ☐ | Nut plug | `nut_plug_x6.stl` | 6 (one file) | on their side |

## 2. Fasteners

Every screw is M3, and every countersunk screw is the same M3×10.

| Have | Item | Standard | Qty | Where it goes |
|:---:|---|---|:---:|---|
| ☐ | M3×10 countersunk screw | ISO 10642 | 12 | 6 side, 4 lid corners, 2 Powerpole clamp |
| ☐ | M3×5 button head screw | ISO 7380 | 4 | BMS to spacer |
| ☐ | M3 hex nut, 5.5 mm across flats | ISO 4032 | 6 | side nut slots in the lid |
| ☐ | M3 heat-set insert, for a 4.2 mm hole, no longer than 7 mm | — | 6 | 4 base corners, 2 lid Powerpole bosses |

Use plain full-height nuts: the slots are 5.7 × 2.6 mm, so nylon-insert lock nuts won't fit. The insert holes are 8 mm deep in the base and 7 mm deep in the lid.

### Fasteners by part

| Part | Screws through it | Captive hardware in it |
|---|---|---|
| **Base** | 6 × M3×10 csk, through the long side walls into the lid beam ends | 4 × heat-set inserts (corner bosses), for the lid corner screws |
| **Lid** | 4 × M3×10 csk, through the corners into the base inserts | 6 × M3 nuts in the beam-end slots, closed by 6 glued plugs; 2 × heat-set inserts (Powerpole bosses, from below) |
| **Powerpole clamp** | 2 × M3×10 csk, from below into the lid inserts | — |
| **Spacer** | 4 × M3×5 button head, up into the BMS standoffs (replacing the BMS's own lower corner screws) | — |

## 3. Foam and adhesives

| Have | Item | Qty / size | Where it goes |
|:---:|---|---|---|
| ☐ | 1 mm foam tape | 1 roll | base saddles, spacer underside, lid rib seats |
| ☐ | 2–3 mm closed-cell EVA or neoprene | 8 pads | faces of the base stops |
| ☐ | Closed-cell foam block, front | about 139 × 9 × 27 mm | front end above the wiring |
| ☐ | Closed-cell foam block, back | about 139 × 8 × 27 mm | back end above the wiring |
| ☐ | Glue (CA or epoxy) | a little | 6 nut plugs |
| ☐ | Kapton tape | 1 roll | over every solder joint |

Cut the end blocks 2–3 mm oversize lengthwise, and slit them where leads rise.

## 4. Electrical

| Have | Item | Qty | Notes |
|:---:|---|:---:|---|
| ☐ | LiFePO4 cell, 3.2 V 15 Ah, Ø33.5 × 136.25 mm, with solder tabs | 4 | within about 0.05 V of each other |
| ☐ | 4S-capable balancing BMS, 30 A, 60 × 120 × 10 mm | 1 | with its balance lead |
| ☐ | Anderson Powerpole housing, red | 1 | output; bond "red right, tongue top" from the mating face |
| ☐ | Anderson Powerpole housing, black | 1 | output |
| ☐ | Single Powerpole pair (2 housings), inline disconnect | 2 | C4+ ↔ red output; C1− ↔ BMS B− |
| ☐ | Powerpole contacts, PP45 (10–14 AWG) or PP30 (12–16 AWG) | 6 | 2 output + 4 inline |
| ☐ | Inline ATM mini fuse holder, 12 AWG | 1 | on the red output lead |
| ☐ | ATM fuse, 30 A | 1 (+ spare) | |
| ☐ | 12 AWG silicone wire, red | about 0.5 m | |
| ☐ | 12 AWG silicone wire, black | about 0.5 m | also the 3 series links |
| ☐ | 22 AWG wire | 5 leads | balance leads, B0–B4 |
| ☐ | Heat-shrink, assorted | — | |

## 5. Tools and consumables

- 80 W+ soldering iron with a big chisel tip, and rosin flux
- Heat-set insert tip for the iron, or an old tip
- Powerpole crimper
- M3 hex keys or drivers for countersunk (2 mm) and button head (2 mm) screws
- Multimeter

## 6. Build options

Sections 1–5 are for the main design (60 × 120 BMS). The two Daly options change only the items below; everything else is the same. See the [README](README.md#build-options).

### Daly 20 A (same base, new lid)

| Have | Change | Qty | Notes |
|:---:|---|:---:|---|
| ☐ | Daly 4S 12 V **20 A** LiFePO4 BMS, 34 × 59 × 9 mm, instead of the 60 × 120 BMS | 1 | the 15 A model is the same box but too small for 100 W TX |
| ☐ | Print `cad/out_daly/lid_daly.stl` instead of the main lid | 1 | or glue `cad/out_daly/daly_caps_only.stl` into a printed lid |
| ☐ | 1 mm double-sided foam tape under the BMS | about 32 × 57 mm | |
| — | M3×5 button head screws | **not needed** | |

### Daly 20 A, low profile

| Have | Change | Qty | Notes |
|:---:|---|:---:|---|
| ☐ | Daly 4S 12 V **20 A** LiFePO4 BMS, 34 × 59 × 9 mm, instead of the 60 × 120 BMS | 1 | |
| ☐ | Print `cad/out_daly_low/base.stl`, `cad/out_daly_low/lid.stl`, `cad/out_daly_low/pp_clamp.stl` and `cad/out_daly_low/nut_plug_x6.stl` instead of the main ones | 1 each (plugs ×6) | the spacer stays the main design's |
| ☐ | 1 mm double-sided foam tape under the BMS | about 57 × 32 mm | |
| ☐ | End foam blocks, front and back | about 139 × 9 × 23 and 139 × 8 × 23 mm | 4 mm lower than the main design's |
| — | M3×5 button head screws | **not needed** | |

