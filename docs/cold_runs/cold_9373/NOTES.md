# Cold run 9373 -- 0 interventions; restaurant_row_001, seed 9003: Level Factory 0.230.0, the advisory sights from the run's body

**What it was for.** The factory's roadmap 289, its second half. Level Factory 0.229.0 fixed the sightline advisory's
eye at Laser Tag's 1.6 m as a literal; 0.230.0 (16ba543) hands the advisory the heights the run's scenario carries --
Laser Tag's own, under the agent contract's body and the job's scenario -- through `_run_scenario`, the precedence
`run` writes, moved out of `run` unchanged. Cold run 9372's level again, staged from it, Level Factory the only tool
that moved.

**Tools** (`before.json`, every repo clean at `--begin`): Level Factory 0.230.0 (16ba543); the rest as 9372 -- Deli
Counter 0.250.0, Zoo 1.120.1, Lot 0.126.0, Lux 0.79.0, Dispatch 0.5.3, Patina 0.32.0, Laser Tag 0.32.0, Pipeline 0.6.0,
Pixelcoat 0.62.0.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0); 8.6 min (12:18:54 to 12:27:31). Art 108
findings, 0 blockers; **findings 108 -> 108 against 9372**. The export's bake: 153 models lightmapped, 2,948 users, as
9372.

**What it shows of 0.230.0** (`patches/lf_sight_contract/cold_compare.py` and its `.out.txt`, the factory's):

- **`run` writes the scenario it wrote.** Each of the three Laser Tag candidates' staged `mission_scenario.tres` is
  byte for byte 9372's -- 1,326 bytes, the contract's body in it (`player_eye_height_m` 1.6, `aim_height_m` 1.0,
  `enemy_eye_height_m` 1.6). A scenario is written only when the contract's body was read, so the advisory, which asks
  the same `_run_scenario` with the same context, sighted from that body.
- **The advisory says what it said.** The 108 findings are 9372's by code, candidate and message; the advisory's own,
  in every candidate as before: `LT_OPENING_STANDOFF` 3, `LT_STOREY_UNSEEN` 3, `LT_MARKER_OFF_FLOOR` 1, and no
  `LT_OPEN_SIGHTLINE`. With the contract's body equal to Laser Tag's stock, that is the outcome a correct 0.230.0 must
  give; what a different body does is proven by the tests (`patches/lf_sight_contract/prove_tests_on_0229.out.txt`).

**The walk copy** is `_runs/walk_9373_restaurant_row_001`.
