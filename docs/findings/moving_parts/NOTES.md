# Small things that move, steps 1 and 2: measured

The walker, 2026-10-02: "start with the roller grill, and i want some
motion on the slurpee stuff too" (design: `docs/proposals/MOVING_PARTS_DESIGN.md`).
Shipped as Zoo 1.55.0 and Level Factory 0.129.0; the patches are
`patches/patch_zoo_moving.py` (+ `zoo_moving/`) and
`patches/patch_lf_moving_parts.py` (+ `lf_moving/`).

## The build this measures

Cold run 9139's workspace copied to `workspaces/moving-ws`, the art leg and
the export rerun with Zoo 1.55.0 and this Level Factory, walked as shipped
(`tools/walk_export.py`), nothing respawned and nothing made by hand. Not a
cold run: the tool repos were edited while it ran, so it counts nothing
toward item 17. The next cold run on `gas_block_001` is the measurement
that counts.

## Frames (`*_0.png`, `*_1.png`, `*_2.png`: half a second apart)

The probe (`moving_probe.gd`, scratch; the approach is written into Level
Factory's 0.129.0 changelog) finds the grill and the station by the
materials they wear, shoots three frames at each and at a still control,
and prints the pixel difference between consecutive frames: mean over the
frame on 0-255, and the count of pixels moved by more than 8 of 186,624
sampled.

    grill_a    (customer's side)   1.72 / 1.29     7,113 / 5,695
    grill_close                    4.39 / 6.23    23,773 / 33,299
    slush_a                        0.66 / 0.66     3,119 / 3,013
    control_ceiling                0.00 / 0.00         0 / 0

`grill_b` and `slush_b` are the camera inside the wall behind each thing
(the probe does not know the room, so both sides are shot) and read 0.

What the frames show: the rollers' highlights and the dogs' shading bands
shift between frames; the churn bands sit at different places round each
barrel. In a still, the grill's motion is a change of shading on
cylinders, which is what a turning cylinder is; it reads as turning in
motion.

## What the import did, read off the shipped scene

    M_Roller_metal_bare_turn_x36      ShaderMaterial  rate +0.628 rad/s  axis 0
    M_Roller_metal_painted_turn_xn36  ShaderMaterial  rate -0.628 rad/s  axis 0
    M_Slush_slushglow_v0_..._Face     StandardMaterial3D, next_pass = ..._churn, period 6.0

## Priced (`perf_9139_a.json`, `perf_moving.json`, `perf_9139_a2.json`)

The fixed-station harness, fresh copies, idle machine, 9139's package
before and after as the control, one session:

| package | mean median ms | mean p95 ms | mean draws |
|---|---|---|---|
| 9139 | 4.35 | 5.07 | 1080.9 |
| this build | 4.09 | 4.41 | 1081.2 |
| 9139 again | 4.00 | 4.22 | 1080.9 |

Draws: 9 of 53 views differ, by +1 to +3, all views that see the store
(two surfaces a grill, one pass a slush machine), as the design priced.
Median ms, this build minus 9139's second pass: mean +0.09, max |2.43|;
9139's first pass minus its second: +0.34, max |3.81|. Within the
instrument's spread. (9139's `attacker_spawn_1` yaw 0 read its 1,169-draw
value again in both passes this session, after reading 1,083 in the last;
the flip is the instrument's, noted in `cold_9139/NOTES.md`.)

## Two refutations kept

1. **The first shipped build turned the rollers 0.7 m off their axles.**
   Zoo wrote the pivots in the engine's axes at build time and compared them
   with the forms' numbers; the test passed; the shipped scene read vertex y
   0.24..0.32 against pivot y 0.95..1.00. `build_module` re-centres a
   module after the recipe returns. The pivot layer now rides with the
   vertices (`core.pivot.recentre`, `geometry.fit_to`) and becomes the
   engine's axes only at export, and the bpy test compares the pivots with
   the vertices AS SHIPPED: every roller corner one radius from the axle it
   carries.
2. **The first Blender build swapped the UV sets.** `merge.pack_by_material`
   created a merged mesh's UV layers in sorted-name order, `Pivot` before
   `UVMap`; glTF writes TEXCOORD_n in layer order, so the pivots went out as
   TEXCOORD_0 and the projection as TEXCOORD_1 (280 distinct "axles" for 14
   rollers). The layers follow the source's order now.

## Open

- The light band the slush tile used to paint is gone: a darkening pass
  cannot lighten, and a pass that could would glow on a dead machine.
- All dogs turn at one rate (the mean radius's); the kinds' radii differ by
  up to 25 %. Not visible at 12 mm; recorded.
- Steps 3 and 4 of the design (wind: trees and flyers; pennants, banners,
  hangers). The pivot lesson above applies to their weights.
- Item 2's residue: the neon letter that drops out, the pump price shimmer.
