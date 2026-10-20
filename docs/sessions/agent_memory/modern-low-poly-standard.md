---
name: modern-low-poly-standard
description: "Walker's production standard for Delco Dangerous assets (2026-10-08) -- docs/reference/MODERN_LOW_POLY_ASSET_STANDARD.md + the Zoo mapping; start every new Zoo species there; roadmap 214"
metadata:
  node_type: memory
  type: reference
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-09T12:40:23.441Z
---

The walker's "Modern Low Poly Asset Creation in Blender: Production standard
for Delco Dangerous" (8 Oct 2026). It is written as the brief for "a human
artist or procedural asset tool", so for props it is Zoo's brief.

- **The standard:** `docs/reference/MODERN_LOW_POLY_ASSET_STANDARD.md`, with
  the original `.docx` beside it.
- **The mapping:** `docs/reference/MODERN_LOW_POLY_IN_ZOO.md` sets it
  against Zoo 1.86.0, measured: what Zoo already does, nine gaps, and
  where house rules decide.
- **The work:** roadmap 214.
- **Addendum A** (same day, the walker's notes): subdivision modeling and
  support/edge-reduction topology, sculpt and retopology, multires. It lives
  in the .md, not the .docx. Never a runtime subdivided mesh: bake sources
  and human-made assets.
- **Zoo's priced trials (A.4), cheapest first:** weighted normals;
  convex-edge wear in vertex colour (`wear_colors` darkens concave vertices
  only); a procedural bake source (a creased second build under a
  Subdivision Surface modifier, baked Selected to Active); detail on that
  source. Zoo bakes nothing today.
- **Trial 1 SHIPPED, Zoo 1.87.0 (2026-10-09).**
  - **What it does:** weighted normals at export. Every bevelled part at the
    50-degree default had been a dome, 28.89 degrees off flat.
  - **What it costs:** census of 121 species, vertices, triangles, draws and
    bytes all identical.
  - **The walker on the frames:** "yeah looks better". The booth seat's
    cushions lost their accidental plumpness; the fix, if wanted, is
    rounded geometry.
  - **Evidence:** cold run 9211 and `docs/findings/weighted_normals/`.
- **The payphone frame has no phone keypad, coin slot or decals.** The
  walker noticed. That is roadmap 210, the full 90s payphone; the trial
  changed normals only.

The walker asked that it "go with Zoo and help future minting". One copy
lives at the factory root; Zoo's README points at it (Zoo 531db42).

**How to apply:**
- **Before minting a species,** read section 15 of the standard (the record
  and the acceptance checks) and the mapping's "Minting a species" list,
  beside [[authorship-guide]].
- **The default target** is "modernized low poly": small selected bevels,
  controlled normals, restrained materials.
- **Its numbers are starting points.** Measured house rules win: draw calls
  are the budget, and [[performance-beats-graphics]].
- **Price every look it proposes,** weighted normals and normal-map bakes
  included, before shipping it.
- **Trim sheets** are Pixelcoat's and Patina's, not Zoo's.
