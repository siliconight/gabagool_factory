# Cold run 9221 -- 0 interventions, 0 retries; a wall's anchors face out and stand on its face

club_block_014, seed 9181 at night, staged from 9220's batch and brief. It
proves roadmap 221: Patina 0.30.0 takes its anchor normals the right way
out, skips the points inside a wall, and stands a conduit on its wall.

Tool versions hashed at `--begin` (`_runs/cold/cold_9221/before.json`):
Deli Counter 0.205.0, Dispatch 0.5.2, Laser Tag 0.25.0, Level Factory
0.165.0, Lot 0.104.0, Lux 0.72.0, Patina 0.30.0, Pipeline 0.6.0, Pixelcoat
0.61.0, Zoo 1.93.0. Only Patina differs from 9220.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0), **retries 0.**
- **Picked: seed_9181.**
- **The shell leg:** 0 blockers of 51. **The art leg:** 0 blockers of 71.
- **Findings 71 to 71.**
- **The bake** is 435 models and 3,897 users, as in 9220, at 90.4 s.

## The orders: every wall-facing cover faces out, on its own side

The run's own `patina_dressing` jobs, read through Zoo's `plan_dressing`
(`docs/findings/patina_cover_normals/replay_dressing.py`):

| building | base courses out / on their side / inside the wall | conduits out / on their side | gutters, downspouts |
|---|---|---|---|
| strip_club_a01 | 45 / 45 / 0 | 2 / 2 | 65 and 8, all out |
| funeral_home_a03 | 45 / 45 / 0 | 2 / 2 | 67 and 10, all out |
| airport_terminal_a02 | 54 / 54 / 0 | 4 / 4 | 95 and 16, all out |

**On 9220, Patina 0.29.2:** the club's base courses were 0 of 51 out and 0
on their side, and 28 stood on the wall's centre line, inside it. The 241
orders are exactly what the replay on the shell gave before the run.

## The merge: each side's mesh on its own face

Each building's dressing GLB, vertices by the face they lie nearest
(`merge_faces.py`). The concrete meshes:

| mesh | 9220 (0.29.2) | 9221 (0.30.0) |
|---|---|---|
| strip club `CoverN_concrete` | N 1,760, S 432 | N 2,960 |
| strip club `CoverS_concrete` | N 1,008, S 720 | S 1,104 |
| strip club `CoverE_concrete` | E 480, W 672 | E 816 |
| strip club `CoverW_concrete` | E 432, W 576 | W 912 |

- **The funeral home and the airport terminal,** 9221: each concrete side
  mesh lies on its own face only.
- **The painted metal** lay on its own faces before and after.
- **On the 12 empty rowhomes,** the vertices on another face fell from
  29,024 of 234,228 (12.4%) to 10,496 of 206,484 (5.1%), and the concrete
  meshes holding any from 96 to 32. The 48 painted-metal meshes are
  unchanged. Those covers come from the Empties' slots, not from 221's
  anchors. On a 6.3 m-wide house, nearest-edge cannot tell a mixed merge
  from a cover near a corner, so what is left there is NOT claimed.

## The price

`price_merge.py` ran Level Factory's fixed-station harness three times, on
9220's walk copy, 9221's, then 9220's again. The two packages stand at the
same 53 headings: the same `gameplay_anchors.json`, the same Level Factory.
Against the two 9220 runs' mean, heading by heading:

| | draw calls a heading, mean | p95 frame time, median |
|---|---|---|
| 9220, first | +1.5 | +0.75 ms |
| **9221** | **-9.4** | **-0.01 ms** |
| 9220, second | -1.5 | -0.75 ms |

- **Fewer draws:** 9.4 a heading, on about 1,150. The controls' own means
  differ by 1.5.
- **No measurable frame time:** the controls' p95 differs by a median 1.50 ms
  a heading tonight, and 9221 sits inside it.
- **Not attributed: two headings drew about 148 more objects.** They are
  attacker_spawn_8 at 90 degrees and patrol_point_18 at 180. The controls
  show a jump of the same size between themselves at a third heading,
  attacker_spawn_8 at 0 degrees, 879 against 719. So a group of about 150
  objects toggles from run to run.
- **Also not attributed by files:** every GLB the run rebuilds differs
  between the two packages, Zoo's unchanged ones included. So the packages
  are not byte-identical outside Patina's change, and only the orders and
  the merges above are Patina's alone.
