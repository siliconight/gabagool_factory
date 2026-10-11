## [0.178.0] - The site spec tells Lot the package will bake its lights

**Roadmap 231, the second lever, beside Lot 0.115.0.** Lot cuts its
plates, slabs and bands to an 8 m tile for Godot's per-mesh light cap,
priced against live lights before this factory baked them; under the bake
the culler pairs no baked light with a lightmapped mesh (0.159.0's paired
census), and the tile was costing cold run 9233 521 of its 795 boxes. Lot
0.115.0 cuts a bigger tile when the spec says the lights bake. Lot cannot
know what the export will do, so the export's own default says it:

- **`BAKE_LIGHTS_CLI_DEFAULT`** (`packages/exporting/export.py`, true):
  the one constant `export`'s `--bake-lights` default reads, and
  **`_write_site_spec`** writes it as `render.lights_baked` into both the
  greybox and the themed spec. `ExportProfile.bake_lights` stays off, as
  its comment says: code that builds a profile says what it wants.
- **`export --no-bake-lights`** says out loud that the site was drawn for
  a bake it did not get, its plates tiled for one, and that the perf
  report's paired light census is the cap's gate. Said, not refused.

**Tests:** 2 in `tests/unit/test_render_in_site_spec.py`. **Suite:** RESULT_SUITE.
