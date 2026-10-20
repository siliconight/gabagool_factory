# Cold run 9345 -- 0 interventions; urban_row_001, seed 9003: a level the hole rate leaves without one

**What it was for.** Roadmap 269's lot path, end to end. The walker, 2026-10-20: "stairs and ladders should be the
primary way to get between floors in this game...with the holes in floors being somewhat rare". Level Factory 0.221.0
decides per candidate whether a level carries a hole in a floor (`building_library.holes_wanted`, rate 0.25) and swaps
a drawn family's variant to match (`apply_hole_rule`, through `draw_lot` for the planner, the compose spec and the site
spec alike); Deli Counter 0.237.0 gave the deli family a variant without the drop (deli_a01). Before them every
urban_row_001 level placed a deli with the 2.2 m cut drop (`docs/findings/hole_frequency/`). All three of this run's
candidates are levels the rate leaves without one.

**Tools:** Level Factory 0.221.0 (2706673), Deli Counter 0.237.0 (1b9650ad), Zoo 1.114.1, Lot 0.125.0, Lux 0.78.0.
Staged from 9336; seed 9003 named.

**Predicted before it finished** (`docs/findings/hole_frequency/predict_9345_9346.out.txt`), and as it ran:

| candidate | `pick_lot` drew | the level places (predicted) | the driver's lot |
|---|---|---|---|
| seed_9003 | deli_a03, pharmacy_a01, office | deli_a01, pharmacy_a01, office | deli_a01, office, pharmacy_a01 |
| seed_9104 | deli_a01, pharmacy_a01, office | deli_a01, pharmacy_a01, office | deli_a01, office, pharmacy_a01 |
| seed_9205 | deli_a03, pharmacy_a02, office | deli_a01, pharmacy_a02, office | deli_a01, office, pharmacy_a02 |

9336 placed the drawn lots: deli_a03 on 9003 and 9205. Every stage of this run agreed on the swapped one -- the
compose spec dressed the buildings the site placed and the export's closure held.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0), read after `cold_run.py --end`.
- **Shell:** 3 candidates, all distinct -- 9003 and 9104 now place the same three buildings, and still differ in
  placement and their Empties; 0 blockers of 72 findings (9336: 76).
- **Art:** 0 blockers of 100 findings (9336: 107, on its pick 9104; this run's is the named 9003). Not attributed by
  code: 9336's workspace is retired, so the drive's own findings diff read every code as new.
- **Export:** exit 0; greybox 0 surfaces; **drop edges: 0 at a declared drop**, 0 undeclared indoors -- the deli's
  hole is not in the level; the light bake 349 models, 3,244 users.

## What it proves, and what it does not

- The lot path: a level left without a hole places the family's variant without one, and the four draws agree.
- Not the rate: three candidates is not a sample. The rate is pinned by Level Factory's
  `tests/unit/test_floor_holes.py` and measured by the replay (`hole_frequency_after.out.txt`).
- Not the look: no frames were shot; the level is the deli without its drop, as on 9336's seed 9104.
