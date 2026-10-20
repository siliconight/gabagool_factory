# Is the pipeline using MultiMesh where it should? (2026-10-19)

The walker, with Godot 4.7's MultiMesh page: "Are we doing this intelligently?" -- "at a high level if we are using it
for our total pipeline, not just openings". This measures one shipped level rather than arguing from the code.

**What MultiMesh is for (the 4.7 page):** drawing ONE mesh many times in one submission. The whole set is one object
to the culler ("every single instance will always render" if any is visible) and to the per-object light limit (8
on GL Compatibility; "once lights are used up, the remaining instances receive no lighting"). It carries per-instance
transforms, colours and custom data. The 4.7 lightmap pages name `MeshInstance3D` as what `LightmapGI` bakes and say
nothing of MultiMesh, so whether a MultiMesh can carry baked light is **unknown here, not assumed**: a bake test
settles it.

## Instrument

`instancing_census.gd` (headless; it reads values and quits). It instances the package's own entry, `mission.tscn`
-- the baked level, the dressing layer and the backdrop it loads -- groups every `MeshInstance3D` by the identity of
its Mesh resource, and records each group's node count, surfaces, triangles, how many of its nodes bake (`gi_mode`
static) and cast shadows, and the branch they stand in. `MultiMeshInstance3D` nodes are listed with their instance
counts. It counts the POOL draws come from (a surface submits only when in view and unoccluded, and shadow passes
submit again); `level_factory/tools/draw_attrib.gd` measures draws at stations.

Run on cold run 9339's walk copy (restaurant_row_001, Level Factory 0.219.0, Deli Counter 0.235.0):
`census_9339.log`, `census_9339.json`.

## What it measured

| | |
|---|---|
| separate mesh nodes | 3,587, in 1,958 distinct meshes |
| surfaces, the draw pool | 3,798 |
| in meshes shared by >= 2 nodes | 2,403 (63.3 %), every one baked |
| in meshes shared by >= 8 nodes | 951 (25.0 %), every one baked |
| in meshes shared by >= 32 nodes | 706 (18.6 %), every one baked |
| MultiMesh nodes | 29, carrying 4,401 instances |

By where they stand: **the buildings hold 2,576 of the 3,798 surfaces (68 %)** -- wall and wall-end panels 796, light
fixtures 400, and 1,380 in other props (shelving 306, desks 88, cartons 87, cubicles 66, filing cabinets 46, windows
46, ...). The street's covers 432 (parking meters 46 + 46, three callery-pear meshes 12 each, utility poles 8 x 4),
the edge's segments 374, the ground's box meshes 155, hung posters and flyers 12. The most repeated mesh is a 12-
triangle wall panel standing in 173 separate nodes.

The MultiMeshes are the two layers built for them: the surface dressing (4 MultiMeshes, about a thousand rubble,
pebble, litter and weed instances each) and the backdrop (25: one a module a side).

**Corrected, kept:** the census's first category pass put 248 nodes under "dressing". They are the empty rowhomes'
merged facade covers (`gs_empty_rowhome_*_dressing_Cover*`); the matcher took "dressing" from their names. The
dressing layer itself is the 4 MultiMeshes.

## What it means

- **MultiMesh is used where it fits** -- many copies of one mesh nobody needs baked light on: ~4,100 dressing
  instances in 4 submissions, the backdrop in 25.
- **Everything else repeated is baked static geometry.** Turning those groups into MultiMeshes would trade the bake
  for probe light (unless the bake test says otherwise) and make each set one culling object. Not the lever.
- **The lever the numbers point at is MERGING, per room and material, inside enterable buildings** -- what the
  Empties already do per side (Level Factory 0.143.0) and the covers per side per material (Zoo 1.68.0). A merged
  mesh keeps its lightmap (it gets its own UV2), and a room is the unit that becomes visible and invisible together,
  which is CLAUDE.md's rule for how big a merge may be. The candidates are the 796 wall-panel surfaces, the 400
  fixture surfaces and the interior props, about 2,500 surfaces of the 3,798. What a merge saves is draws at stations
  standing in those rooms, measured the way the cover merge was priced (two controls, draws and frame time) -- not
  this pool.
- **One rule the measurement contradicts:** CLAUDE.md says a MultiMesh should be "one ... per room, block or wall run
  -- never one for the level". The dressing layer is one a species for the whole site: 4 submissions always on,
  every instance vertex-processed every frame (about 4,100 instances). Draws are the budget here and four is cheap;
  whether the always-on vertex work matters on a low-end GPU is unmeasured.

Roadmap 266 carries the merge; the dressing partition is noted there, unmeasured.
