# Cold run 9346 -- 0 interventions; deli_001, seed 9191: the mission's own deli built without its holes

**What it was for.** Roadmap 269's single-building path, end to end. A one-building mission builds its own building
from Deli Counter's preset per candidate, and before Level Factory 0.221.0 every deli_001 level carried the
corner_deli preset's cut drop and floor hatch (`docs/findings/hole_frequency/`). Now each candidate asks
`building_library.holes_wanted` -- the lot rule's question, of the same candidate id -- and a level left without one
is built `new_level.py --holes off` (Deli Counter 0.237.0: `presets.make(holes=False)`, `hole_causes.without_holes`).
Predicted before it finished (`predict_9345_9346.out.txt`): all three of seed base 9191's candidates are left without.

**Tools:** Level Factory 0.221.0, Deli Counter 0.237.0, Zoo 1.114.1, Lot 0.125.0, Lux 0.78.0. Staged from 9330; seed
9191 named.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0), read after `cold_run.py --end`.

**Each candidate's Deli Counter job, off its own job log and built record:**

| candidate | the command | the built shell's vertical links | holes a player sees |
|---|---|---|---|
| seed_9191 | `--preset corner_deli --seed 9191 --holes off` | the stair | none |
| seed_9292 | `--preset corner_deli --seed 9292 --holes off` | the stair | none |
| seed_9393 | `--preset corner_deli --seed 9393 --holes off` | the stair | none |

The preset's floor hole (`vertical_attack_angle`, 2.2 m from the apartment hideout into the kitchen) and its hatch
(`roof_drop_to_stair`) are gone from every candidate, and with them the slab hole the recipe authors under the drop.

**Against 9330** (this brief on 2026-10-19's breadth sweep, the drops in; it picked 9292, this run names 9191):

| | 9330 | 9346 |
|---|---|---|
| drop edges at a declared drop | 28 | **0** |
| undeclared drop edges indoors | 0 | 0 |
| drop edges at a thing's top | 11 | 8 (not attributed: another candidate) |
| shell findings, blockers | 69, 0 | 69, 0 |
| art findings, blockers | 93, 0 | 92, 0 |
| light bake users | 1,643 | 1,633 |

Greybox 0 surfaces; export exit 0.

## What it proves, and what it does not

- The single-building path: the decision reaches Deli Counter as `--holes off`, and the shell is built without the
  holes and the slab hole under the drop -- no undeclared drop left behind.
- Not a level that keeps its holes on this path: none of these three candidates wanted one. Deli Counter's
  `test_optional_holes.py` builds each of the five presets both ways.
- Not the look: no frames were shot.
