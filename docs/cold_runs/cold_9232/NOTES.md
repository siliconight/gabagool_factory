# Cold run 9232 -- 0 interventions, 0 retries: the first level drawn by a template that shipped

restaurant_row_001 (`corner_deli`, a `strip` site), evening and clear,
seed auto, 9231's batch and brief (`"cluster": "auto"`) re-run on the set
that landed after 9231 stopped at the export: Level Factory 0.176.1 (the
site spec's draw takes the cluster template too), Lot 0.112.0 (the guide's
gameplay targets in the site audit) and Deli Counter 0.207.0 (rows over the
aisles between the shelf runs; the long hall's trade).

Tool versions hashed at `--begin` (`_runs/cold/cold_9232/before.json`):
Deli Counter 0.207.0, Dispatch 0.5.2, Laser Tag 0.25.0, Level Factory
0.176.1, Lot 0.112.0, Lux 0.74.0, Patina 0.30.0, Pipeline 0.6.0, Pixelcoat
0.62.0, Zoo 1.97.0. Against 9231: Deli Counter 0.206.1 to 0.207.0, Level
Factory 0.176.0 to 0.176.1, Lot 0.111.0 to 0.112.0.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0), **retries 0,
driver exit 0.**
- **The shell leg:** 3 candidates built, all distinct, 0 blockers of 76;
  picked seed_9104 on the walktest and Laser Tag's route findings (seed
  9003: 1 major, route completion 0.92; 9104: 0 major, 0.92; 9205: 1
  major, 0.60). The route completion is Laser Tag's `route_completion_rate`
  over 25 crew runs: 0.92 here (progress 0.95; 65 stuck events, 35 player
  deaths) where the station lot read 1.00 in 9229 and 9231; the walktest's
  23 path proofs all pass, no anchor stranded or behind a barrier. A sim
  outcome on a different lot, not a path defect; not chased here.
- **The art leg:** 0 blockers of 108.
- **The export:** `closure verdict: ok=true, 0 issue(s) over 81 resource(s)
  in a package of 2962 file(s)`; the light bake ran (473 models and 1,332
  primitive meshes lightmapped, 207 steady rigs baked, 25 failing left
  live, 215 room fills; 9229: 225 and 29, 267 fills -- a smaller lot);
  `backdrop: site_backdrop.tscn -- 260 instances of 7 module(s) on their
  sides, 25 draw calls (N 94, S 91, E 37, W 37; 1 tower)`; surface dressing
  3,642 instances of 4 meshes, 4 draws.

## Roadmap 230: the draw by template, in every stage

- **`cluster_resolved`** in every candidate's site spec and the themed
  one: asked `auto`, got `C03_station_neighborhood`, known, preferred
  `deli, cr_deli, night_deli, pharmacy, office, office_stepped, bank_tower,
  apartment_walkup, twin`.
- **The three candidates' lots are the template's:** `deli_a03 +
  pharmacy_a01 + office`, `deli_a01 + pharmacy_a01 + office`, `deli_a03 +
  pharmacy_a02 + office` -- the anchor deli, then the guide's pharmacy and
  office, where 9229's and 9231's untemplated draws gave depot and
  self-storage, office and station, supermarket and parking garage.
- **One lot in every stage:** the themed site places `b0 deli_a01` at
  x -51, `b1 pharmacy_a01` at 4, `b2 office` at 48; the art jobs are
  `patina_apply.deli_a01`, `.office`, `.pharmacy_a01` and the twelve
  Empties; the export closes. 9231's planner had dressed a pharmacy the
  site never placed; 0.176.1's one function (`preferred_for_brief`) is read
  by all four draws, and the package is the proof.
