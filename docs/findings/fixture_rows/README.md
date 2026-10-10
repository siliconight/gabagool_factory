# Indoor fixtures stand in a perfect line (roadmap 229): the census

The walker, 2026-10-10: indoor light fixtures should "not always be in a
perfect line, so it looks a little less robotic". Before anything is
designed, this counts what the kit does.

## The mechanism

`deli_counter/lights.py` derives one `fluorescent` row per interior room
(`derive_light_anchors`, line 1166): at the room's centre, along its longer
axis (`_row_for_bounds`, 941), `count = round(length / _TARGET_SPACING)`
held to 1..`_MAX_FIXTURES` (4.0 m, line 137; 5, line 173), `spacing =
length / count`. The lamps spread evenly over the whole room, whatever
stands in it. Zoo expands the row centred on `pos`
(`zoo_keeper/core/fixtures.py:row_points`, the same `start = -(count-1)/2 *
spacing` as Lux's rig) and stands a troffer at every lamp; Lux puts a rig at
every marker. The departures are caused and rare: a run splits at a ceiling
void, a lamp steps 0.40 m off a partition it would hang in, a row lying
along a partition moves to the larger side (DC 0.116.0, roadmap 143). Below
grade and in objective rooms the row is bare bulbs at `area / 25`, on the
same line; the club set is the one layout that steps side to side.

## The count

`row_census.py` over the 131 shipped manifests in `deli_counter/build`
(`row_census.txt`):

- 513 fluorescent rows in 478 rooms; 35 rooms carry more than one run.
- **513 of 513 on the room's centreline; 513 of 513 along its longer
  axis.** No other reading was possible from the code, and the count says
  so.
- Lamps a row: 1 x 41, 2 x 50, 3 x 49, 4 x 70, **5 x 303**. The cap, not
  the room, decides the count in 59 % of rows.
- Spacing runs from 3.0 m to 11.6 m: the five lamps are spread over the
  room's length, so a long room has pools 10 m apart and a short one 3 m.
- The other anchors: 222 pendants (bulbs on a cord, the same line), 32 club
  washes, 15 counter accents, 7 stage lights; 519 windows, 389 wall packs,
  95 signs, 28 canopy washes outside.

## What it does not measure

How the rows READ. The number says every room is lit by the same rule;
whether a given room looks designed is roadmap 18's gate and a person's
eye, and the walker's named it. Frames at interior stations before and after
belong to the fix, not to this census.

## Instruments

- `row_census.py`: reads `*.lights.json` and the `.gameplay.json` beside
  each for the room bounds; prints what it counted and stops.
- `row_census.txt`: the run above, 2026-10-10.
- `row_census_0206.txt`: the library rebuilt on Deli Counter 0.206.0 (the rows laid to the work): 1,156 rows, 4,217 lamps.
- `row_census_0206_1.txt`: the library rebuilt on Deli Counter 0.206.1 (the home rule keyed on the room's words): 1,140 rows, 4,133 lamps; ten more rooms take the home's one fixture.
- `aisle_census.py`, `aisle_census_0206_1.txt`: the AISLES the rows could follow, from the furnished specs (step 2 of the fix): 514 of 702 rooms carry a shelf volume, 293 of them with two or more lanes at least an aisle (1.25 m) wide across the room's long axis; the lane widths and what 0.206.1 lays in those rooms.
- `aisle_rows_diff.py`, `aisle_rows_diff_0207_draft.txt`: the rows two Deli Counter trees derive for the same furnished library, 0.206.1 against the 0.207.0 draft (`patches/patch_dc_aisle_rows.py`): 322 rooms identical, 165 changed, which are the 61 rooms the draft lays over their aisles and the 114 where the lamp cap bound and the long hall's trade gave rows across for lamps along (some rooms are both); rows moved 448, added 4, removed 125; lamps 4,374 to 4,099. The aisle rule alone (the draft's first form) changed 61 rooms and nothing else. Derived with a flat cap and no partitions, so its lamp totals are not the library's; its deltas are.
- The references the walker supplied are digested in
  `docs/reference/INDOOR_FIXTURE_PLACEMENT_GUIDE.md`.
