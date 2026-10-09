## 0.102.2 - a parking meter's windows face across the kerb, one to the sidewalk

**Roadmap 219, the walker's note 4:** "street parking payment 'boxes' should
face toward the sidewalk, rotating 90 Degrees".

**The model.** Zoo's `parking_meter` carries a display window on each wide
face, at its +-Y (`recipes/parking_meter.py`).

**Why it faced the street.** `plan_meters` stood every meter at the road's
angle + 90. On the kerb probe, a meter's `plate_facing(yaw)` came out as
(1, 0), along the road's `along` (1, 0): both windows looked up and down
the street.

**Fixed.** The meter stands at the road's angle, so the windows look across
the kerb, one to the sidewalk and one to the bay. The head is two-faced, so
the same turn serves both kerbs and neither is turned round. Its footprint
along the band is now the head's 0.22 m width rather than its 0.14 m depth.
The bays are 6 m apart, so nothing else moves.

**Not this release's.** Zoo's recipe comments its width as "the head,
across the kerb", which described the old stance.

**Tests.** `test_a_meter_faces_across_the_kerb` asserts every meter's face
is square to the road on both kerbs. It fails on 0.102.1.
