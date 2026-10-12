## [0.194.0] - A site's overhead wires stay out of the lightmap

**Factory roadmap 240, the pole line's wires.** Lot 0.119.0 draws a site's
wires -- three primaries, the neutral, the secondary and two cables on every
span between its utility poles -- as `site_wires_*.obj` beside the scene, one
mesh a 32 m cell, unshaded, on nodes that cast no shadow and take no GI
(`gi_mode = 0`): a wire is a dark line against the sky by day and a silhouette
at night, and unshaded no light ever adds a pass for it. `mark_imports`
(0.177.1) asks every OBJ a package ships for a lightmap UV, so the road paint
bakes like a model; it would have asked the wires too, and counted them in the
bake's "model(s) lightmapped".

**What changed.** `UNLIT_PREFIXES` (`site_wires_`): an OBJ whose name starts
with one is listed under the report's new `unlit` and its sidecar is left as
the engine wrote it -- no second UV made for a 2 cm tube, nothing of the
lightmap spent on it. The summary line is unchanged; `light_bake.json`'s
`imports.unlit` names them.

**Tests:** `tests/unit/test_wires_unlit.py`, two: the paint is asked for a
lightmap UV and a wire is not, each listed where it belongs; the prefix is the
name Lot writes. On 0.193.2 both fail: a wire's sidecar is asked for a lightmap UV and listed under `baked`, and there is no `UNLIT_PREFIXES`. The test pinning `mark_imports`' whole report (`test_static_lightmaps_on_every_model_but_those_whose_uv2_is_shader_data`) gains `unlit`: the first application missed it, and the suite's one failure said so

**Suite:** 2,338 passed, 16 skipped, 0 failed (JUnit, 2,354 tests), where 0.193.2 passed 2,335: the two new tests and the sibling locator's sweep of the new file
