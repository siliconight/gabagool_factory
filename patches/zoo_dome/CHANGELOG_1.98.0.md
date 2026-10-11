## [1.98.0] - the dome a home's room hangs

### What changed

**Roadmap 229's species step.** Deli Counter lays a home's rooms by its own
rule, a fixture a 7 m bay (its 0.207.1), and every one of them was a 2 x 4
office troffer: a fluorescent in a bedroom. A home's room takes a `dome`
anchor from Deli Counter 0.208.0, and this is its hardware.

- **`dome_fixture`**, a new species: a round pressed-steel canopy against
  the ceiling, a frosted glass bowl hanging from its underside -- the lower
  half of an ellipsoid, built as the upper-hemisphere helper mirrored and
  turned back outward, its open rim closed by the canopy rather than laid on
  it -- and a small finial sunk half into the bowl's lowest point. 0.22 to
  0.40 m across, 0.08 to 0.16 m deep, 0.30 by 0.11 m by default. The glass
  is `M_Dome_Lens`, the name Lux's emissive binder keys on.
- **`fixtures.FIXTURES["dome"]`** builds it, mount `hang`: Deli Counter
  writes the anchor at the ceiling plane, so the canopy's top lands there
  and the glass hangs below, as the club's cans do. Without the row the
  type would be skipped, and a skipped anchor emits no marker: a dark room.
- **Census:** `blender -b --python tools/coplanar_census.py -- --species
  dome_fixture pendant_fixture` on Blender 5.1.1 -- the pendant beside it as
  the control that the census sees a pair, its known one reproduced -- read
  the dome's three corners at 292 tris and 0 coincident pairs, first run;
  the genome's budget is that 292.

### Tests

1 in `tests/test_fixtures.py`; the species in `tests/test_genome.py`'s
props; `tests/test_coincident_faces.py`'s census three builds longer.
**Suite:** RESULT_SUITE.
