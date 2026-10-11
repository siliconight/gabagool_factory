## 0.116.0 - a lane lights its own length

**The walker asked for the design calls, 2026-10-11, and this is the dark
lane's.** A road without a sidewalk -- the `block` grammar's service lane,
an alley -- stood no furniture at all, lamps included: `plan_furniture`'s
band loop skips a road with no band. Cold run 9233's lane read black at
dusk between two lit streets, and so did 9236's and 9237's. Measured on
9237's lights manifest: the nearest light to the lane's centre line was a
wall pack 14.4 m off it, over a rear door, at a 5.5 m reach. The row's
rear walls stand 14 m back, and the far side is the plate's edge, so wall
packs on the rear walls -- the first call, made before the measurement --
could not reach it.

- **`plan_lane_lamps`** stands the street's own lamp along a lane: as many
  as its slab carries at **`LANE_LAMP_SPACING`** (40 m) and at least one,
  spread evenly so the first and last stand half a spacing in from the
  mouths. 40 m is further apart than two of the lamp's 14 m reaches, so a
  pool ends before the next begins: a lane lit by the odd pole, not a lit
  street, with the dark between kept.
- **`lane_side`** picks the side the buildings the lane runs behind stand
  on (by their centres within 45 m across it); a lane with none in reach
  takes its left. The pole stands `LANE_LAMP_OUT` (0.6 m) beyond the paved
  edge, on the ground, and steps along the edge clear of a spur or a mouth
  crossing it, as a street lamp steps clear of a kerb cut.
- Each becomes a light like any street lamp (`_streetlight_anchors`), at
  grade rather than on a kerb. A station with no room is said as
  `LOT_LANE_LAMP_SKIPPED` in the furniture findings and stood nowhere.

**Tests:** 5 in `tests/test_lane_lamps.py`. **Suite:** RESULT_SUITE.
