## [0.159.0] - The light census counts what the renderer pairs, beside what reaches

**The walker, 2026-10-08: "make the perf light census bake-aware".** The perf
harness's lights-per-object census (`tools/perf_stations.gd`,
`_light_census`) counted, per mesh, every positional light whose range
reaches the mesh's box. It never read `light_bake_mode`.

### Why that stopped being the cap's number

**The renderer's rule, read from source.** Godot 4.7,
`servers/rendering/renderer_scene_cull.cpp`, `_scene_cull`, where a mesh's
lights are rebuilt (`FLAG_GEOM_LIGHTING_DIRTY`):
- **A masked light is skipped.** The light's cull mask must meet the mesh's
  layers, or it is never paired.
- **A baked light on a lightmapped mesh is skipped:**
  `if ((RSG::light_storage->light_get_bake_mode(E->base) == RSE::LIGHT_BAKE_STATIC) && idata.instance->lightmap) { continue; }`.
- **Not the Compatibility renderer.** Its own per-instance lists in
  `drivers/gles3/rasterizer_scene_gles3.cpp` read no bake mode, because the
  culler has already left those lights out. *As first recalled:* that the
  skip lived in the GLES3 file. Retracted on reading it.

**What the bake did to the count.** Since the light bake (0.131.0) most Lux
rigs are BAKE_STATIC, and most meshes are lightmap users. On cold run 9204's
package, 82 of 95 positional lights are baked and 3,898 of 3,954 meshes have
a lightmap.
- **It could not see a change of bake mode.** The census read "33 of 3,954
  meshes over 8, worst 31" with the club's stage lamps baked and with them
  live (`docs/findings/club_stage_live_price/` at the factory root).

### The change

- **Two counts.** `_light_census` keeps its reach count in the top-level
  fields, labelled `basis: "reach"`, with their old meaning. It adds
  `paired`: of those lights, the ones `_pairs` says the culler binds.
- **The pairing rules (`_pairs`):** the light is visible in the tree, its
  cull mask meets the mesh's layers, and it is not BAKE_STATIC on a mesh
  that has a lightmap.
- **Which meshes have a lightmap (`_lightmap_users`):** every LightmapGI's
  own users, resolved relative to it the way LightmapGI resolves them. A
  mesh gets a lightmap only by being one; `gi_mode` is not the test.
- **How many in all, not only over the cap.** Each count carries `pairs`,
  every (light, mesh) it holds, and `histogram`, meshes by count. A change
  that moves lights under the cap still shows.
- **Static, and printed.** `_light_census`, `_surface_dist` and `_reach` are
  now static, so a test's own scene can call the census. The harness's last
  line and `tools/perf_stations_run.py` print both counts. The runner says
  when a report carries no paired count.

### Measured on cold run 9204's package

`docs/findings/light_census_pairs/` at the factory root runs the harness on
three fresh copies of the package: shipped, shipped again, and a copy with
the club's two stage rigs switched live (`bake_mode` 1 to 0).

| | over the cap of 8 | worst | light-mesh pairs | lights baked |
|---|---|---|---|---|
| by reach, every copy | 33 of 3,954 | 31 (b0's roof) | 6,143 | -- |
| paired, shipped | 0 | 6 (b1's merged cover) | 1,158 | 82 of 95 |
| paired, live | 0 | 6 | 1,578 | 78 of 95 |

- **The control:** the two shipped copies read identical in every field of
  both counts.
- **The dial:** live against shipped, the reach count does not move -- not a
  pair, not a histogram bin.
- **The paired count does move:** +420 pairs, and its histogram's zero bin
  lost 215 meshes. Still nothing over the cap, and the worst is still 6.
- **Every one of the 33 meshes the reach count put over the cap** was over
  it on lights the renderer never binds to it. Their paired counts run from
  0 to 6, read off the root tool's rows below.
- **The root tool agrees on the walk copy:** `tools/mesh_light_census.py` on
  9204's walk export reads 33 over 8 by reach and 0 paired, worst 6, with
  3,898 lightmap users.

### Tests

`tests/unit/test_perf_census_pairs.py`, 4 tests.
- **Two run the census for real.** A headless Godot builds two meshes, a
  LightmapGI whose LightmapGIData lists one of them, and four lights. Each
  light is one that a single rule removes:
  - one BAKE_STATIC;
  - one dynamic;
  - one with cull mask 1, beside a mesh on layer 2;
  - one hidden.
- **What they hold.** The reach count reads 4 and 4; the paired count reads
  2 and 2. Each rule, missing, would make one of those 3.
- **Two drive the runner** through the stub Godot.
- **On 0.158.0, 4 of 4 fail.** The two Godot tests fail because
  `_light_census` is not static, so the call errors and the scene's watchdog
  quits. The two runner tests fail on the printed text.
- **Suite:** 2,026 passed, 14 skipped, 1 xfailed, 0 failed (exit 0;
  progress characters tallied, since the conftest prints no summary).

**The root tool, alongside.** `tools/mesh_light_census.py` at the factory
root, roadmap 54's closing instrument, had the same blindness. It is given
the same rule (`patches/patch_tools_census_pairs.py`).
