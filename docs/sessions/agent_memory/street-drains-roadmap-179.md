---
name: street-drains-roadmap-179
description: roadmap 179 NARROWED 2026-10-12 -- Lot 0.120.0 drains (cold 9269) + 0.120.1 grates step past paint (cold 9270); covers in crosswalks kept; lids read near-black; 244 filed (crosswalks land on raised kerbs)
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-13T02:52:04.165Z
---

Lot 0.120.0 (`site_drains`) places manhole covers (every junction + a run past 121.9 m), storm inlets (one a corner), and sidewalk lids behind inlets. They are flush floaters drawn as Lot meshes (one a material a 32 m cell), with the art only. Lot 0.120.1 steps a grate along the kerb past any marking nearer than 0.3 m, except lines along a road. Cold runs 9269 and 9270 each needed 0 interventions. Price: +1.2 draws a heading, p95 +0.03 ms against a 0.05 ms floor. Root commit 3dc52cb.

- **Found by looking, not by an instrument:** 0.120.0 stood 4 of 8 grates on crosswalk bars. A through road's crosswalks lie in line with the side street's sidewalks, outside the kerb's dropped stretch. `docs/cold_runs/cold_9269/drain_paint.py` measures pieces from the shipped OBJs against `site.markings.json`.
- **As built vs as assigned:** the item assigned the pieces to Zoo species and Pixelcoat iron; they shipped as Lot meshes in a flat iron colour.
- **Kept on purpose:** covers lying on a crosswalk bar match the walker's photograph.
- **Open:**
  - Inlets between corners need a grade and a design storm.
  - The walker's eye: lids read near-black under sodium light.
  - Roadmap 244, filed from the same kerb printout: on seed_9104's lot only 25 % of crosswalk kerb ends are dropped. GROUNDED 2026-10-13 (`docs/reference/CURB_RAMPS.md`): in 1997 Philadelphia a crosswalk meeting a full kerb was real -- Kinney v. Yerusalim (3d Cir. 1993) made the city ramp only streets resurfaced since 1992. Ramps at every crosswalk, at none, or by street is the WALKER'S call; PROWAG numbers recorded for whichever.

**Why:** the walker filed 179 on 2026-10-04 ("only so many, like hydrants").
**How to apply:** start any drains follow-up from `cold_9269/NOTES.md` and `cold_9270/NOTES.md`. See [[lightmap-atlas-repacks-on-new-users]] for why a whole-frame diff can't see flush pieces, and [[floaters-zoo-core-concept]] for the 3 mm / 4 mm rule.
