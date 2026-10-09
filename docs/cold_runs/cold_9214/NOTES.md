# Cold run 9214 -- 0 interventions, 1 retry; street lamps dark by day, and an import pass that stopped short

bank_block_001, seed auto, staged from cold run 9203. It tests **Lux
0.71.0**, the walker's call on 2026-10-09: "street lamps aren't usually on
during the day". The batch also carries the releases since 9203, among them
the lit payphone and its indoor wall form (roadmap 210).
- **The brief is afternoon with rain,** so the level ships under Heavy Rain,
  which its own description calls an overcast day. Lux 0.71.0 makes it a
  day preset (`street_lamps_lit = false`).

Tool versions hashed at `--begin`: Zoo 1.89.0, Lot 0.102.0, Level Factory
0.163.0, Laser Tag 0.25.0, Deli Counter 0.204.0, Lux 0.71.0, Dispatch 0.5.2,
Patina 0.29.1, Pixelcoat 0.61.0, Pipeline 0.6.0. Moved since 9203:
- Zoo, 1.85.0 to 1.89.0;
- Lot, 0.99.0 to 0.102.0;
- Level Factory, 0.158.0 to 0.163.0;
- Deli Counter, 0.203.0 to 0.204.0;
- Lux, 0.68.2 to 0.71.0.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0), **retries 1**:
the export, re-run unchanged after a transient (below). The only files
changed in tool repos are the two Deli Counter specs the pipeline writes.

**Picked: seed_9054,** as in 9200 to 9203. Its figures are 9203's:
- seed_9054: 0 majors, route completion 1.00;
- seed_9155: 0 majors, 0.88;
- seed_9256: 1 major, 0.84.

## The retry: an import pass that stopped short

**The first export stopped.** `driver.log` reads "the Empties' merge
failed ... merge failed: 12 scene(s) failed". Every row of
`merge_empties_attempt1.json` says "no side to merge", with 0 meshes in.

**Why the merge saw nothing.** At 15:30:40 the export ran Godot's
`--import` on the fresh package (`export.py`, `_write_import_sidecars`).
- **It left sidecars on 140 of the package's 975 importable files, and on
  none of its 425 models** (`attempt1_sidecars.txt`). The 140 are all
  SkyMint's, which arrive with Lux's runtime carrying sidecars of their own.
- **Nothing looked.** The pass's exit code and output were discarded.
  `occluders.ensure_imported` took the `.godot` folder it left for an
  import. The occluder bake then loaded a scene with every module missing
  and reported `ok`, 0 occluders from 0 modules
  (`occluders_attempt1.json`). The export printed that line and went on.
- **The merge was the first step to refuse.**

**Not the content.** The same package imported 425 of 425 models in seven
fresh reruns, 37 to 45 s each (`import_reruns.txt`):
- five with every sidecar deleted;
- two from the export's exact starting state, SkyMint's sidecars restored
  to their source text.

The export, re-run unchanged (`--retry`, `driver_resume.log`), imported and
went through.

**What made the pass stop short is not established.** Godot's output was
not kept, and no Godot log from that pass was found afterwards.

**Logged at the time, and not tied to it.**
- The Windows System log carries 30,051 disk hardware errors on 2026-10-09,
  00:06 to 15:27. All are on an external USB drive (WD My Passport) that
  dropped off and came back about a dozen times.
- Cold run 9213 exported cleanly while they ran, and they stopped three
  minutes before this pass.

**The fix shipped after `--end`: Level Factory 0.163.1.** Each import pass
is checked: a model counts once its sidecar names files that are there.
- **A short pass is repeated,** up to 3 times.
- **Every pass's output is kept** beside the package.
- **A pass that never completes stops the export.**
- **`ensure_imported`** no longer takes a cache folder for an import.

The patch is `patches/patch_lf_import_pass_verified.py`.

## What held

**Findings: 60 to 74.** The 14 new ones are Lot's site audit:
- `S_GETAWAY_AT_SPAWN` 0 to 4;
- `S_RESPONDER_ARC` 0 to 4;
- `S_STREET_CROSS` 0 to 6.

Level Factory reads the audit since 0.163.0 (roadmap 215), and 9203 came
before that, so these are newly counted rather than newly made.

