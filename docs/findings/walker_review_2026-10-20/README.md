# The walker's look review, 2026-10-20

**What it is.** One page with today's changes, each beside before-and-after frames, with an answer to tap and a note
for each: https://claude.ai/artifact/TSdXhvhicTf7o3keriGH6Z (private to the walker). It holds 9 questions on roadmap
items 148, 210, 170, 217, 79 and 267. Answers save to the page's own store, collection `verdicts`, one document per
question (`{choice, note, at}`), and are read back with the Artifact tool's data reads -- as 2026-10-19's page
(`docs/findings/walker_review_2026-10-19/`), whose generator this one's is.

**Where the frames came from.** Every frame was shot on 2026-10-20 with `tools/look_shots.py` from walk copies
(`tools/walk_export.py`) of cold runs' packages, except roadmap 79's, which is cold run 9348's own record
(`docs/cold_runs/cold_9348/fronts_9282_vs_9348.jpg`):

| section | before | after | cameras |
|---|---|---|---|
| 148, the office screens | cold run 9349 | cold run 9350 | `docs/cold_runs/cold_9350/office_stations.py` |
| 210, the street phones | cold run 9350 | cold run 9351 | `docs/cold_runs/cold_9351/stop_stations.py` |
| 170, the roof hatch | cold run 9348 | cold run 9352 | `docs/cold_runs/cold_9315/hatch_station.py`, the inspection light |
| 217, morning and noon | -- | cold runs 9353 and 9354 | the level's derived cameras |

The walk copies the page names are in `_scratch/review/`: walk_9350 (the office), walk_9351 (the phones),
walk_9352 (the bank's roof), walk_9353 (morning) and walk_9354 (noon).

    python docs/findings/walker_review_2026-10-20/collect_frames.py <page dir>
    python docs/findings/walker_review_2026-10-20/build_page.py <page dir>

## The walker's answers, 2026-10-20

All 9 questions were answered on the page between 18:56 and 18:57 UTC; `verdicts_2026-10-20.json` is the page's store
as read back that afternoon, one document per question. Each answer now leads its roadmap item's status
(`patches/patch_roadmap_look_review_2026_10_20.py`).

| item | question | answer | the walker's note |
|---|---|---|---|
| 148 | the office screens | Looks right | |
| 210 | each phone facing the sidewalk | Looks right | |
| 210 | the booths' marks | Needs work | "more subtle graffiti/weathering....a large shapie squigle doesn't look like anything" |
| 170 | the hatch's hole against its lid | Looks right | |
| 217 | the morning | Looks right | |
| 217 | the high noon | Looks right | |
| 79 | the stacked fronts | Better | |
| 79 | where stacking and symmetry trade | Symmetry | |
| 267 | arena_a02's barrier | Crowd rails (a new model) | |

The one "Needs work" was answered the same day: Zoo 1.117.0 marks every booth small and mostly with weather, and cold
run 9355 shows it in 9351's level (`docs/cold_runs/cold_9355/`). Symmetry is the rule Deli Counter 0.238.0 already
shipped by default. The crowd rails are a new Zoo species and a Deli Counter mapping, queued under roadmap 267.
