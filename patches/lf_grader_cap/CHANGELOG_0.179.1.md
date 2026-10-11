## [0.179.1] - The Godot cap follows the machine and the width the graders were proven at; the grounded table follows Deli Counter 0.209.1 and Laser Tag 0.26.0

**Why now.** The walker, 2026-10-11: could cold runs be faster "without
losing any certainty of quality or introducing regressions". Measured on cold
run 9245 (restaurant_row_001, 16 buildings) from every job's own `duration=`:
the graders -- each candidate's Laser Tag evaluation and walk test -- are
88 % of the run's job time (Laser Tag 65 %, the walk test 22 %; every Blender
build together 3 %), and `DEFAULT_CONCURRENCY` let two of them run at once on
a machine with 8 cores and 16 logical CPUs, so the shell leg spanned 15.7
minutes in three waves. Its longest single evaluation was 10.25 of them, and
that job bounds the leg at any width.

- **`scheduler.godot_cap(cpu_count)`**: the smaller of what the machine
  allows -- one headless Godot job per physical core, read as half the
  logical CPUs, never below the 2 every machine had -- and
  `GODOT_PROVEN_WIDTH`, 3, the widest load the graders' verdicts were proven
  unchanged under. 3 on the machine that measured it; 2 on a
  four-thread laptop, as before. `DEFAULT_CONCURRENCY["godot_headless"]`
  reads it; no other class moves.
- **What it changes, and what it does not** (`docs/findings/grader_speed/`
  in the factory): every verdict is unchanged at three, and the walker took the trade on 2026-10-11 knowing what moves. Rerun from copies of cold run 9246's staged projects with each job's exact command: alone or two at a time (the old cap), every report identical to its job's in every field -- seed_9191 three times, all 1,943 events, seed_9292 twice; three Laser Tag evaluations at once, three trials, and all six graders at once, two trials: every grade, score, summary figure, finding, event count, time, source and collider identical in every report, the walk tests byte-identical, and in some reports one to three recorded event POSITIONS one rounding step (0.01 m) apart -- the same values each time (seed_9292's run-4 `ShotHitEnemy` at z -1.04 recorded -1.03), sitting on a rounding boundary. The cause is not established; Godot's async navigation iterations and the worker pool shared across processes are the suspects. No evaluation ran slower beside the others than alone (three in 189.5 s where one after another took 375)
- **A faster simulation clock was measured and refused.** Laser Tag's
  `--time-scale` (4 by default) would have halved the evaluation at 8 and
  cut it to 30 % at 16, but Godot scales the PHYSICS STEP with
  `Engine.time_scale`, and the reports changed from their first event: 49
  enemy-stuck events at 4x, 2 at 8x, 0 at 16x. Nothing here passes it.
- **Re-grounded, two rows**: `deli_counter` 0.209.0 -> 0.209.1 (a stair's
  circulation column ends at the top floor it serves) and `laser_tag` 0.25.0
  -> 0.26.0 (an enemy is built and steered as the contract's body), with the
  test stubs' VERSION files.

### Tests

`tests/unit/test_godot_cap.py`, four tests: the cap is the machine's bounded
by the proven width, the default reads this machine, three candidates'
evaluations run at once where the machine allows, and the other classes did
not move (the first three fail on 0.179.0: there is no `godot_cap`).

**Suite:** 2,246 passed, 16 skipped, 0 failed, exit 0, counted from JUnit output since the conftest prints no summary: 0.179.0's 2,241, the four new tests, and `test_sibling_locator`'s check of the new file. The new file fails on 0.179.0 (no `godot_cap`)

**Real-tool smoke:** `LF_TOOLS_DIR=<factory> pytest tests/real_tools` read DRIFT on exactly the two rows before (deli_counter 0.209.1 and laser_tag 0.26.0 installed against 0.209.0 and 0.25.0 pinned) and is all green after, the dispatch example skipped as always
