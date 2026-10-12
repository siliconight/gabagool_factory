## [0.182.0] - The shared textures' import pins are applied again after the last import, and read back off what ships

**Why now.** Found by the control that measured 0.181.0: two exports of
unchanged code differed in which shared textures carried their import pins.
`_pin_shared_texture_imports` pins three keys on every sidecar under `_tex/`,
each for a reason measured in `_write_import_sidecars`' docstring
(`compress/mode` lossless, or VRAM for a texture every sampler filters;
`process/fix_alpha_border=false`, whose default rewrites 7.755 % of pixels;
`mipmaps/generate=true`, without which `zoo_worldskin.gd` rebuilds each
texture on its own and the sharing is undone). Cold run 9248 shipped 65 of
its 415 with Godot's defaults instead.

**Where they went** (factory `docs/findings/texture_pins/`, each step its
own probe, the refuted ones kept):

- one `--import` on a stripped package leaves no texture without a
  sidecar (0 of 415, three trials) -- the first suspicion, refuted;
- the sidecar step itself leaves all 415 pinned, and an import over its
  cache keeps them -- refuted;
- the real export, a pin census around every later phase: all 415 pinned
  until the light bake's FIRST `--import` (after `mark_imports` moves the
  models to static lightmaps), 86 defaulted after it, and nothing after it
  moved one;
- reproduced on a copy with the engine's log: that pass imported textures
  1,843 times for 476 models, the same file again and again with several in
  flight, and 64 came out defaulted; with `detect_3d/compress_to=0` pinned
  as well, 62 and the same 1,843 -- not that setting.

**What changed.** `_repin_after_imports` runs between the cache drop and
the closure verdict: the shared and the sign pins applied again over the
files that ship, then `_shared_texture_pins_missing` reads every shared
sidecar back, and a package that still carries a wrong or a missing pin is
refused (`ExportImportError`) -- a key a sidecar does not carry is not one
the pins write, so it fails rather than shipping on the engine's default.
The export prints how many it re-pinned. The bake itself still read the few
reset textures as the race left them; nothing it bakes depends on a mip
chain or an alpha border.

**Measured:** cold run 9248's export re-run in its workspace (the run's package held aside and put back), a pin census around every phase: the light bake's first import still reset 80 of 415 shared sidecars to Godot's defaults, the read-back re-pinned those 80, and the package shipped 415 of 415 pinned ("[export] import pins: 415 of 415 shared-texture sidecar(s) carry their pins; 80 re-pinned after an import reset them, 0 sign sidecar(s) re-pinned"), the closure verdict ok over 3,041 files as in 0.181.0; 9248's own shipped package, audited the same way, needed 65 re-pinned (docs/findings/texture_pins/pin_phase_probe_0182.out.txt)

**Tests:** `tests/unit/test_texture_pins_survive_the_bake.py`, four (a reset
sidecar is pinned again; a sidecar without a pinned key refuses the
package; the cache is not the package; the export reads the pins back after
its last import and before the verdict), all four failing on 0.181.0.
2,259 passed, 16 skipped, 0 failed (JUnit, 2,275 tests); tests/unit/test_texture_pins_survive_the_bake.py, four, all four failing on 0.181.0
