---
name: baked-look-without-bands
description: "Walker 2026-10-24, walk 9386 finding 2: keep the bake's look, lose the bands. Cause measured: seams where an INTERACTIVE opening's own mesh (breach panel, doorway) meets the merged wall; cure = a casing/frame at the edge, breach panels too (walker: yes)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-24T15:36:09.082Z
---

The walker, on the vertical bands down interior walls (walk of cold run 9386, finding 2): "i think we want the look of baking but where we try to not get those bands". Keep the bake on; fix the seams.

**Cause, measured 2026-10-24** (docs/findings/walk_2026-10-23_9386/seams/, README finding 2): 8 of the walker's 10 marks sit where an opening slot's own mesh meets the room's merged wall -- each has its own lightmap rect and the bakes disagree (-12 %/+13 % at a breach panel's edges). Every such slot is INTERACTIVE (breach panels swap to `_breached`, doorways), so merging them is ruled out. Refuted on the way and kept: module joints (a control on lamp-pool extremes), per-module wear colours (not drawn), UV restarts (world-triplanar), Mach bands (bicubic already on), LF 0.240.0's one-chart unwrap (reverted 0.240.1). My first station was not the walker's view -- use `walker:-8.0,1.6,-0.1,0.4,2.07,-6.34` on restaurant_row_001.

**The walker's call, 2026-10-24:** hide the seam with a casing/frame at the edge, breach panels included: "Yes hide the seam for breaches, we still don't know how they would work in the game but its' really cool we are building it in for potential use".

**Why:** the bake's look is liked ([[sun-baked-by-default]]); the bands read as generated. A casing is how real buildings cover that joint.

**How to apply:** the frame is Zoo geometry inside the interactive slot (no draw added); prove it from the walker's view with before/after frames; the 2 unexplained marks above the bookshelf stay open. Breach mechanics are undecided -- build breach support in, don't design its gameplay. Never fix bands by turning the bake off.
