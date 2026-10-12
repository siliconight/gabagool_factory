# Cold run 9258 -- the bake's clock stopped

**What it tested:** Level Factory 0.192.0: the light bake's editor stops the
engine's clock as its plugin starts (Lux's failing fixtures had made every
bake catch their lenses at a different level), looks for the opened scene
from frame 1 where it waited 240 frames, and the localizer skips class names
a script does not contain (`docs/findings/grader_speed/README.md`, "The
export, process by process; the bake's clock"). Everything else as in 9257;
restaurant_row_001 on 9245's lot and seeds.

**Result: 0 interventions, 0 tool files changed.** seed_9104 picked on the
same route completions; findings 122 -> 122. The export's own lines are
9257's but for the editor's time, 69.9 -> 65.0 s; the plugin saw the scene
open at frame 1, 10.2 s after asking. The walk copy loads the same level
(`walk_copy_census.gd`: 3 scenes, 20,954 nodes, 3,380 meshes, none empty,
242 lights, 3,320 lightmap users).

## The time

    run    shell   art     export   walk   retire   the drive
    9257   73 s    154 s   187 s     9 s    3 s     7.2 min (433 s)
    9258   74 s    154 s   175 s    10 s    3 s     7.0 min (422 s)

From each run's step stamps; the drive from the journal's start to the
driver log's last write.

## The bake, made again

This run's workspace re-exported once (`bake_phases_probe.py`,
`reexport.out.txt`): `bake.exr`, `bake.lmbake` and `bake.exr.import` came
out byte for byte the run's own, the package differing in the 18 files two
exports of one level differ in (`light_bake.json`'s timings, four manifests,
`bake.tscn`, the twelve rowhome Empties' `site.tscn`). Before 0.192.0 no two
exports baked the same bytes.

## Against 9257: the domes again

By layout (`lightmap_compare.py --layout`, `lightmap_layout.out.txt`), the
atlas was packed differently from 9257's, as 9257's was from 9256's: the
same three deli dome glasses changed size and 2,858 of 3,320 users moved.
They swapped back -- 001 and 005 are 14 x 6 texels in 9256 and 9258 and
14 x 10 in 9257, 003 the other way -- so the deli's fixtures come out of
Blender in one of two namings, a run's draw: the domes have two shapes, and
which name each takes varies. The light is the same: where a user stayed,
0.000329 apart on average; where it moved, 0.0033 and falling either way
(signed, under 0.01 % of the mean). That naming is the one thing now known
to stop two cold runs baking the same lightmap; it is roadmap 239's Blender
reproducibility item, with a name.

## What is evidence of what

- The time: the step stamps in `driver.log`; `light_bake.json`'s
  `editor_s`.
- The bake made again: `reexport.out.txt`, the probe's file-by-file
  comparison with the run's own package.
- The layout and the light: `lightmap_layout.out.txt`.
- The result: `cold_run.py --end` and the drive's findings step.
