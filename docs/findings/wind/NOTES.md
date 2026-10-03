# The wind, step 3a: the crowns, measured

The walker, 2026-10-03: "start with the crowns" (design:
`docs/proposals/WIND_DESIGN.md`). Shipped as Zoo 1.56.0 and Level Factory
0.130.0; the patches are `patches/patch_zoo_wind.py` (+ `zoo_wind/`) and
`patches/patch_lf_wind.py` (+ `lf_wind/`).

## The build this measures

Cold run 9139's workspace copied to `workspaces/moving-ws`, the art leg and
the export rerun with Zoo 1.56.0 and this Level Factory, walked as shipped
(`tools/walk_export.py`, `_runs/walk_export_moving`). The previous build --
the grill and the slush, Zoo 1.55.0 -- kept beside it as
`_runs/walk_export_moving_v1`, the same lot with the crowns as they were.
Not a cold run: the tool repos were edited while it ran.

## The gate first: invisible at rest

`wind_probe.gd` (in `patches/lf_wind/`) loads the walk copy, sets the wind
global to zero, stands a camera 9 m from the first London plane with the
crown against the sky, and shoots. The same probe on the previous build,
same camera (the lot is the same seed):

    crown_calm_0, this build vs previous:  mean 0.027 / 255,
    15 pixels of 746,496 differ by more than 8, none by more than 33

The replacement shader reproduces the vegetation skin. The 15 pixels are
along a cluster's edge where the two builds' leaf blobs differ by one
seeded placement.

## The motion

    probe output (this build):
      crowns=18 wearing the sway shader=18
      crown_calm:  frame0->1 moved 0       frame1->2 moved 0
      crown_wind:  frame0->1 moved 47      frame1->2 moved 50      (1.5 m/s)
      crown_storm: frame0->1 moved 116     frame1->2 moved 155     (9 m/s)
    the previous build under the same test: crown_wind 35 / 35 (no shader;
    the sky's own noise), crown_storm 0 / 0

    against the rest frame, same camera:
      breath  431 pixels moved     storm  2,476 pixels moved
      (the differing pixels sit in the crown's box, x 163..1110, y 144..645)

Half a second is a fraction of a seven-second swell, so consecutive frames
differ little; the rest-frame comparison is the one that shows the lean.
In a breath the top of a crown moves 3 cm, a few pixels at nine metres; in
a storm 18 cm, which the frame shows. The amplitudes are the design's
starting values with their derivation written down; the walker's eye sets
them.

## What the import did, read off the shipped scene

    18 crown nodes, 18 ShaderMaterials; the wood and the grate untouched
    project.godot: [shader_globals] lf_wind = Vector3(1.5, 0, 0)  (the brief says clear)

## Priced (`perf_grill_build_a.json`, `perf_crowns.json`, `perf_grill_build_a2.json`)

| package | mean median ms | mean p95 ms | mean draws |
|---|---|---|---|
| grill build (Zoo 1.55.0) | 4.80 | 5.53 | 1079.6 |
| this build | 4.57 | 4.95 | 1079.6 |
| grill build again | 4.92 | 6.03 | 1079.6 |

Draws identical in all 53 views. Median ms, this build minus the control's
second pass: mean -0.34, max |2.75|; the control's first minus its second:
-0.11, max |3.61|. Within the spread; the shader cannot be seen by this
instrument.

## Not measured

- The gust front (two trees twenty metres apart along the wind peaking
  about two seconds apart): the formula says so; no frame sequence was
  shot to read it. Written down as unproven.
- The refusal path on a real skin with a normal map: the wood is never a
  crown, so nothing exercised it in this level. The unit test holds its
  shape.

## Open

- The walker's eye on the amplitudes.
- Step 3b (the flyers), step 4 (pennants, banners, hangers).
- The Empties (roadmap item 106): the walker's call from the shack notes,
  dark inside faces so a window reads as depth -- a wiring item first,
  since no Empty has ever been placed in a level.
