---
name: baked-look-without-bands
description: "Walker 2026-10-24 on wall seams (walk 9386 finding 2): keep the light bake's look, remove the bands at wall-piece joints"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-24T13:31:12.058Z
---

The walker, on the vertical bands down interior walls (walk of cold run 9386, finding 2): "i think we want the look of baking but where we try to not get those bands". Keep the bake on; fix the seams in how walls are baked.

**Why:** the bake's look is liked (see [[sun-baked-by-default]], [[work-order-after-crowns]]); the bands read as generated. Measured so far (docs/findings/walk_2026-10-23_9386/seams/): with the bake off the world-projected plaster runs continuous; as shipped faint lines at joints -- a lean toward lightmap rects meeting at piece joints, not yet proven.

**How to apply:** first prove the cause (read the lightmap rects at the wall's piece joints); then try cures one at a time -- one chart per wall run (merge/unwrap), chart padding, wall texel density, denoiser -- each priced (bake time, VRAM via the reflection/lightmap atlas, frame time) with before/after frames from the walker's eye. Never fix it by turning the bake off. Related: [[lightmap-atlas-repacks-on-new-users]], [[reflection-atlas-is-the-vram]].
