# A stairwell that bakes on one grid in four

**Status, 2026-10-06: the gate and the walk test shipped; seven shells are
frozen, not fixed.** Found while closing cold run 9185. Roadmap item 189.
- **Deli Counter 0.189.0:** the nav gate bakes each shell again at eight
  grid origins. A grid-fragile shell becomes not navigable, so Level Factory
  stops drawing it into themed lots.
- **deli_a03's stair door** widens to 2.4 m and connects at 8 of 8.
- **Lot 0.97.2:** the walk test decides ladder access from the anchor's
  column, not from Godot's fallback.
- The census, the second neck finder and the open list are below.

## What was seen

Cold run 9185 (restaurant_row_001, 9179's brief) dropped two of its three
candidates, seed_9003 and seed_9205, for `walktest not ok`. Both stand
deli_a03, and both fail on one anchor: `proxy_2`, deli_a03's `OBJECTIVE_A`,
upstairs in the apartment hideout.

The same anchor was off the main network in 9179 as well, in the two
candidates that stood deli_a03 there. 9179 passed it.

| run / seed | proxy_2 cluster | `home->proxy_2` | Godot path errors in the job log |
|---|---|---|---|
| 9179 / 9003 | 1 of 12 | ok: "walkable to (-54.7, 0.3, 9.4); 3.3 m VERTICAL access" | 0 |
| 9179 / 9205 | 1 of 12 | ok: "walkable to (-44.7, 0.3, 7.4); 3.3 m VERTICAL access" | 7 |
| 9185 / 9003 | 1 of 12 | FAIL: "path stops 60.99 m short (disjoint islands): ends (-8.6, 0.2, -28.1)" | 10 |
| 9185 / 9205 | 1 of 11 | FAIL: "path stops 43.61 m short: ends (-9.9, 0.3, 20.1)" | 9 |

Frames: Godot world, Y up, metres. Anchors are snapped standing points.

## Two things, measured separately

### 1. The walk test's verdict came from an engine error, not from geometry

`nav_qa_director.gd` (Lot) `_prove_path` asks `map_get_path` for a route to
the anchor.
- When the target is unreachable, Godot returns a path to the nearest point
  it could reach.
- If that point is within 1.5 x `SNAP_MAX` horizontally of the anchor and
  more than 1 m below or above it, the leg passes as "VERTICAL access
  (ladder/drop)".
- Otherwise it fails as "disjoint islands".

In both 9185 failures the job log shows Godot's own internal error on the
call immediately before the FAIL line:

    ERROR: It's not expect to not find the most reachable polygons
       at: _query_task_build_path_corridor (modules/navigation_3d/3d/nav_mesh_queries_3d.cpp:404)
       [0] _prove_path (res://addons/heist_nav_qa/nav_qa_director.gd:724)

- The path that came back stopped near the start: 2.9 m from home in
  seed_9003, and 4.2 m in seed_9205.
- `proxy_1->proxy_2`, the same unreachable target, ended under the anchor
  and passed in both.
- **The verdict on one anchor in one navmesh therefore depends on the start
  point, and on whether Godot's fallback succeeds.**
- The census in the same report already called the anchor stranded in all
  four runs (`stranded_anchors: 1`), and `ok` does not read the census.

### 2. The anchor is off the network because of a stairwell

**`bake_modes`** (`run_bake_modes.py`, output `bake_modes_base.txt`) bakes
the imported deli_a03 alone with the site's navmesh settings: cell 0.1,
height 0.15, radius 0.4, climb 0.15, slope 55.

| parsed geometry | upper floor and objective with the kitchen? |
|---|---|
| meshes only | no. The stair ramps are collision-only, so no stair bakes. |
| colliders only | yes, one island of 1,212 polygons |
| both (what the site bakes) | yes, one island of 1,209 polygons |

**`bake_sweep`, the site** (`run_bake_sweep.py ... res://site.tscn`, output
`sweep_site9003.txt`) bakes seed_9003's whole site the same way. It
reproduces the walk test's own count, **4,254 polygons**, so the instrument
is seeing what the walk test saw.

| point | island |
|---|---|
| home, the deli's kitchen | 0 (3,377 polygons) |
| the stair's lower end, its upper end, the upper hall, the manager's office, `OBJECTIVE_A` | 21 (364 polygons) |

The stairwell, the stair and the whole upper floor are one island, cut off
from the street. The stair works. What fails is the stairwell's join to the
rest of the ground floor.

**`bake_sweep`, the building alone over 32 grid origins** (`sweep32.json`,
output `sweep_bldg.txt`) moves the bake's grid origin through
`filter_baking_aabb`:
- X by 0, 0.025, 0.05 and 0.075 m;
- Y by 0, 0.0375, 0.075 and 0.1125 m;
- Z by 0 and 0.05 m.

The geometry is identical every time.
- **The upper floor joins the kitchen in 8 of 32.** All 8 share the X
  offset 0.075.
- The Y and Z offsets change nothing.
- Where the deli lands in a site picks its grid origin, so the site decides.

**Where the join is** (`plot_two_offsets.py`,
`deli_a03_stairwell_two_offsets.png`, ground floor, X offsets 0 and 0.075):
- The stairwell's only walkable way in is `office_stair_door`: 1.25 m, the
  contract's `min_door_width_m`, in the wall `int_0_1` at local x -15.
- The other opening, a 1.4 m breach in `int_0_0`, is an intact panel.
- Through the door the walkable area narrows to a neck. It is pinched
  between the head of `deli_stair_down` (axis x -15.8) and the side of
  `deli_stair_up` (axis x -11.8).
- At X offset 0 the neck's polygons do not share an edge with the
  stairwell's, and at X offset 0.075 they do.
- Deli Counter's stairwell checks had already flagged both stairs as
  laterally open in this room (`nav_gate.txt`, `STAIR_LATERAL_OPEN`).

**Why Deli Counter's own gate passed it.** `deli_a03.navgate.json` reports
`objective_A` reachable. The gate bakes once, at the grid origin its own
bounds give it, and at that origin the join holds. My own unswept bake of
the building (`bake_modes`) joined too.

## Refuted, kept

**"The site outgrew Godot's 4,096-polygon path-search cap, so the fallback
stopped early."** 9185's failing seed_9003 baked 4,254 polygons. 9179's
passing seed_9003 baked 5,251, and its seed_9104 4,697. Polygon count does
not separate pass from fail.

**Three of this finding's own instruments were wrong first.** Each is kept
beside what replaced it.

1. **The first census's snap was too loose** (`census_loose_snap.txt`,
   `.json`).
   - It snapped a point up to 1.0 m above itself, within 1.0 m.
   - It called the four gas stations split at 1 of 8 origins. Their safe
     markers stand at z 0.5 to 0.6, and at seven origins they landed on the
     safe's own top, a six-vertex island.
   - Re-run with the gate's own rule (a marker at most 0.3 m and a climb
     above itself, within 2.0 m), 16 shells split (`census.txt`, `.json`).
     The gas stations are still among them, at 3 of 8. So "just a snap
     artifact" was only half right.
