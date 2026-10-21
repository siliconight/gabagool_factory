---
name: rooms-not-crowded-not-barren
description: "Walker 2026-10-21 on density: levels and buildings must not feel crowded or cluttered, nor boring and barren -- a band, not a direction"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-21T12:00:41.281Z
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

Related: [[game-is-a-series-of-shooting-galleries]], [[open-work-2026-10-09]].
