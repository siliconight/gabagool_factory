---
name: late-pieces-guard-width
description: "A piece placed late in a furnished room must narrow no route -- keeping off the reserved routes keeps length, not width; ask room_necks/_narrows (DC 0.256.0)"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-22T00:09:11.747Z
---

Keeping a late piece off a room's reserved routes (`protected_routes`, half `two_abreast_width()` wide) protects each pair's LENGTH, not its WIDTH: a route may run one body radius from a wall, so a piece just off its corridor can still leave single file between itself and that wall. Measured 2026-10-21 (Deli Counter 0.256.0, roadmap 284, `patches/dc_desk_move/arms_A.json`): 19 desks moved back off the routes narrowed nine pairs to single file in two rooms (landmark_hall_a01 curator_band, train_yard_a01 dispatch_office).

`level_design.room_necks(spec, room)` (DC 0.256.0) is the factory census's own neck asked of one room -- same cell, obstacles, snapping, door disc, union-find; 187 pairs in 64 rooms read identically (`patches/dc_desk_move/census_agreement.out.txt`) -- and `_narrows(before, after)` refuses any width lost under two abreast or a pair parted. An open room's neck is ~1.6 m clearance (the wall a door stands in, just past its 1.0 m open disc), not the 2.0 cap.

**Why:** the walker's first priority is free navigation; a "put back" piece is a new obstacle the recipe never priced.

**How to apply:** any new late placement in furnish (a finer grid for `_move`, another rescue, a shelter-like pass) asks `_narrows(before, room_necks(spec, room))` after seating, and is priced with a census arm run like `patches/dc_desk_move/arms.py` (control arm must reproduce `route_cost.json` pair for pair first). Related: [[route-census-reads-furnishing]], [[rooms-not-crowded-not-barren]].
