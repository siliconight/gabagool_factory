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

**`crew_full`: 18 of 18 pass, as recorded** (2026-10-09, `crew_full.log`,
`results_crew_full.json`, `reports/crew_full/`). The settings: `crew_body`
with Laser Tag 0.24.0's step-up in place of the director's. Walks took 117 to
206 s each.
- **Its first walk was its load test.** Cold run 9204's seed_9181 passed,
  with all 68 targets reached.
- **The dial turned, so the pass is evidence:**
  - in 12 of the 18 walks, walkers' records end on the crew step's own
    refusal ("crew step refused: the wall is not ahead", 40 walkers; "the
    top rises -0.00 m", 16). Those strings exist only in the patched copy;
  - 110 of the 312 walkers travelled differently from `crew_body`, by up to
    2.50 m.
- **What it says.** Laser Tag's step-up asks what it lands on, and still
  fails none of the 18. On these candidates, the director's lenient step-up
  hid nothing the crew's rule cannot climb.
- **What it cannot say:** the report keeps only each walker's LAST step
  refusal, so how many steps the rule took or refused along the way is not
  recorded.

**The waypoint radius, on paper and in practice:**
- **On paper,** the director's waypoint rule cannot be met for the crew's
  body (the retraction above).
- **In practice,** the default 0.072 m failed no walk here.
- **That is an outcome on 18 candidates, not a derivation.** A walk-test fix
  that widens the body needs a slower walk, a higher physics rate, or a
  different consumption rule.

## Next: the order

The crew's body is measured, with all three of its differences: radius,
floor and step-up. None fails a kept candidate, so `radius_only` and
`floor_only`, which would attribute a failure, have nothing to attribute.

**What is left is 208's third difference.** The director walks home to each
anchor, plus a chain through them, and never the mission's own order: spawn,
then objective, then extraction. Cold run 9194's chain walked the vault to a
ground-floor anchor, never the vault to the extraction. Re-walking that
order needs the director to take a route rather than a set, so it is a
director change to measure, not a variant of this one.

*Kept, as filed before it ran:* "`crew_full`: all 18 with Laser Tag 0.24.0's
step-up, about 50 minutes; never yet run in Godot, so the first walk is its
load test; a 9194 failure would mean the copied rule is wrong." It loaded,
and its walks took 2,805 s between them, about 47 minutes. 9194's three
passed.

## Records beside this README

- **The instruments:** `rewalk.py` (the re-walk) and `summarize.py` (the
  table).
- **The table:** `summary.txt`.
- **The control:** `results_as_run.json`, with its report under
  `reports/as_run/`.
- **The crew's body:** `results_crew_body.json`, its 18 reports under
  `reports/crew_body/`, and `crew_body.log`.
- **The crew's body and step-up:** `results_crew_full.json`, its 18 reports
  under `reports/crew_full/`, and `crew_full.log`.
- **Refuted, kept:** `results_crew_body_wp003_refuted.json`,
  `reports/crew_body_wp003_refuted/` and `crew_body_wp003_refuted.log`.
- **Deleted:** the scratch copies, once each report was kept.
