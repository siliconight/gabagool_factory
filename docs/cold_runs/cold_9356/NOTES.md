# Cold run 9356 -- 0 interventions; restaurant_row_001, seed 9205: the level install test 10 could not ship

**What it was for.** Install test 10, certifying factory 1.41.0, made the first level with its seed left to the pick;
the pick took seed 9205, whose lot stands a parking garage, and the export stopped at Level Factory's drop-edge gate
on 33 edges round the garage's ramp -- its slab cut ran half a run past the ramp's head
(`docs/findings/ramp_cut_241/`). Deli Counter 0.241.0 stops the cut at the head, rails it, and keeps a landing past
it. This run made THAT level: the first level's own brief (`docs/first_level/briefs/restaurant_row_001.json`, copied
byte for byte -- it leaves `road_grammar` and `cluster` to their defaults, where the cold runs' brief names `block`
and `auto`, so the cold runs' brief at the same seed draws another lot) at seed 9205.

**Tools:** Deli Counter 0.241.0 (35d88455), Level Factory 0.226.2 (44d3b2d), Zoo 1.117.0 (48fdc71), Lot 0.126.0
(49dcf8d), Lux 0.79.0 (9132d32), Dispatch 0.5.3, Patina 0.32.0, Laser Tag 0.32.0, Pipeline 0.6.0, Pixelcoat 0.62.0 --
the set factory 1.41.0 certifies. Staged from 9355, its brief replaced as above; seed 9205 named.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0), read after `cold_run.py --end`; 8.5 min.
Shell 0 blockers of 74 findings; art 0 of 105. The driver's "findings 108 -> 105" compares against 9355, which is
another level (seed 9003 under the cold runs' brief), and says nothing about this change.

**The package is the level that failed** (`workspaces/cold-9356-ws/`): its lot stands deli_a01, parking_garage and
supermarket_a01, seed 9205's, as install test 10's did.

| the export, seed 9205 | install test 10 (Deli Counter 0.240.0) | cold run 9356 (0.241.0) |
|---|---:|---:|
| unguarded drop edges | 54 | 13 |
| ... UNDECLARED indoors, the class the gate refuses | **33** | **0** |
| ... a thing's top (reported) | 9 | 1 |
| ... a flight's own side / a ladder's shaft / outdoors | 2 / 6 / 4 | 2 / 6 / 4 |
| standable cells reached | 54,284 of 75,244 | 54,282 of 75,296 |
| enterable buildings' slots merged | 865 | 868 |
| surfaces / merged meshes | 1,584 / 778 | 1,587 / 781 |
| lightmap users | 2,772 | 2,775 |
| the export | **STOPPED** (exit 5) | shipped; closure ok, 0 greybox |

Every row that moved is the ramp's: the 33 refused edges gone, 8 of the 9 reported "thing's top" edges with them (the
ramp's sides and top end where they stood beside the overshoot), and three slots, surfaces, merged meshes and
lightmap users more -- the cut's three rails, `stair_guard_rail_7` to `_9` in the garage's built slots, painted steel,
the two long ones 5.0 m and the entry one 3.6 m, standing on the first floor. The rest of the level is install test
10's: the reach within 2 cells, the standable count by 52 cells -- the rails' footprint and the floor past the head
the cut no longer takes.

Not shot: frames of the rails. The walk copy is `_runs/walk_export_restaurant_row_001/`; the garage stands at plan
(59, -1), and its ramp climbs 10 m north from plan (72, -6) to (72, 4), the cut over its last 5 m.
