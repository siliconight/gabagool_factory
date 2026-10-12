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

## Lever 4 on a stranger's level: the body moved seed_9205, not the clock (install test 8)

Install test 8 (factory 1.39.0, `docs/findings/stranger_install/`) read the
candidate it passed over, seed_9205, WARN 70 where install test 7 had read
PASS_WITH_TUNING 82: the crew dying in 7.0 s on average and 25 deaths in 25
runs, against 75.66 s and 2. The scene Laser Tag evaluated is the same byte
for byte in the two tests (`scene_hash` bd08d17d56c6 in both fingerprints;
level.tscn, site.tscn, the walk scripts and every building GLB the same in
the two staged projects, which differ in the addon, Lot 0.117.0's
`lot_navqa_setup.gd` that only the walk test's scene loads, the drawn JSON's
absolute paths and the import cache's `.scn` files). Laser Tag moved twice
between them: 0.26.0, the enemy's body, and 0.27.0, this lever.
`body_or_clock_ab.sh` ran the job's own command on copies of test 8's staged
project, the addon's files swapped for each commit's (the staged addon is
the commit's files and Godot's `.uid` files, checked):

    arm     body    clock, navigation           grade                survival  deaths  enemy stuck  events
    f27     0.27.0  fixed, its own setters      WARN 70              7.0 s     25      36           1,981
    f26     0.26.0  fixed, project settings     WARN 70              7.0 s     25      36           1,981
    f25     0.25.0  fixed, project settings     PASS_WITH_TUNING 82  75.66 s   2       57           1,726

f27 reads test 8's job in every field (the control: the instrument
reproduces the job); f26 reads f27 in every field (0.27.0's setters are
0.26.0 with the settings, as `runtime_setters_ab.sh` found on the deli); and
f25 -- the old body under the new clock, in test 8's project -- reads test
7's job in every field, all 1,726 events. **So the body moved it and the
clock did not**, and the import cache's differences moved nothing. On the
jobs' own waiting clock, the navigation asynchronous, the same both ways:

    arm     body    clock, navigation                           wall      reads
    w25_7   0.25.0  waiting, asynchronous, test 7's project     515.8 s   test 7's job in every field (the control)
    w25     0.25.0  waiting, asynchronous                       515.9 s   w25_7 in every field, and f25
    w26     0.26.0  waiting, asynchronous                       526.8 s   test 8's job in every field, and f26

against 22.9 to 23.9 s for each fixed arm. On this candidate neither the
clock nor the navigation setting moves a field for either body; the body
moves the grade on both clocks, the event logs apart (1,726 events against
1,981, 1,722 of the first 1,726 different; `body_or_clock_ab.out.txt`). With the pill scene's 0.40 m capsule seed_9205's enemies
jammed 57 times and seldom reached the crew (first contact 2.6 s); with the
contract's 0.35 m one they jam 36 times, reach it in 1.67 s and kill it in
every run. What the evaluation now reads is what an npc_standard body does
(`agent_contract.json`), so the WARN is the truer reading of that layout.
0.26.0's own measurement (deli_001 seed_9191) moved the other way -- a
grade up, 49 -> 28 stuck -- which is the point: freeing a jammed enemy can
make a map read safer or deadlier, and only the body the game will use can
say which.

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

## Then the compose: sixteen commands in turn (Level Factory 0.186.0)

With Blender at three, cold run 9251's largest block in the art leg was one
job, the compose: 64 s, the mission shell's compose and then one per
building, one after another. The buildings do not depend on each other --
each command clears and writes only its own folder under
`presentation/lot/` -- but the shell's must go first, because Deli Counter's
`build_package` clears its output folder and that folder holds theirs.

`compose_replay_ab.py` replays the job's own sixteen commands, read from
9251's workspace index, every input the run's own job outputs, into scratch
folders three ways: in turn twice (the control), and the shell's first and
alone with the buildings four at a time (`python_cpu`'s width):

| arm | wall | files | differ from SEQ1 |
|---|---|---|---|
| SEQ1, in turn | 58.3 s | 928 | -- |
| SEQ2, in turn | 58.2 s | 928 | 0 |
| PAR, the shell then four at a time | 25.4 s | 928 | 0 |

The first run (`compose_replay_ab.draft1.out.txt`) read 59.2, 58.5 and
25.5 s with the same zeros. The replay is the job: against the run's own
output folder, 928 of 928 files are identical, and that folder's other 928
are the scheduler's provenance sidecars. In every arm, and in the run, the
deli and the office exit 3 -- Deli Counter's z-fight gate, two coplanar
pairs each, which the compose job treats as advisory (`exit_advisory`; the
finding is `PRESENTATION_ZFIGHT`, moderate) -- so the job carried on past
them before the change and still does.

Level Factory 0.186.0 lets a planned command say it may run beside its
neighbours (`PlannedCommand.parallel`), runs a run of them up to the job's
class width with the results in plan order, and marks the per-building
composes. `job.log` now holds every command of a job, the defect behind
9249's refuted note above. Not measured here: the compose beside the other
jobs a real drive runs at the same time. A cold run is that measurement.

**What the art leg waits on** (`leg_spans.py`, from a workspace index: the
critical chain, from the job that finished last back through whichever
dependency finished last, and each job's wait between that dependency and
its own start). It reproduces 9250's and 9251's figures (251.7 and 177.1 s,
Blender windows 114.0 and 45.7 s). 9251's chain: Pixelcoat 16.6 s, a wait of
22.2 s for a Blender slot, the office's kit 9.6 s, a wait of 11.9 s, its
dressing 2.2 s, the compose 64.1 s, the themed site 8.3 s, a wait of 26.8 s,
Lux 3.7 s. Nothing else ran during that last wait: the Lux job's receipt
(written after planning, before the cache is asked) is stamped at its start,
so the 26.8 s is the scheduler's own work for the job -- staging a project of
the whole themed site, 2,040 files, and a full Godot `--import` of it
(`stage_godot_project`), which the driver needs, since it instantiates the
scene and reads the fixtures' mesh bounds. Unsplit between the copy and the
import.

## The export again: the bake's lightmap requests in the second pass (Level Factory 0.187.0)

Cold run 9252 stamped its steps: the export was 284 s of a 615 s drive. It
imports the package three times over -- the sidecar step's first pass (no
sidecars yet), its second (sidecars rewritten, the cache dropped,
everything again), and the light bake's, which asks every model for a
lightmap UV (`light_bake.mark_imports`) and imports again for it.

