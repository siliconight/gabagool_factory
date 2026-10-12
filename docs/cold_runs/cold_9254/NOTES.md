# Cold run 9254 -- the walk copy starts from the export's own import

**What it tested:** Level Factory 0.188.0 (the export keeps its import cache
beside the package) with the factory's `tools/walk_export.py` moving it into
the walk copy. Everything else as in 9253; restaurant_row_001 on 9245's lot
and seeds.

**Result: 0 interventions, 0 tool files changed.** seed_9104 picked on the
same route completions (0.96, 1.00, 0.48); findings 122 -> 122; the export
as 9253's (148 merged meshes, 415 of 415 pins with none re-pinned, 3,320
users). Its log says what is new: "import cache moved beside the package
(LF_restaurant_row_001.portable-godot.import_cache)"; after the walk step
none is left beside it, and the walk copy carries it as its `.godot` (85 MB).

The walk copy loads the same level the probe's copies did
(`docs/findings/grader_speed/walk_copy_census.gd` on
`_runs/walk_export_restaurant_row_001`): 3 scenes, 20,954 nodes, 3,380
meshes, none empty, 242 lights, 3,320 lightmap users.

## The time

    run    shell   art     export   walk   retire   the drive
    9253   73 s    153 s   241 s    88 s   17 s     9.7 min (580 s)
    9254   74 s    154 s   241 s    11 s   18 s     8.4 min (505 s)

From each run's step stamps; the drive from the journal's start to the
driver log's last write. The walk step is 77 s shorter and nothing else
moved by more than a second. Both runs' retire steps deleted an old
workspace (0.9 GB each).

## Where the drive goes now

    shell    74 s   15 %
    art     154 s   30 %   26 s of it before the Lux job, the scheduler staging and importing
    export  241 s   48 %   the editor's bake 96 s of it
    walk     11 s    2 %
    retire   18 s    4 %

## What is evidence of what

- The time: the step stamps in `driver.log`.
- The walk copy: the export's own line in `export.log`, the exports folder
  after the walk step, and the census of the copy.
- The result: `cold_run.py --end` and the drive's findings step.
