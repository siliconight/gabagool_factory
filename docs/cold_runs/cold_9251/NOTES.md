# Cold run 9251 -- three Blender jobs at once

**What it tested:** Level Factory 0.184.0's `LF_CONCURRENCY=blender=3`, the
Blender cap measured at three where TDD 19.2 set one and nothing measured
it. Everything else as in 9249 and 9250; restaurant_row_001 on 9245's lot
and seeds.

**Result: 0 interventions, 0 tool files changed; baked on its first
attempt.** seed_9104 picked; findings 122 -> 122. The art log says the
override took: `[scheduler] LF_CONCURRENCY: blender 1 -> 3`.

## The time

    run    Blender   Blender window   art leg's jobs   shell + art   the drive
    9249   1                                            5.8 min      12.1 min
    9250   1         114.0 s          251.7 s           6.0 min      12.6 min (legs profiled)
    9251   3          45.7 s          177.1 s           4.5 min      10.8 min

From each run's workspace index (every job's own start and finish).

## The models

Two runs at one already differ, so the question is whether three adds a
difference one does not. `docs/findings/grader_speed/blender_width_compare.py`
classes every file a Blender job built -- identical; the same but for a
mesh's triangle order or a normal within 1e-4; a Blender scene file (set
aside, it carries per-save data); or different -- for two controls (9248
against 9249, 9249 against 9250) and the change (9250 against 9251):

- files different in some control: 10 -- two merged meshes' vertex order
  (roof props, an Empty's dressing), two fixtures, a trash-bag prop's
  normals, Deli Counter's three shell manifests;
- different in the change: 10, of which one in no control: the other
  trash-bag prop, its weighted normals 0.000108 apart at most where the
  controls read 0.000100 for it and 0.000203 to 0.000299 for its twin.
  The same drift, across the comparison's line; not a new kind.

So Level Factory 0.185.0 makes three the default where the machine allows
(`blender_cap`: half the logical CPUs, never below 1, never above three).

## Found on the way

**The Blender builds are not reproducible run to run, one at a time or
three.** A model built twice from the same inputs can come back with its
triangles or its merged vertices in another order and its weighted normals
a few 1e-4 apart. Nothing on screen depends on the order, and nothing
visible on normals that close -- but a cache keyed on content sees a new
file, and every comparison like this one needs classes instead of bytes.
Unmeasured: why. Iteration order that varies from process to process (a
set of strings under Python's hash seed) is the first suspect.

## What is evidence of what

- The time: the workspace index's per-job times; the drive from the journal
  and the driver log.
- The models: the three runs' job outputs, file by file
  (`blender_width_compare.out.txt`).
