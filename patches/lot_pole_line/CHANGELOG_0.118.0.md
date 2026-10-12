## 0.118.0 - the pole line: one kerb of every street carries wooden utility poles, and the poles carry its lamps

**Factory roadmap 240**, the walker's Philly comps (`docs/reference/PHILLY_STREET_COMPS.md`
at the factory root): in two of the three photographs the overhead network is
the strongest line in the frame -- a wooden pole at the corner carrying a
cobra-head, cobra-heads on poles along the rowhouse street, wires overhead --
and Lot stood a steel lamp on both kerbs every 25 m and not one pole. The
walker's calls of 2026-10-12 (`docs/proposals/POLE_LINE_DESIGN.md`): one side
of every street; a cobra-head on every pole; a transformer can every third or
fourth pole; the full wire set without house drops, which is the next release.
Zoo 1.104.0 built the pole.

- **`site_poles.py`, the line.** One kerb of every road with a sidewalk, the
  one with fewer dropped kerbs and shop bands to dodge (`pole_kerb`; a stable
  hash of the road only breaks a tie). Per run -- a kerb broken at each road
  crossing, so a corner pole stands each side of a junction's mouth and a span
  crosses it -- poles evenly spaced no more than `POLE_SPAN` (36 m, 118 ft)
  apart (`stations`), each stepped along up to 6 m off a dropped kerb, a piece
  the band already stands, a parking meter, a shop band or a marker. Planned
  last on its band, so nothing else has to know where it is.
- **Where it stands.** `POLE_INSET` (0.61 m) from the kerb face to the pole's
  centre: 18 in from the curb's face to the pole's (AASHTO) and its radius.
  Not on the furniture line 0.45 m from the band's building edge, where the
  crossarm, 1.22 m behind the pole at 10 m up, would stand in a rowhouse's
  front wall; here it stops 1.17 m short of the building line on a 3 m band
  and the cobra-head hangs 1.56 m over the near lane. The cobra-head faces the
  road: the pole takes the road's angle on the left kerb, plus 180 on the right.
- **The lamps are on the poles.** A band road stands no steel `streetlight` on
  either kerb now; every pole's light hangs at its cobra-head's lens
  (`site_poles.lens_point`: 2.171 m toward the road on the arm, 7.401 m up), a
  `streetlight` anchor as before, so Lux's rig, its photocell and its
  every-third-pole failing ballast are unchanged. A lane, which has no band,
  keeps its own lamps (0.116.0). The trees keep the stations the lamps'
  spacing gave them.
- **A can every third or fourth pole**, by cause: on whichever of the first
  four poles the most buildings front, then the better served of the 3rd and
  4th pole after the last one (the nearer when they tie); a window serving
  nothing carries none (`_transformers`). The can's pole asks Zoo for its
  `transformer` form, 0.46 m wide.
- **The pole is the record; the module is not centred on it.** A pole
  record's `at` is the pole a body meets -- the greybox box, the navmesh carve,
  the markers' clearance, a flyer's sleeve -- and `module_at` is its slot's
  centre, 0.615 m toward the road (Zoo's `POLE_AT`: the cobra-head reaches
  2.45 m one way and the crossarm 1.22 m the other, and `fit_exact` centres
  the drawing's bounds). `write_site_slots` and the scene writer stand the
  module there; `write_site_slots` writes the can's form; `COVER_MATERIALS`
  says wood.
- **Flyers go on the poles** (`site_posters.POLES`): the street's lamps were
  half the poles a flyer went on, and a wooden utility pole is the classic one;
  the sleeve clears its corners at grade (0.15 m).
- **The numbers Zoo owns are mirrored** (`POLE_DIMS`, `POLE_AT`, `LENS_AT`,
  `WIRES`), pinned to literals here and there, as `BLADE_DIMS` is.

**Measured:** On the four stored site fixtures of cold runs (bank_block_001 seed 9256, club_block_014 seeds 9080 and 9181, restaurant_row_001 seed 9205), 0.117.0's 18, 20, 15 and 16 steel lamps become 8, 9, 9 and 9 poles carrying 3 cans each, with a light at every pole's lens -- 8, 9, 9 and 9 street lights where there were 18, 20, 15 and 16, the walker's pools with dark between; the trees (16, 21, 18, 14) and the hydrants (3, 3, 2, 2) as they were (the factory's `docs/findings/pole_line/pole_census.py`, each version's planner on the same specs). On the kerb probe the first kerb now takes every corner hydrant the site's spacing allows, its lamps having refused two: four hydrants across both kerbs become three on one

**Tests:** `tests/test_site_poles.py`, eleven: the mirrored numbers; one kerb
carries the line and no band road stands a steel lamp; the line stands its
inset from the kerb face, the cobra-head toward the road; no further apart
than a span and its steps; clear of the cuts and the meters; every pole's
light at its lens, END TO END through the transform the scene writer emits
(Zoo's lens point in the module's frame, carried by `_godot_transform` of the
slot, lands on the anchor); the slot stands the module at `module_at` with
its form and material; the stems are the ones Zoo 1.104.0 built; a can every
third or fourth pole where buildings are served, and none where they are not;
the line takes the kerb with less to dodge. The tests that held a steel lamp
on both kerbs are restated for the line -- `test_site_furniture.py`'s spacing,
slot-height and tree tests, `test_site_band_clear.py`'s lamp tests (a pole now
steps out of a band and the finding names it), `test_lot.py`'s
lights-on-poles test (the light at the lens, not on the axis) and
`test_lane_lamps.py`'s street half. On 0.117.0 the three files that import `site_poles` fail to collect, the eleven new tests with them, and of the restated tests the two in files that collect fail (`test_lights_stand_on_the_poles_the_site_stands`, `test_the_streets_keep_their_bands_and_the_names_stay_the_sites`)

**Suite:** 808 passed, where 0.117.0 passed 797: the eleven new tests
