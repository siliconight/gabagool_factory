# Cold run 9227 -- 0 interventions, 0 retries; the parkland stands beyond the fence

county_hospital_001 (`county_hospital`, a `campus` site), night and rain,
seed auto, staged from 9173's batch and brief. It proves roadmap 228's
`parkland` recipe end to end: Level Factory 0.175.0 decided the surroundings
from the archetype (the brief names none: `surroundings_resolved: {asked:
"", got: "parkland", known: true}`), Lot 0.109.0 laid the tree belts, Zoo
1.96.0's site kit built the trees, and Level Factory 0.174.0 shipped them as
MultiMeshes behind 9224's fence.

Tool versions hashed at `--begin` (`_runs/cold/cold_9227/before.json`): the
set 9226 ran on, unchanged -- Deli Counter 0.205.0, Dispatch 0.5.2, Laser
Tag 0.25.0, Level Factory 0.175.0, Lot 0.109.0, Lux 0.73.0, Patina 0.30.0,
Pipeline 0.6.0, Pixelcoat 0.62.0, Zoo 1.96.0.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0), **retries 0.**
- **Picked: seed_9107** on the walktest and Laser Tag's route findings.
- **The shell leg:** 0 blockers of 51. **The art leg:** 0 blockers of 67.
- **The bake:** 115 models and 776 primitive meshes, 44 steady rigs baked,
  24 failing left live, 119 room fills, 1,638 users, 49.8 s. The backdrop is
  not in it.

## The parkland, laid, built and shipped

- **Lot** (`themed_site_assemble/1/job.log`): `LOT_PERIMETER_FENCED: 4
  run(s), 367.7 m` on the 87 x 71 m plate, and `LOT_BACKDROP_PLACED: recipe
  parkland, 0 rowhome(s) in 3 bands a side (N 90, S 90, E 46, W 47), 3
  module(s), 0 water tower(s)` (the rowhome tally is 9226's cosmetic defect,
  Lot 0.109.1's to fix). The site's slot manifest counts 273 `site_backdrop`
  slots, every one a `backdrop_tree`: 87 at 5 x 5 x 7 m, 103 at 7 x 7 x 10
  m, 83 at 9 x 9 x 13 m.
- **Zoo's site kit** built the three tree modules PASS (x87, x103, x83).
- **Level Factory** (`export.log`): `[export] backdrop: site_backdrop.tscn
  -- 273 instances of 3 module(s) on their sides, 12 draw calls (N 0, S 0,
  E 0, W 0; 0 tower)`: three modules on four sides, one draw a module a
  side, the tree's two materials in one mesh each.

## Seen

`edge_before_after.png`: the control is this package with the backdrop
scene not loaded (`tools/backdrop_off.py`), the subject the package as
shipped; the stations are the three road ends that reach this plate's edge
(`tools/edge_stations.py`, `stations.txt`) and look_shots' four elevated
views. In heavy rain at night:
- **Down road 0 to the east edge** (`road0_b_E`): where the control's road
  ends at the fence against the flat glow band, the subject's ends under a
  line of round crowns, the near belt's trees standing over the fence line
  at the horizon. **Up road 1 to the north edge** (`road1_b_N`): the same, a
  cluster of crowns closing the view past the gate. To the west edge
  (`road0_a_W`) the belt is behind the clinic's own trees and reads as
  little more than them.
- **From the four elevated views** the effect is the strongest of the three
  recipes so far: where the control shows the hospital's flat facade against
  fog, the subject shows ranks of faceted crowns standing over and behind
  the roofline on every side, 7 to 13 m tall against a 2-storey building,
  overlapping into a wood. From the east (`elev_E`) three crowns of the
  near belt loom in the foreground, 4.75 m past the fence, larger than the
  building behind them.
- **For the walker's eye:** the crowns are one faceted sphere at three
  sizes, and from above the belt reads as a row of the same tree; the
  authorship guide would ask for two or three crown forms (a taller
  narrower crown, a broken one) before more density. And whether the near
  belt should start further off the fence than 2.5 m on a plate this small,
  so an elevated view does not fill with a crown.

## Priced

`price/price.txt`, the package against its own backdrop-off copy through
`docs/findings/horizon_glow/price_glow.py` (control, subject, control; the
harness calls the subject `glow`): 25 headings a run.

| run | draws +mean | +min | +max | p95 +median ms | +max ms |
|---|---|---|---|---|---|
| control_1 | 0.0 | 0 | 0 | 0.03 | 2.01 |
| subject | 31.8 | 4 | 484 | -0.01 | 2.30 |
| control_2 | 0.0 | 0 | 0 | -0.03 | 0.29 |

The controls' spread is 0.16 ms p95 and 0 draws. **The +484 is the
harness's own flip, not the trees:** at `attacker_spawn_0` yaw 0 the
control's two passes of the same heading read 699 and 1,165 draws and the
subject's 1,183 and 717 (`split_perturbed`), an occlusion edge at that
camera that a nudge tips either way; the report takes each run's first pass,
and the two runs fell on opposite sides. Against the controls' mean the
draws' median over the 25 headings is **+14** (+4 to +18 everywhere but that
heading: the 12 backdrop MultiMeshes and the fence), and the p95 median
-0.01 ms, inside the spread. The parkland costs 14 draws a heading and no
frame time at the stations; the +2.30 ms worst heading is the flipped one,
whose two control runs differ by 2.01 ms between themselves.

## What this run does not prove

The parkland by day, where the tree belt's crowns and the sky meet without
the rain; the look from a player's eye at the fence; the roadside recipe,
which 9228 proves.

## Instruments

- `tools/recipe_run_record.sh 9227 county_hospital_001` made the control
  copy, the stations, the frames, the sheet and the price (`record.log`).
- `stations.txt`: three stations, the two ends of road 0 and the north end
  of road 1, which reaches the edge on this plate. `price/`: the three perf
  reports. The frames: `_scratch/frames_9227/` (not tracked).
