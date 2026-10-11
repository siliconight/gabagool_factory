## [0.27.0] - the navigation map updates on the evaluation's thread, so the clock need not wait

### Why now

Roadmap 239: the walker asked for faster cold runs "without losing any
certainty of quality or introducing regressions", and Laser Tag's
evaluations are most of a cold run's time. Cold runs 9245 and 9247 measured
every evaluation simulating 3.91 to 3.97 times its job's wall time: the run is
paced to `--time-scale` x real seconds, so most of a ten-minute job waits.
`run_map_eval.gd`'s own comment said "Headless evaluation shouldn't wait on
real-world seconds"; it did.

Godot's `--fixed-fps 60` (an engine argument) makes each frame one physics
step, computed as fast as the processor allows, with the physics step
unchanged. Cold run 9247's seed_9104 under it: 21 s against 593, the same
grade and score -- and the crew's stuck count 21 against 9, the trajectories
apart by 0.05 mm at run 2's 72nd second and diverging from there. Nothing in
Laser Tag reads the wall clock during a run (`_now` is the run's accumulated
physics delta; the brains and bodies run in `_physics_process`). What does is
the engine's NAVIGATION: Godot 4.7 updates a map and its regions on worker
threads by default (`navigation/world/map_use_async_iterations`,
`region_use_async_iterations`), so when an update lands is wall time. Under the
synchronised clock there is time to spare between steps and it lands the same
way alone or two at a time; three at once it moved a few event positions by
0.01 m (roadmap 239, which the walker accepted as noise), and under the fixed
clock it lands differently every frame.

### What changed

- **`LT_Const.synchronous_navigation(scene_root)`** sets the world's map,
  every NavigationRegion3D under the scene and each region's own map to
  update on the caller's thread, and returns how many regions it set;
  **`navigation_is_synchronous`** reads the dial back. The setters are server
  commands that land at the next sync: read straight back, the map still said
  asynchronous (measured in a probe, 2026-10-11), so a caller lets a physics
  frame pass.
- **`run_map_eval.gd`'s `_run` calls it before the bake**, lets a frame pass,
  reads it back and prints `[LT] navigation: the map and N region(s) update on
  this thread` -- or warns that the report may not repeat.
- **The header documents the clock**: `--fixed-fps 60` before `--`, and that
  `--time-scale` multiplies the physics STEP (4 simulates at 1/15 s). The
  engine does not tell a script which clock it runs on (`OS.get_cmdline_args`
  omits `--fixed-fps`, measured), so the caller chooses it. The comment that
  said the evaluation did not wait on real seconds is corrected.

### Measured (the factory's `docs/findings/grader_speed/`)

On copies of staged evaluation projects, each job's own command, every
report compared field by field. With both iterations synchronous (project
settings, the dial read back by `engine_settings_probe.gd`):

- **Cold run 9247's seed_9104**: the fixed clock 21.1 s and 23.0 s, three at
  once 22.8 to 22.9 s each, and the synchronised clock 593 s -- all six
  identical to the job's report in every field, 2,196 events.
- **Fourteen more candidates over five missions** (restaurant_row_001,
  deli_001, warehouse_yard_001, bank_block_001, club_block_014; the older
  ones carrying the Laser Tag of their day): every fixed-clock report read
  the same run twice (14 of 14), in 11.0 to 38.7 s against jobs of 76.8 to
  590.5 s. Against their jobs, restaurant_row_001's matched in every field;
  nine others moved one to twenty events -- a position by up to 0.12 m, or
  which of two coincident colliders a shot named -- and three diverged far
  enough to move secondary figures (warehouse_yard_001 seed_9105,
  club_block_014 seed_9080, deli_001 seed_9393). Every grade and every
  finding held on all fifteen; one score moved a point (deli_001 seed_9393,
  WARN 66 -> 67, its crew stuck 6 -> 3).
- **The clock or the navigation?** On deli_001 seed_9393 the synchronised
  clock as the job ran reproduced the job exactly, and the synchronised
  clock with synchronous navigation read exactly what the fixed clock did.
  The difference from the job is the navigation setting; the clock adds
  none.
- **This release's runtime setters** (no project settings) against the
  project-setting arms: on cold run 9246's deli_001 seed_9393 with 0.26.0's addon swapped in, under --fixed-fps 60: this release's setters, no project settings, read identical in every field to 0.26.0 with the two settings (1,894 events), and both apart from the asynchronous control in their events, so the candidate can tell the setters from nothing; cold run 9247's seed_9104 under this release identical to its job in every field, 2,196 events, in 19.6 s (docs/findings/grader_speed/runtime_setters_ab.sh)

### Not changed

The physics step: `--time-scale` stays 4 by default. At the game's own 1/60 s
(time scale 1) the fixed clock took 62 s on seed_9104 and read the same
twice; whether the grader should step as the game does is the walker's call.

### Tests

`runners/tests/test_navigation_is_synchronous.gd` (fails on 0.26.0: neither
helper exists, and the runner does not call them): 9 checks, failing on 0.26.0 to parse (neither helper exists, and the runner calls neither); all 19 tests exit 0
