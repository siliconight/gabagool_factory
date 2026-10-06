# Cold run 9185 -- 0 interventions; one name on the deli's band and door, and two candidates lost to a stairwell that bakes on one grid in four

The proof run for the walker's three calls of 2026-10-06:
- **Option A**, one name list on both of a building's signs: Level Factory
  0.148.0, Zoo 1.79.0, Pixelcoat 0.61.0.
- **The blended chain-link fabric:** Zoo 1.78.0, Pixelcoat 0.60.0.
- **The row's end fences meeting the perimeter:** Lot 0.97.1.

It is 9179's brief (restaurant_row_001, `corner_deli`, three buildings, the
lot library by default). The driver picked seed_9104, as in 9179, but the
library has grown since, so seed_9104 stands different buildings. The
candidates are not 9179's.

**Every leg ran, `INTERVENTIONS: 0`, and the package exported.**
- Findings were 65 in both 9179 and 9185, with a different mix, because the
  buildings differ.
- There were 0 blockers in either leg (45 and 65 findings).

## The draws

| candidate | buildings (besides the 12 Empty shells) | walktest |
|---|---|---|
| seed_9003 | deli_a03, depot_a01, self_storage_a01 | not ok |
| seed_9104 | deli_a01, office, rail_station_a02 | ok, picked |
| seed_9205 | deli_a03, parking_garage, supermarket_a01 | not ok |

## Option A: one name, on the band and over the door

Read from the art log, the fixtures jobs and the package
(`LF_restaurant_row_001.portable-godot/lot/<shell>/art/fixtures/`):

| building | band | fixtures `--sign-pack` | door face material |
|---|---|---|---|
| deli_a01 (b0) | `scrapple_sons_deli` | `sign_scrapple_sons_deli` | `M_SignBox_sign_scrapple_sons_deli_Face` |
| office | none | none | Zoo-named face (`M_SignBox_Face_..._37ba7b96_Face`) |
| rail_station_a02 | none | none | Zoo-named face (`M_SignBox_Face_..._fd16d292_Face`) |

- SCRAPPLE & SONS DELI is one of Zoo's four deli door names. The band and
  the door now come from one deal.
- The office and the rail station take no band (0.147.0's `NO_BAND` and
  family rules). Each shows one name, on its door box.
- FLAPPAHS in green is not tested here: this mission draws no gas station
  or convenience store.

## The fence

- **Six runs on the Empty row's front line** (Godot z 33.2): four 3 m gap
  closers, a 13.5 m west end and a 19.5 m east end.
- **The end runs stop on the perimeter.** The west run spans x -98.0 to
  -84.5 and the east run x 78.5 to 98.0, and `perim_W` and `perim_E` stand
  at -98 and 98.
- **The plate** is 196 x 100 m, smaller than 9179's 206 x 102 m. The
  buildings differ, so the two are not a like-for-like comparison. The
  check that matters is that no fence ends beyond a perimeter wall, and
  none does.
- **The fabric** `M_Skin_chain_link_delco_1997` is `alphaMode: BLEND` in all
  three fence models (`cover/prop_chain_link_fence_delco_1997_01_w{300,1350,1950}_...glb`).
  The posts and rails are `OPAQUE`.

## Two candidates out for one stairwell

Both lost candidates stand deli_a03. Both fail on the same anchor:
`proxy_2`, which is deli_a03's `OBJECTIVE_A` upstairs, in the apartment
hideout.

| run / seed | proxy_2 cluster | `home->proxy_2` | Godot path errors in the log |
|---|---|---|---|
| 9179 / 9003 | 1 of 12 | ok, "VERTICAL access" | 0 |
| 9179 / 9205 | 1 of 12 | ok, "VERTICAL access" | 7 |
| 9185 / 9003 | 1 of 12 | FAIL, path stops 60.99 m short | 10 |
| 9185 / 9205 | 1 of 11 | FAIL, path stops 43.61 m short | 9 |

**The anchor was off the main network in all four.** 9179 passed it, and
9185 did not. The full account, with the instruments, is
`docs/findings/stairwell_on_one_grid_in_four/`. In short:

1. **The walk test's verdict came from an engine error, not from geometry.**
   - When a target is unreachable, `_prove_path` passes the leg as ladder
     access if Godot's fallback path happens to end directly under the
     anchor.
   - In 9185 that fallback hit Godot's internal error, "It's not expect to
     not find the most reachable polygons" (`nav_mesh_queries_3d.cpp:404`),
     on the very call before each FAIL.
   - The paths it returned stopped 2.9 m (seed_9003) and 4.2 m (seed_9205)
     from home.
   - `proxy_1->proxy_2`, the same target, still ended under the anchor and
     passed.
2. **The anchor is off the network because of a stairwell, not a ladder.**
   - Bake deli_a03 alone and its upper floor joins the ground floor at
     only 8 of 32 voxel-grid offsets, and all 8 share one X offset. The Y
     and Z offsets change nothing.
   - The stairwell's only walkable way in is the 1.25 m `office_stair_door`.
     The door opens into a neck pinched between the head of the basement
     stair and the side of the up-stair.
   - Deli Counter's own nav gate bakes at one offset, and that offset
     connected.
   - A probe that bakes the whole of seed_9003's site reproduces the walk
     test's 4,254 polygons. In it the stairwell, the stair and the whole
     upper floor are one island of 364 polygons, cut off from the street.
3. **Refuted, kept:** that the site had outgrown Godot's 4,096-polygon
   path-search cap. 9179's seed_9003 baked 5,251 polygons and passed.
   9185's baked 4,254 and failed.

The picked candidate was clean, so this cost nothing here. It is still a
generator defect:
- The walk test's verdict on deli_a03 is decided by where the building
  lands on the voxel grid, and by whether an engine fallback succeeds.
- A brief that draws deli_a03 into every candidate could lose them all.
- Bots in a shipped level where the stairwell did not bake cannot reach the
  objective.

## Everything else

- **`ZOO_PARTIAL_BUILD`:** one module, as in 9179 and in 9132.
  - `prop_flat_top_grill_delco_1997_04_w120_d90_h105_mmetal` builds 0.935 m
    deep against an exact 0.900 m (`fit_depth`). Every other check passes.
  - The resolver falls back to base for it.
- **Bake:** 485 models and 1,478 primitives lightmapped, 6 kept dynamic. 118
  steady rigs baked and 31 failing left live. 4,313 users, 86.4 s. (9179:
  485, 1,594, 8, 112, 28, 4,556, 91.5 s.)
