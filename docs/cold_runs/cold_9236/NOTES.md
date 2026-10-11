# Cold run 9236 -- Lot 0.114.0 + Level Factory 0.177.3 on 9233's lot: the road paint as one mesh a colour, priced

**What it tested:** roadmap 231's first lever, on its third run -- the road
paint as one OBJ mesh per paint colour beside the site scene (Lot
0.114.0, each quad's UVs carrying the per-marking wear offset, one
MeshInstance3D and one material a colour), lightmapped through the import
pass (Level Factory 0.177.1 asks the wavefront sidecar for
`generate_lightmap_uv2`), published by the Lot adapter (0.177.2, 9234's
stop) and carried by the export's assembly step (0.177.3, 9235's stop) --
on 9233's brief and lot (restaurant_row_001, `block` grammar, `cluster:
auto`, seed auto), priced against 9233's package at the fixed stations.

**Result: 0 interventions, 0 stops, the first level with the merged paint.**
Three candidates (seeds 9003, 9104, 9205; 9104 picked on the walktest and
Laser Tag's route findings, as 9233, 9234 and 9235 picked it), 0 blockers
on both legs, findings 86 on the shell leg and 122 on the art leg, 122
after the export -- 9233's count, line for line. The closure verdict:
`ok=true, 0 issue(s) over 81 resource(s)`, 2,964 files. The bake:

    light bake: 474 model(s) and 1136 primitive mesh(es) lightmapped, 6 kept
    dynamic, 1 spawned set dynamic; 211 steady rig(s) baked, 29 failing and
    0 cycling left live; 215 room fill(s); 3953 users, 100.4 s in the editor

The 474 models are 9234's 472 and the two paint meshes: both
`site_marks_*.obj.import` sidecars at the package root read
`generate_lightmap_uv2=true` (texel size 0.2, left alone) and both stand
under `baked` in `light_bake.json`, `unreadable` empty.

## The pool (`draw_census_9233_9236.txt`, `tools/draw_census.py` on both packages' `site.tscn`)

| owner | 9233 | 9236 |
|---|---:|---:|
| BoxMesh mark (a marking each) | 227 | 0 |
| StandardMaterial3D mark (a marking each) | 125 | 0 |
| StandardMaterial3D site_marks (a colour each) | 0 | 2 |
| box meshes, all owners | 795 | 568 |
| materials, all owners | 178 | 55 |
| MeshInstance3D nodes | 795 | 570 |

Every other line is identical: the plate, the slabs, the sidewalks, the
frontages, the paths, the kerb cuts, the yards and the sign blades. The
two `site_marks` nodes hold 125 quads between them (`site.markings.json`
is unchanged, 125 markings: 54 bay ticks, 34 crosswalk bars, 21 centre
lines, 12 edge lines, 4 stop bars).

## The price (`price/`, 9233's package the control, this one the subject, a control run bracketing it)

`docs/findings/horizon_glow/price_glow.py` at Level Factory's fixed
stations, 53 headings; the per-heading reading against the controls' mean
keyed by station and yaw (`price_vs_mean.py`, `price/vs_mean.txt`):

    measured control_1  53 headings  draws mean 2926 worst 6070  p95 median 6.16 ms
    measured glow       53 headings  draws mean 2801 worst 5801  p95 median 5.67 ms
    measured control_2  53 headings  draws mean 2926 worst 6070  p95 median 6.19 ms
    controls' spread, median over 53 headings: p95 0.08 ms, draws 0.0 (the noise floor)
    draws vs controls' mean: median -107.0  min -300.0  max 4.0
    p95 ms vs controls' mean: median -0.36  min -1.20  max +0.41
    controls between themselves, p95 |c1-c2|: median 0.08  max 0.87
    frame p95 at the controls' mean, median over headings: 6.14 ms

- **-107 draws and -0.36 ms p95 a heading median**, on a 6.14 ms frame:
  the second street's +107 draws and +0.55 ms (9233 against 9232) given
  back in draws and two thirds of it in time. 39 of 53 headings are faster
  beyond the 0.08 ms noise, 10 within it, 4 slower by 0.16 to 0.41 ms --
  each of the 4 with fewer draws than its controls (-48 to -140), and the
  controls disagree with each other by up to 0.87 ms on a heading, so a
  single heading's +0.41 is inside what two runs of one package do.
- **The worst headings move most**, because that is where the street is:
  patrol_point_13 yaw 270 from 15.49 and 15.39 ms to 14.24 (-1.20, -228
  draws), longest_sightline 270 from 15.47 to 14.33 (-1.19, -268),
  extraction_15 270 from 15.72 to 14.82 (-1.03, -272), player_start_19 270
  from 9.63 and 9.98 to 8.71 (-1.09, -290). The one heading over 16.7 ms
  in the controls (player_start_19 yaw 90, 19.05 and 18.89 ms, 6,070
  draws) is still over at 17.94 ms and 5,801 draws: the paint was 269 of
  its draws and a millisecond, not its cause.
- Not a flip in the 53: every heading's two passes agree in all three runs.

## The paired-light census: the lever's own gate, tripped

The perf reports carry Level Factory 0.159.0's paired census per station
(`rows[i].light_census.paired`, the culler's own two rules). 9233's
package, both control runs: 2 meshes over the cap of 8 -- the horizon
glow ring under 235 (232 in 9233's own price run) and one roof under 10.
This package: 4 -- the same two, and **each paint mesh under 21 live
lights.** A mesh whose box is the whole plate reaches the failing tube
behind every storefront (29 rigs left live), and GL Compatibility binds
the first 8 it finds; the 13 it drops could include a pole left live over
a crosswalk. Nothing in these frames shows it (the lamps are baked, the
live ones are indoors), and nothing in these frames could. The merge was
measured by the instrument that the finding named as its gate, and the
gate says: cut it up. Lot 0.115.0 writes one mesh a colour a 32 m cell by
each marking's centre (`PAINT_CELL_M`), the colour's one material shared
-- a dozen draws where 227 were, each piece under the lights within its
reach -- and cold run 9237 measures it with the same census.

## Seen (`paint.png`, `lane.png`; `paint_frames.sh`, `tools/paint_stations.py`)

Seven stations derived from the drawn spec and the markings manifest --
down each of the three streets 12 m in from its end, 7 m short of each
street's first crosswalk, 6 m off the first bay ticks -- shot in 9233's
package and this one, a station a row, 9233 left and 9236 right. At dusk,
the sun low across the main street. At every station the two frames read
alike: the crosswalk bars, the stop bars, the edge and centre lines and
the bay ticks in the same places, lit the same, and the WEAR in the same
places -- at `paint_r0_xwalk` the same bars carry the same worn patches in
both, which is the per-marking offset surviving in the UVs under the one
material, as 0.114.0 said it would. Nothing in the fourteen frames tells
the packages apart. `lane.png` is the lane from both ends as 9233's record
shot it: a dark back lane at dusk, no poles of its own, the Lux lever
still queued for the walker.

## What is evidence of what

- The price is lever 1's and nothing else's: the same lot, brief, seed and
  tool set but Lot 0.114.0 and Level Factory 0.177.1-0.177.3, whose three
  changes are the paint's and the pool census shows no other line moved.
- The paired census is read off the perf reports of a package with the
  bake on; a package exported `--no-bake-lights` would pair every lamp.
- Two runs it took to ship a new file kind beside Lot's scene, and the
  failure was the same shape both times (9016's skins before them): a
  suffix list in the adapter, a sibling list in the export, and only the
  closure gate, last in the chain, notices. `docs/cold_runs/cold_9234/`
  and `cold_9235/NOTES.md` carry them; the memory carries the rule.

## Instruments

- `price/`: the three perf reports, `price.txt` (the harness's summary),
  `vs_mean.txt` (the keyed per-heading reading), `price_vs_mean.py`.
- `draw_census_9233_9236.txt`: `tools/draw_census.py` on both packages.
- `paint_frames.sh` and `tools/paint_stations.py`: the fourteen paint
  frames and the two lane frames; the sheets are `paint.png`, `lane.png`;
  the frames themselves in `_scratch/frames_9236_paint/`.