**The legs:**
- **The shell leg:** 3 candidates, all distinct; 0 blockers of 54 findings.
- **The art leg:** 0 blockers of 74. It exits 1 at the approval gate, as
  before.

**The export, on the retry, matches 9203:**
- **Occluders:** 1,481 from 1,491 solid modules.
- **The Empties:** 12 merged into 236 meshes.
- **Room fills:** 217.
- **The light bake:** 415 models lightmapped and 21 failing rigs left live.
  - Steady rigs baked: 81 to 83.
  - Users: 3,641 to 3,639.
  - The responders' car is now set dynamic (Level Factory 0.162.1).

## The street lamps by day

`_runs/day_lamps_9214` measured the walk copy three ways (not kept: the
numbers are here, and the commands are in
`docs/findings/lighting_spec_vs_lux/`):
- **as shipped;**
- **re-baked with the lamps on:** `tools/lux_rebake.py --set
  street_lamps_lit=true`, the way every day level shipped before 0.71.0;
- **re-baked with the bake's sky on:** a separate question, in the finding.

**What the switch is checked against.** The re-bake's own log records
`street_lamps_lit` set to `true`, from `false`. Both the poles and the wall
packs carry `dusk_to_dawn = true`.

**At the light check's 23 stations the lamps change nothing.** Every frame
moves by 0.2 or less, in luma after the grade, 0 to 255. A lamp adds little
to a daylit street, as the lighting spec predicts.

**Close up they show** (`street_lamps_by_day.png`, from `lamp_sheet.py`):

| camera, region | as shipped | lamps on |
|---|---|---|
| wall pack 002, the wall above its door | 32.5 | 48.0 |
| wall pack 002, the sidewalk | 62.3 | 84.2 |
| wall pack 002, its lens | 28.1 | 60.2 |
| pole 24, its head | 75.4 | 98.2 |
| pole 24, the warm patch at its foot | 78.7 | 79.5 |
| pole 7, a cycling lamp drawn live, the whole frame | 53.1 | 55.0 |

**A hidden lamp is not baked.** The wall pack is a baked rig. Its light is
in the lamps-on lightmap and absent from the shipped one, so hiding the rig
keeps its light out of the bake. Lux 0.71.0 had left that question open.

**Pole 24's warm patch is not the pole's light.** It is there with the lamp
on or off, +0.7. What it is was not measured.

## The light check

`tools/light_check.py` on the walk copy at its own slot, and re-baked at
night.

**Heavy Rain as shipped: 10 PASS, 12 WARN, 1 REPORT.**
- **The 12 WARNs:** 12 of the 16 interior stations (15 rooms and the
  objective) read brighter by day than the street's median, 47.5. The 16
  range from 36.6 to 83.8. The street and the facades all pass.
- **Answered** in `docs/findings/lighting_spec_vs_lux/`: Heavy Rain's sun,
  which casts no shadow, lights the rooms through their roofs.
  - Re-baked with its shadow on, the rooms fall 5.6 to 31.6 and 12 WARNs
    become 7.
  - The fluorescent boost is not the cause: re-baked at 1.0 for 4.3, the
    rooms move 0 to 11.8 and all 12 still warn.
  - The shadow was refused on price in Lux 0.38.0, a trade recorded in
    `lux_preset.gd`.

**Delco Night, re-baked: 2 FAIL, 1 WARN.**
- **FAIL:** the bank's grand lobby, p50 9, and the casino's gaming floor,
  p50 9, both under the ROW floor of 10.
- **WARN:** the north elevation, p95 3.

## Records beside this note

- **The legs:** `driver.log` (the first attempt, to its stop) and
  `driver_resume.log` (the retry onward, with the driver's own commands);
  `export.log` and `export_attempt1.log`; `art.log`.
- **The first attempt's evidence:** `merge_empties_attempt1.json`,
  `occluders_attempt1.json` and `attempt1_sidecars.txt`.
- **The reruns:** `import_reruns.txt`, written by
  `import_rerun_fresh.sh` (four runs; the first of the five fresh ones was
  the same commands by hand) and `import_rerun_faithful.sh` (two runs).
- **The retry:** `resume_from_export.sh`. It runs the driver's own lines
  from `== export` on, and a diff against `tools/cold_drive/cold_drive.sh`
  lines 43-73 is empty.
- **The lamps:** `street_lamps_by_day.png` and `lamp_sheet.py`.
