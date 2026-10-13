# Cold run 9270 -- the grates stepped past the paint, in a real drive

**What it tested:** Lot 0.120.1 in a real drive of restaurant_row_001. Cold run 9269's package stood
four of its eight storm-inlet grates over a crosswalk bar (`cold_9269/drain_paint.out.txt`, 0.155 m^2
each), all on the main road at its two T's: 0.120.0 placed a grate a hand past the kerb's dropped
stretch, and a through road's crosswalks lie outside it, in line with the side street's sidewalks.
0.120.1 steps a grate along the kerb past every marking nearer than `INLET_CLEAR` (0.3 m), the lines
along a road excepted. Everything else as in 9269.

**Result: 0 interventions, 0 tool files changed.** seed_9104 picked as before (the three seeds' grades
as in 9269: 1, 0 and 1 major, route completion 1.00 each). Findings 117 -> 117.

## As built

Lot printed `[lot] drains: 4 manhole cover(s), 8 inlet(s), 4 sidewalk lid(s)` in the themed site's job,
as in 9269. The bake: 505 models and 224 primitive meshes lightmapped, 3,346 users, the bake 29.96 s
and its editor 60.1 s -- the same users as 9269's, in the same places (below).

## The paint (`cold_9269/drain_paint.py` on this package, `drain_paint.out.txt`)

    inlet  (-28.495, -16.970)  clear; nearest crosswalk_bar at 0.300 m    9269: (-26.345, ...) over a bar
    inlet  (-11.480, -16.970)  clear; nearest crosswalk_bar at 0.300 m    9269: (-13.630, ...) over a bar
    inlet  ( 66.643, -16.970)  clear; nearest crosswalk_bar at 0.300 m    9269: ( 68.793, ...) over a bar
    inlet  ( 83.657, -16.970)  clear; nearest crosswalk_bar at 0.300 m    9269: ( 81.507, ...) over a bar
    the lane's four inlets       clear at 1.150 m, where they stood
    pieces overlapping paint: 2 covers of 16 (9269: 4 inlets and the same 2 covers)

Each of the four stands exactly a hand from the bar it passed -- the shipped OBJs measured by the
probe agree with the plan Lot's test asks for, to the millimetre. Their two lids moved with them,
clear of the paint at 0.977 m and of the furniture (Lot skips a lid that would stand under a piece).
The two covers on a bar are the lane's junctions, kept: the walker's photograph has a cover out in a
crosswalk.

## The frames (`drains.sh`, `drains.png`)

9269 left, 9270 right. `corner` is 9269's station, which sees both places a grate stood: the main
road's north kerb at the west T's west corner. `up` and `hatch` are the controls.

    station   mean |d| (codes)    pixels over 8 codes   over 32
    corner    2.28 / 2.14 / 2.10   0.659 %               0.181 %
    up        2.50 / 2.25 / 2.54   0.187 %               0.012 %   (control)
    hatch     2.33 / 1.93 / 2.08   0.000 %               0.000 %   (control)

The controls are quiet this time where 9269's moved 2.7 % -- the lightmap atlas did not repack: all
3,346 users kept their rect and slice (`cold_9269/lm_users.out.txt`). At `corner` the grate has left
the crosswalk's end and lies further down the gutter, a gap of asphalt between it and the first bar,
its lid on the sidewalk behind it.

**For the walker's eye, not decided here:** under the sodium light the lids read as near-black plates,
more like holes than iron -- the flat iron colour; a relief that catches the light is the Zoo species
and Pixelcoat iron roadmap 179 first assigned.

No price: the same eight meshes and triangles as 9269's, four grates and two lids moved 2.15 m along a
kerb. 9269's price stands (+1.2 draws a heading, p95 +0.03 ms against a 0.05 ms floor).

## The time

    run    shell   art     export   walk   retire   the drive
    9269   91 s    156 s   167 s    10 s    3 s     7.4 min (441 s)
    9270   92 s    166 s   167 s    11 s   18 s     7.8 min (470 s)

The retire removed one workspace (0.9 GB). It prints only its count; by the listing after it the one
gone is `cold-9266-ws` -- the fifth-newest once 9270 began, which the rule of keeping the newest four
makes the one to go. 9268's and 9269's, which these comparisons read, were kept.

## What is evidence of what

- The placement: Lot's line in `restaurant_row_001.themed_site_assemble/1/job.log`; the 8 OBJs in the
  package; `drain_paint.out.txt`.
- The look: `drains.png`, `drains.log`; the PNGs under `_scratch/frames_9270_drains/`.
- The atlas: `cold_9269/lm_users.out.txt`.
- The count: `cold_run.py --end`.
