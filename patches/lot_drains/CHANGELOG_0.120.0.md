## 0.120.0 - the street's drains: manhole covers and storm inlets

**Factory roadmap 179**, filed by the walker on 2026-10-04 with five photographs: "in various locations,
usually on sidewalks, we should have manhole covers, sewer drain grates (should be like fire hydrants
where there is only so many in shared area)". The rules were read at source first, as the hydrant's
spacing was (the factory's `docs/reference/STREET_DRAINS.md`).

- **`site_drains.plan`**: a sanitary manhole cover at every road-road junction, at its centre where the
  mains cross, and along a street no two farther apart than 400 ft (121.9 m), the Ten States figure
  for sewers of 15 in and under -- none at a road's end at the site's edge, which is not its sewer's;
  a storm inlet upstream of each junction's crosswalk and ramp (TxDOT's inlet locations), in the gutter
  against the kerb on the block side of the cut, ONE A CORNER by the hydrant's `corner_key` -- the
  walker's "only so many"; and a lid in the sidewalk a step behind an inlet (the walker's photograph),
  no two nearer than the hydrant's site-wide minimum and never under a piece of furniture. Inlets
  between corners follow the gutter's spread, which needs a grade and a design storm: not placed.
- **Sizes from standards and catalogues**: a 24 in sewer frame and cover (the lid 25 5/16 in, the frame
  32 3/16 in), a 2 x 3 ft curb inlet grate; the sidewalk lid's 18 in is the photograph's.
- **`site_drains.meshes`**: the frame a ring and the lid a bevelled disc a step above it, carrying a
  band where a cover's one cast word goes and a field of studs; the grate a frame round a dark well,
  nine bars across it, and a dark throat in the kerb face behind it; the lid in the sidewalk a frame
  and a plate. Every piece is a floater (Zoo's README, roadmap 234): a 4 mm skirt into the surface,
  and 3 mm proud of whatever is drawn there -- the road's paint is 3 mm proud of the asphalt, so a
  cover's frame stands 6 mm and nothing fights a crosswalk's bars. One mesh a material (the iron, the
  dark) a 32 m cell, an OBJ beside the scene as the paint and the wires are, lightmapped by Level
  Factory's bake as the paint is, casting no shadow; no collision -- a body walks over a cover.
- **With the art only** (`_outdoor_nodes`, after the wires): a candidate's greybox lot, which Laser Tag
  and the walk test grade, carries none (factory roadmap 242). Lot prints the count it stood.

**On the lot cold runs build** (cold run 9262's seed_9104: a main road, two side streets at a T, a
lane): 4 manhole covers, one at each junction (the main road's two T's and the lane's two), none along a run (no stretch between junctions reaches 121.9 m); 8 inlets, two corners at each T, the lane's mouths among them; 4 sidewalk lids, each a step behind an inlet and no two nearer than 45.7 m; 4,184 triangles in 8 meshes (4 cells, the iron and the dark)

**Suite:** 826 passed; `tests/test_site_drains.py`, 7 checks, the greybox-and-themed one failing on 0.119.2 with the module beside it and no hook
