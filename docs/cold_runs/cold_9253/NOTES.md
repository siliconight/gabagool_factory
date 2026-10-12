# Cold run 9253 -- the light bake's lightmap requests in the export's second import pass

**What it tested:** Level Factory 0.187.0, the bake's marks written before the
export's second import pass, so the bake no longer imports every model a
third time. Everything else as in 9252; restaurant_row_001 on 9245's lot and
seeds.

**Result: 0 interventions, 0 tool files changed.** seed_9104 picked, as in
9251 and 9252, on the same route completions (0.96, 1.00, 0.48); findings
122 -> 122. The export says what the re-exports of 9252 said: the Empties
merged to 148 meshes (236 before), all 415 shared-texture sidecars pinned
with none re-pinned (9251's export re-pinned 72 and 9252's 78 after the
bake's import reset them), the greybox census 3 surfaces, the bake 3,320
users (3,491 before), 96.3 s in the editor.

## The time

    run    shell   art     export   walk   retire   the drive
    9252   75 s    156 s   284 s    91 s   3 s      10.3 min (615 s)
    9253   73 s    153 s   241 s    88 s   17 s      9.7 min (580 s)

From each run's step stamps; the drive from the journal's start to the
driver log's last write, as for every run before. The export is 43 s
shorter; the retire step took 14 s more, deleting an old workspace (0.9 GB)
that 9252's had not had to. The art leg's chain is 9252's to within a
second (`leg_spans.py`): 26.6 s still waits before the Lux job.

## Where the drive goes now

    shell    73 s   13 %
    art     153 s   26 %
    export  241 s   42 %   the editor's bake 96 s of it
    walk     88 s   15 %   the package copied and imported from scratch
    retire   17 s    3 %

The walk copy is next: it imports the package the export imported a minute
earlier and threw the cache of away (`docs/findings/grader_speed/README.md`).

## What is evidence of what

- The time: the step stamps in `driver.log`; the workspace index
  (`leg_spans.py`).
- The package: the export's own lines in `export.log` (the merge, the pins,
  the greybox census, the bake).
- The result: `cold_run.py --end` and the drive's findings step.
