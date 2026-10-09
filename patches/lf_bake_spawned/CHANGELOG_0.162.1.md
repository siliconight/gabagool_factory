## [0.162.1] - The light bake keeps the responders' car dynamic

**Roadmap 212, found by cold run 9208.** Lot 0.101.0 ships the responders'
cruiser in the package's `cover/`, for the gameplay layer to spawn. The
light bake sets every GLB sidecar in the package to
`meshes/light_baking=2`, Static Lightmaps, unless the GLB carries its own
second UV set (`mark_imports`). So the car's import read `2`, with an
unwrap cache beside it.

**Why that was wrong.** Measured on Godot 4.7, in a throwaway project
holding only the car:

| `light_baking` | the car's five meshes' `gi_mode` |
|---|---|
| `2` | STATIC, on all five |
| `3` | DYNAMIC, on all five |

A static mesh that was not in the bake gets neither the lightmap nor the
`LightmapGI`'s probes; only a dynamic one samples the probes. So a spawned
cruiser would have read darker than the level round it.

**The fix.**
- **`mark_imports(export_dir, spawned=())`** sets each spawned path to
  `DYNAMIC` (3) ahead of the second-UV test. It lists them under `spawned`,
  and a spawned path with no sidecar under `spawned_unmatched`.
- **`bake(..., spawned=())`** passes them through. Its log line counts "N
  spawned set dynamic".
- **`responder_vehicle_scenes(themed_site_dir)`** reads the themed site's
  `responders.json`. The export hands its paths to the bake.

**What it costs.** A module shared by a spawned car and a cover piece would
take its in-scene instances dynamic too: probe-lit, not lightmapped. No
cover piece uses the cruiser.

**Tests.**
- `tests/unit/test_light_bake.py`: a spawned model is set dynamic and an
  unmatched path is said; the report test carries the two new keys.
- `tests/unit/test_responder_arrivals_in_package.py`: the bake is told which
  car is spawned. The helper is tested directly, and the export's hand-over
  by its source, since the bake itself needs a GPU.
- `tests/unit/test_merge_empties.py`: its source-order test now finds the
  bake's call by its opening, since the call takes `spawned` as well. The
  first suite run failed it on the old spelling.

On 0.162.0 these fail 3.

**Suite:** 2,034 passed, 14 skipped, 1 xfailed, 0 failed (exit 0; progress
characters tallied): 0.162.0's 2,032 and the two new tests. The first run
failed 1, the source-order test above.
