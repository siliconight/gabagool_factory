# Laser Tag counted the end of a short path as arriving (roadmap 246)

**Found by roadmap 245's census** (`docs/findings/pick_majors/`). Cold run 9185's restaurant_row_001 seed_9003 read
route completion 1.00 in Laser Tag, every run. Its walk test said the objective, b0's apartment_hideout 3.3 m up,
stood on a navmesh island: the path proof stopped 60.99 m short.

## Traced (`arrival_trace.py`, `arrival_trace_9185.out.txt`)

A copy of the candidate's staged evaluation, run on today's Laser Tag (0.31.0) with one print at the arrival, two
runs, eight crew bots. Godot frame, metres: x, y up, z.

- **The objective is route point 1,** at (-54.0, 3.3, 12.47).
- **Every bot "arrived" at it standing about 61.2 m away,** at (-8.3, 0.0, -28.2), about 2.5 m from its spawn.
  The crew never walked toward the objective.
- **At that moment Godot said otherwise:** `is_target_reached()` false, and `get_final_position()`
  (-8.55, 0.0, -28.05), the closest point the network reaches. The walk test measured the same 61 m.
- **The reachable points arrived honestly:** 0.00 to 0.93 m away, their paths ending 0.00 to 0.15 m from them.
- **The report read route completion 1.0.**

**The cause, now traced in a run rather than read.** `_advance_route` counted a route point reached when
`_nav_finished()`, `NavigationAgent3D.is_navigation_finished()`. That is true at the end of the path the
navigation server returned, and for a point the network does not reach, the path ends at the closest point it
does.

## The fix: Laser Tag 0.32.0

- `LT_BotPlayerController.path_reaches_point(path_end, point, tolerance)` (static) asks whether the path ends
  within `tolerance` of the point. That is the question Godot's `is_target_reachable()` asks.
- `_advance_route` counts an arrival only where it does (`get_final_position()` against `target_position`,
  within `target_desired_distance`).
- A point the path stops short of is passed as a jammed one is: the index moves on, the arrival is not counted,
  and the run's log says `RoutePointUnreachable`.
- `runners/tests/test_an_arrival_is_at_the_point.gd` has 7 checks. On 0.31.0 it does not load; all 27 test
  scripts exit 0 on 0.32.0.

## Breadth (`arrival_breadth.py`, `arrival_breadth.out.txt`)

Laser Tag 0.31.0, exported, against 0.32.0. Each lot gets 25 runs from its job's own seed under Godot Physics,
over `route_snag/blocked_breadth.py`'s sixteen lots and 9185's seed_9003.

    the sixteen lots, every route point reachable    0.32.0 reads 0.31.0 exactly: every summary field, the grade, the score
    cold-9185-ws seed_9003, its objective stranded   route completion 1.000 -> 0.000, progress 1.000 -> 0.630,
                                                     PASS 90 -> PASS_WITH_TUNING 81; no other field moves

The fights are as they were: the bot still moves on past the point as before. Only the count is honest now.

## What it changes for the factory

Route completion is now a count of real arrivals throughout, and it is the picker's second key (roadmap 245). A
candidate whose route point is stranded was already out on its walk test. Laser Tag no longer contradicts that,
so the two instruments agree.