Why the one-import plan below failed is in cold run 9251's own import log,
which keeps every pass's output. The worldskin skins a building's slabs by
`load()`ing one of its floor modules. In pass one, a model's first import,
one base left 105 slab meshes greybox and two took their reveal from roof
modules: the floor module was not imported yet. In pass two, its sidecars
present, all three took a floor module and skinned every slab. The second
pass is not a first import.

`uv_second_pass_probe.py` exports 9252's mission twice in its workspace,
each arm in its own process, the run's package held aside and put back: A
as it was, B with `mark_imports` applied once just before the second pass.

| | A | B |
|---|---|---|
| the export | 277.6 s | 238.4 s |
| the sidecar step | 76.0 s | 86.1 s |
| the bake's imports | 55.0 + 4.3 s | 5.0 + 4.3 s |
| pins re-pinned after the last import | 74 | 0 |
| greybox census | 3 surfaces, 49.7 m2 | the same |
| Empties' merged meshes | 236 | 148 |
| the bake's users | 3,491 | 3,320 |
| occluders | 1,370 | 1,370 |
| closure verdict | ok | ok |

**The merge, read** (`merged_materials.py`). Both packages carry the same
148 (Empty, side, material) groups. A splits them into 236 meshes, up to
four in one; B makes exactly one each -- what the merge's own docstring says
it makes, "one mesh a side per material". The merge keys a group on the side,
the material's name, its uv1 flags and the surface format; the names are the
same, so A splits on a flag or the format, which one not measured. The 962
colliders and the 24 dropped doors are the same in both.

**The users, read** (`lightmap_users.gd`, each package's `bake.lmbake`
loaded in a scratch project holding only it and its lightmap). 3,135 users
in both; every one that differs is a merged mesh of an Empty placed across
the street -- 356 in A, 185 in B, the twelve Empty scenes placed 26 times.
B's lightmap needs 15 slices where A's needs 16.

**The control.** The run's own package against A, the same code: 62 files
differ -- the bake's three, the twelve Empties' scenes (their node ids),
five manifests, and 42 texture sidecars, because which textures the bake's
import resets changes from run to run. A against B: those classes, the
merged meshes, and 74 texture sidecars that A's re-pin rewrote with a new
uid and B never reset.

**Level Factory 0.187.0** makes B the export (`_write_import_sidecars`'
`bake_spawned`). Re-exported twice on it
(`uv_second_pass_probe.0187.out.txt`): 243.3 and 238.6 s, the bake's import
of every model 5.0 s, no pin lost, every gate as above; the two re-exports
differ only in the bake's three files, the Empties' scenes, five manifests
and one sidecar's uid -- no texture sidecar, now that no import resets them.

## The walk copy: the export's own import, kept (Level Factory 0.188.0)

Cold run 9253's step stamps: the walk step 88 s of a 580 s drive, 15 %.
`tools/walk_export.py` copies the package and imports it from scratch, a
minute after the export imported the same files and deleted the cache.

`walk_cache_probe.py` re-exports 9253's mission with the cache moved beside
the package (`<package>.import_cache`) instead of deleted, then makes three
walk copies with the real tool: two as the drive does (the control: what an
import changes on its own) and one with the kept cache copied in as its
`.godot` before the same import pass.

| | W0, scratch | W0b, scratch | W1, the kept cache |
|---|---|---|---|
| the walk copy | 86.4 s | 88.2 s | 11.5 s (5.1 + 2.2 + 4.2) |
| imported files differing from W0 | -- | 482 scenes + their 482 checksums | the same, + 1 checksum and the lightmap texture |
| models digested, differing from W0 | -- | 0 of 501 | 0 of 501 |
| the level loaded | 20,954 nodes, 3,380 meshes, 242 lights, 3,320 users | the same | the same |

The probe's first run read 85.6, 86.2 and 9.6 s
(`walk_cache_probe.draft1.out.txt`).

- **An import is not byte-deterministic**: two imports of the same files from
  scratch differ in 482 scene files and their checksums. A file comparison
  cannot say whether W1's scenes are W0's, so `import_digest.gd` loads every
  model the way the level does and digests what loads -- each node, transform,
  mesh surface, vertex and index count, second UV set, material and texture.
  **Its positive control**: one model's sidecar changed in W1 (light baking 2
  -> 1) and imported again moved that model's digest and no other; undoing it
  moved it back. It also shows a sidecar changed after the cache was made is
  imported again by the copy's own pass.
