# Patina's anchor normals point into the building (roadmap 221)

**Question.** In cold run 9217's dressing orders for strip_club_a01, the
covers Patina derives from its anchors faced into the building. The covers
it derives from DC's slots faced out (roadmap 221). Item 221's likely cause
was "NOT verified": for a Y-up shell, `anchors._up_to_z` permutes positions
(x, y, z) to (x, z, y). That permutation is a reflection, and
`_exterior_wall_faces` takes each normal from a cross product of the
permuted positions.

**Step 1, done: every derived wall normal points in.**
- `probe_normals.py` loads the shell the way `patina.cli.run` does, takes
  the anchor pass's own view, and lists `anchors._wall_segments`.
- Measured 2026-10-10 on `deli_counter/build/strip_club_a01.glb` (Patina
  0.29.2): the visual AABB is 34.3 x 3.9 x 24.3 m, Y up, with 10 wall
  segments.
- **All 10 segments' derived normals point toward the building's centre,**
  dot -1.00 each.
- **The same faces with their winding taken first all point out.** That is,
  the cross product taken in the file's frame and only then permuted as a
  vector.

So the reflection inverts the normal. The anchor pass runs every height,
offset and side on that inward normal.

    shell strip_club_a01.glb, up axis Y
    visual AABB, file frame: [-17.15  -0.3  -12.15] to [17.15  3.6  12.15]
    centre (anchor frame, x y): 0.000 0.000; 10 wall segments
    axis along     fixed    derived normal      centre->wall     dot     winding first
       x     y   -17.000   (+1.00, -0.00)   (-1.00, +0.00)   -1.00   (-1.00, +0.00)
       y     x    12.000   (+0.00, -1.00)   (+0.00, +1.00)   -1.00   (+0.00, +1.00)
       x     y    17.000   (-1.00, +0.00)   (+1.00, +0.00)   -1.00   (+1.00, +0.00)
       y     x   -12.000   (+0.00, +1.00)   (+0.00, -1.00)   -1.00   (+0.00, -1.00)
       y     x   -12.150   (-0.00, +1.00)   (+0.00, -1.00)   -1.00   (-0.00, -1.00)
       ...                                       (10 of 10 at -1.00)

**RETRACTED, kept.** The probe's first run skipped `bake_visual_transforms`.
Patina holds each primitive in its node's local frame until that bake, so
that run measured one slab tile's frame, 7 x 3.3 x 4.8 m, and called its
four faces "wall segments". Its verdict, all four pointing in, was right by
accident and is not evidence. The run above replaced it.

**Step 2, done: nothing downstream compensates.** Zoo takes the normal as
given, twice:
- `bpylayer.build._orient_matrix` turns each cover so its proud +Y axis
  points along the order's normal (`dressing.strip_yaw`);
- `dressing.cover_side` puts a wall-facing cover on the side its normal
  leaves.

So an inverted normal turns a cover's face to the wall and files it with
the opposite side. Fixing the normal in Patina fixes both, and Zoo needs no
change. Inside Patina, `_seg_point` puts an anchor ON the segment's plane;
nothing offsets along the normal.

**Step 3, done: why 22 base courses stand on the centre line.** It is a
second defect, not the inverted normal. `surfaces.classify` calls a face an
exterior wall when it is vertical, faces outward in the file's own frame
(correctly: it takes that normal before any permutation), and stands within
`_BOUNDARY_TOL`, 0.25 m, of the visual AABB. Measured on the same shell, the
faces 0.15 m inside, on the 0.3 m wall's centre line (x +-17.0, y +-12.0),
are:
- `slab_0` and `slab_1`'s edges: 70 a long face and 98 a short one, where
  each floor slab stops under the wall;
- the ends of interior walls meeting it: `int_0_0_seg0` and
  `int_0_1_seg5`, 10 each.

All of them qualify, and become wall segments of their own, behind the real
face. Base courses ordered on them stand inside the wall.

**The fix, shipped as Patina 0.30.0:**
1. **The normal's sign comes from the reflection.** Both of `_up_to_z`'s
   permutations are reflections, so `_exterior_wall_faces` negates its cross
   product whenever the view is one. A view that is a rotation instead,
   (x, y, z) to (x, -z, y), would move the canonical frame that
   `blender_to_canonical` composes and every pass agrees with: the larger
   change for the same result.
2. **A point inside a wall is skipped** (`anchors._buried`). That is a point
   with a face of the same facing standing in front of it, within 0.5 m,
   across its run position and its height.
3. **A conduit stands on its wall,** at its segment's plane rather than at
   the pack, which DC stands `_WALL_PACK_OUT`, 0.15 m, proud of the face.

**RETRACTED, kept: the first draft of 2 dropped whole segments.** It dropped
a segment only when a face covered all of its run and height, and on the
club none was covered. The centre-line segments run from -0.3 to 3.6 m, the
floor slab under the wall and the roof slab over it, against the face's 0.0
to 3.3. Replayed, that draft still ordered 28 base courses on the centre
lines. Per point, a base course at the foot is buried, and a roofline on the
roof slab's exposed edge is not.

**Measured, Patina's own dressing job replayed on the shell**
(`replay_dressing.py`, which reads the orders through Zoo's
`plan_dressing`):

    strip_club_a01, 0.29.2: 247 orders
      cover            all walled  outward  own side  inside
      base_course       51     51        0         0      44
      conduit_run        2      2        0         0       0
      gutter_run        65     65       65        64      35
    strip_club_a01, 0.30.0: 241 orders
      base_course       45     45       45        45       0
      conduit_run        2      2        2         2       0
      gutter_run        65     65       65        65       0

By plane:
- **0.29.2:** 28 of the 51 base courses stood on the centre lines (x
  +-17.0, y +-12.0), and 52 of the 57 curbs.
- **0.30.0:** every one of both stands on an outer face (x +-17.15, y
  +-12.15).
- **The `wall_base` anchors** go from 64 (the per-kind clamp) to 54. The
  clamp had been spending anchors on the centre lines.

The "inside" column measures against the orders' own footprint. On 0.29.2
that footprint is the pack-proud conduits' box, which is why a gutter there
reads as inside.

**Not yet measured: the merge's price.** It needs a cold run, at stations
that face one side of a building.
