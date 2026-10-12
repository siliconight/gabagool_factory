## 0.119.0 - the pole line's wires: the full set along every line and across each junction, with the art only

**Factory roadmap 240, build 3.** The walker's call of 2026-10-12: the full
wire set without house drops -- three primaries on the crossarm, the neutral,
the secondary and two communication cables. 0.118.0 stood the poles; this
strings them.

- **Spans** (`site_poles.spans`): each line's consecutive poles, and each
  line's end pole tied to the nearest pole of another road's line within
  `LINK_MAX` (30 m) -- a side street's line tapping the main line, which may be
  a pole in the middle of it -- every pair once.
- **A wire** (`wire_path`): a parabola through the two poles' attachments
  (Zoo's `WIRES`, turned by each pole's yaw), sagging `SAG` of the span at its
  middle: 2.5 % for the primaries and the neutral, 3 % for the secondary, 2 %
  for the cables, which hang on a messenger pulled tighter.
- **Drawn** (`_tube`, `wire_meshes`): a four-sided tube in twelve segments,
  at about twice a real conductor's radius (1.2 to 2.2 cm) as the fence's
  tension wire is -- a real 1 cm line is under a pixel at any distance a player
  reads it from, and a line that comes and goes between frames is the walk's
  jitter. One mesh a `WIRE_CELL_M` (32 m) cell by each span's middle, the
  paint's partition, written as an OBJ beside the scene; one material,
  UNSHADED -- so no light ever adds a pass for it on GL Compatibility --
  double-sided; every node `cast_shadow = 0` and `gi_mode = 0`. No collision.
  Level Factory 0.194.0 keeps the OBJs out of the lightmap's import marking.
- **With the art only.** `_outdoor_nodes` strings them in a themed site, whose
  cover stands as Zoo's modules, and never in a candidate's greybox lot: Laser
  Tag and the walk test grade those lots, Lot's walk navmeshes parse visual
  meshes (`geometry_parsed_geometry_type = 2`), and roadmap 242 measured a
  grade on such a lot moving with any change to what stands on it. A wire is
  visual; it cannot move a grade.

**Measured:** On cold run 9262's lot (its drawn spec, with 0.118.1's corner pole): 12 poles and 11 spans -- 9 along the three lines and 2 ties, each side street to the main line -- from 12.7 to 33.2 m; 7 cells, so 7 draws for every wire on the site and 7,392 triangles; the lowest cable 5.43 m over the road

**Tests:** `tests/test_site_wires.py`, six, on cold run 9262's roads: the spans
are each line's and a tie across each junction (both side streets to the main
line, every pair once, every tie within reach); a wire hangs from its poles'
attachments and sags its share; the lowest cable clears 4.7 m over a road on
every span; one unshaded, shadowless mesh a cell, the vertex, normal and face
counts the spans' own; a line of one pole strings nothing; a greybox lot draws
no wires and a themed one does. On 0.118.1 all six fail: `site_poles` has no `spans`, `wire_path` or `wire_meshes`

**Suite:** 815 passed, where 0.118.1 passed 809: the six new tests
