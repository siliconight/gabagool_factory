## [0.210.0] - The kit modules only merged slots instanced leave the package

**Factory roadmap 249, found attributing cold run 9304's package.** `merge_empties` folds an Empty's sided slots into
`lot/<id>/merged/<side>_<n>.res` and removes the slot children that instanced `lot/<id>/art/zoo/*.glb`. The modules
stayed in the package, and the light bake's `mark_imports`, which walks every `*.glb.import`, set each to Static
Lightmaps and unwrapped it at import. Measured on 9304's package (the factory's
`docs/findings/fire_escape/unreferenced_glbs.py`):
- 289 of its 612 GLBs named by no scene, 9.2 MB with their sidecars;
- 286 of them modules under the Empties' `art/zoo/`: windows 191, walls 39, doorways 20, roofs 10, wall ends 10,
  props 17;
- 315 of the bake's 632 model imports files no scene named.

A merged mesh names no module. Its materials are duplicates pointing at `art/zoo/_tex/*.png`, which stay: read off
gs_midrise_c's thirteen `merged/*.res`, no `.glb` in any.

- **`merge_empties.drop_merged_modules(export_dir, report)`:** for each Empty the merge report merged, an
  `art/zoo/*.glb` that no file of the package names is removed with its `.import` and `.unwrap_cache`.
  - Names are read off scenes, resources, scripts, manifests and configs (`NAMING_SUFFIXES`), by bare file name.
    The import cache and the package's two lists of its own files (`FILE_LISTS`) are not read.
  - A bare name, not a path: a module sharing its name with one another lot's scene instances is kept. The rule
    errs toward shipping a file.
  - Nothing outside a merged Empty's `art/zoo/` is touched. The responders' car under `cover/` is loaded by path.
- **The export** calls it after the merge and before the light bake, and says what went:
  `[export] merged Empties' modules no file names: N removed (X MB), K named and kept`. The closure verdict (4.9) and
  the resource manifest (4.96) are written after both, so they see the folder as it ships.
- **`tests/unit/test_merged_modules_dropped.py`:** a package written in the test, two Empties merged and one not.
  The unnamed modules go with both sidecars and their bytes are counted. What a scene, a script or another lot names
  stays, as do the textures, the cruiser and the untaken Empty. A failed row or an empty report drops nothing, and
  the export's call stands between the merge and the bake. On 0.209.0 it fails to find `drop_merged_modules`.

**Mirrored:** on two copies of cold run 9305's package (the factory's `docs/findings/merged_modules/mirror.sh`): the drop removed 284 modules, 6,876,497 bytes with their sidecars, and kept 4 -- the two corner awnings their scenes instance, and two wall ends a deli scene names by the same file name; Level Factory's own closure scan reads both copies alike, 77 resources, 0 missing, 0 misrooted, 0 issues; 16 frames shot on each and the shipped copy shot again: 1,299 pixels differ by more than 24 levels between the two copies against 2,023 between the shipped copy and itself; a first import 124.6 s against 113.5 s for 612 and 328 model imports, one run each, beside another Godot on the machine

**Suite:** exit 0, 2,433 by the progress tally (2,418 passed, 14 skipped, 1 xfail): 0.209.0's 2,412, the new file's 5 and `test_sibling_locator`'s guard over it; the new file fails on 0.209.0's code, all 5, and passes on 0.210.0's (the factory's `patches/lf_drop_merged_modules/prove_tests.out.txt`)
