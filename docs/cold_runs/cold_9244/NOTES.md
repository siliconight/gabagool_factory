# Cold run 9244 -- the fixture merge priced, on a bake that held

**What it tested:** Zoo 1.100.0 (roadmap 233): a building's fixtures layer
merged by placement, a fixture's same-material parts one mesh and no two
fixtures sharing one. On 9233's lot (restaurant_row_001), priced against
9241's package, the same lot one Zoo release earlier. Third time asked: 9242
and 9243 ran it and shipped unbaked (an open the editor dropped; then a
lightmap image read back empty), and this run carries Level Factory 0.178.6,
which tries a failed bake once more on a fresh copy, under a cold drive that
now stops on an unbaked package.

**Result: 0 interventions, 0 stops, and the package BAKED on its first try.**
seed_9104 picked as in 9241 to 9243, findings 123 as all three. The bake:
491 models and 224 primitive meshes lightmapped, 6 kept dynamic and the
responders' car set dynamic, 213 steady rigs baked and 29 failing left live,
215 room fills, 91.3 s in the editor, one attempt -- 9241's shape exactly --
and **3,483 lightmap users where 9241's read 3,518: the 35 fixture meshes
the merge removes**, now measured in a pipeline bake rather than a copy.

## The price (`price/`, 9241's package the control)

    measured control_1  53 headings  draws mean 2524 worst 5257  p95 median 6.59 ms
    measured glow       53 headings  draws mean 2502 worst 5219  p95 median 6.97 ms
    measured control_2  53 headings  draws mean 2524 worst 5257  p95 median 6.69 ms
    controls' spread, median over 53 headings: p95 0.24 ms, draws 0.0 (the noise floor)
    draws vs controls' mean: median -26.0  min -49.0  max 0.0
    p95 ms vs controls' mean: median +0.06  min -0.87  max +1.17

**-26 draws a heading at the median, -49 at most, and no heading drew
more.** The frame's p95 moved +0.06 ms at the median, inside the controls'
0.24 ms spread: the draws went and no frame time the harness can see came
with them, at about 2,500 draws a heading on this machine.

**More draws went than meshes did at some headings.** The lot's three layers
lost 35 meshes, and a heading looking into the deli lost up to 49 draws. That
is CONSISTENT with GL Compatibility drawing a mesh again for each further
light that reaches it, so a mesh merged away saves a draw per light pass --
an inference from the counts, not measured here.

## Seen (`pendants.png`, `pendant_frames.sh`, `frame_diff.py`)

Six stations at the lot's pendant rows, 9241 left and 9244 right: the same
picture -- the cords, the sockets, the bulbs, where they hung. The frames
differ by 1.9 to 3.2 codes a channel on average and almost nowhere by more
than 32 (0.117 % of one frame, under 0.001 % of the other five) --
consistent with two independent light bakes of one scene, not measured as
such; the merge re-packs triangles and changes none, which the merge's own
triangle check asserts in Zoo's export.

## What is evidence of what

- 0 interventions, the bake and its 3,483 users: this run, one attempt.
- The draws and the frame time: this run's package against 9241's, the
  station harness, both baked.
- That the extra draws are light passes: inferred, not measured.

## Instruments

- `price/`: the perf reports, `price.txt`, `vs_mean.txt`, `price_vs_mean.py`.
- `pendant_frames.sh`, `frame_diff.py`: the six stations, the sheet
  `pendants.png`, each pair's difference.
