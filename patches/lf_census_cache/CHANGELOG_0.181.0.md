## [0.181.0] - The greybox census reads the bake's import cache instead of importing the package again

**Why now.** Roadmap 239, the theory of constraints applied to a cold run:
with the graders on a fixed clock (0.180.0) cold run 9248's drive took 14.3
minutes and its export 7.0 of them -- the constraint moved there. Profiled
on 9248's own export (`python -m cProfile`, 430.7 s): importing the package
was 65 % of it, the same files imported five times -- two sidecar passes
(78 s), two in the light bake (112 s, the UV2 unwrap among them) and one for
the greybox census (100.4 s with the census itself), because the cache was
dropped straight after the bake and the census, three steps later, needs
one.

**What changed.** The cache is dropped after the greybox census and before
the closure verdict and the manifest walk the tree, so the shipped package
stays cache-free exactly as before. Nothing between the bake and the census
reads the cache's file types (`.scn`, `.mesh`, `.md5`, `.cfg`, measured in
two staged projects' caches): the occlusion audit and the handoff walk read
`*.tscn`, the GLB scan `*.glb`, the rest JSON. `greybox_skin.measure` is
unchanged: it already used a cache it found and removed only one it made.

**Measured** (cold run 9248's workspace, its package moved aside and put
back after): the export 340.1 s against 430.7 s for the same code before it (the run's own export took 417.5 s), the census 4.2 s against 100.5; greybox_skin_scan.json identical; the package the old code's file for file but warmup.gd.uid -- a random uid the census's import wrote and nothing names (mission.tscn loads the warm-up by path; Godot writes one at a recipient's first import) -- and the classes a second export of UNCHANGED code varies in too (the control, cold run 9248's own export against a re-export: the bake's EXR, regenerated uids, the Empties' node unique_ids, the manifests, and the shared textures' import pins, a defect of its own -- 65 to 77 of 415 sidecars under _tex/ carry Godot's defaults in every export, which ones varying from export to export)

**Tests:** `tests/unit/test_census_reads_the_bake_cache.py`, two (the cache
is dropped once, after the census and before the verdict; nothing drops or
removes it between the bake and the census), both failing on 0.180.1.
2,254 passed, 16 skipped, 0 failed (JUnit, 2,270 tests); tests/unit/test_census_reads_the_bake_cache.py, two, both failing on 0.180.1
