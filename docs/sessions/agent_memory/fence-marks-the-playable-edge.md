---
name: fence-marks-the-playable-edge
description: "Walker 2026-10-04: a fence between playable and non-playable areas is good player feedback -- every playable boundary next to Empties, vacant lots or backdrop gets one; phase one shipped 2026-10-06 (Zoo 1.77.0 chain_link_fence, Lot 0.97.0 site_fences); far fabric thins away"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-10T13:17:57.489Z
---

The walker, 2026-10-04, after the fenced-vacant-lot mockup: "I like the
idea of a fence between playable areas and non playable areas, thats good
feedback to the player".

Work order the walker set the same day:
1. Empties: non-enterable shells around the walkable level and across the
   street. Finish them, then optimise them for runtime.
2. Unplayable backdrops in or near the skybox. Use
   `docs/reference/PENNSYLVANIA_BACKDROP_WORLDS_GUIDE.md`.

**Why:** the player should read where the level ends from the world itself,
not from an invisible wall or a blank perimeter.

**Phase one shipped, 2026-10-06** (roadmap 188):
- Zoo 1.77.0's `chain_link_fence`: two draws a run whatever its length.
- Lot 0.97.0's `site_fences` closes an Empty row's gaps (any a 0.7 m player
  capsule fits through) and ends, along the front line. It never crosses a
  road, path, building or blocker, and never encloses a marker.
- Pixelcoat 0.59.0 lists `chain_link`.
- Cold run 9183: seven fences on gas_block_001, 0 interventions, findings
  unchanged.

**Open, in order:**
1. **The far fabric:** FIXED (Zoo 1.78.0, Pixelcoat 0.60.0), by blending
   the texture.
   - Tested in-engine on 9184's walk copy.
   - Cutoff 0.2 and alpha hash went solid dark.
   - A far card can't fix a long run seen along its length.
   - Proven in cold run 9185: six fences, every fabric BLEND, end runs on
     the perimeter at x +-98, 0 interventions.
   - **PRICED 2026-10-06, and blended is cheaper.** On 9185, the alpha
     test is +3.3 draws a view and +0.25 ms median (inside the noise), and
     +1.59 ms where the fence fills the view
     (`docs/cold_runs/cold_9185/price_fabric.txt`).
   - What the alpha test would buy: a fence shadow, since Godot's alpha
     blend casts none. Not yet seen in a frame.
2. The plate perimeter: SHIPPED Lot 0.107.0 (2026-10-10, roadmap 228 step
   B): `site_fences.plan_perimeter`, one run a side 0.25 m inside the wall,
   the wall's tiles unseen (collision kept); the glow behind it is Lux
   0.73.0 (step A); the rowhome backdrop is step C. See
   [[edge-menu-walker-picked-e]].
3. Vacant lots.
4. Empties not in a row.
- Lot 0.97.1: fence cover is not ground content; 9183's plate grew 4 m past the end runs.

**How to apply:** fences come from Lot planners and Zoo species, never
hand-placed. The perimeter wall stays until a backdrop exists.

Related: [[land-use-guide-informs-lot]], [[empties-get-dark-interiors]],
[[backdrop-guide-filed-for-later]].
