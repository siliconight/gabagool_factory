# The walk test re-walked with the crew's body (roadmap 208, measure first)

**Question.** The walk test picks the candidate: a walk test that is not ok
puts a candidate out. Its walker is not the crew:

| | the walk test's walker | the crew (Laser Tag's pill) |
|---|---|---|
| radius | `AGENT_RADIUS * 0.7` = 0.28 m | `characters.player.radius_m` = 0.35 m |
| floor | `DC_NAV_SLOPE` + 1 = 56 degrees | none set: Godot's default, 45 |
| step-up | lifts on any wall contact, never asks what it lands on | a top a body-width ahead, its normal inside the floor angle |

It passed the stair foot where cold run 9194's crew wedged. Before the walker
changes and becomes a stricter gate, how many candidates it passed would the
crew's body fail?

**Subject.** Every walk test staged in the kept cold-run workspaces,
cold-9193-ws to cold-9204-ws: 36 staged walks, 18 distinct by content (cold
runs 9196 to 9203 repeat missions and seeds byte for byte). Four missions:
restaurant_row_001, bank_block_001 (three Lot generations: 9194, 9198,
9200), gas_block_001 and club_block_014. All 36 were recorded `ok`.

## How

`rewalk.py` walks a copy of each staged project with its own copy of the
director patched for the variant, through `lot/walktest.py`'s own steps.
- **Not through `walktest.py`'s `main()`.** It calls `sync_addon`, which
  copies the checkout's addon over the project's before every run, so a
  patched copy walked through it would walk the shipped body.
- **The control reproduces the job.** `as_run`, the copy unpatched, on
  cold run 9204's seed_9181: pass, 68 of 68 targets, every walker's status
  identical, 158.2 simulated seconds against the job's 158.2. The walk is
  deterministic and the copy is faithful.

**The variants:**
- `crew_body`: radius 0.35, floor 45, the director's step-up kept.
- `crew_full`: `crew_body` with Laser Tag 0.24.0's step-up in place of the
  director's.
- `radius_only`, `floor_only`: to attribute a failure.

**The waypoint radius stays the director's 0.072 m.** *Retracted, kept:* the
first `crew_body` run set it to the director's own derivation for the wider
body, 0.6 * (0.40 - 0.35) = 0.03 m, and every walker froze at its first
waypoint (`results_crew_body_wp003_refuted.json`, three walks, all failed
inside 18.2 simulated seconds). A body moves 0.067 m a physics frame at
4 m/s, so a capture radius under that can be stepped over forever. The
director's rule needs the radius above the frame step and inside the corner
margin, and for a 0.35 body on the contract's 0.40 bake the margin is 0.05,
under the step: no radius does both. `rewalk.py`'s docstring has the detail.

## Results

From `summary.txt` (`summarize.py`).

**`crew_body`: 18 of 18 pass, as recorded.** The settings: radius 0.35,
floor 45, the director's own step-up and waypoint radius. Every walker in
every walk reached every target. Walks took 117 to 206 s each.

**What it says.** Moving the walk test's 0.28 m radius and 56 degree floor
to the crew's 0.35 m and 45 degrees fails none of the 18 distinct candidates
in the kept workspaces. On these candidates, neither leniency is passing
geometry the crew's body cannot cross.

**What it does not say:**
- **The step-up is still the director's.** It lifts on any wall contact and
  never asks what it lands on. At a 45 degree floor a steeper ramp reads as
  a wall, so this walker can lift its way up a ramp the crew cannot stand
  on. Whether that hid anything is `crew_full`'s question.
- **The order is still the director's.** It walks home to each anchor and a
  chain through them, never the mission's spawn, objective, extraction.
  That is 208's third bullet.
- **9194's wedge was Laser Tag's own step-up,** closed by Laser Tag 0.24.0.
  It was never a question of body width, so `crew_body` passing 9194 says
  nothing about it.

**The waypoint radius, on paper and in practice:**
- **On paper,** the director's waypoint rule cannot be met for the crew's
  body (the retraction above).
- **In practice,** the default 0.072 m failed no walk here.
- **That is an outcome on 18 candidates, not a derivation.** A walk-test fix
  that widens the body needs a slower walk, a higher physics rate, or a
  different consumption rule.

## Next: `crew_full`

    python docs/findings/walktest_crew_body/rewalk.py --variant crew_full

- **What it walks:** all 18, with Laser Tag 0.24.0's step-up in the copy,
  in about 50 minutes.
- **It has never run in Godot.** The patched director passed
  `tools/gdcheck.py`, so the first walk is its load test.
- **A walk with no report is a load failure,** and its log is in
  `_scratch/2026-10-08_walktest_body/crew_full/`.
- **What 9194 should show:** Laser Tag's crew passes that stair now, so a
  `crew_full` failure there means the copied rule is wrong, not the level.
- **After it:** `radius_only` and `floor_only`, on whatever fails.

## Records beside this README

- **The instruments:** `rewalk.py` (the re-walk) and `summarize.py` (the
  table).
- **The table:** `summary.txt`.
- **The control:** `results_as_run.json`, with its report under
  `reports/as_run/`.
- **The crew's body:** `results_crew_body.json`, its 18 reports under
  `reports/crew_body/`, and `crew_body.log`.
- **Refuted, kept:** `results_crew_body_wp003_refuted.json`,
  `reports/crew_body_wp003_refuted/` and `crew_body_wp003_refuted.log`.
- **Deleted:** the scratch copies, once each report was kept.
