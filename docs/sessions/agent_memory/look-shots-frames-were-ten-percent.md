---
name: look-shots-frames-were-ten-percent
description: "look_shots frames of packages exported 2026-09-21..29 were taken during LF's shader warm-up at 10% 3D scale; stats hold, fine detail does not. Fixed 2026-09-29."
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-09-30T00:41:00.181Z
---

Between Level Factory 0.99.0 (2026-09-21, `warmup.gd` sweeps at `scaling_3d_scale` 0.1 for ~360 frames) and the fix in root `tools/look_shots.gd` on 2026-09-29, every look_shots frame of an exported package was a 160x90 render stretched to 1600x900. Found in cold run 9113 when a neon sign rendered as broken dashes.

**Why:** frame-wide numbers (mean, % crushed) held to a code or two when re-shot, but anything thin -- sign strokes, lettering, small lamps -- was destroyed. Decisions made on legibility from those frames are suspect: the price pylon's 2.4 -> 3.4 m enlargement (Zoo 1.26.0) was one; FLAPPHAS reads at 30 m at full scale.

**How to apply:** trust a look_shots report only if its shots carry `scaling_3d_scale` (the fixed tool stamps it) and its notes show the warm-up wait. Re-shoot before reusing any older frame for a detail judgement. `perf_stations.gd` was checked and is unaffected (it warms ~560 frames itself). See [[performance-beats-graphics]].
