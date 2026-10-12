## [0.28.0] - the bot keeps to the mesh it plans on, so it stops meeting the corners it is routed round

### Why now

Factory roadmap 242: Laser Tag's route on restaurant_row_001's picked lot swung with every change to
the street furniture -- 9, 29 and 72 player-stuck events across three cold runs where only the
furniture changed. The factory's `docs/findings/route_snag/` found the place: 64 of 72 events at one
point to fifteen digits, a crew body standing one radius from a deli register counter's corner. The
bot turns toward its next path point once within its arrival radius, about 0.44 m
(`LT_Const.arrival_radius`), and the straight line from there to a point round a corner cuts the
corner: off the navmesh, into the 0.4 m the contract's bake keeps from every collider, where the 0.35 m
body has 5 cm to spare. There Godot Physics pinned it -- `move_and_slide` sliding on the floor's normal
six times a frame -- and Jolt slid past; across sixteen lots of seven mission families Jolt pinned
bodies at other corners instead (player-stuck 36 under Godot Physics against 53 under Jolt without the
counter's lot). The engine was never the fix. The bot leaving the mesh was.

### What changed

- **`_velocity_on_mesh`**: before the bot moves, the end of its step is put to the navigation map. A
  step whose end is off the mesh -- by more than `MESH_TOLERANCE_M` -- is turned toward the mesh's
  nearest point to that end, at no more than the speed it had, so the body slides along the mesh's
  edge round the corner at the bake's clearance and never meets what the mesh was eroded from. A
  nearest point on another level (more than `MESH_LEVEL_M`, the contract's step, above or below) is
  not this step's to judge and leaves it be; so does a bot walking without navigation.
- **`_advance_route` reads its `delta`**, which it had taken and never read since it was written.

### Measured

RESULT_MEASURED

**Tests:** RESULT_TESTS

**Suite:** RESULT_SUITE
