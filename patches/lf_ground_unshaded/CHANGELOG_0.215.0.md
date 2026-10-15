## [0.215.0] - The backdrop's ground is unshaded

**The factory's roadmap 252.** 0.211.0 laid a near-black `StandardMaterial3D` plane under the backdrop, 422 x 338 m
on urban_row_001, and shipped it as "one draw", read off the scene and not priced -- a shaded plane every lamp on
the level reaches, which is the shape the factory refuses on sight. **Priced on cold run 9308's package**
(`docs/findings/walk_2026-10-14/ground_price.sh`: the level against itself with the node removed, bracketed by two
controls, 53 headings): the shaded ground costs +1 to +7 draws a heading, +2.5 on the mean, and at the heaviest
heading (`camera_socket_0` at yaw 90, 2,441 draws) +6 draws and +7.20 ms on the p95 against a 0.40 ms noise floor,
nine of 53 headings beyond the controls' own spread. The same plane unshaded costs +1 draw at every heading and at
most +0.52 ms, +0.04 on the median, a 0.08 ms floor. The reading, not measured: on GL Compatibility a shaded mesh
reached by more lights than one pass takes draws again for the rest, and this plane is reached by every lamp.

- **`with_ground`** writes `shading_mode = 0` on the ground's material: the plane draws its albedo and takes no
  light. The scene is byte for byte the priced arm (`ground_strip.py unshaded` on 9308's, the control that proves
  the price applies). The record carries `"shaded": false` beside its `draw_calls`.
- **What the shaded ground would have bought:** the lamps' pools and the sun's shade on the ground past the fence,
  seen in `docs/findings/walk_2026-10-14/ground_frames/` at the walker's spot; the walker's call to spend it, by
  level, when runtime data says the frame can.
- **`tests/unit/test_backdrop_ground.py`:** the material carries `shading_mode = 0` ahead of its roughness, and the
  record says so; the first test restated. Both fail on 0.214.0.

**Suite:** exit 0, 2,450 by the progress tally (2,435 passed, 14 skipped, 1 xfail): 0.214.0's 2,434 passed and the new test; the 14 skipped are the real-tool smoke, as before
