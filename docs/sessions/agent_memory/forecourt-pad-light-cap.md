---
name: forecourt-pad-light-cap
description: "Measured 2026-10-02: the 8-light cap binds on the gas station pad only at the apron by the door (door spill missing); small. Tiling the pad not built."
metadata:
  type: project
---

docs/findings/forecourt_pad_light_cap/: the 46 x 46 m `forecourt_pad` is one Zoo prop mesh reached by 39 lights. Project cap 8 vs 40 vs a control, 5 stations: no change under the canopy or beside the building; on the apron mean 16.91 -> 17.91, p50 5 -> 8, 6.9% of pixels move (control 0.12%) -- the shop door's spill on the ground is dropped at 8. Cap 1 proved the dial is read.

**Why:** the walker asked to measure before splitting the pad.

**How to apply:** tiling the pad (~12 m, +15 draws on a full view, ~+0.6% of the worst heading) is the walker's call and is not built; raising the project cap is not offered (every mesh pays). See [[performance-beats-graphics]].
