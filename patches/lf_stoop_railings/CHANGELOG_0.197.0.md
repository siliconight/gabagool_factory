## [0.197.0] - A stoop's railings stand in the frontage with it

**Factory roadmap 240, with Deli Counter 0.212.0** (the walker's calls of 2026-10-13: "3 risers,
concrete, railings both sides -- build the railings"). Deli Counter 0.212.0 stands an iron railing on
each side of every rowhome Empty's stoop. It writes their colliders as it writes the stoop's: a box along
the landing, and a slab under the flight's rail. The terrace reads a house's street edge off its collider
hulls and leaves the stoop's out (`STOOP_COLLIDERS`, 0.195.0). Read with the house, each railing's flight
would have been the house's street edge -- its slab's low corner 1.4088 m in front of the facade on all
twelve built rowhomes -- and the terrace would have stood every one of them that much further back.
Read off the shells with the reader the terrace uses (`glb_collision.collision_solids`), by the factory's
`patches/lf_stoop_railings/rail_hulls.py`: `rail_hulls_0196.log` on 0.196.0, where 0.195.0's three
names are skipped and the street edge is at -7.5588 against the facade's -6.15 on every shell.

- **`street_line.STOOP_COLLIDERS`** names the railings' colliders too: `stoop_rail_`, Deli Counter's
  `stoop_rail_<w|e>_<level|flight>_col`. A twin's `stoop_right` volume is still its building's; the
  prefix stops at the name's boundary.
- The merge already reads the railings as the front (`merge_empties.gd`, `stoop_*` -> S, 0.196.0): one
  more surface a side, the iron's.
- `tests/unit/test_terrace_stoop.py`: the railings' hulls, as the reader gives them off a built
  `gs_empty_rowhome_a`, leave the house's extent and the stoop's reach as they were. Skipping only
  0.195.0's three, the flight is the street edge. Fails on 0.196.0.

**Suite:** exit 0, 2,360 by the progress tally (2,345 passed, 14 skipped, 1 xfail): 0.196.0's 2,359 and `test_a_stoop_s_railings_are_the_stoop_s_not_the_house_s`, which fails on 0.196.0, run against an export of it, with the house's street edge at -7.5588 where its walls end at -6.15
