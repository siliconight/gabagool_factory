# Cold run 9230 -- 0 interventions, 0 retries; the parkland again, with trees that have a silhouette

county_hospital_001 (`county_hospital`, a `campus` site), night and rain,
seed auto, staged from 9227's batch and brief: the level 9227 built, rebuilt
on the landed set. It shows roadmap 228's step F in a level after the
walker's verdict on 9227 ("those trees in the distance are a little lazy
imo (giant lolipops vs. trees)"): Zoo 1.97.0's tree, a flaring trunk that
forks into three limbs under ten overlapping lobes in three forms by the
slot's proportions, and Lot 0.110.0's belt in clusters of mixed forms, 6 m
off the fence. Deli Counter 0.206.0's rows and Lux 0.74.0's one failing
tube a room are in the set too and show in the bake line.

Tool versions hashed at `--begin` (`_runs/cold/cold_9230/before.json`): the
set 9229 ran on -- Deli Counter 0.206.0, Dispatch 0.5.2, Laser Tag 0.25.0,
Level Factory 0.175.1, Lot 0.110.0, Lux 0.74.0, Patina 0.30.0, Pipeline
0.6.0, Pixelcoat 0.62.0, Zoo 1.97.0. Against 9227: Deli Counter 0.205.0 to
0.206.0, Level Factory 0.175.0 to 0.175.1, Lot 0.109.0 to 0.110.0, Lux
0.73.0 to 0.74.0, Zoo 1.96.0 to 1.97.0.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0), **retries 0.**
- **Picked: seed_9107,** the seed 9227 picked: the same hospital on the
  same lines, so the comparisons below are of one level.
- **The shell leg:** 0 blockers of 51. **The art leg:** 0 blockers of 67.
- **The bake:** 115 models and 776 primitive meshes, **98 steady rigs baked
  where 9227 baked 44** (Deli Counter 0.206.0's rows, roadmap 229), **12
  failing left live where 9227 left 24** (Lux 0.74.0's one tube a room,
  across the rows), 119 room fills, 1,722 users, 48.0 s (9227: 49.8). The
  backdrop is not in it.

## The trees, laid, built and shipped

- **Lot** (`themed_site_assemble/1/job.log`): `LOT_PERIMETER_FENCED: 4
  run(s), 367.7 m` as 9227, and `LOT_BACKDROP_PLACED: recipe parkland, 185
  piece(s) (backdrop_tree 185) by side (N 58, S 56, E 36, W 35), 6 module(s),
  0 water tower(s)` -- 0.109.1's line counting pieces, and **185 trees in
  clusters where 9227 laid 273 in ranks**, six dims two a form: oaks at 8 x
  8 x 8 (37) and 11 x 11 x 12 (27), maples at 5 x 5 x 7 (27) and 7 x 7 x 10
  (32), elms at 4 x 4 x 9 (24) and 6 x 6 x 13 (38).
- **Zoo's site kit** built all six modules PASS.
- **Level Factory** (`export.log`): `[export] backdrop: site_backdrop.tscn
  -- 185 instances of 6 module(s) on their sides, 24 draw calls` (9227: 273
  of 3, 12 draws): twice the modules, twice the MultiMeshes, two thirds the
  trees.

## Seen

`edge_before_after.png`: the control is this package with the backdrop
scene not loaded (`tools/backdrop_off.py`), the subject the package as
shipped; the stations are 9227's three road ends (`stations.txt`) and
look_shots' four elevated views, so the sheet is 9227's sheet of the same
level with the new trees. In heavy rain at night:
- **The crowns have a shape.** Down road 0 to the east edge (`road0_b_E`)
  the road ends under trees that fork: a trunk, two or three limbs, lobes
  at different heights, the tallest at the right of the frame with the glow
  showing between its limbs, where 9227's ended under a line of balls on
  sticks. Up road 1 (`road1_b_N`) a cluster of crowns past the gate, no two
  the same height. To the west edge (`road0_a_W`) the belt is behind the
  clinic's own trees, as in 9227.
- **From the elevated views the belt is a wood in clumps, not ranks.** From
  the north (`elev_N`) a cluster of five: a broad oak-form crown in the
  middle twice the height of its neighbours, two maple forms at the right
  with the fork in view, two small at the left; the fence and the glow band
  show between the clusters where 9227's ranks closed the whole edge. From
  the south (`elev_S`) the densest stretch: overlapping crowns, flat broad
  ones against tall narrow ones, dark against the glow. From the west
  (`elev_W`) one mid-sized tree stands alone before the fence, a taller one
  at the right edge, a small one at the left.
- **For the walker's eye:** from the east (`elev_E`) one near crown still
  fills the foreground, the belt's inner edge at 6 m off the fence now (Lot
  0.110.0's `TREE_BELT`) where 9227's stood at 2.5, and up close its lobes
  read as a pile of faceted boulders rather than foliage. Two calls: whether
  the near band wants a minimum distance from an elevated station, and
  whether the lobes want the tree guides' method (alpha-tested cards on a
  sculpted trunk, step G) before the forms are made species.

## Priced

`price/price.txt`, the package against its own backdrop-off copy through
`docs/findings/horizon_glow/price_glow.py` (control, subject, control; the
harness calls the subject `glow`): 25 headings a run at the package's
anchors, the frame 2.03 ms p95 at the controls' median.

| run | draws +mean | +min | +max | p95 +median ms | +max ms |
|---|---|---|---|---|---|
| control_1 | 0.0 | 0 | 0 | 0.01 | 0.05 |
| subject | 22.2 | 4 | 36 | 0.10 | 0.44 |
| control_2 | 0.0 | 0 | 0 | -0.01 | 0.22 |

Against the controls' mean, heading by heading (`price_vs_mean.py`, its
output in `price/vs_mean.txt`): **the trees cost +22 draws a heading median
(+4 to +36) and p95 +0.10 ms median (+0.01 to +0.44)**, over the controls'
0.03 ms spread on 23 of 25 headings and over 0.10 ms on 12. 9227's twelve
MultiMeshes cost +14 draws and no frame time the harness could see (-0.01
ms inside a 0.16 ms spread); 9230's twenty-four cost +22 and a tenth of a
millisecond on a 2 ms frame, the first parkland frame cost the harness can
see, in the band 9228's roadside read (+25 draws, +0.20 ms on 4.8). The
cost follows the submissions: six modules a belt on four sides is twice the
MultiMeshes, with two thirds the instances.

The flip at `attacker_spawn_0` yaw 0 fell the same way in all three runs
this time (first passes 737, 737 and 761 against second passes 1,245, 1,245
and 1,271), so no heading carries the harness's flip; the controls' own
worst disagreement is 0.44 ms at that heading (3.04 against 3.48), the same
size as the subject's worst (+0.44 at `defender_spawn_2` yaw 90), so the
worst heading proves nothing and the median does.

The lever, if a tenth of a millisecond matters on the low-end target: one
module a form with the slot's size as instance scale (three modules and
twelve draws, as 9227) at the cost of the six dims' varied proportions;
recorded, not taken, until a real session's telemetry says.

## What this run does not prove

The parkland by day, where the crowns and the sky meet without the rain
and the lobes' facets show in full light; the look from a player's eye at
the fence (the stations are the road ends and the elevated views); the
species forms of step G, which are not drawn; and the price on the low-end
target, which this harness measures on this machine's renderer only.

## Instruments

- `tools/recipe_run_record.sh 9230 county_hospital_001`: the control copy,
  the edge stations (the same three 9227 shot), the frames, the sheet and
  the price (`record.log`, `price/`). The frames: `_scratch/frames_9230/`
  (not tracked).
