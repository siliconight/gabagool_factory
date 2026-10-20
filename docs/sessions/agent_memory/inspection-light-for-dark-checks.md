---
name: inspection-light-for-dark-checks
description: "When a night frame can't settle a geometry question, shoot it with look_shots --inspect studio; never judge the look from those frames"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-14T23:04:25.210Z
---

When a question is about what is THERE (which way a monitor faces, whether a step exists), and the level's own night light is too dark to decide it, shoot with `python tools/look_shots.py <pkg> --scene mission.tscn --inspect studio --station NAME:EX,EY,EZ,TX,TY,TZ`.
- What it does: a shadowless key light rides over the camera's shoulder, with flat white ambient. Fog, glow and colour adjustments are off, the tonemap is linear, and every CanvasLayer is hidden.
- Files come out as `INSPECT_studio_<shot>.png`.
- It added about 2.5 min a run on 2026-10-14.

**Why:** the walker asked on 2026-10-14: "a tool to make the area brighter for checking things so its not too dark and you get mistaken... just for visual checks". A dark office had left the cubicle-monitor fix undecided by frames. The studio light settled it at once (`docs/findings/walk_2026-10-14/cubicles_9305_9308_inspect.png`).

**How to apply:**
- Use it for geometry and orientation checks only. Its exposure numbers describe the inspection light, never the level, so never cite them, or its frames, as the level's look.
- `fullbright` (DEBUG_DRAW_UNSHADED) was REFUTED and removed. Under GL Compatibility it drew the office darker than studio (mean 44-59 against 100-152) and flattened the floor tiles. Don't re-add it without a new measurement.

**In a walk (2026-10-14, the walker asked):** L toggles the same light in every walk copy, with a banner saying nothing on screen is the look (`tools/walk_work_light.gd`, root 3922d65). For a copy assembled before, add it with `python tools/walk_add_work_light.py <walk copy>`. Any edit to the walk scene must COUNT `load_steps`, never expect a number: `cold_drive/wire_sky.py` asserted 7 and silently refused every fresh copy once the light made it 8.

Related: [[elevated-shots-are-orthographic]], [[look-shots-frames-were-ten-percent]].
