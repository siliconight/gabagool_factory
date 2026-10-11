## [0.178.5] - The light bake keeps its editor awake and asks for the scene until it opens

**Cold run 9242.** The export's bake reported `bake.tscn did not open`
after 83.7 s in the editor and shipped the package unbaked, where cold run
9241 had baked the same lot in 94.4 s. The run still counted 0
interventions, because a failed bake is a warning. Nothing said why: the
editor's output went to DEVNULL. A re-run of the same bake with its output
kept failed the same way after 371.8 s, and showed the editor re-importing
every texture its first open finds used in 3D, then giving up.

**What it was.** The plugin waited on the scene in FRAMES: 180 before it
asked, 3,000 before it gave up, with the open asked once. An editor whose
window has no focus sleeps 100 ms a frame (Godot's unfocused low-processor
mode), and a bake opens its window on somebody's desktop while they work,
so 3,180 frames came to minutes while the first open's re-import crawled at
the same pace. The same plugin with the three changes below opened 9242's
scene in 21 s and baked it in 49.4 s: 213 steady rigs, 215 room fills and
3,483 lightmap users, where 9241's pipeline bake read 3,518; the copy baked
the responders' car, which a pipeline bake keeps dynamic, so the difference
is left to cold run 9243 to measure. The three were tried together; which of them would have been enough
alone was not isolated.

- **The editor stays awake:** `OS.low_processor_usage_mode = false` at
  start and every frame.
- **The scene is asked for once the file scan is idle, and again every 300
  frames until it opens.**
- **The open's wait is a clock:** `OPEN_LIMIT_MS`, five minutes, where it
  was 3,000 frames; a failure says how long it waited and how many frames.
- **The editor's output is kept** beside the package, never inside it
  (`<package>.lightbake.log`), and `light_bake.json` names it
  (`editor_log`). `_run` writes a process's output to a log when given one.

**The bake:** `docs/cold_runs/cold_9242/rebake_probe.py` in the factory, Level Factory's own `bake()` on a fresh copy of 9242's package: on 0.178.4 `bake.tscn did not open` after 371.8 s; on a clone at 0.178.5, the scene asked for at frame 180 and open after 20.2 s at frame 240, baked in 40.4 s, ok, 213 steady rigs, 215 room fills, 3,483 users, 102.5 s in the editor, and the editor's output kept by the runner itself beside the copy.

### Tests

Two in `tests/unit/test_light_bake.py`: the plugin's three changes, read
from its text, and the editor's output reaching the log while the bake
names it in the report. Both fail on 0.178.4. The three editor fakes take
the log.

**Suite:** 2,228 passed, 14 skipped, 1 xfailed, exit 0: 0.178.4's 2,226 and the two new tests, which fail on 0.178.4 (17 of 19 in the file passed there).
