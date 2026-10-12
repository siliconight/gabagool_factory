## [0.186.0] - The export's first import pass imports the models as they ship, so nothing imports them again

**Why now.** Roadmap 239: after the graders, the export is again the
cold run's constraint (cold run 9251: 4.7 of 10.8 minutes), and importing
is most of it. The sidecar step imported every file with Godot's defaults,
rewrote the models' sidecars (embedded images, mode 3) and the shared
textures' pins, wiped the cache and imported everything again; the light
bake then rewrote every model's sidecar to Static Lightmaps and imported
them all once more -- the pass that imports the shared textures 1,843 times
and resets 62 to 86 of their pins (0.182.0's backstop catches them).

**What changed.**

- The export's FIRST import pass runs with `gltf/embedded_image_handling: 3`
  in `project.godot`'s model defaults, and `meshes/light_baking: 2` when the
  export will bake (`lightmaps=profile.bake_lights`); the file is put back
  byte for byte, line endings too, before anything else reads it, so the
  package ships the `project.godot` it always did. Defaults reach only files
  without a sidecar, and after that pass every model has one.
- A cache wipe and a full second pass now follow only a MODEL's sidecar
  rewrite (a model whose sidecar arrived at another mode); when only the
  textures' pins changed, the second pass re-imports just those.
- `light_bake.mark_imports` writes `STATIC` (1, the engine's default) for a
  model whose second UV set is shader data, instead of leaving it to the
  default -- which is now Static Lightmaps for the first pass, and would
  have regenerated those models' UV2 (three street trees, the ATMs and a
  video poker machine in cold run 9251's package).

**Measured** (the factory's `docs/findings/grader_speed/import_plan_probe.py`,
stripped copies of cold run 9251's package, the sidecar step and the
bake's first import): 121.6 s as it was -- the two passes 73.1 s, the
bake's import 48.5 s, 62 pins reset -- against 53.6 s -- the first pass 40.1
s, the pinned textures 8.6 s, the bake's import of the seven models whose
setting it changes 4.9 s, every pin kept. The sidecars of the two are the
same once uids are set aside but for the 62 the race reset and the six
shader-UV2 models, which this release ships as before. RESULT_AB

**Tests:** `tests/unit/test_import_once.py`, seven (the defaults join the
model defaults; none for lightmaps without a bake; a project without model
defaults gets them, beside another importer's; the first pass sees them and
the file comes back byte for byte; the pins alone re-import without wiping
the cache; a shader-UV2 model is written Static; the export asks for
lightmap UVs when it bakes), all failing on 0.185.0. RESULT_SUITE
