# Cold run 9255 -- every model imported once

**What it tested:** Level Factory 0.189.0, the export's sidecar step
importing every model once, with its final settings, in three passes over
three sets (the textures, every model but the late ones, the worldskin bases
and the models with a light baking of their own). Everything else as in
9254; restaurant_row_001 on 9245's lot and seeds.

**Result: 0 interventions, 0 tool files changed.** seed_9104 picked on the
same route completions (0.96, 1.00, 0.48); findings 122 -> 122. The export's
own lines are 9254's: the Empties merged to 148 meshes, 415 of 415 pins with
none re-pinned, the greybox census 3 surfaces, the bake 3,320 users, 96.1 s
in the editor; its import log shows the three passes. The walk copy loads
the same level as before (`walk_copy_census.gd`: 3 scenes, 20,954 nodes,
3,380 meshes, none empty, 242 lights, 3,320 lightmap users).

## The time

    run    shell   art     export   walk   retire   the drive
    9254   74 s    154 s   241 s    11 s   18 s     8.4 min (505 s)
    9255   76 s    156 s   217 s    10 s    4 s     7.8 min (470 s)

From each run's step stamps; the drive from the journal's start to the
driver log's last write. The export is 24 s shorter, as the re-exports said
(235.9 -> 212.2 s). The retire step deleted nothing this time (9254 deleted
an old 0.9 GB workspace), which is 14 of the drive's 35 s.

## Where the drive goes now

    shell    76 s   16 %
    art     156 s   33 %
    export  217 s   46 %   the editor's bake 96 s of it
    walk     10 s    2 %
    retire    4 s    1 %

## What is evidence of what

- The time: the step stamps in `driver.log`.
- The package: the export's own lines in `export.log`; its import log beside
  the package; the walk copy's census.
- The result: `cold_run.py --end` and the drive's findings step.
