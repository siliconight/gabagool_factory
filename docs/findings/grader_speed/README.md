# Grader speed: where a cold run's time goes, and what may be cut without changing a result

**Question.** The walker, 2026-10-11: "is there anything intelligent we can
do to make our coldruns faster without losing any certainty of quality or
introducing regressions? Im thinking this is the most time consuming part of
our iteration process". The constraint sets the test: a speedup is accepted
only if every report it touches comes out byte-identical. Lever 4 is the one
place that bar moved, and why is recorded there: the old reports were
themselves wall-time-dependent, so "identical to the job" was a comparison
with a reading that could not repeat under load; the new one repeats under
any clock and load, and against the old jobs every grade and finding held.

## Where the time goes (cold runs 9245 and 9246, every job's own `duration=`)

    cold-9245-ws (restaurant_row_001, 16 buildings), 90 jobs:
      job time summed 31.6 min; first job start to last job end 20.5 min;
      the whole drive 32 min (the rest: export, light bake, walk copy, findings)
      laser_tag_evaluate     3 jobs   20.6 min   65.4 %
      walktest_navqa         3 jobs    7.1 min   22.5 %
      zoo_kit_build         16 jobs    1.0 min    3.1 %
      everything else       68 jobs    2.9 min    9.0 %
    cold-9246-ws (deli_001, 1 building), 28 jobs: 11.2 min summed, 7.8 span;
      laser_tag_evaluate 55.8 %, walktest_navqa 27.8 %

**The graders are 88 % of job time, and they queue.** `scheduler.DEFAULT_
CONCURRENCY` caps `godot_headless` at 2, so on 9245 the three candidates'
Laser Tag and walk-test jobs ran two at a time: the shell leg spans 15.7 min
(Laser Tag seed_9003 0.4 -> 6.8, seed_9104 2.9 -> 13.2, seed_9205 9.1 -> 13.1;
the walk tests 0.3 -> 2.8, 6.9 -> 8.9, 13.2 -> 15.7) on a machine with 8
cores, 16 logical, 16 GB.

## Laser Tag's evaluation is deterministic (`timescale_ab.sh`, `ab_9246`)

Cold run 9246's seed_9191 evaluation rerun from a copy of its staged project
with the job's exact command, twice on a quiet machine: **identical to the
job's own report in every field, all 1,943 events** -- the job ran beside a
walk test, so across processes and across load.

## Lever 1, REFUSED: a faster simulation clock

`run_map_eval.gd` takes `--time-scale` (default 4). Measured on the same
evaluation:

    time-scale  wall      events  identical to the job  enemy stuck  grade
     4          108.7 s   1,943   yes                   49           WARN 68
     8           46.5 s   1,498   no, from event 0        2           WARN 70
    16           30.9 s     777   no, from event 0        0           WARN 63

Godot scales the PHYSICS STEP by `Engine.time_scale` (4x simulates at 1/15 s
steps, 8x at 2/15), so a faster clock is a coarser simulation, not the same
one sooner. Refused. It also shows that the shipped 4x is a modelling choice
the findings move with: the game steps at 1/60 s (`realtime_ab.sh` measures
the evaluation there).

## Lever 2: the candidates' graders side by side (`concurrency_ab.sh`, `sixwide_ab.sh`)

