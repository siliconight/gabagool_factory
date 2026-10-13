## [0.28.1] - a bot that reaches where it was going is not stuck

### Why now

Factory roadmap 242, the stuck detector's second false positive. `_update_stuck` measures NET
displacement over its 4 s window, so a crew body that walked out to a route point and back inside one
window ended near where the window began and read as stuck -- 10 traversal points and a skipped route
point. 0.28.0 surfaced it: over the factory's sixteen lots, its fix of the first (a stand to fight)
lowered three lot-engine rows by adding stuck events, and the factory traced every one
(`docs/findings/route_snag/`, `pin_trace.py trace --wide`, each control held): on gas_block_001
seed_9282 the body walks along the upper floor to its route point, reaches it (route 1 -> 2), turns and
walks back through the same spot; on warehouse_yard_001 seed_9206 the same out and back. 0.28.0's entry
called them bodies going back and forth over one spot; they were round trips, and 0.27.0's fixed grid
had missed them by its alignment, not by being right.

### What changed

- **`_restart_stuck_window()`**, the one place the window restarts where the body stands: on a stand to
  fight (0.28.0's restart, now through it), and now on reaching a destination -- a route point
  (`_advance_route`, where `_route_reached` counts it) or a cover point (`_seeking_cover`'s arrival).
  An arrival is progress; a jam after it is still counted, a window later. Route points are finite and
  each is reached once, so arrivals cannot hold a window open.

### Tests

`runners/tests/test_an_arrival_is_not_stuck.gd` drives `_physics_process` at 0.25 s a frame with a bot
that cannot move itself and walks the body a metre a frame, out along x and back: [1] the control,
reaching nothing, stuck on frame 16; [2] a route point reached on frame 8, no stuck event on frame 16;
[3] a route point reached and the body held there, stuck on frame 23, a window on; [4] a cover point reached, none
on frame 16. 8 checks PASS on 0.28.1; on 0.28.0 three fail -- [2] and [4] record a stuck event for a round trip to a route point and to a cover point, and [3] counts the jam on frame 32 rather than 23

All 23 tests exit 0 in the repository on 0.28.1, `test_nav_bake_is_the_contract` and `test_a_fight_is_not_stuck` among them

### Measured

Over the factory's 16 lots in seven mission families (`docs/findings/route_snag/engine_breadth.py` with this addon, each lot's two Godot Physics passes identical on all 16): against 0.28.0, scores up on 11 of the 32 lot-engine rows and down on none; player-stuck 92 -> 70 under Godot Physics and 24 -> 3 under Jolt, what is left one real pin (67 events at restaurant_row_001 seed_9104's deli register counter) and three events on crossroads_9600 seed_9600 under each engine. The three rows 0.28.0 lowered are back: gas_block_001 seed_9282 PASS 100 under both engines, warehouse_yard_001 seed_9206 WARN 68 under Godot Physics. Against 0.27.0, this morning's: up on 22 rows, down on none, player-stuck 108 -> 70 and 60 -> 3
