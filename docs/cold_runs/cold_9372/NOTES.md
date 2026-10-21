# Cold run 9372 -- 0 interventions; restaurant_row_001, seed 9003: Level Factory 0.229.0, the sightline advisory's eye

**What it was for.** The factory's roadmap 289: Level Factory's sightline advisory sighted from a stale 1.4 m eye and
crossed at 1.2 m where Laser Tag, Lot and the agent contract cross at 1.3. Level Factory 0.229.0 (1f6f047) sights from
1.6 and holds its heights to the evaluator's with the check Lot's copies answer to. Cold run 9371's level again, staged
from it, Level Factory the only tool that moved.

**Tools** (`before.json`, every repo clean at `--begin`): Level Factory 0.229.0 (1f6f047); the rest as 9371 -- Deli
Counter 0.250.0, Zoo 1.120.1, Lot 0.126.0, Lux 0.79.0, Dispatch 0.5.3, Patina 0.32.0, Laser Tag 0.32.0, Pipeline 0.6.0,
Pixelcoat 0.62.0.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0); 8.6 min (11:24:55 to 11:33:29). Shell 0
blockers of 79 findings; art 108; **findings 108 -> 108 against 9371**, the same 108 by code, candidate and message
(`.level_factory/validation/restaurant_row_001.json` in each workspace). The export's bake: 153 models lightmapped,
2,948 users, as 9371.

**What it shows of the advisory.** The advisory ran in all three Laser Tag jobs of both runs -- the scheduler asks a
job's advisory at dispatch, a cache hit included -- and its spawn-placement half is in each validation record:
`LT_OPENING_STANDOFF` 3, `LT_STOREY_UNSEEN` 3, `LT_MARKER_OFF_FLOOR` 1. Its sightline half drew no
`LT_OPEN_SIGHTLINE` in either run, under 9371's 1.2 m crossing or 9372's 1.3 m one: no line in this level farther than
the 45 m opening range turns on a solid between the two. So the level cannot show the crossing's move, and the tests
are its proof (the factory's `patches/lf_sight_crossing/prove_tests_on_0228.out.txt`); this run shows that 0.229.0
leaves the pipeline at 0 interventions and its findings unmoved.

**Refuted, kept.** This note first said the advisory runs in a pre-flight a cold run does not reach. That was read off a
search of both workspaces for the advisory's codes which guessed two of their names (`LT_STANDOFF`, `LT_FLOATING`) and
found only Laser Tag's own scripts; the validation record, read for the codes the advisory actually writes, answers it.

**The walk copy** is `_runs/walk_9372_restaurant_row_001`.
