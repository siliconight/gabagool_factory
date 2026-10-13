## [0.195.0] - An Empty's stoop stands in the terrace's frontage

**Factory roadmap 240's rowhouse front, with Deli Counter 0.211.0.** Deli Counter now stands every rowhome
Empty three steps up, its stoop's colliders reaching 1.74 m in front of its front face. The terrace
reads a house's extent off its collider hulls (`street_line.shell_extents`) and stands its street edge
on the line, `FRONTAGE` (2.0 m) behind the far sidewalk's back edge. Read whole, each stoop's foot would
have stood on that line and its house 1.74 m behind it: the row and the plate set back for nothing,
and the 2.0 m strip a Philadelphia stoop stands in left empty in front of every stoop.

- **`street_line.shell_extents(glb, skip=())`**: the name prefixes of colliders left out of a shell's
  extent, and `STOOP_COLLIDERS`, Deli Counter 0.211.0's three (`stoop_landing`, `stoop_under_`,
  `stoop_ramp`). Every other caller reads the whole shell as before: a lot's own building keeps its
  porch or canopy off the walk by its furthest solid, and a twin's `stoop_right` volume is its own lot's.
- **The terrace** (`apps/cli`) reads each Empty's extent with the stoop skipped, so its front face stands
  on the line as it did. **`empties.stoop_reach`** measures how far a stoop reaches in front of its
  house, and the CLI reports `EMPTY_STOOP_PAST_FRONTAGE` when one would reach past the strip onto the
  walk -- the check Deli Counter's own test holds against a copy of `FRONTAGE`, made here against the
  real one.

**On the built library:** Deli Counter 0.211.0's twelve rowhomes, read off their GLBs: whole, each street edge is -7.888 m (the stoop ramp's foot); with `STOOP_COLLIDERS` skipped -6.150 m, the edge every rowhome had before; the stoop's reach 1.738 m on all twelve, inside the 2.0 m frontage; the widths unchanged

**Suite:** exit 0, 2,358 by the progress tally (2,343 passed, 14 skipped, 1 xfail); `test_terrace_stoop.py`, 4 checks, needing the `skip` and `stoop_reach` 0.194.0 has not got -- and holding the 1.738 m the terrace would have set each house back read whole
