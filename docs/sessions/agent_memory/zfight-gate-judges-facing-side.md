---
name: zfight-gate-judges-facing-side
description: "Roadmap 177: DC 0.198.0 makes the z-fight gate judge a pair by the side its faces face; 9189's 436 pairs were 5; frames of the 5 too dark to show anything; block/warn/delete is the walker's call"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-07T02:43:56.311Z
---

Found 2026-10-06 on cold run 9189's composed buildings
(`docs/findings/zfight_by_facing_side/`).

**What was wrong.** The z-fight gate buried a coplanar pair only when a
third solid had matter on BOTH sides of the plane. So bottoms pressed on a
slab counted as flicker: chairs, counters and stair treads with the floor
modules they stand in. deli_a01 read 198, office 121, rail_station 117. Only
5 of those 436 have an open side.

**The fix, DC 0.198.0.**
- `visible_fights` now asks the side the faces face.
- `OUTWARD_GAP` is `themed_tscn.SLAB_CAP_SINK` (mirrored, pinned by a test)
  plus `TOL`: 5.5 mm.
- `_rect_covered` gives a 2-D joint cover with tolerance. The float32 seams
  between slab tiles are 2.4e-7 m.

**The 5 left:**
- two partition-ends inside exterior-wall junctions (deli_a01,
  rail_station_a02);
- the office's reception desk, flush with its ledge.

Framed with `tools/look_shots.py --station` on 9189's walk copy: mean
luminance was 3.5 to 25 of 255, so nothing could show.

**Open:**
- 177's decision is the walker's: block, warn or delete. My recommendation
  was warn.
- Lit or moving frames of the 5.

**How to apply:**
- A gate's count is a claim about what a player sees. Check one instance
  against geometry before acting on the number.
- Use `look_shots --station name:ex,ey,ez,tx,ty,tz` to frame a spot.
