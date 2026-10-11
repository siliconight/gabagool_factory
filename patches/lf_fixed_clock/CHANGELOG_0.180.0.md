## [0.180.0] - Laser Tag's evaluation runs on a clock that does not wait on real seconds; the grounded table follows Laser Tag 0.27.0 and Zoo 1.102.0

**Why now.** Roadmap 239, the walker's question: faster cold runs "without
losing any certainty of quality or introducing regressions". 0.179.1 ran the
graders three at a time; cold run 9247 measured it (shell leg 15.7 -> 10.4
minutes, the drive 30.4 -> 24.3) and found the floor: the leg now ends when
its longest Laser Tag evaluation does, and every evaluation in 9245 and 9247
simulated 3.91 to 3.97 times its job's wall time. Godot paces a run to Laser
Tag's 4x clock in REAL seconds, so most of a ten-minute job was waiting --
which is also why three at once ran no slower than one.

**What changed.**

- **`LaserTagAdapter.fixed_fps` = 60, passed to the engine as `--fixed-fps
  60`, before `--`.** Each frame is one physics step (the staged project's 60
  ticks), computed as fast as the processor allows; the step itself is
  `--time-scale`'s and is not passed, so Laser Tag's default 4 stands. Laser
  Tag cannot see the flag (the engine leaves it out of
  `OS.get_cmdline_args`), so this command is the one place the clock is
  chosen; `fixed_fps = 0` restores the synchronised clock.
- **Grounded table: laser_tag 0.26.0 -> 0.27.0** (the navigation map updates
  on the evaluation's thread, which is what makes the fixed clock read the
  same report) **and zoo 1.101.0 -> 1.102.0** (what a roof carries follows
  what the building is). The stubs follow.

**Measured** (the factory's `docs/findings/grader_speed/`, copies of staged
projects, each job's own command, every report compared field by field):

- With the navigation synchronous, cold run 9247's seed_9104 read identical
  to its job in every field, 2,196 events, under the fixed clock (21.1 s and
  23.0 s; three at once 22.8 to 22.9 s each) and under the synchronised one
  (593 s).
- Fourteen more candidates over five missions read the same twice each
  under the fixed clock, in 11.0 to 38.7 s against jobs of 76.8 to 590.5 s.
  Against their jobs every grade and every finding held; one score moved a
  point (deli_001 seed_9393, WARN 66 -> 67) -- and on that candidate the
  difference is the navigation setting, not the clock (the synchronised clock
  with synchronous navigation read exactly what the fixed one did).
- Without the synchronous navigation the fixed clock does NOT read the same:
  seed_9104's crew stuck count 9 -> 21. Laser Tag 0.27.0 is required, which is
  why the table moves with this release.

**Real-tool smoke:** 12 tests against the factory's own tools: before this release exactly the two rows read DRIFT (laser_tag grounded 0.26.0, installed Laser Tag 0.27.0; zoo grounded 1.101.0, installed 1.102.0), after it 11 passed and 1 skipped (dispatch's example inputs absent, as before)

**Suite:** 2,251 passed, 16 skipped, 0 failed (JUnit, 2,267 tests); tests/unit/test_laser_tag_clock.py, 4 tests, two failing on 0.179.1 (no --fixed-fps in the command, no fixed_fps on the adapter)
