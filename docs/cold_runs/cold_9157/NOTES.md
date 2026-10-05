# Cold run 9157 -- 0 interventions; the storey-seam dashes gone, stone lintels and sills on the Empties

gas_block_001, seed 9080, `empties: "across"`, `--bake-lights`.

**Stack:**
- Zoo 1.70.0: a run module's top and bottom are butt planes, so there is no
  V-groove at a storey seam.
- Patina 0.27.0: orders a `lintel` over every facade window and door and a
  `window_sill` under every facade window.
- Zoo 1.71.0: builds them in cream plaster.
- Unchanged: 9156's Deli Counter 0.181.0, Patina's fixtures and Zoo's
  fixtures.

**Result:** every leg ran in 33 minutes, `INTERVENTIONS: 0`. Art exited 1
on 55 findings, as before. No `STEM COLLISION`. The walk copy is this
run's.

## The storey seams

**The finding** (9153-9155's frames, measured on 9155's module GLB): short
pale-then-dark dashes at the stone Empty's storey line.
- The wall panels' 3 mm x 3 mm chamfers met as a 6 mm V where storeys stack.
  Deli Counter 0.175.2 stacks an Empty's storeys wall on wall: 0.0-3.1, then
  3.1-5.9.
- In those frames that V is a quarter to a third of a pixel: the camera is
  65 degrees at 1152 x 648, the wall 10-15 m away. So it aliased into a row
  of dashes.

**Before the run, on the stone rowhome's own kit rebuilt**
(`patches/zoo_storey_seams/check_kit_seams.py`). Vertices within 1 cm of a
module's top or bottom plane but not on it:

| modules | 1.69.0 | 1.70.0 |
|---|---|---|
| wall | 20-24 each | 0 |
| window | 152 each | 0 |
| the doorway's stone | 120 | 0 |

The doorway's door leaf keeps its own bottom chamfer, 1 mm off the floor:
a real corner, unchanged.

**Tests:** both Blender tests in `test_butt_joints.py` pass inside Blender
5.1. The pins that had held the top chamfer as kept are reversed, and each
says what it used to assert.

**The frame:** `stone_endwall_9156_vs_9157.png`, the same wall from the
same camera. 9156 shows the row of dashes; 9157 shows none.

## Lintels and sills

- **Dressing:** every rowhome's GLB gains a plaster mesh on its front and
  its back. The rowhomes are 10-11 meshes now (8, plus 2 plaster, plus a
  barred side's iron); the three enterable buildings are unchanged at 8.
  `refused 0` everywhere.
- **The bake's users went 5,138 -> 5,190, +52:** 26 placements x 2 plaster
  meshes.
- **Geometry** (the Blender pre-flight on rowhome_a): the south plaster mesh
  runs y -6.151..-6.211, from 1 mm off the face out to the sill's 6 cm.
  Heights:
  - the ground sill at 0.78-0.85;
  - a door lintel from 2.30;
  - the top lintel at 8.65-8.85, its top on the gutter's underside at
    8.85, touching without overlapping.
- **Frames:** `docs/findings/empties_trim_9157/`; `trim_closeups_9157.png`
  crops a front and a unit on its sill. Cream lintels over every window and
  door, a projecting sill under every window. The units sit on their sills,
  brackets below. The doors are still the stained wood; Deli Counter
  0.182.0 is next.

## The price

A = 9156's package, B = 9157's, A2 = 9156's again: 53 station x heading
pairs, measured back to back. All 53 are stable this time: A and A2 agree
within 1 ms everywhere.

- **Draws:** median +14, mean +18, at most +59 a view (longest_sightline at
  90: 5,922 -> 5,981). That is the two plaster meshes of every rowhome in
  view. The control: 0 everywhere.
- **Median frame**, against the mean of A and A2: median +0.024 ms, mean
  +0.025, range -0.107 to +0.159. The control's own median is -0.008, so the
  net is about +0.03 ms, inside the instrument's spread (control range -0.227
  to +0.187).
- **p95:** median -0.002 ms.
- **The harness light census:** 61 of 5,244 meshes over the cap, the same 61
  as 9156. The plaster meshes add none.
- **The seam fix** removes a few triangles from every wall-family module and
  changes no draw. Nothing about it is measurable in frame time at this
  resolution; the frames are its evidence.

Outputs: `price_trim.txt` (`compare_price.py`) and `price_trim_robust.txt`
(`price_robust.py`).