Copies of cold run 9246's staged projects, each job's exact command, every
report compared with the job's own:

    width  what ran at once                          reports identical to their jobs'
    3      the three Laser Tag evaluations           3 of 3, every field  (trial 1)
           (each no slower than alone: 109.2 s against the job's 109.0; all three in
           189.5 s where one after another took 375)
    6      three evaluations + three walk tests      5 of 6   (trial 1: seed_9292's events)
    6      the same, again                           4 of 6   (trial 2: seed_9191's, seed_9292's)
    3      the three evaluations, trial 2            1 of 3   (seed_9191's, seed_9292's events)
    3      the three evaluations, trial 3            2 of 3   (seed_9292's events)
    1      seed_9292 alone, twice                    2 of 2, every field (event 244 at -1.04)

**Two at a time is bit-exact; three is verdict-exact.** Alone and at the old
cap of two, every report matched its job's in every field (seed_9191 three
times, seed_9292 twice). From three up, the verdicts never moved -- grade,
score, every summary figure, every finding, every event's count, time, source
and collider -- but some reports recorded one to three event positions one
rounding step apart, the SAME values each time (seed_9292's run-4
`ShotHitEnemy` at z -1.04 recorded -1.03 in four of the wider runs): numbers
sitting on a rounding boundary, nudged across it by a sub-millimetre
difference under load. **The walker's call, 2026-10-11: adopt three and note
the noise** (asked with the numbers above; "Adopt 3, note the noise").

**What differed at six.** In the reports that were not identical, every
outcome, total, grade and finding was: the difference is one to three events
whose recorded position moved by one rounding step, 0.01 m (seed_9191 run 14:
`ShotHitEnemy` at x -14.5 recorded as -14.49, two `ShotBlocked` at 4.7 and 4.5
as 4.71 and 4.51; seed_9292 run 4: one `ShotHitEnemy` z -1.04 as -1.03), the
same event, time, source and collider. So something in the simulation is not
bit-exact under six-wide load -- a sub-millimetre difference that surfaces only
where a value sits on a rounding boundary. The cause is not established:
gameplay runs on fixed physics ticks (the run state, the enemy brain and
movement, the bot), and Laser Tag's frame-paced code (the harness's trace
print, a destructible's debris timer) records no event; Godot's own threaded
physics or navigation under contention is the remaining suspect, unmeasured.

**REFUTED, KEPT: the first six-wide run's evidence was deleted by the script
that produced it.** Its cleanup ran `rm -rf "$X"/lt_9*` to remove the copied
project directories, and the glob matched the report `lt_9292.json` beside
them -- the one report that differed. The script now removes the directories
by name and prints the differing events itself; the second run is the one
quoted above.

**The cap that follows.** The longest single evaluation bounds a shell leg at
any width (9245's seed_9104 took 10.25 of its 15.7 minutes), so three recovers
nearly everything six would: `GODOT_PROVEN_WIDTH` = 3 in Level Factory
0.179.1 (`scheduler.godot_cap`: the smaller of half the logical CPUs, never
below 2, and that width), raised only on a measurement at the wider load.

**Open, then ANSWERED below (Lever 4):** the noise's cause. The settings a
staged evaluation runs with (`engine_settings_probe.gd`): physics engine
DEFAULT, not on a separate thread, 60 ticks, jitter fix 0.5, the worker pool at
all 16 logical CPUs, and `navigation/world/map_use_async_iterations` and
`region_use_async_iterations` both TRUE -- the navigation map updates on worker
threads, so when an iteration lands can move with contention. It was the
navigation: synchronous, three at once read identical to one (Lever 4).

**Measured on cold run 9247** (restaurant_row_001 on 9245's lot, its lots and
walk tests byte-identical to 9245's): the shell leg 15.7 -> 10.4 minutes, the
drive 30.4 -> 24.3, ending with its longest evaluation as predicted
(`docs/cold_runs/cold_9247/NOTES.md`).

## Lever 4, ADOPTED: a clock that does not wait, with the navigation on the evaluation's thread

**Every evaluation waited on real seconds.** Simulated time (the sum of a
report's run durations) against its job's wall time, cold runs 9245 (two at
once) and 9247 (three at once): 3.93, 3.97, 3.91 and 3.94, 3.96, 3.92 -- the
4x clock less the import and the nav bake. Godot keeps physics in step with
real time at whatever `Engine.time_scale` says; `run_map_eval.gd`'s comment
"Headless evaluation shouldn't wait on real-world seconds" stated an intent
the engine did not honour. It is also why three side by side ran no slower:
each process mostly slept.

**`--fixed-fps 60` alone (`fixedfps_ab.sh`, 9247's seed_9104, the job 593 s):**

    arm                                   wall      against the job
    A  the job's command, alone           593.4 s   identical in every field
    B  --fixed-fps 60, the 4x step         21.2 s   same grade and score; crew stuck 21 against 9,
                                                    from run 2's 72nd second, 0.05 mm apart
    C  --fixed-fps 60, time scale 1        63.2 s   the game's 1/60 s step: a different simulation
                                                    (first event 0.03 s against 0.13), grade held

**With the navigation synchronous (`syncnav_ab.sh`, both settings in the
copies' project.godot, read back by `engine_settings_probe.gd` first):**

    arm                                   wall      result
    D1, D2  --fixed-fps 60                 21.1, 23.0 s   identical to A and the job in every field,
                                                          2,196 events, and to each other
    L1-L3   the same, three at once        22.8-22.9 s    identical to D1
    E       the job's synchronised clock   593 s          identical to D1
    G1, G2  --fixed-fps 60, time scale 1   62.1, 61.7 s   identical to each other

**Fourteen more candidates over five missions (`breadth_ab.py`, each run
twice under the fixed clock with synchronous navigation):** 14 of 14 read the
same twice, in 11.0 to 38.7 s against jobs of 76.8 to 590.5 s. Against their
jobs: restaurant_row_001's two matched in every field (the staged Laser Tag
0.26.0); nine moved one to twenty events (a position by up to 0.12 m, or
which of two coincident colliders a shot named); three diverged far enough to
move secondary figures. **Every grade and every finding held on all fifteen;
one score moved a point** (deli_001 seed_9393, WARN 66 -> 67, crew stuck 6 ->
3; `breadth_verdicts.out.txt`). REFUTED, KEPT: the script's first draft guessed
the seeds and stopped on the fifth case (`breadth_ab.draft1.out.txt`).

**The clock or the navigation? (`clock_or_nav_ab.sh`, deli_001 seed_9393):**
the job's own command alone reproduced the job in every field; the
synchronised clock with synchronous navigation read exactly what the fixed
clock did. The difference from the job is the navigation setting -- when a
worker thread's update landed -- and the clock adds none. With the setting on
the evaluation's thread the report no longer depends on wall time at all:
not on the clock, not on load.

**Shipped:** Laser Tag 0.27.0 (`LT_Const.synchronous_navigation`, called by
`run_map_eval.gd` before the bake and read back after a frame -- the setters
are deferred server commands; `runtime_setters_ab.sh` showed them reading
identical to the project-setting arm, against an asynchronous control that
differs) and Level Factory 0.180.0 (`LaserTagAdapter.fixed_fps` 60, passed to
the engine before `--`). The engine hides `--fixed-fps` from scripts
(`OS.get_cmdline_args`, probed), so the command is the one place the clock is
chosen.

**Not changed, and the walker's call:** the step. Laser Tag still steps at 4x
(1/15 s). At the game's own 1/60 s an evaluation now costs about a minute
(G1, G2), not the 40 the synchronised clock would take, and reads the same
twice; `realtime_ab.sh`, written to measure 1x on the synchronised clock, is
superseded by those arms and was never run.

## The constraint moved: the export (cold run 9248)

With the graders on the fixed clock, cold run 9248's drive took 14.3 minutes
and its export 7.0 of them. Profiled (`python -m cProfile` over a re-export of
9248 in its own workspace, the run's package held aside and put back), 430.7 s:

    step                                         seconds   what it is
    the light bake                                 208.8   two --imports 112.1, the editor 88.3
    the greybox census                             100.4   one full --import, then the census
    the sidecar step                                81.9   two --import passes 78.0
    localize, dressing, occluders, merge, ...       ~40

**Importing was 65 % of the export: the same files five times.** The census's
import was pure waste -- the cache had been dropped straight after the bake and
the census, three steps later, needs one. Level Factory 0.181.0 drops it after
the census instead: the export 340.1 s, the census 4.2 s, its report identical.

The control that measured it (the run's own export against a re-export of the
same code) found a defect of its own: the shared textures' import pins, lost in
a random sixth of every export by the light bake's first import. Level Factory
0.182.0 reads them back off what ships (`docs/findings/texture_pins/`).

## Then the art leg: Blender one at a time (cold runs 9250, 9251)

After the export cuts (9249: the drive 12.1 minutes, the export 4.7) the
shell and art legs were the larger part. Cold run 9250 ran its legs under
cProfile (`PROFILE_LEGS=1`); its job records put about 102 s of the art leg
in Blender jobs one after another, `blender` capped at 1 since TDD 19.2 and
never measured. Cold run 9251 ran at three (`LF_CONCURRENCY`, Level Factory
0.184.0): the Blender window 114.0 -> 45.7 s, the art leg's jobs 251.7 ->
177.1 s, the drive 10.8 minutes. `blender_width_compare.py` classed every
file the Blender jobs built against two controls at one, since two runs at
one already differ (triangle and merged-vertex order, weighted normals a few
1e-4 apart, a manifest); nothing new beyond the same normal drift across
the comparison's tolerance. Level Factory 0.185.0 makes three the default
where the machine allows.

**REFUTED, KEPT:** cold run 9249's note said the compose job spent 62 s of
its 63.7 outside its command. `job.log` holds only the last of the job's
sixteen commands; the 63.7 s is sixteen buildings composed in turn -- the
next candidate, with the work the scheduler does for a cache hit (staging,
the git probe) before it asks the cache.

## Lever 3: one import of a package, not several

The export imports its package to bake it, the bake's work copy is a copy,
the walk copy imports again from scratch (`walk_export`), and each walk test
imports its staged project first (`walktest.py import_pass`, up to 600 s
allowed). Godot re-verifies an import cache against each source's hash, so a
reused cache is safe by construction where the sources are the same files.
Not yet measured.

## What is evidence of what

- The time split: every job's own `duration=` in its `job.log`; the spans
  from the logs' modification times less their durations.
- Determinism: one candidate of one mission, three runs. A broader claim
  needs the wider run each lever is accepted on.
- Lever 4: fifteen candidates over five missions, each run twice; the older
  staged projects carry the Laser Tag of their day, so "every grade held" is
  a statement about those versions under the two configurations, and only
  restaurant_row_001's three ran Laser Tag 0.26.0. The next cold runs grade
  0.27.0 itself.
- Which clock a job ran on: its own command line, the first line of its
  `job.log` (Level Factory 0.180.0 adds `--fixed-fps 60` there).
