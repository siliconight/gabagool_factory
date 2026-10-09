# Session handoff -- 2026-10-09

Written at the close, from the artifacts. It follows `SESSION_1008_HANDOFF_2.md`.
Read `CLAUDE.md` and the memory index first, then this, then
`PIPELINE_ROADMAP.md` items 217 and 218.

## State at close

| repo | version | unpushed commits |
|---|---|---|
| zoo | 1.89.0 | 0 |
| lot | 0.102.0 | 0 |
| level_factory | 0.163.1 | 0 |
| lux | 0.71.0 | 0 |
| deli_counter | 0.204.0 | 0 |
| lasertag, dispatch, patina, pixelcoat, pipeline | 0.25.0, 0.5.2, 0.29.1, 0.61.0, 0.6.0 | 0 |
| factory root | -- | 0 after this handoff's push |

- **Clean.** Every tree is clean.
- **Pushed.** Every repo was pushed at the walker's word ("commit, push").
- **Nothing running.** No cold run is in flight (`_runs/cold/ACTIVE` is
  absent), and no Godot or Blender process is left.
- **Disk:** 15 GB free (97% used). `tools/factory_retire.py` lists 17.3 GB
  retirable in 22 items. Nothing was retired; that is the walker's call or
  the disk's. A cold run adds about 0.7 GB.

## What shipped

Cold runs 9210 to 9214, 0 interventions each. 9214 also took 1 retry.

- **Roadmap 215 NARROWED.** Lot's site audit reaches the report (Lot
  0.102.0, Level Factory 0.163.0).
- **Roadmap 214 NARROWED.** Trial 1: weighted normals (Zoo 1.87.0).
- **Roadmap 210 NARROWED: the payphone.**
  - Redrawn (Zoo 1.88.0).
  - Lit: Zoo 1.89.0 and Lux 0.70.0.
  - A wall unit indoors: Deli Counter 0.204.0.
- **Roadmap 208 NARROWED.** The walk test with the crew's whole body.
- **Roadmap 216 OPEN.** Trees, filed.
- **Roadmap 217 NARROWED: levels read by day and by night.**
  - **Root tools:** `light_breakdown.py`, `light_check.py` and
    `lux_rebake.py` (`--preset`, `--set`, `--no-fills`,
    `--bake-environment`).
  - **Lux 0.71.0:** street lamps dark by day, proven in 9214.
  - **The walker's lighting spec,** filed in `docs/reference/` and set
    against the code in `docs/findings/lighting_spec_vs_lux/`.
- **Roadmap 218 NARROWED: the import pass.** 9214's export imported 0 of
  425 models and went on. Level Factory 0.163.1 checks, repeats and logs
  every pass.

## The walker's calls, open

- **217, the sky in the bake.** Level Factory's `environment_mode` 0 to 1 is
  one line, recommended.
  - On a clear afternoon it lifts the street +15 to +21, and shade goes from
    near black to daylight.
  - At night and dusk it adds +0.5 to +4.4 outside.
  - Rooms move 1.2 or less in every slot, and it costs nothing at run time.
  - Sheet: `docs/findings/lighting_spec_vs_lux/sky_in_the_bake_clear_afternoon.png`.
  - Walkable copies of the clear afternoon, sky off and on:
    `_runs/day_lamps_9214/rebake_clear` and `rebake_clear_sky`.
- **217, Heavy Rain's sun.** Its shadowless sun lights rooms through roofs,
  12 of 16 brighter than the street. That was Lux 0.38.0's trade on price.
  The ways forward:
  - re-price its shadow on today's package (shadow on: rooms -5.6 to -31.6);
  - the free cull-mask split;
  - or keep it.
- **217, the night boost.** Fluorescents scale 1.0 by day to 6.0 at night.
  Keep it as a recorded override, or move it out of the lamps.
- **217:** morning and noon presets.
- **From earlier:**
  - 210: Lot's placement themes, and an eye on the lit booth;
  - 216's look;
  - 215's arc options;
  - the stage-lamp lens;
  - the `.docx`.

## Ready, no input needed

- **Cold run 9215 is staged:** bank_block_001 on Level Factory 0.163.1, to
  close item 218. Run it, then end it:

      bash tools/cold_drive/cold_drive.sh 9215 9214 bank_block_001 auto > docs/cold_runs/cold_9215/driver.log 2>&1
      python tools/cold_run.py --end

- **217: the light check's failures on bank_block_001.**
  - At night: the bank's grand lobby and the casino's gaming floor (p50 9).
  - At Blue Hour: the grand lobby (p50 3), the stone vault (p50 2), and the
    extraction "collapsed to black" (p50 1).
  - Cold run 9213's airport check-in hall (p50 8) at midnight.
- **216's first step:** price an alpha-tested card crown against a blended
  one.
- **214:** trial 2, convex-edge wear.

## Environment

The walker's external WD My Passport (USB) logged 30,051 disk hardware
errors on 2026-10-09 and kept re-attaching. The walker was told. C: and the
WD hard disk report healthy. Nothing ties the drive to 9214's import stall.
