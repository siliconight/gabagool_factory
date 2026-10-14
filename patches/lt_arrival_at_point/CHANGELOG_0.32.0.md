## [0.32.0] - an arrival is at the point, not at the end of a path that stops short of it

### Why now

Factory roadmap 246, found by the factory's census of what a pick counts (roadmap 245). Cold run 9185's
restaurant_row_001 seed_9003 read route completion 1.00 in every run, while its walk test said the objective
stood on a navmesh island 60.99 m from the main network.

`_advance_route` counted a route point reached when `_nav_finished()`: `NavigationAgent3D.
is_navigation_finished()`, true at the end of the path the navigation server returned. For a point the network
does not reach, that path ends at the closest point it does.

Traced in a run, on 0.31.0 (the factory's `docs/findings/lt_arrival/arrival_trace.py`):
- **Every crew bot "arrived" at the objective standing 61.2 m from it,** and 2.5 m from its spawn.
- **Godot itself said otherwise at that moment:** `is_target_reached()` read false, and
  `get_final_position()` was (-8.55, 0.0, -28.05).
- **Reachable points arrived honestly:** 0.00 to 0.93 m away, their paths ending 0.00 to 0.15 m from them.

### What changed

- **`LT_BotPlayerController.path_reaches_point(path_end, point, tolerance)`** (static). The path's end must lie
  within `tolerance` of the point. That is Godot's `is_target_reachable()`, made testable without a scene.
- **`_advance_route` counts an arrival** (`_route_reached`) only where the path reaches the point
  (`get_final_position()` against `target_position`, within `target_desired_distance`).
  - A point the path stops short of is passed as a jammed one is (`_update_stuck`): the index moves on, and the
    arrival is not counted.
  - The run's log says where, as `RoutePointUnreachable` with how far short.
  - So `route_walked` and `ObjectiveReached`, which route completion reads, now ask real arrivals throughout.
- **`runners/tests/test_an_arrival_is_at_the_point.gd`** has 7 checks. PASS on 0.32.0; on 0.31.0 it does not load (Godot: `path_reaches_point()` not found in `LT_BotPlayerController`). All 27 scripts in `runners/tests` and `runners` exit 0 on 0.32.0, headless under Godot 4.7, among them `test_route_progress.gd` and `test_a_skipped_route_is_not_walked.gd` beside the changed lines.

### Measured

The factory's `docs/findings/lt_arrival/arrival_breadth.py`, 0.31.0 exported against 0.32.0, 25 runs a lot from each job's seed under Godot Physics. On the factory's sixteen lots, every route point reachable, 0.32.0 reads 0.31.0 exactly: every summary field, the grade and the score. On cold run 9185's restaurant_row_001 seed_9003, its objective stranded, route completion 1.000 -> 0.000 and progress 1.000 -> 0.630, PASS 90 -> PASS_WITH_TUNING 81, and no other field moves: the fights are as they were, only the count is honest.
