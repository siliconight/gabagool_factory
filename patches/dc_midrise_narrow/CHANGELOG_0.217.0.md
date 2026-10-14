## [0.217.0] - three narrow mid-rises: the blocks that fit between the mission's buildings

**Factory roadmap 241, the near side.** Level Factory 0.201.0 fills an urban street's near frontage between
the mission's own buildings, keeping a 4 m passage beside each. On urban_row_001's three candidates (cold run
9288) the rooms left were 12.67 m, 11.35, 7.33, 6.70 and none. The narrowest of the six mid-rises measures
15.3 m, so nothing stood (the factory root's `docs/findings/urban_street/near_room.py`). Real streets carry
two- and three-bay buildings between the wide blocks. This is that capability, grown where it belongs.

- **`presets.EMPTY_MIDRISE_NARROW`**: `gs_midrise_g`, `_h` and `_i`, 12.0, 10.0 and 6.3 m wide (12.3, 10.3
  and 6.6 as built, a wall's thickness more) at 6, 5 and 4 storeys. They are narrower and lower than the six,
  in the family's bricks, and named under its prefix, so Level Factory's urban street draws them with the
  rest. A separate table, so the six keep their own rule of five to twelve storeys with no two the same
  height. Three specs are written from it, and `specs/CATALOG.md` is regenerated.
- **`empty_midrise`'s bays floor at two, not three.** A 6.3 m front holds two windows in the family's 3.2 m
  rhythm, where three would stand 2.1 m apart. No block of the six has fewer than five bays, so their specs
  stand byte for byte.
- **`navgate_baseline.json`** records the three UNJUDGED, as it records every Empty: no interior for a spawn
  marker to stand in. `counts.unjudged` 27 -> 30.
- **`test_empty_midrise_narrow.py`** checks:
  - the three narrower and lower than the six, and named under the prefix;
  - each the preset's own output, an Empty with its windows in the family's rhythm, one door a face at
    grade;
  - the six unchanged by the two-bay floor.

**Built:** `build.py --all` under Blender 5.1.1, 155 shells in 368 s, exit 0, no error in the log. The three narrow blocks build 12.30, 10.30 and 6.60 m wide and 15.30 deep. Each of the 152 shells before them moves by `built_utc` alone, the six mid-rises included, so the two-bay floor moved none of them. `layout_lint --all`: 155 specs, 0 FAIL, 391 WARN, the three adding none

**Suite:** 1,497 passed, 2 skipped, exit 0: 0.216.0's 1,493 and `test_empty_midrise_narrow.py`'s 4
