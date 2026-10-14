# The modules the Empties were merged from, out of the package (roadmap 249)

Found attributing cold run 9304's package against 9303's (`docs/findings/fire_escape/unreferenced_glbs.py`,
`unreferenced_glbs_9304.out.txt`). Level Factory's `merge_empties` folds an Empty's sided slots into
`lot/<id>/merged/<side>_<n>.res` and removes the slot children that instanced the kit's module GLBs. The GLBs stayed
in `lot/<id>/art/zoo/`, and the light bake's `mark_imports` -- which walks every `*.glb.import` -- set each to Static
Lightmaps and unwrapped it at import.

## Measured before the fix

- **9304's package:** 612 GLBs, 289 named by no scene or resource, 9.2 MB with their `.import` and
  `.unwrap_cache`; 315 of the light bake's 632 model imports files no scene named.
- **Where they are:** 286 under the Empties' `art/zoo/` -- windows 191, walls 39, doorways 20, roofs 10, wall ends
  10, props 17 (the fire escapes among them) -- and 3 elsewhere: `assets/lot.glb`, `assets/shell.glb`, and the
  responders' car under `cover/`, which the gameplay layer loads by path (roadmap 212).
- **What names them:** a module checked by name appears only in `light_bake.json` and
  `portable_resource_manifest.json`, the package's own lists of its files. No script, config or resource names
  one: `zoo_worldskin.gd` is an import script scoped by file prefix; `occluders.json` records module stems, not
  files.
- **What a merged mesh needs:** gs_midrise_c's thirteen `merged/*.res` name no `.glb`. Their materials are
  duplicates pointing at `art/zoo/_tex/*.png`, which stay.

## What shipped: Level Factory 0.210.0

`merge_empties.drop_merged_modules(export_dir, report)` (`patches/patch_lf_drop_merged_modules.py` and
`lf_drop_merged_modules/`). For each Empty the merge report merged, an `art/zoo/*.glb` that no file of the package
names -- by its bare file name, in a scene, resource, script, manifest or config, the import cache and the two file
lists aside -- goes with its `.import` and `.unwrap_cache`. The export calls it after the merge and before the light
bake, and the closure verdict and resource manifest are written after both. A bare name, not a path: a module that
shares its file name with one another lot's scene instances is kept.

## Proven on a mirror of cold run 9305's package (`mirror.sh`, `mirror_steps.py`)

- **The drop** (`mirror_drop.out.json`): 284 modules removed, 6,876,497 bytes with their sidecars; 4 kept, each
  attributed -- the two corner awnings their scenes instance, and gs_midrise_b's and gs_midrise_f's
  `wallEnd_delco_1997_01_mbrick_idrywall.glb`, kept by name because deli_a01's scene instances a module of that
  name. 284 and those 2 are 9305's 286 merged-only modules.
- **The closure** (`mirror_closure.out.txt`), Level Factory's own scan, reads both copies alike: 77 resources, 0
  missing, 0 misrooted, 0 issues.
- **A first import**, the way a consumer's editor opens a package (`mirror_import_run1.out.txt`,
  `mirror_import.out.txt`): 612 model imports against 328, 115.0 s against 102.9 s, then 124.6 s against
  113.5 s. Two runs, each a then b, so the order is not controlled: a measurement, not a price.
- **The frames** (`mirror_frames.out.txt`): look_shots at the walk-up and corner stations on a, on b, and on a
  again as the control. Over all 16 frames, 2,023 pixels differ by more than 24 levels of 255 between the two
  shots of a, and 1,299 between a and b. One frame, `extraction`, differs more against b (194) than against
  its control (1). Not attributed: the frames are no longer in `_scratch/mirror_249`, and the table is all
  that is left of them.
- **Refuted and kept** (`mirror_frames_nocontrol.out.txt`): the first frame check had no control and counted any
  differing pixel, and it read 70-93 % of every frame different. Two shots of one copy differ that much.

## Proven in the pipeline: cold runs 9308, 9309 and 9310

Level Factory 0.210.0's first cold runs, each also carrying the walk's fixes 1-4 (`docs/findings/walk_2026-10-14/`).
0 interventions each, and nothing the graders read moved.

    run    mission              removed (MB)   kept   bake models    package         files
    9308   urban_row_001        284 (6.9)      4      632 -> 348     205.6 -> 198.5  3,343 -> 2,487
    9309   gas_block_001        218 (3.4)      2      547 -> 329     166.9 -> 163.4  3,233 -> 2,577
    9310   restaurant_row_001   218 (3.4)      2      564 -> 346     (9306's package is retired)

Each against the run whose brief and seed it repeated: 9305, 9307 and 9306. The bake's users are unchanged in
each (3,153; 3,191; 3,490). Every file that left 9305's package or joined 9308's, and 9307's or 9309's, is one of
these (`package_files.py`, `package_files_9305_9308.out.txt`, `package_files_9307_9309.out.txt`):
- the modules' files, 852 and 654;
- the door boxes' band-pack textures out and their painted faces in (the walk's finding 4);
- the corner shops' pane emission texture, out and in (its finding 1).

The editor's bake read 75.3 -> 71.5 s, 61.9 -> 61.5 s and 59.8 -> 60.6 s, one run each beside other Godot jobs:
not a price.

**Left, not this finding's:**
- `assets/lot.glb` and `assets/shell.glb`, named by no scene and not attributed;
- the responders' cruiser, shipped for the gameplay layer by design (roadmap 212);
- the two wall ends kept by a name another lot's scene uses.

## Instruments

- `mirror.sh`: two copies of 9305's package, the drop on one; `mirror_steps.py` holds its steps.
- `docs/findings/fire_escape/unreferenced_glbs.py <package>`: the GLBs no scene or resource names.
- `package_files.py <package A> <package B>`: every file that left or joined, the kit modules counted apart.