- **The pair rules said nothing** (`S_ADJACENCY`: no line in any candidate's
  or the themed site's audit). A deli, a pharmacy and an office on one
  block fit the guide's matrix without a rule to quote, and a plain fit
  says nothing by design; 9231's station lot drew three `P17 prefer` lines.
  The quiet audit is the template's point.
- **The targets spoke** (`S_TARGETS`, Lot 0.112.0, every line INFO, in the
  themed site audit): `3 enterable building(s), inside the guide's starting
  3 to 8; 22 Empties stand beside them`; `ordinary fabric 96% of 25
  building instances, the objective the one hero, above the guide's 50% to
  75%: the terrace outnumbers the level's buildings`; `2 road end(s) reach
  the plate's edge and 2 distinct first hop(s) reach the objective from the
  spawn across the site graph; the guide asks 2 meaningful approaches`;
  `0 loop(s) in the road graph over 1 junction(s): the way back is the way
  in, and the guide prefers a return loop`; `spawn->objective: 99 m as the
  crow flies, the longest stretch between focal points 55 m against the
  guide's 20 to 50 m traveled ... wants a corner, a threshold or a landmark
  view` (and the same for the way back); `1 parking field(s) with 6
  bay(s), 1 driveway(s) and 3 yard(s) with a dumpster for 3 building(s)`.
  The loop and the focal stretch are what roadmap 230 step 3 and 199 are
  for (`docs/findings/rear_lane/`).

## Roadmap 229: the rows over the aisles, and the hideout

- The deli's generate log: `17 row(s) laid to the work, 1 room(s) over
  their aisles` (9231, on 0.206.1: `17 row(s) laid to the work`).
- The merged lights (`site.site.lights.json`): `b0/market_aisles_ceiling`,
  `_r1`, `_r2` at x -56.2, -50.6 and -46.2 in the world, the deli standing
  at -51 -- that is -5.2, +0.4 and +4.8 off its centre, the three lanes
  between the preset's authored aisle shelves (at -2.0 and 2.5, 1 m
  deep), four lamps each; 0.206.1 laid them at -5.6, -0.4 and 4.4 across
  the room. `b0/apartment_hideout_ceiling` is one fixture (9229: three
  rows). Site-wide 41 rows and 161 lamps (9231: 42 and 163; 9229: 44 and
  174).

## Seen

`rooms_before_after.png`: the deli's four largest rooms from the same room
stations (`tools/room_stations.py`, derived in each workspace: the deli
stands at x -58 in 9229 and -51 here), 9229's package (Deli Counter
0.206.0) on the left and 9232's (0.207.0, 0.206.1) on the right, the
ceiling in frame.
- **The market aisles:** three rows in both, running away from the camera
  with the gondolas dark on either side. 9232's rows stand on the three
  lanes' centres by construction (-5.2, +0.4, +4.8 off the room's centre)
  where 9229's grid stood at -5.6, -0.4, +4.4 and missed the authored
  gondolas by luck: a 0.4 to 0.8 m shift the frame barely shows. The rule
  earns its keep in the rooms where a grid crossed a run -- the
  warehouses' racks, the stockrooms' wall runs, 15 rooms in the library --
  none of which this level has in frame.
- **The hideout:** one fixture over the room's middle where 9229 hung
  three rows of four, and the 21 x 16 m room reads dark at both ends,
  lit like a bedsit. The home rule's "one fixture whatever the size" is
  right for a flat and wrong for a hideout the size of a hall. **For the
  walker's eye, and a refinement to queue:** a home's room takes its
  fixtures by area (a ceiling dome a room, as homes have, one per 30 to
  40 m2) or bulbs, rather than one.
- **The manager's office and the server room:** unchanged, as the rule
  says: no shelves, and the cap's trade not binding differently.

The three rows across the office's ceiling, on the tile grid, read as
9229's did; whether that is the density a 12 x 11 m room wants is still
the walker's call from 9229's record.

## What this run does not prove

The price of 0.207.0's rows (fewer lamps than 0.206.1 site-wide, so
cheaper, but not measured at stations here); the route completion's drop
from 1.00 to 0.92 on the templated lot; the look of a template whose
families the library lacks (said rather than drawn by 0.176.0; not
exercised); the long hall's trade, which this lot has no room for.

## Instruments

- `room_frames.sh`: the deli's four largest rooms from
  `tools/room_stations.py` in each workspace, shot in 9229's and 9232's
  packages, the sheet `rooms_before_after.png`.
