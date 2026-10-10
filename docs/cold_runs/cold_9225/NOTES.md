# Cold run 9225 -- 0 interventions, 0 retries; the borough stands beyond the fence

restaurant_row_001, evening and clear, seed auto, staged from 9224's batch
and brief. It proves roadmap 228's steps C, D and E together: Zoo 1.95.0's
rowhome and water tower, Lot 0.108.0's bands by recipe, and Level Factory
0.174.0's composition of them as MultiMeshes, behind 9224's fence and under
its glow.

Tool versions hashed at `--begin` (`_runs/cold/cold_9225/before.json`):

| tool | version |
|---|---|
| Deli Counter | 0.205.0 |
| Dispatch | 0.5.2 |
| Laser Tag | 0.25.0 |
| Level Factory | 0.174.0 |
| Lot | 0.108.0 |
| Lux | 0.73.0 |
| Patina | 0.30.0 |
| Pipeline | 0.6.0 |
| Pixelcoat | 0.62.0 |
| Zoo | 1.95.0 |

Against 9224: Level Factory 0.173.0 to 0.174.0, Lot 0.107.0 to 0.108.0, Zoo
1.94.0 to 1.95.0.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0), **retries 0.**
- **Picked: seed_9104,** on the same lines as 9222 to 9224.
- **The shell leg:** 0 blockers of 52. **The art leg:** 0 blockers of 74.
- **The bake:** 481 models and 1,420 primitive meshes, 4,242 users, 91.7 s
  (9224: 104.0 s). The backdrop is not in it: a MultiMesh is not lightmapped.

## The backdrop, laid, built and shipped

- **Lot** (`themed_site_assemble/1/job.log`): `LOT_BACKDROP_PLACED: recipe
  borough, 276 rowhome(s) in 3 bands a side (N 96, S 101, E 41, W 38), 6
  module(s), 1 water tower(s)`, with the fence as 9224 stood it
  (`LOT_PERIMETER_FENCED: 6 run(s), 589.7 m`). The site's slot manifest
  counts `prop/site_backdrop: 277` beside its 148 cover slots.
- **Zoo's site kit** built 18 rowhome modules and the tower: six width and
  height pairs, but at THREE depths, one a band (10, 11 and 12 m), so
  `prop_backdrop_rowhome_delco_1997_01_w500_d1000_h800` and its `d1100` and
  `d1200` siblings are three modules where the plan counted one. That is the
  defect Lot 0.109.0 fixes by giving every band the same depth; its six
  modules a level become six, and the draws below fall with them.
- **Level Factory** (`export.log`): `[export] backdrop: site_backdrop.tscn
  -- 277 instances of 19 module(s) on their sides, 69 draw calls (N 96, S
  101, E 41, W 38; 1 tower)`. The package carries `site_backdrop.tscn` with
  69 MultiMeshInstance3D nodes, `backdrop/` with 19 `.res` meshes,
  `backdrop_layer.json`, and `mission.tscn` instances the scene beside the
  level.

## Seen: the borough behind the fence

`docs/cold_runs/cold_9224/edge_frames.sh` shot 9224's package and 9225's at
the same stations through each package's entry scene
(`edge_before_after.png`; the sky band in `sky_band.txt`; the rows enlarged
in `north_road1_backdrop_zoom.png` and `west_end_backdrop_zoom.png`):
- **Up the side road to the north edge,** 9224 ends at the fence and the
  dusk sky. 9225 ends at the fence with a skyline behind it: a row of
  rowhome blocks, their cornices a band apart, a few windows lit, some
  faces pink in the dusk sun, and the water tower's tank pale on the
  horizon to the left. It reads as a borough at dusk. The band's luma
  falls 3.4 and it cools 0.9 where the houses stand in the sky.
- **Down the main road to either end,** the near band stands 4 m beyond
  the fence, so the end of the road is a dark terrace of blocks with lit
  windows, blue-grey in the sky's light (the painted brick is (0.4, 0.2,
  0.16); samples read (45, 56, 88)). At the west end it fills the gap
  between the last buildings and the sky band darkens 12.6: the menu's
  caution about E, "a dark wall of windows", stands at this hour and this
  distance, and whether the near band belongs so close is the walker's
  call (the mockup's figure, kept).
- **From the elevated camera over the north edge,** the houses' backs and
  roofs read black against the dusk with their lit windows, over the
  fence's posts and fabric.
- **Where the edge is not in view,** nothing moves (the objective, the
  spawn, road 0's facade, the elevated views over the plate's middle).
- **The paint travelled:** each extracted mesh carries its two textures
  (`backdrop_layer.json`, `embedded_textures: 2`), 106 KB a module.

## Priced: the borough's backdrop

`docs/findings/horizon_glow/price_glow.py` on copies of the two packages,
9224's as the control, at Level Factory's fixed stations (`price/`):

| run | draws, +mean a heading | p95 frame, +median | p95 frame, +worst |
|---|---|---|---|
| control 1 (9224) | 0.0 | -0.34 ms | +0.17 ms |
| **9225** | **+51.8** | **+0.02 ms** | **+1.25 ms** |
| control 2 (9224) | 0.0 | +0.33 ms | +2.99 ms |

- **Draws: +43 a heading median, +17 to +91.** The 69 MultiMeshes, one a
  module a side: every heading sees some of them, and `extraction_15`
  facing 270 sees the most. Lot 0.109.0's one depth a band cuts the modules
  from 19 to 7 and the MultiMeshes to about 25; the next borough run
  measures it.
- **Frame time: inside the noise.** +0.02 ms median against the controls'
  mean, whose own spread is a median 0.67 ms a heading (their medians 6.59
  and 7.41 ms); p90 +0.58, 7 of 53 headings over +0.5 ms, the worst +1.25
  at `attacker_spawn_3` facing 270.
- The draw calls are the budget (CLAUDE.md), and 43 a heading for a
  backdrop is more than the menu's A paid (+16, one MultiMesh a band a
  side, 4 sides x 3 bands); the fix is the module count, not the sides.

## Roadmap

228's steps C, D and E are proven. Lot 0.109.0 (the other recipes, and one
depth a band), Zoo 1.96.0 (the tree and the warehouse) and Level Factory
0.175.0 (`surroundings` from the brief or the archetype) land after this run;
the recipe runs follow.
