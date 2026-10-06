# A stairwell that bakes on one grid in four

**Status, 2026-10-06: measured, not fixed.** Found while closing cold run
9185. Roadmap item 189.

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

## Open

1. **How many shells?** A census of every library shell at several grid
   origins: does each marker and stair keep its island at all of them?
2. **The source fix.** It depends on the census. Two candidates:
   - a door is never placed where a stair head pinches its landing;
   - Deli Counter's gate requires connectivity at every origin.
3. **The walk test.** Its ladder-access pass reads Godot's fallback
   endpoint, and that endpoint is not stable. The pass should be decided
   from the geometry the test can see, the same from any start. It should
   also say when the engine errored.

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
- The project probed is cold run 9185's staged walk test for seed_9003:
  `workspaces/cold-9185-ws/.level_factory/staging/restaurant_row_001.walktest_navqa.candidate.seed_9003`.
  It is mirrored to a temp directory on every run (`tools/godot_probe.py`),
  so the original is never touched.
