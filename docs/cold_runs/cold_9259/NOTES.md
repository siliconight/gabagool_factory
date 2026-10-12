# Cold run 9259 -- the bake draws nothing while it bakes

**What it tested:** Level Factory 0.193.0: the bake's editor stops its 3D
viewports drawing as Bake is pressed, and the bake's work copy is copied on
eight threads and removed on a thread while the export goes on
(`docs/findings/grader_speed/README.md`, "The bake draws nothing while it
bakes; the work copy"). Everything else as in 9258; restaurant_row_001 on
9245's lot and seeds.

**Result: 0 interventions, 0 tool files changed.** seed_9104 picked on the
same route completions; findings 122 -> 122. The export's own lines are
9258's but for the editor's time, 65.0 -> 61.5 s; the bake 35.7 -> 31.7 s
(`light_bake.json`'s `bake_ms`); no work copy left beside the package. The
walk copy loads the same level (`walk_copy_census.gd`: 3 scenes, 20,954
nodes, 3,380 meshes, none empty, 242 lights, 3,320 lightmap users).

## The time

    run    shell   art     export   walk   retire   the drive
    9258   74 s    154 s   175 s    10 s    3 s     7.0 min (422 s)
    9259   74 s    153 s   167 s    10 s    3 s     6.9 min (413 s)

From each run's step stamps; the drive from the journal's start to the
driver log's last write.

## Against 9258: the domes, a third way

By layout (`lightmap_compare.py --layout`, `lightmap_layout.out.txt`), the
atlas was packed differently from 9258's: one deli dome glass changed size
this time (005, 14 x 6 -> 14 x 10 texels) and 2,859 users moved with it.
Four runs, three namings: 9256 and 9258 alike, 9257 with 001, 003 and 005
the other way round, 9259 with 005 alone. So the deli fixtures' Blender build
names its domes in an order a run draws, not one of two. The light is the
same user by user: where a user stayed, 0.000215 apart on average; where it
moved, 0.0032 and falling either way (signed, 0.02 % of the mean).

## What is evidence of what

- The time: the step stamps in `driver.log`; `light_bake.json`'s
  `editor_s` and `bake_ms`.
- The layout and the light: `lightmap_layout.out.txt`.
- The result: `cold_run.py --end` and the drive's findings step.
