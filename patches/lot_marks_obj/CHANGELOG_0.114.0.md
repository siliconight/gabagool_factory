## 0.114.0 - the road paint as one mesh per colour, beside the scene

**Roadmap 231.** Cold run 9233 priced a street for the first time: +107
draws and +0.55 ms p95 a heading median on a 5.7 ms frame
(`docs/findings/street_draws/` in the factory). Every marking was its own
Node3D, its own tiled BoxMesh and its own `StandardMaterial3D`, identical
to the next in every line but the wear offset: 227 submissions and 125
materials for one level's paint.

- **`_marking_meshes`:** one OBJ per paint colour (`site_marks_<colour>.obj`,
  written beside `site.tscn` by the scene writer and declared as a `Mesh`
  ext_resource), every marking a flat quad in it at the paint's top face,
  one `MeshInstance3D` and one material a colour. A MultiMesh would have
  merged them too and is not lightmapped, and the bake is what lights a
  street at night; a model beside the scene imports through the same pass
  as the buildings and bakes like them, Level Factory setting the OBJ
  sidecar's `generate_lightmap_uv2` as it sets the GLBs' light baking.
- **The wear offset survives:** each quad's UVs are what the per-marking
  material's world projection gave it, plan x and Godot z times the pack's
  tile scale plus `paint_offset`'s hash of the marking, and the one
  material maps by UV1 (`_mat_sub(..., triplanar=False)`), so every bar
  wears its own scuffs under one material. The greybox writes the same
  UVs under its flat colour. The face is double-sided (`cull_mode = 2`)
  with an up normal, and has no collision, as before.
- The fields' bay lines are quads in the same meshes. `site.markings.json`
  is unchanged. `_outdoor_nodes(..., files=)` hands the OBJ texts to the
  caller that writes them; without it, the nodes are written and nothing
  is.

**Tests:** 4 in `tests/test_marking_meshes.py`; the four that pinned
`mark_<n>_<kind>` nodes and per-marking materials now read the quads.
**Suite:** RESULT_SUITE.
