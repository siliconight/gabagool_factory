---
name: stair-head-ledge
description: "Roadmap 190 CLOSED: every stair collision ramp's head stood 0.2 m over its landing; DC 0.190.0 TRIMS the head; proven in cold 9187 (deli_a03 25/25 runs vs 0/25); sinking was refuted because the nav bake reads VISUAL treads"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-06T21:08:37.928Z
---

Found 2026-10-06 in cold run 9186. Fixed in Deli Counter 0.190.0 and proven
in cold run 9187, roadmap 190 CLOSED.

**The defect.** deli_a03 was newly reachable upstairs (see
[[stairwell-on-one-grid-in-four]]). Laser Tag's bots stuck 3,148 times at
the head of its up-stair and finished 0 of 25 runs.
- All 174 ramps in the library topped out 0.19 to 0.21 m over their
  landing. The ramp rides the nosings half a step proud, and the foot was
  fixed in 2026-07 while the head never was.
- Going up, the ledge is a drop. Going down, it is a riser a capsule can't
  walk.
- The navmesh climbs 0.15 m and Lot's walkers step 0.5 m, so neither saw it.

**The fix:** `stairwell.ramp_head_trim` cuts the head back along the
incline and keeps the foot. Measured:
- census 0 of 174;
- walk down in 2.4 s and up in 3.8 s;
- gate 144 of 144;
- 9187: the same deli objective finished 25 of 25 runs, with 3 stuck
  events, all on the ground floor.

**Refuted, kept:** sinking the ramp. It passed the census and the walk, then
the gate failed 94 of 144 shells.

**How to apply:**
- The nav bakes read VISUAL meshes, both the gate's and the site's. A
  "collision-only" stair change must keep every visual tread at or below the
  collision ramp.
- Before trusting a collider fix, measure the gate as well as the collider.
- A walk instrument needs a control that fails, or it proves nothing about
  that direction.

**Why:** a collision census can pass a change the bake fails.
