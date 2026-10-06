# Cold run 9186 -- 0 interventions; deli_a03 back and walkable to its objective, and a stair-head ledge in every stair

The proof run for Deli Counter 0.189.0 (the nav gate's grid sweep, deli_a03's
2.4 m stair door) and Lot 0.97.2 (the walk test decides ladder access from
the anchor). It is 9185's brief, restaurant_row_001.

**Every leg ran, `INTERVENTIONS: 0`, and the package exported.**
- Findings went from 65 to 67 against 9185, and 0 blockers in either leg
  (47 and 67).
- The lot grades **101 of 127** shells fit for a theme, where 9185 graded
  102. twin_a01 left, on the sweep.
- The deli's band and door box still name one business:
  `scrapple_sons_deli`.

## The walk test, against 9185

| candidate | buildings | 9185 walk test | 9186 walk test |
|---|---|---|---|
| seed_9003 | deli_a03, marina_a03, country_club_a02 | -- (9185 drew others) | ok, 0 stranded |
| seed_9104 | deli_a01, rail_station_a03, casino_a02 | ok | ok, 0 stranded, **picked** |
| seed_9205 | deli_a03, auto_shop_a01, ... | -- (9185 drew others) | ok, 0 stranded |

- **Both deli_a03 candidates pass.** In 9185 both were dropped, on
  "walktest not ok".
- Its upstairs objective is on the main network: cluster 13 of 13, reached by
  stairs. It is no longer passed as "VERTICAL access".
- Godot's internal path error ("It's not expect to not find the most
  reachable polygons") fired 0 times in either deli_a03 log, against 10 and
  9 in 9185. Nothing asked for an unreachable target.
- `WALKTEST_ANCHOR_ISOLATED` went from 2 to 0.

## What the fix exposed: a ledge at the head of every stair

seed_9003 went out on Laser Tag's `LT_ROUTE_NEVER_COMPLETED`.
- Its bots walked 70% of the route and finished 0 of 25 runs.
- Players stuck 3,148 times, every one in a single 2 m cell: deli_a03's
  upper landing at the head of its up-stair, local (-12, 3.3, -6.99).
- The route goes up to the objective and has to come back down.

**Measured** (`docs/findings/stairwell_on_one_grid_in_four/`,
`ramp_ridge_census.py` and `stair_head_walk.gd`):
- **The library census:** every one of the library's 174 stair collision
  ramps, in 98 shells, tops out 0.19 to 0.21 m above the floor it delivers
  to.
  - That is the half-step-proud offset that makes a ramp ride the nosings,
    plus half the slab's thickness through the tilt.
  - Deli Counter's foot fix of 2026-07-21 handled the bottom and said, in
    its own words, that it left the head untouched.
- **The walk:** a capsule of Laser Tag's size (r 0.35, h 1.8, no step-up)
  on deli_a03's up-stair.
  - As built: **down stuck on the landing for the full 8 s**; up arrived.
  - Ramp lowered one riser (the control): down in 2.4 s, up in 3.8 s.
- **Two instruments missed it.** Going up, the ledge is a drop. The navmesh
  climbs 0.15 m and Lot's walkers step 0.5 m, so neither saw it.

**Refuted first, kept:** sinking every ramp by the overshoot
(`ramp_head_drop`, `patches/patch_dc_ramp_head.py`).
- It read 0.000 on the census and walked both ways.
- Then the swept gate failed stair traversal on **94 of 144** shells. The
  ramp ran a riser under the nosings, so every visual tread stood above it,
  and the bake reads visual meshes.
- The census and the walk measured collision only.
- The first version of these notes named the sink as the fix.

**The fix is Deli Counter 0.190.0's `stairwell.ramp_head_trim`.**
- It cuts each ramp's head back along the incline by
  `overshoot / sin(pitch)`. The top corner lands on the landing at the top
  tread's front edge, and the foot and the nosing line stay where they were.
- Rebuilt: 0 of 174 ramps stand over their landing. The capsule goes down in
  2.4 s and up in 3.8 s, and the swept gate traverses every stair in 144 of
  144 shells.
- The same release draws no flight narrower than a corridor
  (`presets.STAIR_FLIGHT_WIDTH`, 1.2 m). That brings twin_a01 back to 8 of 8
  grid origins and the themed pool back to 102.

## Everything else

- seed_9205 went out because Laser Tag refused its map: "Enemy_5 could not
  path to the player spawn" (`LT_MAP_UNREACHABLE_SPAWN`, `LT_NOT_EVALUATED`).
  Not looked into.
- **Bake:** 502 models and 1,638 primitives lightmapped. 4,807 users, 138.3 s.