- **The lightmap texture** in W1 is the editor's encoding: the export's cache
  has carried the bake editor's import of `bake.exr` since 0.183.0, and the
  copy's headless import encodes it otherwise. Both are the same lightmap at
  the same settings.
- **REFUTED, KEPT: the first census** (`walk_cache_probe.draft1.out.txt`)
  instantiated the walk scene and counted 1,380 nodes, no mesh and no light in
  every copy. `mission.tscn` loads its content in `_ready`, which a scene
  instantiated outside the tree never runs, so it counted the frame and could
  not have failed. `walk_copy_census.gd` now loads the scenes the entry script
  loads.

Level Factory 0.188.0 keeps the cache beside the package
(`occluders.keep_cache`) and `walk_export.py` moves it in -- moved, not
copied, so it costs no disk, and a second walk copy imports from scratch as
before. A cold run is the drive's measurement.

## The sidecar step: every model imported once (Level Factory 0.189.0)

Cold run 9254's export was 48 % of its drive, and its sidecar step imported
the package twice: a first pass with Godot's defaults, then -- the sidecars
rewritten, what extract wrote deleted, the cache wiped -- everything again,
86 s. `sidecar_once_probe.py` re-exports 9254's mission in its workspace, an
arm a process, and judges each on the gates, the pin census and the digest
of every model as Godot loads it from the arm's kept cache (`import_digest.gd
-- --full`, which says for each differing surface whether its texture alone
moved). Each arm's failure is what made the next one; every file is kept.

| arm | what it did | sidecar step | what was wrong |
|---|---|---|---|
| A | as it was | 86.0 to 86.8 s | -- |
| B | models' final settings as the project's defaults, bases held to a second pass | 60.4 s | 461 models embedded a copy of their shared textures, 1,463 surfaces: imported before the textures were (`draft1`) |
| C | three passes: textures, models, bases | 62.1 s | 26 textures re-pinned at the end (`arms_A_C`) |
| E | C with the pinned textures imported alone first, the pins counted every pass | 66.4 s | the same 26 -- and none lost inside the step (`arms_A_E`, `phases_E`) |
| F | C with the filtered set read before the models were held | 62.8 s | 2 pins reset, 3 surfaces embedded: six models imported twice, their light baking set back (`arms_A_F`) |
| G1 | F with those models held to the last pass, from written sidecars | 62.2 s | 3 models without the worldskin: a written sidecar does not get the project's defaults (`arms_A_G1`) |
| G2 | G1 with the import script written in | 62.1 s | 7 sidecars `gltf/texture_map_mode=0` where every new import reads 1 (`arms_A_G2`) |
| G3 | G2 with whole sidecars copied off an imported model | 62.2 s | nothing: 501 of 501 models the same, every gate, no pin lost, the packages differing only where two exports of the same code do (`arms_A_G3`) |

What each taught, each now a line of the step's comment:

- **A model imported before its shared textures embeds a copy of each** --
  and every gate passed B, because none checks texture sharing. Only the
  digest saw it.
- **E's 26 were not a race.** The census after every pass read 415 of 415
  pinned; the 26 were `_filtered_shared_textures` reading the models' glTF
  while every model was renamed `.glb.held`, finding none filtered, and
  pinning 26 VRAM textures lossless until the read-back after the last
  import corrected them.
- **A model imported twice, its textures already imported, is the race
  0.182.0 backstops** -- F re-imported six models to set their light baking
  back and reset two pins and embedded three copies.
- **A sidecar written by hand is not a new import**: the project's defaults
  reach only a file with no sidecar (G1), and a key it lacks takes the value
  an import from before the key existed would have had (G2).
- **The digest's counter.** Its first reading (`draft1`) found 463 models
  different; two were Godot's made-up names for unnamed nodes,
  `@StaticBody3D@19801` against `@19798`, a counter that runs across
  everything loaded before. `import_digest.gd` sets the counter aside, and
  `import_describe.gd` prints what a digest digests, for reading one.

**Level Factory 0.189.0** is G3, applied. Re-exported against the step as
0.188.0 had it, read from its commit (`sidecar_once_probe.0189.out.txt`; the
first try, `0189.draft1`, failed to load the old module): the sidecar step
85.8 -> 61.5 s, the export 235.9 -> 212.2 s, everything else as G3.

## Found on the way: the lossless pins do not survive an editor (the walker's call)

Reading why the bake's editor takes 20 s to open the scene: its own log
(`<package>.lightbake.log`) says, texture by texture, "Texture detected as
used in 3D. Enabling mipmap generation and setting the texture compression
mode to VRAM Compressed (S3TC/ETC/BPTC)" -- 426 of them in 9255's re-export,
the shared textures the export pins LOSSLESS (`SHARED_TEX_PINS`,
`compress/mode=0`, roadmap 89's reason) among them, and 22 normal maps
"detected as used as a normal map", set to red-green compression. Every
shipped `_tex/` sidecar keeps `detect_3d/compress_to=1`. So the pins hold in
a headless import -- the export's own, the walk copy's -- and in no editor:
the bake's, the walk copy opened to be walked, a recipient's. What anyone
has looked at in an editor has been the VRAM-compressed textures.

Priced (`sidecar_once_probe.py`, arm D: `detect_3d/compress_to=0` added to
the pins, `detect3d.out.txt`): the bake's editor re-encoded 12 textures
where it had 426 (the 22 normal maps as before: a different detection), the
scene opened in 16.4 s against 20.3, the export 209.1 s against 213.8;
every model loading the same. About 5 s; the question is not speed. The
choice is the walker's, because it is a look and a memory trade, and not
changed here:

- **Lossless everywhere** (detection pinned off): what the pins were written
  for; more texture memory than the compressed textures every editor has
  shown; the look changes from what has been seen.
- **VRAM everywhere** (the pins say mode 2): what every editor has shown;
  less memory; roadmap 89's reason for lossless set aside on the record.
- **As it is**: a package whose textures depend on whether it was ever
  opened in an editor.

**DECIDED, the walker, 2026-10-12: "go with compressed everywhere"** --
Level Factory 0.190.0. `editor_texture_probe.py` re-exports a workspace with
the light bake's work copy -- the project its editor opened -- kept, and
compares every texture sidecar in it with the package's, key by key. On
0.189.0 (`editor_texture_probe.0189.out.txt`) the editor changed 426: on
every texture it found in use the detection 1 -> 0, `compress/mode` 0 -> 2
and a mip chain (the 8 skins); on the 22 normal maps -- exactly the 22 the
models' glTF names as `normalTexture` -- red-green compression and a
roughness limiter Godot points at the map itself; on nothing else (the
runtime's and the validation overlays' images, the lightmap, and the
cruiser's livery, which only spawns at run time). 0.190.0 pins those
decisions before any import (shared, skins, every sign whatever its pack
asks, the normal maps read off the glTF). Re-exported on it
(`editor_texture_probe.0190.out.txt`): the editor logged nothing detected
and left all 572 texture sidecars as they ship; it opened the scene in
14.7 s against 20.3; the export 200.3 s.

## The bake's editor: twenty seconds reading the scenes' groups (Level Factory 0.191.0)

After 0.190.0 the export was still the longest leg (cold run 9256: 204 s of
a 452 s drive) and the light bake's editor the longest part of it (88.1 s).
The run records the editor's whole time and two of its parts -- the scene's
opening and the bake -- and nothing of the rest. `bake_phases_probe.py`
re-exports a workspace's mission with the bake's plugin swapped for a copy
that prints the engine's own clock at each of its steps (`BAKE_T`), holding
the workspace's package aside while it does. On 9256's workspace
(`bake_phases_probe.out.txt`):

| the engine's clock | step | since the step before |
|---|---|---|
| 4.9 s | the plugin entered the tree | |
| 32.4 s | the scene asked for | 27.5 s |
| 47.1 s | the scene open | 14.7 s |
| 48.7 s | Bake pressed | 1.6 s |
| 84.5 s | the light data read | 35.7 s (`bake_ms` 35,676) |
| 85.2 s | the scene saved | 0.7 s; the editor exits 2.8 s later, 88.0 s in all |

The plugin asks for the scene once 180 frames have passed and the editor's
file system has stopped scanning, and marks the ask when
`open_scene_from_path` returns. Run again with Godot's `--verbose` and the
scan sampled every 30 frames (`--verbose --scan`,
`bake_phases_probe.scan.out.txt`; everything slower under the logging, the
editor 128.7 s): the file system said it was scanning at every sample from
8.4 s to 47.0 s, at four frames a second, and between the plugin's start and
the bake scene's load the log records the load of every one of the package's
482 models -- 438 under `lot/`, 42 under `cover/`, 2 under `assets/`, each
through its imported `.scn` -- and 1,870 texture loads, with the shader
variants they compile. The work copy's `.godot` held no
`scene_groups_cache.cfg`: the export's imports are headless, and none of
them writes one.

Given one -- the cache an editor had written for the same scenes, from the
work copy `editor_texture_probe.py` kept on its re-export of 9255
(`--groups-cache`, `bake_phases_probe.groups.out.txt`) -- the file system
said it was not scanning at the first sample (6.0 s, frame 30), the scene
was asked for at 13.1 s and the editor took 68.0 s in all; the opening
(14.5 s) and the bake (`bake_ms` 35,147) as before; the export 182.1 s
against 202.9.

The cache's content is in the scenes. It lists each scene whose nodes are
put in any group, with the groups (`[res://<path>]`, `groups=[&"a", ...]`):
the editor's own lists 3 of the package's 22 scenes -- the `site.tscn` of
`lot/deli_a01`, `lot/office` and `lot/pharmacy_a01` -- and the `groups=[...]`
of each scene's `[node ...]` headers, parsed, give exactly those 3 with
exactly those groups, the order within a scene aside.

**Level Factory 0.191.0** writes it: `light_bake.write_scene_groups_cache`,
into the package's `.godot` after the bake's import pass and before its work
copy, so the work copy starts with it; `occluders.keep_cache` moves it with
the rest of that `.godot` to the walk copy, and the package ships none, as
before. Measured on 9256's workspace, four re-exports in the order change,
control, control, change (`bake_phases_probe.0191.out.txt` and
`.0191b.out.txt`; the control, `--no-groups-cache`, is the same code with the
write made a no-op -- the bake as 0.190.0 ran it):

| | 0.191.0 | control | control | 0.191.0 |
|---|---|---|---|---|
| the arm | `groups0191` | `control0190` | `control0190b` | `groups0191b` |
| the scene asked for | 13.6 s | 32.5 s | 33.8 s | 13.1 s |
| scanning at a sample | at none | frames 30-90 | frames 30-90 | at none |
| the scene open, after the ask | 14.8 s | 14.7 s | 14.8 s | 14.5 s |
| the bake (`bake_ms`) | 35,727 | 35,127 | 38,775 | 35,473 |
| the editor in all | 69.3 s | 87.6 s | 92.6 s | 67.5 s |
| the bake's two imports | 5.1, 4.2 s | 5.1, 4.2 s | 5.1, 4.5 s | 5.1, 4.3 s |
| the export | 184.1 s | 202.5 s | 212.5 s (*) | 183.2 s |

(*) The second control's first 25 s shared the disk with a `du` left running
by another command; it was stopped at 05:00:30, about two minutes before
that arm's editor started.

`light_bake.json` is the same in every count in all four (3,320 users; 494
models baked, 6 dynamic, 1 spawned; 224 primitive meshes; 213 steady rigs,
29 live; 215 room fills); each changed arm wrote 3 scenes, 548 bytes, and
the cache kept beside its package carried the same bytes. Every package
differs from 9256's own in the same 21 files -- the five bake files, the
twelve rowhome Empties' `site.tscn`, `LF_MANIFEST.json`, `LICENSES.json`,
`export_closure_scan.json` and `portable_resource_manifest.json` -- and the
change from the control in those 21 too: the files any two exports differ
in. Byte identity, the bar this README sets, cannot be asked of the bake --
two exports of the same code differ in its five files -- so the bar here is
the control's: nothing differs that two exports do not, and in the lightmap,
which they do, no more than they do.

**The lightmap, texel by texel.** `lightmap_compare.py` has Godot read each
`bake.exr` (`exr_dump.gd`, headless; 1024 x 15,360 half-float texels) and
compares every pair over the colour channels (`lightmap_compare.0191.out.txt`;
its null control first, in `lightmap_compare.controls.out.txt`: 9256's
lightmap against itself, 100 % the same). The lightmap's mean is 0.031:

| pair | texels the same | mean difference | largest | texels apart by > 0.01 |
|---|---|---|---|---|
| 0.191.0 against the control (`groups0191b`, `control0190b`) | 93.44 % | 0.000002 | 0.0103 | 1 |
| 0.191.0 against 9256's own | 90.96 % | 0.000028 | 1.127 | 11,257 |
| the control against 9256's own | 90.84 % | 0.000030 | 1.127 | 12,184 |

The change's lightmap is nearer the control's than two exports of 0.190.0
are to each other.

**Found on the way: compressed everywhere moved the baked light.** The same
instrument on cold runs 9254, 9255 and 9256 -- one level, one lot, one seed
-- reads 9255 against 9254 (0.189.0 against 0.188.0; in both the bake's
editor re-encoded the shared textures it found in use) at 89.76 % of texels
the same and a mean difference of 0.000141, and 9256 against 9255 (0.190.0,
every texture compressed before any import) at 29.53 % the same, 0.000613 on
average -- 2 % of the lightmap's mean, about four times what two exports
differ by -- 0.066 at the 99.9th percentile and 2.95 at most. The control
and 0.191.0 against 9255 read as 9256 does (`lightmap_compare.controls.out.txt`,
`lightmap_compare.0191.out.txt`).
Whether a 2 % shift in bounced light shows is a question for frames, not for
this instrument; it is part of what the walker's call of 2026-10-12 bought.

**What is left of the editor** after 0.191.0, from the same clock: its own
start to the plugin (5.0 s); the plugin's 180-frame floor (frame 180 at
8.7-8.8 s, 55 frames a second once nothing scans); `open_scene_from_path`
until it returns (4.4-4.8 s, where the control's took 3.3-3.4 s -- part of
what the groups pass had loaded is loaded here instead); the scene's opening
after it (14.5-14.8 s: the bake scene loads the level, every model again,
and compiles its shaders into a fresh copy's empty shader cache); the press
(1.6 s); the bake (35.5-35.7 s); the save and the exit (2.7-3.5 s).

**Residual.** The verbose log's counts (482 models, 1,870 texture loads)
were read in the session that ran it, and the next run of the probe wrote
its own log over the same file; they rest on that reading and on the scan
samples kept in `bake_phases_probe.scan.out.txt`. The probe now keeps each
arm's log, and its lightmap, under the arm's name.

## The export, process by process; the bake's clock (Level Factory 0.192.0)

After 0.191.0 the export was still the drive's longest leg (cold run 9257:
187 s of 433). `export_timeline_probe.py` re-exports a workspace's mission
with every process the export starts timed -- its start since the export
began, how long it ran, a short form of its command -- and every line the
export prints stamped; `--profile` runs it under cProfile as well. On 9257's
workspace, 182.8 s (`export_timeline_probe.9257.out.txt`):

