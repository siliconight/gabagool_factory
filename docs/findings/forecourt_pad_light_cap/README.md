# The forecourt pad and the 8-light cap -- measured 2026-10-02

**The lead** (cold run 9126's light census, Level Factory 0.125.0): the gas
station's `forecourt_pad` is ONE mesh, 46 x 46 m, and 39 lights reach it by
range against GL Compatibility's `max_lights_per_object` of 8. The census
counts reach; it does not say whether the 31 lights over the cap would have
lit anything a player sees. The walker's question: does splitting the pad
change anything?

**What was measured.** Cold run 9130's walk copy, `tools/look_shots.py`,
five fixed stations on the forecourt, the project's
`rendering/limits/opengl/max_lights_per_object` at 8 (as shipped), 8 again
(the control), 40 (above the 39, so nothing is dropped) and 1 (the proof the
dial is read). Whole-frame luminance, 0-255:

    station      cap 8            cap 8 again      cap 40           cap 1
    lane         34.99 / p50 30   34.99 / 30       35.01 / 30       11.64 / 1
    apron        16.91 / p50 5    16.87 / 5        17.91 / 8         5.70 / 0
    side_strip   22.29 / p50 8    22.29 / 8        22.29 / 8        22.27 / 8
    canopy_far   10.58 / p50 2    10.57 / 2        10.80 / 2         9.59 / 2
    pad_top      48.35 / p50 54   48.35 / 54       48.46 / 54       47.99 / 54

`pad_top` looks down from 14 m and its frame is mostly the canopy's roof: it
is not evidence about the pad either way.

**What it says.**

* The dial is live: at a cap of 1 the lane loses two thirds of its light.
* Under the canopy and beside the building the cap does not bind: 8 and 40
  agree to the control's noise.
* On the APRON, between the storefront and the canopy, it does: 16.91 ->
  17.91 mean, p50 5 -> 8, and 6.9% of the frame's pixels move by more than
  8 levels against 0.12% between the two cap-8 runs.
  `apron_cap8_vs_cap40.png` (cap 8 left, 40 right): at 8 the door's spill
  onto the pad by the entrance is missing; at 40 it is there.

So splitting the pad would change something, and it is small: the light the
shop door throws on the ground in front of it.

**What it would cost, not yet measured.** The pad is a Zoo prop
(`Prop_Panel`), one draw. Tiled at about 12 m it is 16 draws, +15 on a
heading that sees all of it, against 2,648 on the worst heading (+0.6%).
Deli Counter already tiles a slab's visual to light-budget meshes (0.96.0);
the pad is a volume and does not go through that. Raising the project's cap
instead is not offered: it is paid by every mesh in every level.

Frame time is not claimed from these runs; `gpu_ms` in the reports moved by
more between the two cap-8 runs than between 8 and 40.
