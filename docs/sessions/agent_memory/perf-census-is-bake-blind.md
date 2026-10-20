---
name: perf-census-is-bake-blind
description: "FIXED 2026-10-08 (LF 0.159.0 + root mesh_light_census): the light census now counts PAIRED (what Godot binds) beside by-reach; on 9204 reach said 33 meshes over 8, paired says 0 -- cite paired for the 8-light cap"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-08T21:08:39.024Z
---

Both light censuses -- `level_factory/tools/perf_stations.gd` `_light_census`
and the root `tools/mesh_light_census.py` -- counted every positional light
whose range reaches a mesh, baked or live. Godot 4.7's culler
(`servers/rendering/renderer_scene_cull.cpp`, `_scene_cull`) never pairs a
light masked off a mesh's layers, nor a BAKE_STATIC light with a mesh that has
a lightmap (a LightmapGI user). Since the light bake (LF 0.131.0) that made the
reach count wrong for the 8-lights-a-mesh cap.

**Fixed 2026-10-08:** LF 0.159.0 adds `paired` (with `pairs` and a histogram
for both counts); the root tool adds `paired_*` and `--count paired`. Cold run
9204: by reach 33 of 3,954 over 8, worst 31; paired 0 over, worst 6; with the
club's stage lamps live, paired +420 pairs and still 0 over.
`docs/findings/light_census_pairs/`.

**Why:** the walker asked for it 2026-10-08, and roadmap 213's live-stage call
needed the cap measured.

**How to apply:** for the per-mesh cap, cite the PAIRED count; the reach count
is kept for one release only so old and new reports compare. A change of
light RANGE moves pairing; energy does not. Related:
[[performance-beats-graphics]], [[perf-stations-follow-package-anchors]].
