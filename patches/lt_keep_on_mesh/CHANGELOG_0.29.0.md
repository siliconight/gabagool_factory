## [0.29.0] - the bot keeps to the mesh it plans on, so it stops meeting the corners it is routed round

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

Drafted first as 0.28.0 and HELD: over the same sixteen lots its stuck counts fell, and five lots'
rose -- 18 of those 21 events were 0.28.0's subject, bots standing to fight counted stuck as their
window closed; on 0.28.0 the rows it lowered were round trips to a route point read as stuck, 0.28.1's
subject. This is that draft on top of 0.28.1.

### What changed

- **`_velocity_on_mesh`**: before the bot moves, the end of its step is put to the navigation map. A
  step whose end is off the mesh -- by more than `MESH_TOLERANCE_M` -- is turned toward the mesh's
  nearest point to that end, at no more than the speed it had, so the body slides along the mesh's
  edge round the corner at the bake's clearance and never meets what the mesh was eroded from. A
  nearest point on another level (more than `MESH_LEVEL_M`, the contract's step, above or below) is
  not this step's to judge and leaves it be; so does a bot walking without navigation.
- **`_advance_route` reads its `delta`**, which it had taken and never read since it was written.

### Measured

Over the factory's 16 lots in seven mission families on 0.28.1 (`docs/findings/route_snag/engine_breadth.py` with this addon, each lot's two Godot Physics passes identical on all 16): player-stuck 70 -> 0 under Godot Physics and 3 -> 0 under Jolt -- restaurant_row_001 seed_9104's 67 events at the deli register counter and crossroads_9600 seed_9600's three under each engine gone. Scores up on 4 of the 32 lot-engine rows (crossroads_9600 seed_9600 77 -> 88 under both engines, its route to 1.00; restaurant_row_001 seed_9104 PASS_WITH_TUNING 80 -> PASS 90 under Godot Physics), down a point on 3 (deli_001 seed_9191 under Jolt; warehouse_yard_001 seed_9004 under Godot Physics, its route 1.00 -> 0.96 and PASS -> PASS_WITH_TUNING; seed_9206 under Jolt, 0.92 -> 0.88), the same on 25. Keeping to the mesh moves where crews meet guards, so deaths moved both ways (warehouse_yard_001 seed_9004 28 -> 35 under Godot Physics); the two shorter routes are not attributed. Drafted first on 0.27.0 and held: what it seemed to break there was 0.28.0's and 0.28.1's subjects, fights and round trips counted as stuck

**Tests:** `test_bot_keeps_to_the_mesh.gd`, 3 checks, PASS on 0.29.0; on 0.28.1 [1] fails, the body's axis 0.359 m from the counter where the mesh keeps 0.40 m

**Suite:** All 24 tests exit 0 in the repository on 0.29.0
