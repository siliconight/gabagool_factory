# Cold run 9189 -- 0 interventions; deli_a01's upper storey reaches the street in a level

The measurement run for three Deli Counter releases, on 9188's brief
(restaurant_row_001):
- **0.194.0:** deli_a01's server room gets a door (the walker's call), and
  L24 names every room only a breach reaches.
- **0.195.0:** the seeder leaves `min_corridor_width` round every piece.
  35 seeded pieces moved and 7 dropped in 13 shells, among them deli_a01's
  two stairwell crate stacks.
- **0.196.0:** the nav gate asks whether an entrance reaches each stair.

**Every leg ran, `INTERVENTIONS: 0`, and the package exported.**
- **Findings: 64, the same as 9188.**
- **The draw is 9188's.** seed_9104 was picked again on the walk test and
  Laser Tag's route findings, as the brief predicted.
- **Bake:** 4,308 users (9188: 4,310), 97 s.
- **Export closure:** ok, 0 issues over 79 resources, 2,962 files.

## deli_a01, in the level

Baked as 9188's was: the walk-test scene of seed_9104, `run_bake_sweep`, the
same settings and home point
(`docs/findings/deli_a01_upper_storey_9188/`).

| | 9188 | 9189 |
|---|---|---|
| islands | 165 | **161** |
| deli_a01's islands of its own | upper storey 592 m2, server room 186 m2, roof 957 m2 | **roof 957 m2 only** |
| the street's island over deli_a01 | basement and ground floor | basement 783, ground 672, **stair and upper storey 759** m2 |
| the street's island, whole site | 16,944 m2 | **17,728 m2** |

**The prediction was met.** The swap-and-bake on 9188's staging read the
same 161 islands and the same deli_a01 areas.

**A bad bake, discarded and kept.** The first bake of this run's walk-test
site came back with no building in it. It ran three minutes into the art
leg, and read 1,643 polygons and 72 islands, heights -0.5 to 6.6 m: no
basement and no roof anywhere.
- The same command, run twice more about 20 minutes later, read 4,362
  polygons and 161 islands.
- So did a run that kept Godot's own output. Its one warning, about parsing
  meshes at runtime, also appears in 9188's.
- It was not reproduced, and the cause is not established. **A bake's
  bounds belong in its reading:** one without basements or roofs is not the
  level.

## Laser Tag

- **seed_9003 and seed_9205:** identical to 9188 in every field read
  (grade, score, completion, progress, stuck, deaths, timeouts).
- **seed_9104:** PASS_WITH_TUNING 79 and completion 1.0, as 9188. **Player
  stuck events went 4 -> 9.** Every other event count is identical: 199
  route progress, 375 shots blocked, 150 enemies killed, 25 objectives
  reached. The five new events:
  - are all LT_Player_04, and all inside deli_a01;
  - four are at building (-15.3, -7.5), the ground floor 0.3 m from the
    front register counter, at t 52-56 s in runs 3, 7, 8 and 10;
  - one is in the basement at (3.8, 4.2), beside a counting table, at t 40
    in run 22.
- **No piece near either spot moved** between the two shells.
- **Not established: why.** The report carries a position and a source,
  not a goal. What changed near those spots is that the upper storey is now
  reachable.

## Deli Counter's gates, at the release before the run

- **The entrance check:** 148 of the library's 149 judged stairs are reached
  from an entrance. primos_pizza is frozen (roadmap 189's discharge neck).
- **L24:** 15 rooms frozen for the walker's call.
