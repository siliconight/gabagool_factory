---
name: rooms-not-crowded-not-barren
description: "Walker 2026-10-21 on density: levels and buildings must not feel crowded or cluttered, nor boring and barren -- a band, not a direction"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-21T15:01:12.264Z
---

The walker, 2026-10-21, mid-way through roadmap 148's density work (after "Too sparse" on 2026-10-19): "To temper
us, we don't want levels and building to feel overly crowded or cluttered, but not boring and barren either".

**Why:** 148 was pushing rooms denser, and density is easy to overshoot -- a room packed to real-world fill, or filled
with scattered small pieces, reads as clutter, and in a shooting gallery it also chokes the lanes. The ask is a
middle, not a maximum.

**How to apply:**
- Treat density as a BAND. Measured with `level_design.room_floor_share` (Deli Counter 0.247.0): the review's sparse
  rooms were 3.7-16 % of their floor under furniture; the convenience stores the walker had already seen were 11-12 %;
  the corner-store rows landed 19-23 % and cap at `rows_share` 0.25 (a real grocery is 35-40 %). Aim furnished rooms
  at roughly 12-25 %, and never raise a cap past 25 % without showing the walker a frame.
- Fill with the room's PRIMARY furniture in rows (gondolas, racks, desks) rather than more loose pieces: cartons,
  bins and clusters are seasoning, not how a room reaches its share. The "more pieces" approach was measured and
  refuted for exactly this (`docs/findings/denser_rooms_148/plateau_dry_run.py`).
- Keep lanes open: the contract's 1.25 m aisle at least; a room left a little under the band beats one packed to it.
- Report a change's floor share (before -> after) with its frames, so the walker judges the band, not just the look.

- Read the band BESIDE what it costs a route: [[route-census-reads-furnishing]]. Since Deli Counter 0.250.0 the
  corner stores reserve their routes first and sit at 17.2-22.1 %, inside the band; the walker's guide of the same
  day (`docs/reference/Lived_In_Levels_Clear_Navigation_4P_PVE_1999_PA.md`) puts movement before building use before
  story clusters.

- DC 0.251.0 (routes in objective rooms) made a few already-barren rooms barer: a cluster group that fits nowhere
  off its routes is dropped whole (clinic_a01's dispensary ~5 -> 2.4 %). Objective rooms sit at 3-7 %; the band
  wants their PRIMARY furniture raised, not more piles. Queued for the walker: desks off objective routes too?

- DC 0.252.0 (roadmap 284) took away 24 desks and a table no chair fits beside -- offices barer, marker rooms most (office's exec_suite 7.2 -> 5.4 %, train_yard_a01's dispatch_office 7.0 -> 4.0 %). Queued for the walker: move such a desk instead? The re-draw that would move it was priced and refuted on this draw.

Related: [[game-is-a-series-of-shooting-galleries]], [[open-work-2026-10-09]], [[route-census-reads-furnishing]].
