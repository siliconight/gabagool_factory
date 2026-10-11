# Cold run 9237 -- Lot 0.115.0 + Level Factory 0.178.0 on 9233's lot: the plate families on the 32 m baked tile and the paint in cells, priced, and both gates held

**What it tested:** roadmap 231's second lever and the first lever's own
gate, landed together as Lot 0.115.0 and Level Factory 0.178.0: the
plate families (ground, paths, courtyards, fields, yards, perimeter,
street slabs, frontages) cut to `MESH_TILE_BAKED` (32 m) where the site
spec says the lights bake -- `render.lights_baked`, which Level Factory
now writes from its export's own default (`BAKE_LIGHTS_CLI_DEFAULT`) --
and the road paint written as one mesh a paint colour a `PAINT_CELL_M`
(32 m) cell by each marking's centre, the colour's one material shared,
after 9236's paired census put each level-wide paint mesh under 21 live
lights against the engine's cap of 8. On 9233's brief and lot
(restaurant_row_001, `block` grammar, `cluster: auto`, seed auto), priced
against 9236's package at the fixed stations.

**Result: 0 interventions, 0 stops.** Three candidates (seeds 9003, 9104,
9205; 9104 picked, as every run on this brief has picked it), 0 blockers
on both legs, findings 86 and 122, 122 after the export -- 9233's count
again. Every Lot job printed its new line:

    [lot] plate tile 32 m: the site spec's render says the lights bake (MESH_TILE 8 m under live lights)

The closure verdict: `ok=true, 0 issue(s) over 81 resource(s)`, 3,015
files. The bake:

    light bake: 491 model(s) and 224 primitive mesh(es) lightmapped, 6 kept
    dynamic, 1 spawned set dynamic; 211 steady rig(s) baked, 29 failing and
    0 cycling left live; 215 room fill(s); 3514 users, 93.8 s in the editor

The 491 models are 9236's 474 less its two paint meshes plus the 19 cells
(10 of the yellow paint, 9 of the white; every `site_marks_*.obj.import`
reads `generate_lightmap_uv2=true`, all 19 under `baked`); the 224
primitives are 9236's 1,136 less the tiles the bigger tile no longer
cuts; the lightmap has 3,514 users where it had 3,953.

## The pool (`draw_census_9236_9237.txt`, `tools/draw_census.py` on both packages' `site.tscn`)

