## [1.98.1] - the dome's glass hangs, and the dome is two meshes

### What changed

**Cold run 9239 saw the dome and priced it,** and both readings were
wrong for the same release.

- **The glass hung up, into the ceiling.** The frames showed a dark canopy
  and a finial hanging alone under it. Measured in the shipped fixtures
  GLB, the glass spanned from the canopy's underside to 5.4 cm ABOVE the
  ceiling plane. `geometry.add_hemisphere` documents an upper half and
  keeps the lower one -- printed in Blender 5.1.1: z -1 .. 0 at unit
  radius, faces down and out -- and 1.98.0 mirrored what it took to be an
  upper half downward. Each vertex is now laid at `rim - |z|`, so the bowl
  hangs below the rim whichever half the helper keeps, and its rim rises
  `BOWL_BURY` (4 mm) into the canopy and is closed there: a closed shell,
  so the finisher's normal recalculation has an inside to face away from.
  Built in Blender: the glass from 3.7 cm down to -4.5 cm in the module
  frame, under the canopy's underside at 3.3 cm, its faces pointing down
  and out.
- **A dome cost one more draw than the troffer it replaced.** The fixtures
  GLB keeps each fixture's parts as separate meshes (a layer, not a
  module, so it is exported unmerged), and the canopy and the finial share
  one material but were two objects: three meshes a dome where a troffer
  is two. 9239 measured exactly that, +6 draws at 24 of 53 headings for its
  six domes. They are one object now.
- **Census:** `blender -b --python tools/coplanar_census.py -- --species
  dome_fixture`, 310 tris at all three corners -- the closed rim's 18 --
  and 0 coincident pairs; the budget is 310.

**Not fixed here, and recorded:** the four other callers of
`add_hemisphere` -- `bollard`, `exhaust_fan`, `soda_cup` and `helmet` --
place it as a cap on top, so each builds its cap hanging inside its body.
Each needs its own census and frame (the factory's roadmap).

### Tests

1 in `tests/test_fixtures.py`. **Suite:** RESULT_SUITE.
