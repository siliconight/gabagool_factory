# Cold run 9260 -- Zoo's faces in one order

**What it tested:** Zoo 1.103.0: every mesh leaves `bm_to_object` with its
faces sorted, operator inputs given in one order, and the faces a fill or a
bisect makes started at their lowest vertex
(`docs/findings/grader_speed/README.md`, "Two cold runs, one lightmap").
Everything else as in 9259; restaurant_row_001 on 9245's lot and seeds.

**Result: 0 interventions, 0 tool files changed.** seed_9104 picked; findings
122 -> 122. The export's own lines are 9259's but for the editor's time
(56.0 s); the bake's 3,320 users and 215 room fills as before. The lightmap
is 16 slices of 1024 x 1024 where it was 15: Godot's unwrap packs the charts
of the reordered triangles differently -- one more slice, about a megabyte
of BPTC texture.

## The time

    run    shell   art     export   walk   retire   the drive
    9259   74 s    153 s   167 s    10 s    3 s     6.9 min (413 s)
    9260   78 s    167 s   167 s    11 s    3 s     7.2 min (434 s)

Slower, and not by Zoo. Every kind of job ran 10 to 18 % slower than in
9259 (`leg_spans.py`): Pixelcoat's build, which runs no Zoo, 17.0 -> 20.0 s;
the Godot jobs 24.8 -> 28.5 job-seconds; the Python jobs 144 -> 161; the
Blender jobs 116 -> 129. Timed apart, alternated on the same 16 kit builds
(`docs/findings/grader_speed/zoo_repro_probe.time_ab.out.txt`), Zoo 1.102.0
took 55.7 and 56.4 s and 1.103.0 55.4 and 58.7 s. The machine was slower
for this run and the next; nothing measured says why (the disk was 99 %
full, 6.7 to 7.4 GB free).

## What is evidence of what

- The time: the step stamps in `driver.log`; `leg_spans.py` on the two
  workspaces; the alternated kit builds for Zoo's own cost.
- The result: `cold_run.py --end` and the drive's findings step.
- The comparison with a second run of the same set: `docs/cold_runs/cold_9261/`.
