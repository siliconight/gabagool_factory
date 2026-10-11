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

**Census:** RESULT_CENSUS.

### Tests

1 in `tests/test_cargo_container.py`. **Suite:** RESULT_SUITE.
