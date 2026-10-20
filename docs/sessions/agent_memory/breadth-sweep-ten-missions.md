---
name: breadth-sweep-ten-missions
description: "Walker 2026-10-05 evening -- next big session is a BREADTH sweep: Empties + light bake ON by default, then one cold run on each of ten mission families; continuous mode"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-06T12:18:46.561Z
---

The walker approved this on 2026-10-05: "yes to both defaults, do the ten
first".

**Why:** the zeros so far were all on one mission. Cold runs 9135-9165 all
built gas_block_001, and no other mission had a COLD RUN since 9134 (2 Oct).
So nothing shipped since had been through a cold run elsewhere: the light
bake (LF 0.131.0), street-facing fronts (LF 0.132.0), parking fields (Lot
0.94.0), dumpsters (Zoo 1.58.0), the cover merge (Zoo 1.68.0) or the
Empties.
- Correction, made 2026-10-05: I first said "built". The fronts and fields
  WERE built on club_block_014 and crossroads_9600, in before/after
  workspaces on 3 Oct, just never in a cold run. The
Empties were opt-in per brief (`empties` defaulted to "" in
level_factory/packages/core/models.py), and the bake was opt-in
(`--bake-lights`).

**Plan:**
1. **Defaults ON.** Empties "across" and the light bake, both with an
   explicit opt-out. The export already falls back to unbaked with a warning
   when the bake fails.
2. **Sweep.** One cold run per family, seed `auto` (the driver picks):
   - gas_block_001 first, as the control, at seed 9080 for comparison with
     9165;
   - then club_block_014, bank_block_001, video_block_001, card_block_001,
     county_hospital_001, precinct_yard_001, restaurant_row_001,
     warehouse_yard_001, gas_stop_001.
   - Run WITHOUT `EXPORT_FLAGS`, so the bake default is what's exercised.
3. **Fix what breaks, in the tool repos.** For each one: a failing test, the
   fix, a version bump, and a re-run of that mission. Count every
   intervention.
4. **Close.** A table per mission: interventions, frame time, one street
   frame. Then update roadmap 17.
5. **Stretch.** The fence at the playable edge
   ([[fence-marks-the-playable-edge]]).

**Staging other missions:** the old workspaces are deleted
([[perf-copies-fill-the-disk]]). So stage from the mission's last docs run
(`stage_batch.py N <that run>` copies batch.json and briefs from
docs/cold_runs). Then drive with PREV set to the newest EXISTING workspace:
`cold_drive.sh` copies `workspaces/cold-$PREV-ws/tools.local.json` and dies
if it's missing. The findings diff against PREV is harmless when the mission
differs (a missing file reads as an empty count).

**DONE 2026-10-06 (cold runs 9166-9177; record
`docs/findings/breadth_sweep_2026-10-06/`).**
- **Score:** first attempt, 8 of 10 shipped untouched; after two Level
  Factory fixes, 10 of 10 at 0 interventions.
- **Fixes, all LF:**
  - 0.144.0: a failed bake's report broke the closure scan.
  - 0.144.1: the export now reads a blocker's `candidate_id` (9170).
  - 0.144.2: no-library site specs are written again at dispatch via a
    scheduler `prepare` hook, so the judged site is the shipped site
    (9171).
  - 0.144.3: the price probe re-walks the tree (county_hospital's warm-up
    frees nodes).
- **Price:** every view of every mission is under 16.7 ms p95; worst 13.65 ms
  (precinct_yard_001).
- **Roadmap:** 17 gained the sweep era (still NARROWED: no never-seen spec
  yet), 106 CLOSED, 185 filed (demo/ref shells, the walker's call).
- **Commits:** local only, not pushed.

**Order the walker set on 2026-10-06:**
1. Demo shells out (DC 0.187.0 + LF 0.144.4), then the lot library by
   default where it honours the brief (LF 0.145.0). Proof runs 9178-9180.
2. The detail audit ([[detail-lives-in-generator-logic]]).
3. The fence.

**How to apply:** continuous mode ([[keep-it-rolling]]). Summarise at each
block's end, then start the next. Rules that still hold:
- never edit a tool repo during a cold run
  ([[never-edit-tool-repos-during-a-cold-run]]);
- check disk before each run;
- one cold run at a time;
- commit locally, push only when the walker says.
