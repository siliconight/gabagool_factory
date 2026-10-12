# Cold run 9252 -- the compose job's buildings side by side

**What it tested:** Level Factory 0.186.0, the compose job's per-building
commands side by side (up to `python_cpu`'s width, four) and a `job.log`
that keeps every command, with 0.185.0's Blender default of three and no
override set (9251 ran three by `LF_CONCURRENCY`). Everything else as in
9251; restaurant_row_001 on 9245's lot and seeds.

**Result: 0 interventions, 0 tool files changed.** seed_9104 picked, as in
9251, on the same route completions (0.96, 1.00, 0.48); findings 122 ->
122; the bake 494 models, 3,491 users, 94.7 s in the editor (9251: 94.3 s).

## The time

    run    compose job   art leg's jobs   begun -> art done   export   walk + retire   the drive
    9251   64.1 s        177.1 s          270 s               282 s    95 s            10.8 min
    9252   31.0 s        146.0 s          237 s               284 s    94 s            10.3 min

9251's legs from its logs' last writes (`art.log`, `export.log`,
`driver.log`); 9252's from its own step stamps, the first run to carry them
(`tools/cold_drive/cold_drive.sh`), which agree with its logs' writes to the
second. The jobs from each workspace index
(`docs/findings/grader_speed/leg_spans.py`). The drive is 33 s shorter, and
the compose job is 33 s shorter; nothing else moved.

The compose job's `job.log` now holds its sixteen commands: 61.0 s of
command time in a 31.0 s job -- the shell's 8.2 s alone and first, then the
buildings four at a time, the deli the longest at 16.9 s. 9251's held only
the last command, 1.6 s. The deli and the office exit 3 on Deli Counter's
z-fight gate (two coplanar pairs each), advisory, as in 9251.

## Where the drive goes now

The step stamps, for the first time:

    shell    22:36:20 -> 22:37:35     75 s
    art      22:37:36 -> 22:40:12    156 s
    export   22:40:12 -> 22:44:56    284 s   46 % of the drive
    walk     22:44:56 -> 22:46:27     91 s   15 %
    retire   22:46:27 -> 22:46:30      3 s

- **The export**, 284 s, is the constraint. The editor's bake is 94.7 s of
  it; most of the rest is importing the package three times over (the
  sidecar step's two passes and the light bake's re-import of every model).
- **The walk copy**, 91 s, is the step the stamps made visible:
  `tools/walk_export.py` copies the package and imports it from scratch,
  where the export has just imported the same files and dropped its cache.
- **The art leg's chain** (`leg_spans.py`): Pixelcoat 17.4 s, a wait of
  21.7 s for a Blender slot, the office's kit 9.5 s, 12.1 s, its dressing
  2.1 s, the compose 31.0 s, the themed site 8.5 s, then 26.9 s before the
  Lux job's 3.8 s -- the scheduler staging the whole themed site and
  importing it, before the command, with nothing else running.

## What is evidence of what

- The time: the step stamps in `driver.log`; the workspace index's per-job
  times (`leg_spans.out.txt`); the compose job's own `job.log`.
- The result: `cold_run.py --end` and the drive's findings step.
