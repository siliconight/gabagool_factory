---
name: moving-parts-shipped
description: "Alive item 3 (small things that move) steps 1-2 SHIPPED 2026-10-02: Zoo 1.55.0 + LF 0.129.0 -- roller grill rollers/dogs turn (UV2 axle + vertex shader), slush churn bands walk (darkening next_pass); wind steps 3-4 not started"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-03T02:13:57.829Z
---

Design: `docs/proposals/MOVING_PARTS_DESIGN.md` (walker: "start with the roller
grill, and i want some motion on the slurpee stuff too"). Shipped 2026-10-02:
Zoo 1.55.0 (rollers `metal_bare_turn`, dogs `metal_painted_turn`: own surfaces,
axle in UV2 `Pivot`, rate in the material name `_turn_x36` / `_turn_xn36`; slush
tile loses its painted bands, churn facets carry (u, v) in UV2 `Churn`, v = 2
elsewhere) and Level Factory 0.129.0 (`zoo_worldskin.gd` `_turning_parts`
replaces the material with a vertex-rotating shader; `_churn_passes` hangs a
darkening next_pass on `M_Slush_*_Face`). Measured in the shipped package with
`patches/lf_moving/`'s probe approach: frames half a second apart differ at the
grill and the slush, zero at a still control. Price: +2 draws a grill, +1 a
slush machine; frame time within noise. Findings: `docs/findings/moving_parts/`.

**Why it matters for steps 3-4 (wind: trees, flyers; pennants, banners):**
- A pivot/weight written into vertex data at BUILD time goes stale: Zoo
  re-centres every module after the recipe returns (0.7 m here) and `fit_to`
  scales. The `Pivot` layer now rides with the vertices (`core.pivot.recentre`,
  `geometry.fit_to`, `geometry.map_pivots`) and converts to engine axes only in
  `export.pivots_to_engine`. Any new per-vertex positional data must do the same.
- `merge.pack_by_material` orders UV layers by source now (sorted order put
  `Pivot` before `UVMap` and swapped TEXCOORD_0/1).
- Test the SHIPPED GLB against its own vertices, not against the forms' numbers.
- Lit `_Face` materials cannot be replaced by a ShaderMaterial (Lux's binder
  needs a BaseMaterial3D) -- motion on a lit face must be a darkening next_pass.
- Turning kinds take the flat material path (`materials.base_kind`, TURN_SUFFIX)
  and are deliberately not in `skins.KNOWN_KINDS`.

Item 2's residue still open: the neon letter dropping out and the pump price
shimmer. Related: [[levels-feel-static-make-them-alive]], [[failing-fixtures-paused]].
