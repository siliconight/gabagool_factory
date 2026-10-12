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
