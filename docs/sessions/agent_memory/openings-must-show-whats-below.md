---
name: openings-must-show-whats-below
description: "Walker 2026-10-23 -- you must be able to see into a hole/stair opening to know you can go forward; the black was LF's backdrop ground lidding it (fixed 0.237.0), judge an opening THROUGH its rim"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-23T13:27:20.681Z
---

The walker, 2026-10-23, after a deli_a03 stair opening read pitch black: "you should be able to see into holes to know you can go forward into them".

**Why:** an opening is a route; a black one reads as a wall or a drop and a player will not take it. Moodiness is fine for a room, never for the place an opening leads to.

**How to apply:**
- Landings are lit (DC 0.261.0), and tools/light_check.py looks down every opening on every cold run.
- Judge an opening by p95 luma THROUGH ITS RIM (the rim projected into the frame), never the frame's p50. The frame is mostly the floor round the hole: it passed a black hole at 42 and failed lit ones.
- Before blaming light, check what is IN the hole. The first diagnosis ("basement is MOODY") was refuted.
- The real cause: Level Factory 0.211.0's backdrop ground plane at y -0.10 sat inside every ground slab and lidded every hole into a basement. LF 0.237.0 makes it a frame round the plate.
- The method that found it: shoot under `--inspect studio`, then list every VisualInstance3D crossing the hole's column (docs/findings/walk_2026-10-23_deli/hole_column.gd), then hide one suspect at a time in a scratch copy.

See [[interiors-must-read-at-night]] and [[light-tools-breakdown-and-check]]. Findings: docs/findings/walk_2026-10-23_deli/.