| owner | 9236 | 9237 |
|---|---:|---:|
| BoxMesh Ground + Ground_t (the plate's bands and their tiles) | 377 | 50 |
| BoxMesh road | 78 | 13 |
| BoxMesh sidewalk | 66 | 22 |
| BoxMesh frontage | 25 | 8 |
| BoxMesh path | 9 | 8 |
| BoxMesh kerbcut | 6 | 4 |
| box meshes, all owners | 568 | 112 |
| materials, all owners | 55 | 55 |
| MeshInstance3D nodes (the boxes and the paint) | 570 | 131 |

The paint: 2 nodes to 19, 2 materials still. The yards and the sign
blades did not move. Across the three runs the site scene's pool is 795
boxes and 795 nodes (9233) to 112 boxes and 131 nodes, and 178 materials
to 55.

## The price (`price/`, 9236's package the control, this one the subject, a control run bracketing it)

    measured control_1  53 headings  draws mean 2801 worst 5801  p95 median 5.50 ms
    measured glow       53 headings  draws mean 2522 worst 5253  p95 median 5.21 ms
    measured control_2  53 headings  draws mean 2801 worst 5801  p95 median 5.79 ms
    controls' spread, median over 53 headings: p95 0.27 ms, draws 0.0 (the noise floor)
    draws vs controls' mean: median -255.0  min -557.0  max -48.0
    p95 ms vs controls' mean: median -0.39  min -2.21  max +0.09
    controls between themselves, p95 |c1-c2|: median 0.27  max 2.16
    frame p95 at the controls' mean, median over headings: 5.65 ms

- **-255 draws and -0.39 ms p95 a heading median**, on a 5.65 ms frame.
  Every one of the 53 headings draws fewer (-48 to -557); 46 are faster
  beyond 0.08 ms, 6 within it, 1 slower by 0.09 ms, and none is slower
  beyond the controls' own spread.
- **The noise floor is wider this time, 0.27 ms**, because the second
  control run came in 0.29 ms slower than the first at the median (5.79
  against 5.50) and 2.16 ms slower on one heading. Two runs of one
  package disagreeing by that much is the harness's own variance on this
  machine tonight, not the subject's; the subject's median sits below
  both controls' medians (5.21 against 5.50 and 5.79), and the draws,
  which do not vary, are the cleaner reading.
- **The worst heading moves most:** player_start_19 yaw 90 -- the one
  heading over 16.7 ms on every run of this lot -- from 18.28 and 19.70
  ms to 16.78 (-2.21, -548 draws); longest_sightline 270 from 14.38 to
  12.96 (-1.79, -510); patrol_point_13 270 from 14.29 to 12.99 (-1.72,
  -455); camera_socket_1 180 from 6.81 to 6.06 (-1.79, -329).
- Not a flip in the 53.
- **Against 9233's package, the two levers together** read about -360
  draws and -0.75 ms p95 a heading median (the sums of the two prices'
  medians; the headings' deltas are not strictly additive), on the 6.14
  ms frame 9233 measured: a street's markings, slabs and plate cost a
  tenth of the frame less than they did, and the second street's +107
  draws and +0.55 ms (9233 against 9232) are paid back three times over.

## The gate: the paired-light census, and it held

The three perf reports carry Level Factory 0.159.0's paired census per
station. 9236's package (both control runs): 4 meshes over the cap of 8
-- the horizon glow ring at 240, one roof at 10, and the two paint
meshes at 21 each. This package: 2 -- the glow and the roof -- and
nothing else over 8: no plate tile, no slab, no band, no paint cell. The
histogram's tail reads three meshes at exactly 8 (the cap, not over it),
one at 10, one at 240, the same three-eight-ten-glow tail as 9236's with
the two 21s gone. So the 32 m tile pairs each piece with no more live
lights than the 8 m tile did (a tile four times the side sits under the
same failing tubes, which are indoors), and the cells did what they were
cut for.

The two over the cap are not this item's: 9233's package carried both
before any of this work. The glow ring's box is the sky and its material
is unlit, so the lights it pairs with light nothing; the roof is
`b0/roof_footprint/Roof_brick_delco_1997`, a building's roof mesh under
the tubes inside the building, which cannot light a roof from below. Nil
to the eye, both, and recorded in the roadmap as an observation rather
than a defect.

## Seen (`paint.png`, `lane.png`; `paint_frames.sh`, `tools/paint_stations.py`)

The same seven paint stations and the lane's two, shot in 9236's package
(left) and this one (right), at dusk with the sun low across the main
street. At every station the two frames read the same to the eye: the lamp
pools on the road, the shadows the buildings throw, the crosswalk bars,
stop bars, edge and centre lines and bay ticks in the same places with the
same wear -- the 32 m tile bakes the same light onto the same ground, and a
paint cell's edge shows nowhere, because the cells share one material and
one world-space UV. Nothing in the sixteen frames tells the packages
apart, which is what a merge that costs 456 boxes and a quarter of the
draws is supposed to look like. The lane (`lane.png`) is as 9233's and
9236's: dark at dusk between the dim yards, no poles of its own -- the
walker asked for a call and it is recorded under roadmap 231's close as
the next Lux lever: wall packs on the rear walls, by the rear doors and
over the dumpster pads, no poles.

## What is evidence of what

- The frame time is the two changes' together (the tile and the cells);
  the pool census separates them -- the cells add 17 nodes, the tile
  removes 456 boxes -- and 17 draws on a frame are below the harness's
  noise, so the time is the tile's to within the noise.
- The paired census is read off a package with the bake on. A package
  exported `--no-bake-lights` pairs every lamp, which is what Level
  Factory 0.178.0's note under that flag is for.
- One seed, one lot, one time of day. The 32 m number is derived from
  this census; a lot with live poles cycling along a street (`29 failing
  and 0 cycling left live` here) is the case to read next.

## Instruments

- `price/`: the three perf reports, `price.txt`, `vs_mean.txt`,
  `price_vs_mean.py`.
- `draw_census_9236_9237.txt`: `tools/draw_census.py` on both packages.
- `paint_frames.sh` and `tools/paint_stations.py`: the paint frames at
  seven stations in both packages and the lane from both ends; the
  sheets `paint.png`, `lane.png`; the frames in `_scratch/frames_9237_paint/`.