| part | seconds |
|---|---|
| the sidecar step's three imports (textures and the rest; the models; the bases and own-light-baking models) | 17.8, 32.1, 7.0 |
| the bake's editor | 68.0 |
| the bake's two imports (its UV2 pass, the one after) | 5.0, 4.2 |
| the dressing's and the backdrop's extraction (an import and a script each) | 7.5 |
| the occluders' bake and count, the Empties' merge, the greybox census | 6.5, 2.2, 3.2 |
| the export's own Python, between the processes | 29.3 |

By the profile (`export_timeline_probe.9257.profile.out.txt`), the largest
parts of the Python are the localizer (9.1 s under the profiler, 7.9 of it
rewriting text), the light bake's own steps around its editor (7.2 s under
the profiler: the timeline's 4.9 s gap before the editor is the work copy
being made; the 2.6 s after the bake's log line, by the code's order, its
removal -- not timed apart), and the manifest and closure verdict (about
4 s).

**The open's floor.** The bake's plugin asks for the scene once the file
system is idle and looks for it 240 frames later. Cold runs 9254 to 9257
each logged it open at frame 240, the floor itself: the scene was open at
the first look. With the floor at one frame (`bake_phases_probe.py
--open-floor 1`, `bake_phases_probe.openfloor.out.txt`; change, control,
control, change on 9257's workspace) the plugin saw it open at frame 1, 9.8
and 10.0 s after asking -- the editor's first frame of the opened level --
and the editor took 64.1 and 64.4 s against 67.9 and 68.4.

**The bake's clock.** The two floor-1 lightmaps were nearer each other than
the two controls were (`lightmap_compare.openfloor.out.txt`, by layout: a
mean difference of 0.000001 against 0.000032), and each was further from
its control than the controls from each other (0.000051, 0.000061), the
users most apart outdoor props by the streetlights. Lux's failing fixtures
keep a clock in the bake's editor too (`lux_streetlight_rig.gd`,
`lux_fluorescent_rig.gd`: `_fail_t += delta`, the lens's
`emission_energy_multiplier` following the lamp), and a lens's emission is
baked, though the failing lamps themselves are left live: every bake kept
each failing lens at the level it had when Bake was pressed. The test
(`--freeze-time`: `Engine.time_scale` 0 as the plugin starts, so every such
clock stays at 0; `bake_phases_probe.freeze.out.txt`,
`lightmap_compare.freeze.out.txt`): two bakes, one pressed 4.4 s after the
other, came out with every user's light the same to the last bit, and
`bake.exr`, `bake.lmbake` and `bake.exr.import` byte for byte the same; each
against its running-clock arm 0.000093 and 0.000133 apart, the users most
apart the streetlights' metal, the newspaper boxes and the parking meters
by them. So the lightmap differences every comparison above was measured
against were never the bake's: they were the failing lenses, caught at a
different moment each time.

