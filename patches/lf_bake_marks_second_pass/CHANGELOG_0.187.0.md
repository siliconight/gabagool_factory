## [0.187.0] - The light bake's lightmap requests ride the export's second import pass

**Why now.** Roadmap 239: with the compose side by side (0.186.0) the export
is 46 % of a cold run's drive (284 s of cold run 9252's 615). It imports the
package three times over: the sidecar step's first pass (no sidecars yet),
its second (sidecars rewritten, the cache dropped, everything again), and
the light bake's, which asks every model for a lightmap UV
(`light_bake.mark_imports`) and imports again for it -- in cold run 9248
that pass imported the shared textures 1,843 times for 476 models, and it
is the pass that loses their import pins (0.182.0 puts them back).

The one-import plan was refuted (the factory's
`docs/findings/grader_speed/README.md`): asked for in the FIRST pass, the
lightmap UVs left 105 slab surfaces greybox. Cold run 9251's own import log
says why: the worldskin skins a building's slabs by `load()`ing one of its
floor modules, and on a model's first import that module may not be
imported yet -- pass one left 105 slab meshes greybox and took two reveals
from roof modules; pass two, its sidecars present, skinned every slab from
a floor module. The second pass is not a first import.

**What changed.**

- `_write_import_sidecars(..., bake_spawned=None)`: given the models the
  gameplay layer spawns, it applies the bake's marks
  (`light_bake.mark_imports`: Static Lightmaps on every model but those
  whose own second UV set is shader data, Dynamic on the spawned) after the
  pins and before the second pass.
- `export_mission` passes the bake's own list,
  `responder_vehicle_scenes(themed_site_dir)`, when the export bakes, and
  nothing when it does not.
- The bake still marks and imports: it finds nothing left to change, and it
  stays the net for any caller that did not.

**What it changes in the package** (measured against the same export as it
was, the factory's `docs/findings/grader_speed/uv_second_pass_probe.py` on
cold run 9252's workspace). The Empties' merge now sees models that carry
their lightmap UV, and makes one mesh a side per material as it was written
to: 236 merged meshes became 148, the same 1,061 meshes, 1,660 surfaces and
962 colliders in, 24 doors dropped as before -- the old merge split one side's single
material into two to four meshes (gs_empty_rowhome_a's north brick into
three, gs_empty_rowhome_e's north paint into four), by a flag or the surface format, which one not measured. The
bake's users 3,491 -> 3,320: every one of the 171 a merged mesh of an Empty
placed across the street, every other user the same. The lightmap 16
slices -> 15. The greybox census, the occluders and the closure verdict
identical; no shared-texture pin lost, where the control lost 74.

**Measured:** cold run 9252's package re-exported twice in its workspace on 0.187.0, the run's package held aside and put back (the factory's docs/findings/grader_speed/uv_second_pass_probe.0187.out.txt): the export 243.3 and 238.6 s against 277.6 s for 0.186.0 measured the same way (uv_second_pass_probe.out.txt), the bake's import of every model 5.0 s against 55.0, the sidecar step 88.7 and 87.4 s against 76.0; no shared-texture pin lost, against 74; the greybox census 3 surfaces, the occluders 1,370 and the closure verdict ok, as before; the Empties merged to 148 meshes, one a side per material in every Empty (merged_materials.py), the bake's 3,320 users and a lightmap of 15 slices; and the two re-exports differ from each other only where two exports of the same code always do (the bake's three files, the twelve Empties' scenes, five manifests, one sidecar's uid), where 0.186.0's run and re-export differed in 42 texture sidecars besides

**Tests:** `tests/unit/test_bake_marks_second_pass.py`, four: the marks are
on every model when the second pass runs, the spawned one Dynamic; the
bake's own marking then finds nothing to change; the export passes the
bake's list only when it bakes -- these three failing on 0.186.0 -- and no
bake, no marks, which holds what 0.186.0 already did and passes on both.
2,291 passed, 16 skipped, 0 failed (JUnit, 2,307 tests: the four above and the sibling-locator check over the new file)
