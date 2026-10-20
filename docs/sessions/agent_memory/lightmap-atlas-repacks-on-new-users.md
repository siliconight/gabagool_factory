---
name: lightmap-atlas-repacks-on-new-users
description: "adding/removing any lightmap user repacks the WHOLE atlas (9269 - 127 of 3,338 users kept their rect), so frame diffs across it carry noise everywhere; read the controls, pair with a no-repack run"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-13T02:52:10.478Z
---

Measured 2026-10-12, cold runs 9268 -> 9269 -> 9270:

- **9268 -> 9269 (8 meshes added to the bake):** only 127 of the 3,338 shared lightmap users kept their rect and slice. A control station moved 2.7 % of its pixels past 8 codes, as much as the stations aimed at the change.
- **9269 -> 9270 (no users added):** all 3,346 kept their rect and slice, and the controls stayed at 0.19 % and 0.00 %.

The instrument: `docs/cold_runs/cold_9269/lm_users.gd` dumps a `.lmbake`'s `user_data` headless in an empty scratch project, with `set_abort_on_missing_resources(false)`. `lm_users.py` compares two dumps.

**Why:** for a small flush change, a whole-frame percentage past 8 codes cannot separate the change from re-bake noise. A map of the pixels past 32 codes did separate them.

**How to apply:** when a change adds or removes a baked mesh:
- expect the controls to move;
- use a past-32 map, or crops at the change, rather than the frame-wide percentage;
- when the change's own effect needs proving, pair it with a run that adds no users.

Before blaming the bake, check whether the user count moved (`light_bake.json` `result.users`). Related: [[street-drains-roadmap-179]].
