## [0.163.1] - The import pass checks its own work

**Cold run 9214 stopped at export, and this is why.** The export's first
`--import` left sidecars on 140 of the package's 975 importable files and on
none of its 425 models. The 140 were SkyMint's, which arrive with Lux's
runtime. Nothing looked:
- **`_write_import_sidecars`** threw away the pass's exit code and output and
  returned.
- **`occluders.ensure_imported`** took the `.godot` folder's existence for an
  import.
- **The occluder bake** loaded a scene whose every module was missing and
  reported `ok` with 0 modules (`occluders.json`: `modules: []`, `solid: 0`,
  2 `other`). The export printed "0 occluder(s) from 0 solid module(s)" as a
  result.
- **The Empties' merge** was the first step to refuse: "no side to merge" on
  all 12.

**The same package imports.** It imported 425 of 425 models in seven fresh
reruns, 37-45 s each, two of them from the export's exact starting state
(SkyMint's sidecars restored to their source text). So the pass is a
transient, and the cure is to look. What made it stop short is NOT
established: Godot's output was not kept, and that is the second half of
this change. The records are `docs/cold_runs/cold_9214/import_reruns.txt`
and `attempt1_sidecars.txt` at the factory root.

**What counts as imported.** `occluders.unimported_models(export_dir)` lists
the package's models Godot has not imported here. A model counts once its
`.import` sidecar names the files Godot made of it in `dest_files` and
those files are there. A sidecar with no `dest_files` is an unrecognised
shape and does not count.
- The shape was read off a real one: cold run 9214's
  `doorway_delco_1997_01_w100_mbrick_orange_enavy_o3e3b2d.glb.import`,
  Godot 4.7, one `.scn` under `.godot/imported/`.
- `package_models` gives the set: every `.glb` and `.gltf`, less `.godot/`
  and any folder holding `.gdignore`, as Godot skips them.

**The export's pass** (`export.py`, `_write_import_sidecars`):
- **Each pass is checked, and repeated up to `IMPORT_PASSES` (3) times.**
  The second pass, after the sidecar rewrite, is checked the same way: it
  deletes the cache, and a pass that stopped short there would leave
  sidecars over an empty cache.
- **Every pass's exit code and output** go to `<package>.import.log`,
  beside the package and not in it, so the resource manifest never sees it.
- **A retry prints a line.**
- **A pass that never completes raises `ExportImportError`** and stops the
  export, before the occluder bake can measure an empty scene.
- **No Godot at all is still a setup problem,** not a failure: the package
  ships consistent and unimported, as before.

**`ensure_imported`** now returns early only when the cache is there and
`unimported_models` is empty. It refuses an import that leaves any model
behind. The occluder bake, the Empties' merge and the greybox skin census
all start there.

**`IMPORT_PASSES` is chosen, not derived.** One short pass was seen in eight
on this package. A pass costs about 40 s, so 3 bounds a bad export at about
two minutes before it says so.

**The stub Godot imports the models** (`tests/fixtures/bin/godot.py`). Its
`--import` used to leave a bare `.godot/imported` and nothing in it, and two
integration tests passed on that only because nothing checked:
- `test_presentation_export_and_portability`;
- `test_export_and_portability_via_service`.

On this change both stopped with `ExportImportError`, "3 of 3 model(s)
unimported", which is the check working on an incomplete fixture. The stub
now writes each model's sidecar the way Godot 4.7 does, `dest_files` naming
`res://.godot/imported/<name>-<md5 of its res:// path>.scn`, and that file.
The greybox census's branch in the same stub was fixed the same way when
its gate arrived.

**Tests.** `tests/unit/test_import_pass_verified.py`, 9. Eight fail on
0.163.0, each on its own count:
- **The four that say what "imported" means:** there is no
  `unimported_models`.
- **A short first pass is imported again:** `1 == 2`. One pass, no retry.
- **A pass that never completes stops the export:** there is no
  `ExportImportError`.
- **A cache folder alone is not an import:** `ensure_imported` returned
  False on `is_dir()`.
- **An import that leaves models behind is refused:** it did not raise.

The ninth, "no Godot still returns 0", is a guard and passes on 0.163.0
too. With the change, these 9 and the 68 in `test_occluders.py` and
`test_shared_texture_imports.py` pass, 77 in all.
`test_the_sidecar_pass_leaves_the_cache_for_the_bake` and
`test_the_extract_cleanup_spares_the_shared_textures` are unchanged.
