# Cold run 9245 -- roof props reach a level

**What it tested:** roadmap 181's three releases together, on 9244's lot
(restaurant_row_001): Zoo 1.101.0 (the scatter keeps off a roof's hatches
and landings, tests a yawed prop as the box it occupies, plans a water tank
only from 12 m up, and merges a roof to about one mesh a species), Deli
Counter 0.209.0 (the landings on the roof slot's `keep_out`, the `roofprops`
layer, the circulation gate's third arm) and Level Factory 0.179.0 (a
`zoo_roof_props_build` job per enterable building, the third compose layer,
the brief's `roof_props`). Priced against 9244's package: the same lot one
release earlier in each, no roof props.

**Result: 0 interventions, 0 tool files changed, hygiene clean, 32 minutes
end to end; the package baked on its first attempt.** seed_9104 picked as
in 9241 to 9244 (route completion 1.00). Findings 123 -> 125: the two new
are `PRESENTATION_CIRCULATION` moderates on the deli and the office, and
every one of their eight conflicts was a roof prop standing over a STAIR
COLUMN the gate extended to +/-1e6 in z -- seven HVAC parts on the office's
roof over `office_stair_0` (floors 0 to 2, the roof two slabs up) and a dish
over `deli_stair_down`, the basement stair; none a body could meet. The
instrument, not the placement: Deli Counter 0.209.1 bounds a stair's column
to the floors it serves, and `docs/findings/roof_props/regate_9245.py` run
against this run's own composed buildings reads roofprops 8 -> 0 with the
shell and dressing arms unmoved (`regate_9245_0_209_0.txt`,
`regate_9245_0_209_1.txt`). Counted as findings of the gate, fixed after the
run; the count above is the run's.

**The roofs.** Three enterable buildings got a roof-props layer -- deli_a01,
office, pharmacy_a01 -- and the twelve Empties none, as planned. Each roof:
17 props (4 HVAC units, 6 vent stacks, 3 exhaust fans, 2 skylights, 2
dishes; no tank, every roof under 12 m), 59 parts merged to 6 meshes, 4,392
triangles, the roof's hatch and landing kept off (the deli's index records 2
forbidden rects, its hatch's hole and the landing around it; the office's
and the pharmacy's roofs carry neither, 0 each). The same
mix on all three: at density 1.0 every cap saturates on any roof over about
300 m2, which is the antennas' uniformity again (the walker, 2026-10-09:
"too uniform and computer generated") and a taste call queued below.

**The bake:** 494 models and 224 primitive meshes lightmapped, 6 kept
dynamic and the responders' car set dynamic, 213 steady rigs baked and 29
failing left live, 215 room fills, 92.6 s in the editor, one attempt, and
**3,501 lightmap users -- 9244's 3,483 plus exactly the 18 merged roof
meshes.**

## The price (`price.sh`, `price/`, 9244's package the control)

    measured control_1  53 headings  draws mean 2502 worst 5219  p95 median 8.56 ms
    measured glow       53 headings  draws mean 2515 worst 5243  p95 median 6.39 ms
    measured control_2  53 headings  draws mean 2502 worst 5219  p95 median 6.37 ms
    controls' spread, median over 53 headings: p95 1.11 ms, draws 0.0 (the noise floor)
    draws vs controls' mean: median +13.0  min 0.0  max +33.0
    p95 ms vs controls' mean: median -0.46  min -7.79  max +0.59
    headings with p95 delta over the controls' 1.11 ms spread: 0 of 53

The anchors of the two packages were compared first: 34 and 34, identical.
**+13 draws a heading at the median, +33 at most, never fewer, and no frame
time the harness can see** -- the first control pass ran slow (8.56 ms at
the median against the second's 6.37), which is why the spread is 1.11 ms
where 9244's read 0.24; the subject sits between the two controls. Eighteen
meshes at +33 draws at most is consistent with GL Compatibility drawing a
mesh once more for each further light that reaches it, the inference 9244
made and did not measure.

## Seen (`roof_frames.sh`, `roofs.png`)

Two stations shot in 9244's package and this one. **hatch** -- a body's eye
at the deli's roof ladder, looking across the roof: 9244's is bare paving to
the parapet; 9245's carries low dark units, stacks and a dish throwing long
shadows from the evening sun, 5.6 % of the frame changed by more than 32
codes. **street** -- across the street from the extraction point, looking up
at the deli's roof edge: 0.7 % changed; the props stand behind the parapet
as a real roof's units do, so what they add is seen from roofs, ladders and
upper floors, not from the pavement. Two things for the walker's eye: the
species themselves (the first time any has been in a level), and -- not this
item's -- the roof surface, which reads as brick paving in both runs.

**The walk bots** (`walk.log`, `level-factory walk restaurant_row_001` on
the package, exit 0): its re-export baked as the run's did (3,501 users,
93.7 s), the closure ok over 81 resources in 3,054 files; **the walk bot
climbed `Ladder_ladder_0` to 6.6 m and stood up on the deli's roof among
its 17 props -- the landing the scatter kept off is where it stood -- and
`Ladder_ladder_1` to 3.3 m; the shot bot passed all five stations,**
`Ladder_ladder_0_top`, which looks across that roof, at 0.57 % jitter and
0.04 % fighting, where install test 7's walk on the same building read
0.58 % and 0.07 % on a bare roof: the props fight nothing.

## What is evidence of what

- 0 interventions, the bake, the 3,501 users, the findings: this run.
- The draws and the frame time: this package against 9244's, the station
  harness, both baked, anchors proven equal.
- The eight conflicts being the gate's: `regate_9245.py` on 0.209.0 and
  0.209.1 against this run's own compose output.
- That the extra draws are light passes: inferred, as in 9244.
- The texture-memory finding filed from this package is roadmap 238's
  (`docs/findings/texture_memory/`), measured here because the package was
  at hand, not because roof props changed it (their five images are 0.2 MiB).

## Taste calls queued for the walker

- the uniform mix: 17 props on every roof over about 300 m2 (density 1.0
  saturates each cap); the antennas' answer was 30 % as many, varied;
- the water tank's height gate (12 m; two of the library's 133 roofs);
- the species' look, seen for the first time.

## Instruments

- `price.sh`, `price/`: the perf reports, `price.txt`, `vs_mean.txt`,
  `price_vs_mean.py` (9244's copy).
- `roof_frames.sh`, `roofs.png`: the two stations, each pair's difference
  (`docs/cold_runs/cold_9244/frame_diff.py`).
- `walk.log`: the walk bots' run on the package.
- `driver.log`, `art.log`, `export.log`: the drive's legs.
