## [0.193.0] - The bake's editor stops drawing for the bake; its work copy is copied in parallel and removed in the background

**Why.** Factory roadmap 239, the cold-run speed loop. Since 0.192.0 two
exports of one level bake byte for byte the same files, so a change to the
bake's editor can be held to that and nothing looser.

- **The editor drew the level while it baked.** The bake's progress bar
  pumps the editor's main loop, and with its 3D viewports drawing, every
  pump drew the whole level again. Stopped as Bake is pressed, the bake took
  31.4 and 31.5 s where it took about 35.8, with the same bytes. Stopped from
  the plugin's start instead, before the opened scene had ever been drawn,
  the level baked 17.5 % darker on average, the outdoor ground most: the bake
  reads something only a drawn frame makes (the sky's light is the likely
  one; not shown). The first frame of the opened level is still drawn, and
  takes as long either way (about 10 s).
- **The work copy was copied file after file and removed before anything
  else could start.** The bake copies the package and its import cache before
  its editor opens them, and removes the copy after: on cold run 9258's
  package, 6,058 files and 252 MB, `copytree` took 4.7 and 5.3 s and
  `rmtree` 2.1 to 2.8 s.

**What changed.**

- `light_bake_plugin.gd`: `_stop_drawing` sets the editor's four 3D
  viewports' render targets not to update, called after the room fills are
  laid and just before Bake is pressed, never earlier. The header says why
  not from the start.
- `light_bake._copy_project` makes the work copy: the directories, then every
  file by `shutil.copy2` across `COPY_WORKERS` (8) threads; a file that fails
  to copy raises, as in `copytree`.
- `light_bake._remove_later` renames the work copy aside, which is immediate,
  and removes it on a thread the interpreter waits for at exit, while the
  export goes on; a copy left aside earlier is removed first, and a rename
  that fails removes the copy at once, as before.
- `tests/unit/test_scene_groups_cache.py`'s order test reads the work copy's
  new line.

**Measured:** cold run 9258's workspace re-exported, each change tried in a copy of the plugin first (the factory's docs/findings/grader_speed/bake_phases_probe.py). With the viewports stopped as Bake is pressed (--no-viewport-at-bake), two bakes of 31.4 and 31.5 s and the editor 59.3 and 60.2 s, against 9258's own bake of 35.7 s and a re-export's 35.8 on 0.192.0, and bake.exr, bake.lmbake and bake.exr.import byte for byte the run's own. Stopped from the start (--no-viewport; its first draft set `update_mode`, which a SubViewport does not have, and stopped nothing -- kept as bake_phases_probe.noviewport.draft1.out.txt), two bakes byte for byte the same as each other and 17.5 % darker than the run's on average, the outdoor ground most (lightmap_compare.noviewport.out.txt), the first frame still about 10 s. The work copy timed on 9258's walk copy, 6,058 files and 252 MB: copytree 4.7 and 5.3 s, eight threads 2.1 and 2.0 s, rmtree 2.1 to 2.8 s. As shipped (bake_phases_probe.0193.out.txt, export_timeline_probe.0193.out.txt): exports of 162.4, 164.3 and 163.8 s against 171.4 to 173.2 on 0.192.0 (9257's workspace and 9258's); the editor 59.4, 60.7 and 60.4 s; the export's own Python 17.2 s against 22.3, the gap before the editor 2.0 s against 5.1; the bake files byte for byte the run's own and the package differing in the 18 files two exports differ in; no work copy left beside it

**Tests:** `tests/unit/test_bake_draws_nothing.py`, eight: drawing stops after
the room fills are laid and before Bake is pressed, and not in `_enter_tree`;
the stop is the viewports' render target; the parallel copy is `copytree`,
file for file, byte for byte and in modification time; a file that fails to
copy raises; the work copy is gone at once and removed behind; a copy left
aside earlier is removed first; a rename that fails removes it at once; and
the bake makes and removes its work copy so. All eight fail on 0.192.0.
2,332 passed, 16 skipped, 0 failed (JUnit, 2,348 tests; the ninth new one is test_sibling_locator's check of the new file)
