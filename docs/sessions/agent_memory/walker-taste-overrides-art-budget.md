---
name: walker-taste-overrides-art-budget
description: "The art standard's chroma/contrast budget is advisory; when the walker likes a look that the audit flags, keep it and record why."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4bb794c9-c366-4613-95bd-3c61e9a0d0f9
  modified: 2026-09-13T17:36:30.069Z
---

The walker loves `carpet_delco`'s saturated burgundy/mauve look, even though
Pixelcoat's art standard audit measures it at chroma_mean 0.064 against a
0.030 budget and I first reported it as a defect from cold run 9044's frames.

**Why:** the budget is an instrument standing in for the walker's judgement of
whether a surface reads well; the walker's eye on a real frame is the thing it
approximates. Period-true late-1990s accents (mauve, teal, hunter green) are
part of the Delco art direction.

**How to apply:** before "fixing" a grammar only because it is over the
art-standard budget, check whether the walker has commented on it. Present an
over-budget finding as a measurement and a question, not as a defect to
retune. Keep the walker's call in the grammar's `notes` so a later session does
not burn it down. Related: [[walker-wants-retro-style-with-real-structure]].