2. **The first neck finder measured walls** (`necks_closest_approach.txt`,
   `.json`).
   - It reported the closest approach between the two islands.
   - deli_a03 came out at 0.000 m, at its door: a true neck.
   - The others came out 0.4 to 2.1 m apart, beside windows and party walls:
     the thinnest wall between two rooms, not the neck.
   - Its replacement walks the route that exists at a passing origin, and
     reports where a failing origin breaks it. It is written and not yet run
     on the frozen seven.
3. **Lot's first fix was stricter than the rule it replaced**
   (`patches/patch_lot_vertical_access.py`, then `_column.py`).
   - It asked for the single point closest to the anchor's column, which is
     always the floor under the anchor's own foot.
   - On 9185's seed_9003 it failed `proxy_2 -> proxy_3`, a drop off the
     deli's upstairs edge 2.7 m out, which the old rule had passed.

## The census (`grid_census.py`, gate snap rule)

129 shells measured at 8 origins; 17 skipped for having fewer than two
points.
- **16 have a pair of points connected at some origins and not all.**
- deli_a03 is the positive control, at 4 of 8.
- **The gate (`nav_gate.py --all`, 144 shells) flags 8 of them.** It asks a
  narrower question: objective-type markers reached from a spawn, not every
  pair of floor markers. It also calls a marker its base bake cannot reach
  unreachable, not fragile.
- **The eight only the census flags** are cbp_town_finale_midbalanced_schemafixed,
  bank_job, gs_auto_shop, night_auto and the four gas stations. They are not
  yet classified.

## What it costs

- **The walk test is a coin toss on deli_a03.** It depends on the grid the
  site lands on, and then on Godot's fallback. Here the toss cost two
  candidates of three. A brief that draws deli_a03 into every candidate
  could lose them all, and that is an intervention.
- **Bots in a shipped level cannot reach the objective** when the stairwell
  did not bake. No exported package under `workspaces/` stands deli_a03
  (searched 2026-10-06). 9179 and 9185 both picked seed_9104, which has
  none.
- **The gate that should catch it bakes once.** Any shell whose
  connectivity runs through a neck this narrow is in the same state, and
  nothing measures how many there are.

## What shipped

**Deli Counter 0.189.0, the gate.**
- `nav_gate.gd` `_grid_sweep` bakes the same parsed geometry again at eight
  origins inside one cell, as fractions of the contract's cell.
- `nav_gate.py` makes a shell not navigable when a stair, or an interior
  marker the base bake reached, connects at only some of them. The exit
  code is unchanged.
