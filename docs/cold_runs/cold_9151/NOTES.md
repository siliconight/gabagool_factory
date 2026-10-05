# Cold run 9151 -- 0 interventions; the painted windows face INTO the houses

gas_block_001, seed 9080, `empties: "across"`, `--bake-lights`.

**Stack:** Zoo 1.65.0 and Deli Counter 0.180.0 -- the painted windows: one
sixteen-state atlas, four room lights, one `M_Window_pane_Face` material, a
state per window, one vacant house.

**Result:** every leg ran -- export, findings, walk -- in 32.7 minutes, with
`INTERVENTIONS: 0`.

The batch ran as id `cold_9147`, a staging slip shared by 9148-9151 and
recorded in `docs/COMMANDS.md`. `tools/cold_drive/stage_batch.py` now sets
the id.

## Measured, and right

- **The package.** Greybox surfaces 0; no `STEM COLLISION` in any job log.
- **The modules.** All 31 painted window modules across the six houses wear
  `M_Window_pane_Face`. 15 of the 16 states shipped; plain `lit` did not
  come up on this seed.
- **The import** (`patches/lf_empties/pane_census.gd`, headless on 9151's
  walk copy): 164 painted-window surfaces, `StandardMaterial3D`, emission on,
  an emission texture, energy 1.60. They match Lux's binder name test, so the
  power cut binds them.

The probe's other row -- 52 surfaces in `M_Skin_wood_panel_delco_1997` -- is
the shut doors, 26 houses x 2. Its filter matched "pane" inside "panel"; a
probe artefact, not a finding.

## Found in the frames: the picture is on the inside face

`docs/findings/empties_windows_9151/`, the same five views, fill and night.
From the street every pane reads as one flat beige-grey -- no sash, no blinds,
no colour -- and at night none of them glows.

**Measured** (`patches/lf_empties/pane_face_probe.gd`), on the Empty at
x 1.55:
- the pane is at z 37.8; the house runs back to z 49.95; the street is
  toward z 27.65;
- the face carrying the atlas CELL has world normal **(0, 0, +1), into the
  house**;
- the face toward the street, **(0, 0, -1)**, carries the frame point:
  `FRAME_RGB` x `ALBEDO`, the beige.

**Why:** `_arch.build_slab` (Zoo 1.64.0) maps the cell onto the pane face
with local normal +Y, on the stated assumption "+Y is outdoors". That holds
for a wall module through its placement. This measurement says it does not
hold for these window modules as placed.

**RETRACTED, kept above what replaced it.** My first reading of the
from-above night frame was that the fronts showed lit windows. The warm
rectangles there are the same beige face catching the warm street light --
uniform, which is the tell.

**The fix, not made** (pausing here, at the walker's request):
- Paint the cell on BOTH big faces, each mapped to read unmirrored from its
  own side, so the result does not depend on a module's orientation at all.
- Re-run `pane_face_probe.gd`: the street-side face must carry a CELL.
- Shoot the night frames.

The emission, material and states measured above are unaffected; only the
face is wrong.
