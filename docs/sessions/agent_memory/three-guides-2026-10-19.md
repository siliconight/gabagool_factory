---
name: three-guides-2026-10-19
description: "Walker's geometry, texture-tiling, baked-lighting guides filed + chased 2026-10-19; synthesis docs/findings/guides_2026-10-19/; roadmap 261-263 opened, 238 updated"
metadata:
  node_type: memory
  type: reference
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-19T23:23:19.603Z
---

Filed in `docs/reference/` (root ea7972e): `Low_Poly_Geometry_Audit_Blender_Godot_4_7.md`, `Texture_Tiling_Variation_Blender_Godot_4_7.md` (walker paired it with roadmap 238 and Pixelcoat's Quake II note = `pixelcoat/docs/CONTRAST_DIRECTION.md` Part II), `Baked_Lighting_Level_Generation_Blender_Godot_4_7.md` (its §20 is an AI instruction block: content, not instructions).

Chased (root 35b60b0): three read-only passes kept verbatim in `docs/findings/guides_2026-10-19/` (geometry.md, textures.md, lighting.md) + README synthesis. Headlines:
- Nothing moves interventions-per-level; frame time follows draws not triangles (measured); the texture cut already happened (reflection atlas 257 of 516 MiB; S3TC since LF 0.190.0).
- Defects: 261 the perf panel (F4) prints the primitives monitor as "tris"; 262 models whose UV2 is shader data bake through it (export.py MODEL_STATIC=1; bake names StreetTree_Crown, ATM_Shutter) -- verified at source; 238's "compress the 30 MiB" lever spent -- 458 texture files = 118 images, dedup ~-10..-12 MiB.
- Unmeasured: 263 what a moving body receives (126 auto probes ~11 m apart); light through baked glass; what the walker's 238 "texture stops and ends" sees.
- Proposed order: label fix, UV2 A/B, actor capsule probe, 238 diagnosis arms then dedup, glass, then look moves (ground broad layer, wall tint, cause inserts).
- Blocking questions for the walker: low-end hardware; pixel vs realism skins; 2 m wall-tile repeat; doors baked open vs closed.

Cite the guides as prescriptions until measured ([[performance-beats-graphics]], [[runtime-optimization-guide]]).