- **Level Factory reads `navigable` for themed lots.** Measured with its own
  `themed_fitness`: 102 shells fit before, 101 after. twin_a01, the twin
  family's only shell, leaves; no brief names that family.

**The library run flagged eight.** Seven are frozen in
`navgate_baseline.json` `grid_fragile`:

| shell | what connects at only some origins |
|---|---|
| foundry_heist_vertical | stair_0, stair_1 |
| primos_pizza | stair_0; the safe and the stash (6/8) |
| twin_a01 | stair_1; objective_UPSTAIRS (7/8) |
| cr_deli, night_deli, corner_deli_heist_01 | objective_REGISTER (2/8) |
| fuel_stop_heist | objective_REGISTER (4/8) |

**deli_a03, fixed.** `office_stair_door` goes from 1.25 m to 2.4 m, on
x -14.5 (`deli_counter/specs/deli_a03.json`, with its reason on
`deli_stair_up`'s `meta` as `door_why`).
- Its west part still meets the basement flight's top.
- Its east part opens 0.5 m straight onto the strip beside the up-stair.
- **Gate:** objective_A at 8 of 8. **Census, baked as the site does:** 0
  split. Both hold again after the re-furnish moved one table 1 m.

**Lot 0.97.2, the walk test.**
- `_vertical_access` samples the anchor's column, nearest height first,
  inside the old concession's window, and accepts a surface a strict route
  reaches.
- On a copy of 9185's staged seed_9003 it passes, as 9179's did.
- `home` and `proxy_1` now agree.

## Where the rest break (`neck_finder.py --census census.json`, `necks.txt`)

The route-walking neck finder took 22 cases across the 16 split shells. They
come apart into two kinds.

**A real floor neck, located (the nearest colliders are in `necks.txt`):**

| shell | where the route tears at a failing origin |
|---|---|
| foundry_heist_vertical | a stair's discharge plate and landing against the north wall, at z 0.36 and z 7.05 |
| primos_pizza | the basement stair's discharge plate against the north wall and its breach panel |
| twin_a01 | between the top of `stair1` with its guard rail and `fridge_right_0` |
| cbp_town_finale_midbalanced_schemafixed | the 2.0 m `third_vomitory` door, whose west half stands inside the west wall |
| bank_job | a 1 m pocket between a crate stack and a desk, at a cover point |

**Not a floor neck: the route survives, the marker moves.** For cr_deli,
night_deli, corner_deli_heist_01, fuel_stop_heist, the four gas stations,
gs_auto_shop and night_auto:
- the passing origin's route stays on one island at the failing origin;
- what changes is the polygon the marker snaps to: a counter top or a pocket
  at some origins, the floor at others.
- So the split is marker placement, not connectivity.
- The gate re-snaps each marker at each origin. Testing the base bake's own
  standing point at every origin would report only floor fragility.

## Open

1. **Fix the located necks**, starting with twin_a01. It is the only one
   whose family lost its last fit shell: move the fridge off the stair top.
   Then foundry_heist_vertical's and primos_pizza's discharges, the
   vomitory door, and bank_job's pocket.
2. **The gate's marker sweep** should test the base bake's standing point,
   not a fresh snap. The register markers would then stop reading as
   fragile for where they snap.
3. **The register markers** stand inside their counters. Placing them on the
   floor beside the counter would end the question at the source.

## Files

- `bake_modes.gd`, `run_bake_modes.py`: one building, three parse modes.
  Points: `points_deli_a03.json`. Output: `bake_modes_base.txt` and `.json`.
- `bake_sweep.gd`, `run_bake_sweep.py`: one scene, optionally over a sweep
  of grid origins.
  - Points: `pts_bldg.json` (building frame) and `pts_site_9003.json`
    (seed_9003's world frame).
  - Sweeps: `sweep32.json` and `sweep2.json`.
  - Outputs: `sweep_bldg.txt`, `sweep_site9003.txt` and their `.json`.
- `plot_two_offsets.py`: draws the dump that `sweep2.json --dump` writes.
  The dump itself, 337 KB, is not kept.
- `grid_census.gd`, `grid_census.py`: every library shell at eight grid
  origins, with the gate's snap rule. Outputs: `census.txt` and `.json`.
  The superseded first run is `census_loose_snap.*`.
- `neck_finder.gd`, `neck_finder.py`: where a split connection breaks, by
  walking the passing origin's route at a failing origin. The superseded
  closest-approach output is `necks_closest_approach.*`.
- The project probed is cold run 9185's staged walk test for seed_9003:
  `workspaces/cold-9185-ws/.level_factory/staging/restaurant_row_001.walktest_navqa.candidate.seed_9003`.
  It is mirrored to a temp directory on every run (`tools/godot_probe.py`),
  so the original is never touched.