What the stopped clock bakes a failing lens at is the level of its curve at
0: a stuttering tube at full, a filament at about 0.97, and a cycling
streetlight -- every third one -- wherever its own seed puts it in its
cycle. Fixed for a level now, where it was drawn anew every bake; which
level a failing lens SHOULD bake at (dark like its lamp, full, or its
cycle's mean) is a look, and the walker's.

**The localizer.** `_rewrite_text` pulls a tool's script into the package
when a localized `.gd` names its global class, and asked that of every class
name the tools declare (68), each with its own pattern over the whole
script: one pass over 9257's 76 text files took 1.69 s, 1.67 of it in 1,804
searches over the 44 scripts, twelve of them a 95 KB `zoo_worldskin.gd`.
The export runs about three passes. A name the text does not contain cannot
match, so a substring test now comes first.

**Level Factory 0.192.0** ships all three: the plugin stops the engine's
clock as it starts, looks for the scene from frame 1, and the localizer's
scan skips names a script does not contain. Measured as shipped on 9257's
workspace (`bake_phases_probe.0192.out.txt`,
`export_timeline_probe.0192.out.txt`): exports of 172.5, 172.0 and 171.4 s
against 182.9 and 184.7 on 0.191.0; the editor 64.6, 64.2 and 63.8 s; the
export's own Python 22.3 s against 29.3, its first import at 11.7 s against
18.8; the localizer's pass over the 76 text files 1.69 -> 0.079 s. The two
shipped bakes are byte for byte the same as each other and as the
stopped-clock bakes of an hour before, so two exports of one level now
differ in 18 files where they differed in 21: `light_bake.json` (its
timings), four manifests, `bake.tscn` and the twelve rowhome Empties'
`site.tscn` -- the last thirteen not yet asked why. Against a 0.191.0
export the package differs in its 21 files alone and in none of its 378
scripts.

**SUPERSEDED, KEPT: "byte identity cannot be asked of the bake."** The
0.191.0 section above says two exports of the same code differ in the
bake's five files, and set the bar at the control's noise. Three of the
five were never the bake's: with the clock stopped they are byte for byte
the same, so since 0.192.0 a change to the bake's editor is held to
identical `bake.exr`, `bake.lmbake` and `bake.exr.import`.

## The bake draws nothing while it bakes; the work copy (Level Factory 0.193.0)

With two exports of one level baking the same bytes since 0.192.0, a change
to the bake's editor is held to identical `bake.exr`, `bake.lmbake` and
`bake.exr.import`, and nothing looser.

**The editor drew the level while it baked.** The bake's progress bar pumps
the editor's main loop, and with its 3D viewports drawing, every pump drew
the whole level again. `bake_phases_probe.py --no-viewport-at-bake` sets the
four viewports' render targets not to update as Bake is pressed: on cold run
9258's workspace two bakes of 31.4 and 31.5 s and the editor 59.3 and 60.2 s,
against the run's own bake of 35.7 s, with the run's bytes
(`bake_phases_probe.noviewport_at_bake.out.txt`).

**REFUTED, KEPT: stopping the drawing from the start.** The first try
(`bake_phases_probe.noviewport.draft1.out.txt`) set `update_mode`, which a
Godot 4 `SubViewport` does not have; the editor logged a script error,
`_enter_tree` stopped there, and no viewport was stopped -- its "no change"
was a dial never turned, found by the missing line in the editor's log, not
by the timings. Set right (`render_target_update_mode`,
`bake_phases_probe.noviewport.out.txt`), the stop from the start gave two
bakes byte for byte the same as each other and 17.5 % darker than the run's
on average, the outdoor ground most (`lightmap_compare.noviewport.out.txt`):
the bake reads something only a drawn frame makes; the sky's light is the
likely one, not shown. And the opened level's first frame took about 10 s
with nothing drawn, so that frame's time is not the viewport's -- what it is
remains unmeasured.

**The work copy.** The bake copies the package and its import cache before
its editor opens them and removes the copy after. Timed on 9258's walk copy,
6,058 files and 252 MB: `copytree` 4.7 and 5.3 s, the same files across
eight threads 2.1 and 2.0 s, `rmtree` 2.1 to 2.8 s. 0.193.0 copies across
eight threads and renames the copy aside to be removed on a thread while the
export goes on.

**As shipped** (`bake_phases_probe.0193.out.txt`,
`export_timeline_probe.0193.out.txt`): exports of 162.4, 164.3 and 163.8 s
against 171.4 to 173.2 on 0.192.0; the editor 59.4, 60.7 and 60.4 s; the
export's own Python 17.2 s against 22.3, the gap before the editor 2.0 s
against 5.1; the bake files byte for byte the run's own, the package
differing in the 18 files two exports differ in, and no work copy left
beside it.

## Two cold runs, one lightmap: Zoo's faces in one order (Zoo 1.103.0)

Since Level Factory 0.192.0 two exports of one workspace bake the same bytes.
Two cold runs did not: 9256 to 9259 packed the deli's lightmap three ways,
each time because one deli dome glass came out of Blender with a different
chart in Godot's lightmap unwrap and some 2,860 users moved with it
(`docs/cold_runs/cold_9257/` to `cold_9259/`).

**Where it entered.** The deli fixtures job (`zoo_fixtures_build.deli_a01`) had
the same inputs in 9258 and 9259 -- its fingerprints differ in their time
stamp alone -- and wrote two GLBs. `zoo_repro_probe.py` replays a Zoo build N
times against a chosen Zoo and compares every output, mesh by mesh, array by
array: built twice (`zoo_repro_probe.before.out.txt`), every dome glass and
every pendant bulb had the same vertices, normals, UVs and colours, and its
triangles in another order, or some of them other triangles, a few normals
1e-4 apart with them. What it was not: Python's hash seeds (Zoo's random
streams are seeded from digests), Blender's threads (`--threads 1`,
`zoo_repro_probe.t1.out.txt`, still differs), Zoo's weighted normals alone
(off, `zoo_repro_probe.nown.out.txt`: the domes matched once, every bulb still
differed). Read off the two builds' .blend (`blend_mesh_dump.py`): each bulb's
vertices the same, in the same order; 54 of its 60 faces at other places.

