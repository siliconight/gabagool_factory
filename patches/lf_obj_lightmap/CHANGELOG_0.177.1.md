## [0.177.1] - The paint's OBJ meshes bake: the wavefront sidecar's lightmap UV

**Roadmap 231, beside Lot 0.114.0.** Lot ships a site's road markings as
one OBJ per paint colour beside `site.tscn` now, so that 227 marking
submissions become two and the bake still lights them -- a MultiMesh is
not lightmapped, a model is. The wavefront importer generates no lightmap
UV unless asked: measured on Godot 4.7 by importing a one-quad OBJ
headless, its sidecar reads `generate_lightmap_uv2=false` with a texel
size of 0.2.

- **`light_bake.mark_imports`** asks every `*.obj.import` sidecar in the
  package for `generate_lightmap_uv2=true`, as it sets
  `meshes/light_baking` on the GLBs', and lists the mesh under `baked`; a
  sidecar without the line is `unreadable`, said rather than guessed. The
  sidecars themselves come from the export's import pass, as the GLBs' do.
- Nothing else moves; a package with no OBJ reads as before.

**Tests:** 2 in `tests/unit/test_light_bake.py`. **Suite:** RESULT_SUITE.
