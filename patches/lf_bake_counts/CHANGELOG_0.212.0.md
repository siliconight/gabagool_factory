## [0.212.0] - The light bake counts what it bakes

**The factory's roadmap 251**, found writing cold run 9308's notes (the factory's `docs/cold_runs/cold_9308/NOTES.md`).
`[export] light bake: N model(s) and M primitive mesh(es) lightmapped` printed the sum of `add_primitive_uv2`'s
per-scene counts, and that function wrote `add_uv2 = true` on every inline primitive in every scene of the package.
Measured on 9308's `light_bake.json`: `site.tscn` 112, `presentation/lux.applied.tscn` 112, `site_backdrop.tscn` 1,
the log's 225. `bake.tscn` instances the presentation alone, so the content scene's 112 were the same primitives
counted a second time. The backdrop's ground (0.211.0), which `mission.tscn` loads at run time outside the bake and
`bake.lmbake` does not name, was counted as lightmapped and given a UV2 nothing uses. 9305's log read 224 the same
way.

- **`baked_scenes(export_dir)`:** the scenes the bake draws -- the presentation and every scene it instances,
  transitively -- package-relative and sorted.
- **`add_primitive_uv2(export_dir, only=None)`:** with `only`, it writes and counts those scenes alone. `None` is
  every scene, as before.
- **The export** passes `only=baked_scenes(export_dir)`, so the log line counts what the bake draws.
- **What moves in a package:** `site.tscn` and `site_backdrop.tscn` no longer carry `add_uv2 = true`. The
  presentation's primitives are unwrapped and baked as before. The log line reads the presentation's count: 112
  on urban_row_001, where it read 225.
- **`tests/unit/test_bake_counts_what_it_bakes.py`:** what the bake draws, a nested instance among it; only those
  scenes written and counted; a package with no presentation bakes nothing; the call site. On 0.211.0 all four fail (proven on 0.211.0; 0.211.1 moved only the certified table).

**Suite:** RESULT_SUITE
