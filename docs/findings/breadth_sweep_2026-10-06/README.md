# The breadth sweep, 2026-10-05/06: ten missions, cold

**Why.** Cold runs 9135 to 9165 all built gas_block_001, so their zeros were
one level's zeros. The walker approved making the Empties and the light bake
the defaults (Level Factory 0.144.0) and running one cold run per mission
family: "yes to both defaults, do the ten first".

**How.**
- Each mission ran on its brief as last run cold, staged out of
  `docs/cold_runs/`, with the seed picked by the driver (`auto`), except the
  control.
- No export flags were passed, so the bake ran because of the default.
- One cold run at a time; fixes went into the tool repos only between runs.
- The scripts: `tools/cold_drive/sweep_one.sh`, one run per call, and
  the staging recipe in `docs/COMMANDS.md`. The sweep ran a scratch copy
  with `PREV` pinned to 9165; the committed one finds the newest workspace
  that has a tool config.

## The result

**First attempt: 8 of 10 shipped untouched. After two Level Factory fixes,
10 of 10 at 0 interventions.** Each fix is in the tool, proven by a re-run
of the same brief, and every mission now runs with both.

| mission | brief as of | cold run | seed | site | Empties | bake: users, editor s | findings, shell / art | median frame (worst) | views over 16.7 ms p95 |
|---|---|---|---|---|---|---|---|---|---|
| gas_block_001 (control) | 9165 | 9166 | 9080 | street block, 3 + library | 12 (the brief asked) | 3,309, 79.0 | 40 / 55 | 3.54 ms (12.11) | 0 of 53 |
| club_block_014 | 9134 | 9167 | 9080 | street block, 3 + library | 12, by default | 3,839, 86.4 | 42 / 62 | 3.39 ms (11.28) | 0 of 53 |
| bank_block_001 | 9054 | 9168 | 9054 | street block, 3 + library | 12, by default | 3,891, 87.8 | 45 / 63 | 2.26 ms (11.66) | 0 of 53 |
| video_block_001 | 9133 | 9169 | 9080 | street block, 3 + library | 12, by default | 3,271, 79.7 | 44 / 64 | 3.56 ms (11.56) | 0 of 53 |
| card_block_001 | 9061 | 9170 STOPPED, 9174 | 9263 | street block, 3 + library | 12, by default | 3,438, 81.0 | 50 / 68 | 4.69 ms (12.55) | 0 of 53 |
| precinct_yard_001 | 9001 | 9172 | 9001 | courtyard, 4 + library | 12, by default | 4,247, 98.0 | 33 / 54 | 5.17 ms (13.34) | 0 of 53 |
| gas_stop_001 | 9011 | 9177 | 9011 | strip, 3 + library | 12, by default | 2,896, 75.5 | 37 / 55 | 3.88 ms (12.18) | 0 of 53 |
| county_hospital_001 | 9006 | 9171 STOPPED, 9173 | 9006 | campus, 1, no library | none (no library) | 1,634, 41.6 | 43 / 57 | 1.65 ms (2.71) | 0 of 33 |
| restaurant_row_001 | 9003 | 9175 | 9104 | strip, 3, no library | none (no library) | 4,871, 65.6 | 60 / 80 | 5.45 ms (13.11) | 0 of 53 |
| warehouse_yard_001 | 9004 | 9176 | 9105 | yard, 2, no library | none (no library) | 1,793, 40.8 | 49 / 64 | 1.25 ms (4.26) | 0 of 45 |

- **Every leg ran on every exported mission:** shell, approvals, art, export,
  findings, walk. Every shell built 3 distinct candidates, and no leg
  recorded a blocker.
- **Every Empties export merged the same way:** 1,061 meshes of 1,660
  surfaces into 236, with 962 colliders kept.
- **The price** is the fixed-station harness (`_runs/perf_inner/run.py`),
  two passes a view with the lower p95 kept. All ten packages were priced in
  one session on this machine with 60 s cool-downs, and the hospital last,
  after the probe fix below.
  - These are absolute figures, with no A/B control, so they compare
    missions with each other and not with any earlier session.
  - The reports are `_runs/perf_inner/sw_<mission>.json`.
- **Frame time held 60 fps at every view of every mission.** The worst
  single view anywhere was 13.65 ms p95, on precinct_yard_001.

## What the sweep found and fixed, all in Level Factory

1. **0.144.0, found by the defaults themselves.** A failed light bake wrote
   the package's absolute path into `light_bake.json`, and the closure scan
   refused the export. So any machine that could not bake could not export.
   The report joined the scan's metadata exemptions.
2. **0.144.1, cold run 9170.** The export refused over `LT_NOT_EVALUATED` on
   seed_9061, a candidate nobody chose. `_open_blockers` read the candidate
   from `location`, while the finding carried it in `candidate_id`, the field
   `cmd_run`'s `aggregate` already read. 9174 exported the same level, with
   the same finding now discounted.
3. **0.144.2, cold run 9171.** The selected site was re-assembled two seconds
   after the functional lock.
   - With no lot library, the site spec was written at plan time, before
     Deli Counter had generated the shell it measures. So it was sized from
     `DEFAULT_FOOTPRINT`, and the art run re-measured it.
   - That is the default path for every new brief.
   - The fix: the scheduler finishes a job's spec at dispatch (`prepare`),
     and Lot's spec is written again there. 9173, 9175 and 9176 exported on
     it.
4. **0.144.3, the close-out.** The price probe could not measure
   county_hospital_001.
   - It walked the scene at load and read the list after the level's
     warm-up had freed its own nodes.
   - `is` on a freed instance killed its coroutine, and it idled until its
     600 s watchdog, twice.
   - The level itself ran 300 frames in 2.8 s. The fix re-walks the tree
     before counting.

## Open, and not this sweep's to close

- **Demo and reference shells drawn into lots** (roadmap 185).
  `setback_demo` and `pvp_station_ref` are complete Deli Counter builds, and
  the library draws them. Whether they belong in real levels is the
  walker's call.
- **Briefs without a `lot_library` get no Empties**, three of the ten. The
  library is opt-in for the reason its own comment gives; making it the
  default is a separate decision.
- **Every brief had been through the pipeline before**, on older tools.
  Roadmap 17's acceptance test asks for a spec that never has.
- **"Works" is measured here; "good" is not.** The overview frames beside
  this file are for the walker's eye, which is still the only instrument for
  that (roadmap 18).

## Frames

`<mission>_overview.png`: one overview per mission, from `tools/look_shots.py`
on that mission's walk copy (the exporting run's). Every view look_shots
takes (four elevations, spawn, objective, extraction, overview) is in
`_runs/sweep_frames/<mission>/`.

The frames show each brief's own time and weather. Two read poorly from
above, and neither is a defect the sweep measured:
- **precinct_yard_001** (`afternoon`, `clear`) reads washed out under the
  afternoon haze.
- **county_hospital_001** (`night`, `rain`) is mostly rain streaks and fog;
  its eye-level frames show more.
