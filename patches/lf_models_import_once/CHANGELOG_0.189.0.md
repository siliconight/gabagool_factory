## [0.189.0] - Every model is imported once, with its final settings, in three passes over three sets

**Why now.** Roadmap 239. The export was 48 % of cold run 9254's drive, and
its sidecar step imported the package twice: a first pass with Godot's
defaults, then, the sidecars rewritten (embedded images, the pins, the
bake's marks), what extract wrote deleted and the cache wiped, every file
again -- 86 s of a 238 s re-export of 9254.

**What a first import gets wrong, measured** (the factory's
`docs/findings/grader_speed/sidecar_once_probe.py`, the export re-run in
9254's workspace against itself, every model digested as Godot loads it by
`import_digest.gd`):

- A model imported before the shared textures it names embeds a copy of
  each instead of naming the file: 1,463 surfaces in 461 models, when the
  models' final settings were the first pass's defaults -- and every gate
  passed, because none checks texture sharing.
- A worldskin base skins its slabs from a sibling floor module it `load()`s,
  which a first import cannot promise is there (the refuted one-import plan:
  105 slab meshes greybox).
- A model imported twice, its textures already imported, is the race
  0.182.0 backstops: re-importing six models to set their light baking back
  reset two textures' pins and embedded a copy in three.
- Read while the models were held, the filtered-texture set
  (`_filtered_shared_textures`, off the models' glTF) was empty, and 26
  textures went lossless until the read-back after the last import.
- A sidecar written by hand is not a new import: `project.godot`'s defaults
  reach only a file with no sidecar, and a key a sidecar lacks takes the
  value an import from before the key existed would have had
  (`gltf/texture_map_mode=0` where every new import reads 1).

**What changed.** `_write_import_sidecars` gives `project.godot` the models'
final settings as `[importer_defaults] scene` (embedded images; Static
Lightmaps when the export bakes), reads the filtered set, holds every model
(`.glb.held`, an extension Godot does not import), and imports in three
passes: the textures and everything that is not a model, then pins them;
every model but the late ones; then the late ones -- the worldskin bases
(`site_base*`) and the models whose light baking is their own (Static for a
second UV set that is shader data, Dynamic for a spawned one), each of the
latter from a whole sidecar: every `[params]` line of a model the second
pass imported, its light baking set. Every model and `project.godot` are put
back whatever happens. Nothing is extracted, so nothing is cleaned up, and
the cache is never wiped. `_pin_shared_texture_imports` takes the filtered
set it is given.

**Measured:** cold run 9254's package re-exported twice in its workspace, the run's package held aside and put back (the factory's docs/findings/grader_speed/sidecar_once_probe.py; arm O the sidecar step as 0.188.0 had it, read from its commit, arm A this one): the sidecar step 85.8 -> 61.5 s, the export 235.9 -> 212.2 s; no shared-texture pin lost in either; the greybox census 3 surfaces, the Empties' merge 148 meshes, the bake's 3,320 users, the occluders 1,370 and the closure verdict ok in both; every model loading the same, 501 of 501 by import_digest.gd; and the two packages differing only where two exports of the same code always do, the bake's three files, the twelve Empties' scenes, five manifests and one sidecar's uid (sidecar_once_probe.0189.out.txt)

**Tests:** `tests/unit/test_models_import_once.py`, seven, against a fake
Godot that applies the project's defaults only to a model with no sidecar
and gives a sidecar lacking `gltf/texture_map_mode` the old value: no model
seen by the first pass, the late ones by the last alone; every model
imported once with its final settings; without a bake every model keeps the
importer's light baking; the bake's own marking then finds nothing to
change; a texture every sampler filters pinned though the models were held;
`project.godot` and every model put back; and put back when an import fails.
The first three fail on 0.188.0; the other four hold what 0.188.0 already
did, against the ways holding models could break it. Changed with the pass
count:
`test_import_pass_verified.py`'s two that count calls (the models' first
pass is now the second call), `test_bake_marks_second_pass.py` (its two
pass-counting tests moved to the new file, the wiring test kept),
`test_shared_texture_imports.py`'s extract-cleanup test (no cleanup: the
step deletes no texture), and `test_sign_texture_imports.py`'s check that
the signs are pinned beside the shared textures, at the calls' new lines.
2,302 passed, 16 skipped, 0 failed (JUnit, 2,318 tests)
