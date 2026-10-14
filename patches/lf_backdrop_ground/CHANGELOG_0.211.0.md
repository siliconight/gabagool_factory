## [0.211.0] - A ground under the backdrop

**The walker's walk of cold runs 9305-9307, 2026-10-14, finding 2** (the factory's
`docs/findings/walk_2026-10-14/`). At urban_row_001's east fence: "looks like the bottom of the level just
disappears", and "from a distance it looks fine... but as you get close". The backdrop's scene (0.174.0, roadmap 228
step E) held its rowhomes and its water tower and no ground. Past the plate's edge they stood on nothing, the sky and
the fog showing below and between them (`edge_9305_sheet.png` there, shot from 26 m up). The fence and the
buildings hide it from the street; from beside the fence one looks over it.

- **`backdrop_layer.with_ground(text, orders)`:** one `PlaneMesh` under the whole backdrop.
  - It spans the pieces' extent and `GROUND_MARGIN` (30 m) past it.
  - It stands at `GROUND_Y` (-0.10 m), under the plate, which covers it wherever both stand. The plate's ground
    reaches past its fences, so a ground beginning at an edge would lie on it.
  - Dark (`GROUND_RGB`), unshadowing, outside the light bake like the rest of the backdrop. One draw.
- **`ship_backdrop`** lays it into the scene it writes and reports it under `ground`. `draw_calls` still counts the
  MultiMeshes, as before.
- **`tests/unit/test_backdrop_ground.py`:** the plane's size, height and centre, the spec's (x, y) as Godot's
  (x, -z), its place after the root, and `load_steps` counting its two resources. On 0.210.0 it fails: there is no
  `with_ground`.

**Suite:** exit 0, 2,437 by the progress tally (2,422 passed, 14 skipped, 1 xfail): 0.210.0's 2,418, the new file's 3 and `test_sibling_locator`'s guard over it. The new file fails on 0.210.0's module, all 3, and passes on 0.211.0's (the factory's `patches/lf_backdrop_ground/prove_tests.out.txt`). Laid into a copy of cold run 9305's package and shot (the factory's `docs/findings/walk_2026-10-14/backdrop_ground_9305_mirror.png`, `backdrop_ground_grazing.png`): a 422 x 338 m plane, the void past the fence gone at the walker's spot and from 26 m up, no shimmer looking 140 m down the street at 0.6 m
