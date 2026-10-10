## [1.96.0] - the backdrop's tree and warehouse

### What changed

**Roadmap 228.** The walker asked for edges that differ by level. Lot's
`site_backdrop` names five recipes and could lay one, the borough (Zoo
1.95.0's rowhomes and water tower); `parkland`, `roadside` and `yards` laid
the borough with a finding for want of their kits. These are the two
species those kits are made of; Lot 0.109.0 lays them.

- **`backdrop_tree`:** a trunk and one faceted crown, the edge menu's
  mockup's shape, for a belt that stands behind the fence twenty to forty
  metres off and is composed as a few MultiMeshes; bark and the style's
  vegetation, two materials. Not a street tree: those are grown branch by
  branch at two thousand triangles. The crown's twelve facets put a vertex
  on both axes so the extents are the slot's, and its top is the slot's
  top. 3 to 12 m wide, 5 to 16 m tall.
- **`backdrop_warehouse`:** a long low box with three roof monitors, its
  front painted as siding with a roll-up door and a strip of high windows,
  one in three lit cool white by the module's stem; one material, one
  surface, as the rowhome. 16 to 48 m wide, 5 to 12 m tall.
- Both are backdrop: `collision: false`; every part stands exactly the
  slot's dims, the monitors INSET into the roof.
- `cargo_container`, which the yards recipe stacks in its near band, is the
  species it has been since 0.4x; nothing here changes it.

**Built in Blender:** a three-slot kit (trees at 7 x 7 x 10 and 4 x 4 x 6 m, a warehouse at 30 x 16 x 8 m) built in Blender 5.1.1, theme delco: all three PASS, the trees at 132 triangles (bark and vegetation, two materials), the warehouse at 48 with one material and one primitive (`docs/findings/backdrop_kit/backdrop_slots_2.json`, built on the draft).

**The census:** `tools/coplanar_census.py`, three builds a species: "6 builds, 0 with coincident pairs, 0 that did not build", first run; the trunk ends inside the crown and the monitors stand INSET into the roof from the start.

**Tests:** 7 pure in `tests/test_backdrop_2.py` (12 cases), and the
registries carry the two. **Suite:** 4,141 passed, 424 skipped (the builds that need bpy), 1 xfailed, exit 0 on the repo (4,122 as 1.95.0 and the 19 new cases); the draft copy's suite had run with the census count still at 378 and failed that one test, as it should.
