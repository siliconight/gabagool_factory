## [1.68.0] - a building's covers merge, one side at a time

Patina's covers -- curbs, base courses, edge strips, conduit, gutters and
downspouts -- reached the level as one mesh each: one draw call for every
visible cover. Measured on cold run 9154's package (roadmap 180):

- **Count:** 3,370 cover instances in gas_block_001, because the six rowhome
  Empties are placed 26 times.
- **Hiding them all:**
  - the worst view goes from 8,690 draws at 27.33 ms p95 to 5,571 at
    17.74 ms;
  - the median view drops 850 draws and 2.06 ms;
  - the control (the same package measured twice) moved 0 draws and 0.05 ms.

### Changed

- **`build_dressing` merges a building's covers, ONE SIDE OF THE BUILDING
  PER MATERIAL** -- through the same `merge.pack_by_material` every module
  goes through. On the rowhome that is 103 covers into at most 8 meshes.
  Never one mesh a building: the export culls by occlusion (1,407 box
  occluders on 9154), and one mesh holding a building's front and back
  covers keeps the back drawn whenever the front is seen. A side enters and
  leaves view together.
- **The side is decided in `core.dressing`, pure** (`cover_side`,
  `footprint`, `SIDES`, a `side` on every plan). Facings are Deli Counter's:
  N = +y, E = +x, S = -y, W = -x.
  - **A wall-facing cover** takes the side its normal leaves.
  - **An up-facing cover** -- a curb at the wall's foot, an edge strip on
    the roof, 60 of a rowhome's 103 -- has no side of its own. It takes the
    side it stands nearest, measured in units of the footprint's half-size,
    so a long building's end curbs go to its end and not its flank. Grouped
    by normal alone, every curb and roof edge of a building would have been
    one mesh the size of the building.
- **Covers are built in place.** Each cover's placement is baked into its
  vertices and its object is left at identity. The merge reads raw
  coordinates and leaves any object with a transform unmerged
  (`merge._identity`), so a placed cover could never have joined a group.
  The placement is a yaw and a translation; nothing it bakes changes a UV, a
  colour or a shading edge, all of which are written before placement.
- **The group is the name.** `dress_cover` names a cover
  `Cover<side>_<kind>`; `partnames.family` is everything before the first
  underscore, so the family is the side. A merged mesh is
  `Cover<side>_<material slug>`, e.g. `CoverN_concrete_delco_1997`.
- **`--no-merge-parts` reaches the dressing**, as it reaches kits: one
  build, the merge off, as the control. `build_dressing` reads
  `merge_parts` like `build_module`, and its result and index carry the
  merge's stats (`merge`) and the count a side (`sides`).

### Corrected

- **`build_dressing` said covers were "already handled downstream"**:
  Level Factory's `extract_meshes.gd` was to merge them "per visible chunk".
  It does not. That script belongs to the surface-clutter layer; the only
  Level Factory code naming `_dressing.glb` is the worldskin's tiling list,
  and the census showed every `Dressing/Cover_*` as its own MeshInstance3D
  (Patina notes on cold runs 9147 and 9152).
- **1.67.0's own cost note repeated it**: "Level Factory merges covers per
  visible chunk and per material". It was wrong for the same reason.
- **That comment's worry was right.** Welding opposite faces of a building
  into one bounding box trades their culling. It is why the unit is a side
  and not the building.

### Not done here, said so

- **`tools/dressing_in_nav.py`** at the factory root tested each
  `Cover_*` mesh's box. After this a mesh is a side, and the name no
  longer starts `Cover_`. That tool is changed in the same breath: its
  prefix matches both names, and it refuses to report a clean result when
  it found no cover at all.
- **The price is a cold run's**: draws and frame time at the same
  stations, A = 9154, B = the merged run, A2 = 9154 again. Also re-read:
  - the lights-per-object census, because a merged side is touched by more
    lights than one cover;
  - the lightmap bake.
