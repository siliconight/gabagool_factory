## [0.184.0] - The scheduler's caps can be overridden for one invocation, so a wider width is measured before it becomes a default

**Why now.** Roadmap 239: with the graders and the export cut, cold run
9249's drive took 12.1 minutes, its shell and art legs 5.8 of them. Cold
run 9250 ran its legs under cProfile and the art leg's own job records show
the critical path: about 102 s of Blender jobs one after another (16 kit
builds 61.5 s, 15 dressing builds 24.2 s, the fixtures 11 s, the roof
props, the clutter), because `blender` is capped at 1 -- TDD 19.2's
default, never measured, where `godot_headless`'s cap is a measurement
(`godot_cap`). A wider width needs measuring first, on the factory's own
runs, and there was no way to set one without editing this file.

**What changed.** `LF_CONCURRENCY="blender=3"` (any classes, comma
separated) overrides the caps for the command line's scheduler -- one built
without caps of its own; caps a caller passes stay the caller's -- and the
run says so: `[scheduler] LF_CONCURRENCY: blender 1 -> 3`. A class the
scheduler does not know, a width that is not a whole number, or one below 1
refuses the run with the variable named, rather than being ignored. The
defaults are unchanged.

**Tests:** `tests/unit/test_concurrency_override.py`, nine cases (widths
per class; five spellings refused; the command line's scheduler takes it
and says so; a caller's caps are left alone; without it the defaults
stand), all failing on 0.183.0. 2,273 passed, 16 skipped, 0 failed (JUnit, 2,289 tests); tests/unit/test_concurrency_override.py, nine cases, all failing on 0.183.0
