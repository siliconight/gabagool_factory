## 0.99.1 - a stage light's aim moves with its club

**Roadmap 207.** `merge_lights` carried each light anchor's `pos` into site
space -- turned and offset with its building -- and copied the rest of the
record verbatim. `target`, the stage light's aim in Deli Counter's club rig,
rode in that copy in the building's own frame.

**What that did.** A club standing off the site's origin aimed both stages at
points near the site's origin. Cold run 9197 placed strip_club_a01 as b2 at
(69, -1.5), unturned, and shipped:
- `b2/main_floor_stage`, pos (73.0, -6.5, 3.2), aimed at (0.0, -5.0, 1.68):
  a 73.03 m throw;
- `b2/vip_wing_stage`, pos (69.0, 5.5, 3.2), aimed at (-5.0, 7.0, 1.68):
  74.03 m.

Lux clamps a stage light's range to 12 m and refused both: `LUX_CLUB_REFUSED`,
42 of 44 club rigs built, and the two refused were the rooms a club is for.
Cold runs 9060, 9167 and 9197 carried the code, and Lux's loader had named
the cause in a comment since 9060.

### The fix

- **`_LIGHT_POINTS` = (`pos`, `target`)**: every point a light anchor carries,
  each placed with its building. With the fix, 9197's stages aim at
  (69.0, -6.5, 1.68) and (64.0, 5.5, 1.68): throws of 4.28 and 5.23 m, as in
  the building.
- **`_LIGHT_NOT_POINTS` = (`size`, `color`)**: numeric triples that are not
  points. `size` is an extent in the light's own frame, which Lux turns with
  `rot_y`.
- **Anything else is refused.** A light anchor carrying a numeric triple in
  neither list raises rather than shipping it in the building's frame. That
  is the rule `_ladder_to_site` keeps, and the defect `target` was.

**Surveyed first.** 131 building light manifests on disk, 2,609 anchors. The
only numeric triples are `pos` (2,609), `size` (1,391) and `target` (7, every
one a `stage_light`). None of Lot's own fixtures carries one the refusal would
trip.

### Tests

`tests/test_light_targets.py` runs against Deli Counter's build of
strip_club_a01's light manifest (`deli_counter/build/`, manifest 1.3.0),
verbatim. A placement is a rotation and a translation, so each stage must
throw as far as it does in its own building -- under Lux's 12 m -- at any
turn and offset:
- three placements: 9197's (69, -1.5) unturned, and two turned 90 and 270
  degrees at other offsets;
- 9197's two targets, exactly;
- an unclassed triple refused.

**On 0.99.0, 5 of 6 fail.** The sixth checks that the fixture holds both
stages.

**Suite:** 701 passed (695 + 6), `python -m pytest -q`.

**Not yet:** a club lit in a level -- the cold run after this, on
club_block_014, where 9167 carried the code.
