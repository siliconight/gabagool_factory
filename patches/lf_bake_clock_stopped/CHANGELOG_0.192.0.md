## [0.192.0] - The light bake's editor stops its clock and looks for the scene at once; the localizer skips class names a script does not contain

**Why.** Factory roadmap 239, the cold-run speed loop, with the certainty it
asks for. Timing the export of cold run 9257's level process by process
(the factory's docs/findings/grader_speed/export_timeline_probe.py, with
cProfile) found two waits that buy nothing, and pricing the first of them
found why two exports of one level never baked the same lightmap.

- **The scene was open at the plugin's first look in every bake.** The
  plugin asked for it and looked 240 frames later; cold runs 9254 to 9257
  each logged it open at frame 240, the floor itself. Looking from frame 1,
  the scene is open at frame 1: the editor draws the opened level's first
  frame in about 10 s, and the 239 after it took about 4 more.
- **The lightmap depended on when Bake was pressed.** Lux's failing fixtures
  keep a clock in the bake's editor too (`_fail_t += delta`) and dim their
  lenses with their lamps; their lamps are left live and unbaked, but a
  lens's emission is baked. So each bake kept every failing lens at whatever
  level it had at that moment -- two bakes of the same inputs differed in
  `bake.exr`, `bake.lmbake` and `bake.exr.import` every time, most near the
  failing streetlights and tubes. With the engine's clock stopped from the
  plugin's start, the bake is byte for byte the same whenever it is pressed.
- **The localizer searched every script for every class name the tools
  declare.** For each `.gd` it built a pattern per name and searched the
  whole text with it -- 1,804 searches a pass over cold run 9257's 44
  scripts, twelve of them a 95 KB `zoo_worldskin.gd`, 1.67 of the pass's
  1.69 s -- though a name the text does not contain cannot match.

**What changed.**

- `light_bake_plugin.gd` sets `Engine.time_scale` to 0 as it enters the tree
  and never back: frames still advance, and every wait it keeps counts frames
  or reads `Time.get_ticks_msec()`, which is not scaled. Which level a
  failing lens should bake at is a look and is not settled here: at 0 a
  stuttering tube is at full, a filament at about 0.97, and a cycling
  streetlight wherever its own seed puts it in its cycle -- fixed for a
  level now, where it was drawn anew every bake.
- `OPEN_FLOOR_FRAMES`, 1, where the plugin waited 240 frames before it first
  looked for the opened scene; an open that has not landed is still asked
  again, and the wait is still bounded by `OPEN_LIMIT_MS`.
- `localize._rewrite_text` skips a class name its text does not contain
  before it stats the name's runtime copy or builds its pattern; the pattern
  still decides every name the text does contain.

**Measured:** cold run 9257's workspace re-exported with each change swapped into a copy of the plugin first (the factory's docs/findings/grader_speed/bake_phases_probe.py, --open-floor and --freeze-time). Looking for the scene from frame 1, the plugin found it open there 9.8 and 10.0 s after asking, against frame 240 at 14.2 and 14.5 s, and the editor took 64.1 and 64.4 s against 67.9 and 68.4 (change, control, control, change). With the clock stopped, two bakes pressed 4.4 s apart came out byte for byte the same in bake.exr, bake.lmbake and bake.exr.import, where every pair with the clock running differed in all three, most at the outdoor props by the failing streetlights (lightmap_compare.py --layout). As shipped (bake_phases_probe.0192.out.txt, export_timeline_probe.0192.out.txt): exports of 172.5, 172.0 and 171.4 s against 182.9 and 184.7 on 0.191.0; the editor 64.6, 64.2 and 63.8 s; the export's own Python 22.3 s against 29.3, its first import starting at 11.7 s against 18.8; the two shipped bakes byte for byte the same as each other and as the stopped-clock bakes of an hour before, so two exports of one level now differ in 18 files where they differed in 21; light_bake.json the same in every count (3,320 users, 494 models baked, 215 room fills). Against a 0.191.0 export the package differs in those 21 files alone and in none of its 378 scripts; the localizer's pass over 9257's 76 text files 1.69 -> 0.079 s

**Tests:** `tests/unit/test_bake_clock_stopped.py`, four, read off the
plugin's source as the rooms' floor test reads it: the clock stopped in
`_enter_tree` before the first counted frame, set once in the code and never
back, the open looked for from frame 1 with 240 gone, and an open that has
not landed still asked again and bounded. `tests/unit/test_localize_class_scan.py`,
three: a script naming no class runs no search; a name inside a longer one
is still decided by the pattern (asked once, not localized); a name used as
a word still pulls its script. Five of the seven fail on 0.191.0; the other
two are guards on what is kept (the open asked again, a word still pulling
its script). 2,323 passed, 16 skipped, 0 failed (JUnit, 2,339 tests; two of the nine new are test_sibling_locator's checks of the new files)
