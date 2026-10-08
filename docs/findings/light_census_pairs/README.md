# The light census, made bake-aware (roadmap 213)

**The question.** The walker, 2026-10-08: "make the perf light census
bake-aware". GL Compatibility binds at most `max_lights_per_object` (8)
positional lights to a mesh. Both censuses here counted every light whose
range reaches a mesh, baked or live. They are the perf harness's
(`level_factory/tools/perf_stations.gd`) and the root tool
`tools/mesh_light_census.py`. So:
- Which lights does the renderer actually bind?
- Would switching the club's four stage lamps live push any mesh over the
  limit? Roadmap 213's "not measured".

## The renderer's rule, from source

Godot 4.7, `servers/rendering/renderer_scene_cull.cpp`, `_scene_cull`, the
block that rebuilds a mesh's lights (`FLAG_GEOM_LIGHTING_DIRTY`):
- **A masked light is skipped:** one whose cull mask misses the mesh's
  layers.
- **A baked light on a lightmapped mesh is skipped:** BAKE_STATIC, on a mesh
  that has a lightmap:

      if ((RSG::light_storage->light_get_bake_mode(E->base) == RSE::LIGHT_BAKE_STATIC) && idata.instance->lightmap) {
          continue;

**It is the culler, so it holds for every renderer.** The Compatibility
renderer's own lists (`drivers/gles3/rasterizer_scene_gles3.cpp`) read no
bake mode; the lights are already gone by then.
- *As first recalled* (the 2026-10-08 handoff): that the skip was in the
  GLES3 file. Retracted on reading both files.

**Which meshes have a lightmap.** Those a `LightmapGI` lists as users. That
is how the engine gives a mesh one, and both censuses read it from there.

## The change

- **Level Factory 0.159.0** (`patches/patch_lf_census_pairs.py`): the
  harness's census keeps its reach count and adds `paired`. Each count
  carries `pairs` (every light-mesh pair) and a histogram.
- **The root tool** (`patches/patch_tools_census_pairs.py`): the same rule,
  with `--count paired` to gate on it.

## What it measured

Cold run 9204's club_block_014 package. `census_three.py` runs Level
Factory's harness on three fresh copies, reports in `census_*.json`, the
comparison in `census_three.txt`:

| | over the cap of 8 | worst | light-mesh pairs | lights baked |
|---|---|---|---|---|
| by reach, every copy | 33 of 3,954 | 31 (b0's roof) | 6,143 | -- |
| paired, shipped | 0 | 6 (b1's merged cover) | 1,158 | 82 of 95 |
| paired, shipped again | 0 | 6 | 1,158 | 82 of 95 |
| paired, stage rigs live | 0 | 6 | 1,578 | 78 of 95 |

- **The control:** the two shipped copies are identical in every field.
- **Reach cannot see a bake.** Switching the stage live moved the reach
  count by nothing -- not one pair, not one histogram bin.
- **Paired can.** It moved by 420 pairs. The histogram's zero bin lost 215
  meshes, so those now bind at least one live light. The bins are net
  counts, so they cannot say where each of them landed.
- **The answer to 213's question:** with the four stage lamps live, no mesh
  is over the cap, and the worst is still 6.

**The root tool on the walk copy** (`mesh_light_census_9204_walk.txt`)
agrees: 33 over 8 by reach, 0 paired, worst 6, 3,898 lightmap users.
- **What the 33 really carry.** Their paired counts run from 0 to 6. Every
  one was over the cap on lights the renderer never binds to it.

## What it does not say

- **Both counts take a light's range as a sphere** against the mesh's box,
  including a spot's. Both are upper bounds on what the renderer binds,
  which pairs a spot by its cone's bounds.
- **Range moves it; energy does not.** Pairing reads range and position,
  not energy, so a brighter stage at the same range keeps these counts. A
  longer range would add pairs.
- **No frame was shot.** This counts bindings. The frames that showed the
  stage lamps live are `docs/findings/club_stage_live_price/`.