**Blender's own operators.** `uvsphere_order_probe.py`, in fresh Blender 5.1
processes with no Zoo code: `bmesh.ops.create_uvsphere` laid its vertices in
one order and its faces in two orders across four processes, and a sphere
through `bisect_plane` as Zoo's `add_hemisphere` cuts it came out with its
faces in four orders -- the same faces every time, sorted. And an operator
that makes a face starts it where it likes: the dome's 20-cornered cap
(`holes_fill`) started at one of two neighbouring corners, dome by dome across
four builds, with its rim given in one order or not; the exhaust fan's hood,
cut at an odd ring count, had 11 of its 48 faces start at another corner. A
GLB's triangles follow the faces, and a face is triangulated from its first
corner. Zoo's own `add_hemisphere` also handed its bisect `list(set(geom))`.

**Zoo 1.103.0.** `in_one_order` (elements sorted by kind, then by their
vertices' indices) for every operator input that had none; `start_at_lowest`
(a face remade to start at its lowest vertex, refused if corner data exists)
for the faces `holes_fill`, `contextual_create` and the hemisphere's bisect
make; and `bm_to_object` sorts every mesh's faces before writing it. The
faces, their corners and windings are the recipes'; what changes is their
order, where a filled or split face starts, and so every Zoo model's bytes,
once.

**Measured** (`zoo_repro_probe.py --jobs`: cold run 9259's 38 Zoo jobs, each
replayed twice from its own command): on 1.102.0, 31 of 38 built the same
bytes both times and seven did not -- the deli's and the office's fixtures,
the deli's and the pharmacy's roof props, a rowhome's dressing, the site
kit's trash bags and the clutter's pebble
(`zoo_repro_probe.jobs_before.out.txt`); on 1.103.0, all 38
(`zoo_repro_probe.jobs_after.out.txt`), every output but the .blend. Which
jobs differ is a run's draw -- the pharmacy's fixtures matched in that
control and differed between cold runs -- so the control is a floor, not a
census. The deli's fixtures built four times on 1.103.0: one GLB
(`zoo_repro_probe.after.out.txt`).

**In cold runs** (`docs/cold_runs/cold_9260/`, `cold_9261/`): two runs of
one set, Level Factory 0.193.0 and Zoo 1.103.0, placed all 3,320 lightmap
users the same, and their lightmaps are bit for bit the same in all but 15
of 16,777,216 texels, those under 0.00005 apart. What still differs between
the two packages: the 18 files any two exports differ in; the bake files
those 15 texels live in; one rowhome's dressing model -- its merged covers'
triangles in another order from the same Patina plan, a Zoo residue two
replays had not caught -- and the files that hash it; and Lux's applied
scene's resource ids, which Godot draws anew at every save. The atlas is 16
slices where it was 15 (about a megabyte of BPTC): the unwrap packs the
reordered triangles' charts differently. Zoo's own cost, timed on cold run
9261's 16 kit builds alternated (`zoo_repro_probe.time_ab.out.txt`): 55.7
and 56.4 s on 1.102.0, 55.4 and 58.7 s on 1.103.0.

## REFUTED, KEPT: the Lux staging's import is not texture compression or detail meshes

Cold runs 9251 to 9254 wait about 26.7 s before the Lux job's command, the
scheduler staging a project of the whole themed site and importing it. The
staged project sets no importer defaults, so the guess was Godot compressing
textures it detects in 3D and building level-of-detail meshes, neither of
which Lux reads. `lux_staging_probe.py` stages 9254's Lux project the way the
job does (`stage_godot_project`), times a fresh import and the job's own
command on each copy, and compares what Lux writes:

| | S0 | S0b | S1, no 3D texture compression | S2, and no detail meshes |
|---|---|---|---|---|
| the import | 24.7 s | 24.0 s | 24.0 s | 23.5 s |
| the apply | 3.7 s | 3.6 s | 3.6 s | 3.6 s |

**The knobs were read**: S2's model sidecars carry `generate_lods=false`;
every arm's texture sidecars carry `compress/mode=0` and
`detect_3d/compress_to=0` -- the staged import never compressed a texture
for 3D, so S1 had nothing to turn off. Lux's quality and validation reports
are identical in all four; its applied scene differs between any two runs,
the control included, in the same 14 light energies alone (the control's
pair up to 0.023 apart: lamps whose energy varies at save time). The 24 s is
480 models and 428 textures imported; where it goes inside Godot's import is
not measured.

## REFUTED, KEPT: one import pass with the models' final settings as defaults

`import_plan_probe.py` timed the export's import plan on stripped copies of
cold run 9251's package: as it was, the two sidecar passes and the light
bake's re-import of every model took 121.6 s; with embedded images and
lightmap UVs as the FIRST pass's model defaults (`project.godot`'s
`[importer_defaults] scene`), a second pass over only the pinned textures and
a bake import of the seven models it changes, 53.6 s -- and the sidecars the
two would ship matched once uids were set aside. A patch was written
(`patches/patch_lf_import_once.py`, Level Factory "0.186.0") and the real
export said no: re-exporting 9251 with it FAILED the greybox-skin gate, 105
slab surfaces on a greybox material (good exports: 3), the Empties merged to
148 meshes instead of 236, the bake lit 3,320 users instead of 3,491.

