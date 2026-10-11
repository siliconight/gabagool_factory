## [1.99.0] - a container's roof is the dirty face it is from above

### What changed

**Cold run 9226's pale slab.** From the elevated west camera, a cargo
container's top face in the backdrop's near band read as a bright flat
rectangle, (191, 191, 202) at 180 x 40 px, floating over a storefront's
roofline. The roof took the walls' paint at full strength on its crests,
and it is the one face square to the sky.

- **Every roof face takes `ROOF_SHADE`**, the walls' own valley shade
  (`FORM_SHADE["valley"]`, 0.66 of the paint): the darkest face of the box
  from above, the way a box that has sat in a yard wears its weather and
  grime on top. It joins a surface the box already carries, so it costs no
  draw and no triangle; the cost is the roof's ribs, which stop reading
  from above, where nobody stands close enough to see them.
- `_Wall.sheet` takes an optional fixed `shade` for that; the side walls
  and the end keep their per-rib shades.

**Census:** `blender -b --python tools/coplanar_census.py -- --species cargo_container` on Blender 5.1.1, on an unpatched clone and on the patched one: 3,060 / 2,814 / 3,824 tris and 0 coincident pairs at the three corners in both, and 31 exported primitives over the three builds in both -- the roof joins `CargoContainer_RibValleys`, a surface the box already had.

### Tests

1 in `tests/test_cargo_container.py`. **Suite:** 4,154 passed, 424 skipped (the builds that need bpy), 1 xfailed, exit 0 on the repo (4,153 as 1.98.1 and the new test; the container's 51 on the draft copy first).
