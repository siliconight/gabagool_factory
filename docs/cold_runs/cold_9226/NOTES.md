# Cold run 9226 -- 0 interventions, 0 retries; the yards stand beyond the fence

warehouse_yard_001 (`industrial_warehouse`, a `yard` site), night and rain,
seed auto, staged from 9180's batch and brief. It proves roadmap 228's
`yards` recipe end to end: Level Factory 0.175.0 decided the surroundings
from the archetype (the brief names none: `surroundings_resolved: {asked:
"", got: "yards", known: true}`), Lot 0.109.0 laid them, Zoo 1.96.0's site
kit built the warehouse and the tower beside the cargo container, and Level
Factory 0.174.0 shipped them as MultiMeshes behind 9224's fence.

Tool versions hashed at `--begin` (`_runs/cold/cold_9226/before.json`):

| tool | version |
|---|---|
| Deli Counter | 0.205.0 |
| Dispatch | 0.5.2 |
| Laser Tag | 0.25.0 |
| Level Factory | 0.175.0 |
| Lot | 0.109.0 |
| Lux | 0.73.0 |
| Patina | 0.30.0 |
| Pipeline | 0.6.0 |
| Pixelcoat | 0.62.0 |
| Zoo | 1.96.0 |

Against 9225: Level Factory 0.174.0 to 0.175.0, Lot 0.108.0 to 0.109.0, Zoo
1.95.0 to 1.96.0.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0), **retries 0.**
- **Picked: seed_9105** on the walktest and Laser Tag's route findings (0
  major, route completion 1.00; 9004 and 9206 carried 1 major each).
- **The shell leg:** 0 blockers of 57. **The art leg:** 0 blockers of 80.
- **The bake:** 318 models and 996 primitive meshes, 47 steady rigs baked,
  14 failing left live, 56 room fills, 1,937 users, 70.0 s. The backdrop is
  not in it.

## The yards, laid, built and shipped

- **Lot** (`themed_site_assemble/1/job.log`): `LOT_PERIMETER_FENCED: 6
  run(s), 445.7 m` on the 105 x 100 m plate, and `LOT_BACKDROP_PLACED:
  recipe yards, 0 rowhome(s) in 3 bands a side (N 41, S 37, E 21, W 21), 5
  module(s), 1 water tower(s)`. The site's slot manifest counts 121
  `site_backdrop` slots: 97 `cargo_container`, 23 `backdrop_warehouse`, 1
  `water_tower`.
- **Zoo's site kit** built every module PASS: the container at 2.44 x 6.06
  x 2.59 m (x97), three warehouses at 24 x 16 x 7, 32 x 16 x 8 and 40 x 20
  x 9 m (x10, x8, x5), the tower at 14 x 14 x 40 m (x1).
- **Level Factory** (`export.log`): `[export] backdrop: site_backdrop.tscn
  -- 121 instances of 5 module(s) on their sides, 17 draw calls (N 0, S 0,
  E 0, W 0; 1 tower)`.
- **Two summary lines count rowhomes where they mean pieces.** Lot's says
  `0 rowhome(s)` of a recipe that lays none, and Level Factory's by-side
  count reads `N 0, S 0, E 0, W 0` beside its 121 instances; both read
  `summary["houses"]` / the rowhome tally rather than the pieces a side. The
  numbers that matter (121 instances, 17 draws, 5 modules) are right.
  Lot's and Level Factory's to fix; cosmetic.

## Seen

`edge_before_after.png`: the control is this package with the backdrop
scene not loaded (`tools/backdrop_off.py`), the subject the package as
shipped; the stations are the two road ends (`tools/edge_stations.py`,
`stations.txt`: the eye 45 m inside each edge on the road's centre line)
and look_shots' four elevated views. In heavy rain at night:
- **Down the road to the west edge** (`road0_a_W_edge_zoom.png`): where the
  control's road ends at the fence against the flat glow band, the
  subject's ends against low dark blocks, the stacked containers of the
  near band, with a warehouse's longer silhouette behind them.
- **To the east edge** (`road0_b_E_edge_zoom.png`): the same, and left of
  the plate's own box truck a pale low slab at the horizon, a warehouse's
  siding catching the glow; its lit high windows do not read at this
  distance through the rain.
- **From the elevated west camera** (`elev_W_zoom.png`): above the
  storefront's roofline a bright flat rectangle, (191, 191, 202), 180 x 40
  px at frame (113..291, 177..216): a container's top face in the near band,
  3 to 10 m past the fence, seen from above. The cargo container is one
  bevelled box on a near-white tintable, and its roof reads as a pale slab
  floating over the building from any elevated view. Behind it the
  warehouses stand as dark red-brown faces through the rain. **For the
  walker's eye:** whether the near band's container tops want a darker,
  dirtier roof (Zoo's `cargo_container`), or the near band wants to stand
  further off at a yard.

## Priced

`price/price.txt`, the package against its own backdrop-off copy through
`docs/findings/horizon_glow/price_glow.py` (control, subject, control; the
harness calls the subject `glow`): 45 headings a run.

| run | draws +mean | +min | +max | p95 +median ms | +max ms |
|---|---|---|---|---|---|
| control_1 | 0.0 | 0 | 0 | -0.04 | 0.18 |
| subject | 27.7 | 15 | 37 | -0.01 | 0.53 |
| control_2 | 0.0 | 0 | 0 | 0.04 | 0.22 |

The controls' spread is 0.12 ms p95 and 0 draws: the yards cost 28 draws a
heading and no frame time at the stations (p95 median 2.53 ms against the
controls' 2.62 and 2.61). The draws are the 17 backdrop MultiMeshes seen
from most headings plus the fence's.

## What this run does not prove

The look from a player's eye at the fence (the stations are 45 m in); the
yards by day; the other two recipes, which 9227 (parkland) and 9228
(roadside) prove.

## Instruments

- `tools/recipe_run_record.sh 9226 warehouse_yard_001` made the control
  copy, the stations, the frames, the sheet and the price (`record.log`).
- `stations.txt`: the derived stations. `price/`: the three perf reports.
- The frames: `_scratch/frames_9226/` (not tracked); the sheet and the
  three zooms here.