**Why it was wrong.** The light bake's re-import of every model is
load-bearing. It is the import in which `zoo_worldskin.gd` -- the models'
import script -- skins them with the texture packs already imported; that is
also why that pass imports the shared textures 1,843 times. Asked for in the
first, cold pass, lightmap UVs made that pass the models' last import, and the
worldskin found no pack for the slabs. The probe compared sidecars, and a
sidecar does not record what an import script did; the patch refuses to run
and says so. What would make one import enough: a worldskin that finds its
packs without the textures imported first (Zoo), measured on the gate and the
merge, not on sidecars.

**CORRECTED, KEPT (the section above, 9251's import log).** Two parts of
this were wrong. The worldskin does not need the texture packs imported
first; it needs a building's floor module imported before its base, which a
model's first import cannot promise and the second pass can. And the 148
merged meshes were not a failure: models that carry their lightmap UV when
the Empties merge make one mesh a side per material, as the merge was
written to (`merged_materials.py`); the 3,320 users are the same merge seen
by the bake. Only the greybox gate was a real failure, and it was the first
import's.

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
- The compose replay: the job's commands as the workspace index recorded
  them, against the job's own output folder file by file. A replay that
  matched nothing of the run would be timing some other job.
- The bake editor's steps: the plugin's own clock (`BAKE_T`, the engine's
  milliseconds since it started), printed into the editor's log beside the
  package; the editor's whole time from `light_bake.json`. The probe swaps
  the plugin in its own process; Level Factory's is never touched.
- A lightmap: Godot's own reading of its EXR (`exr_dump.gd`), compared in
  numpy. 9256's against itself is 100 % the same, and two exports of one
  version differ in about a tenth of their texels, so a difference no
  larger than that says nothing about a change -- to 0.191.0. Since
  0.192.0 the bake's editor stops its clock and two exports bake the same
  bytes; the tenth was the failing lenses. Texel by texel holds only
  while the atlas is packed alike: cold run 9257's was not -- three dome
  glasses came out of Blender with different charts and 2,858 of 3,320 users
  moved -- and read texel by texel it looked twelve times further from
  9256's than it is user by user (a mean difference of 0.0246 against
  0.0021). `lightmap_compare.py --layout` reads each bake's layout
  (`lightmap_layout.gd`) and compares every user's own light wherever the
  atlas put it (`docs/cold_runs/cold_9257/NOTES.md`).
