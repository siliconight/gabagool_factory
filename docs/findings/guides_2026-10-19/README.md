# Three guides, chased: geometry, texture tiling, baked lighting

The walker, 2026-10-19, shared three guides "for optimizing our levels", the second "pairing with the question of
texture-memory cutting ... to get the best look, leaning into the pixelcoat/zoo note about quake 2 we should have on
file", the third "to chase/address". They are filed in `docs/reference/` and pointed at from
`docs/PERFORMANCE_CONTRACT.md`. Each was checked against the repository by a read-only research pass, kept here as given,
with its own verified/inferred marks:

| guide | the pass's report |
|---|---|
| `Low_Poly_Geometry_Audit_Blender_Godot_4_7.md` | `geometry.md` |
| `Texture_Tiling_Variation_Blender_Godot_4_7.md`, with roadmap 238 and `pixelcoat/docs/CONTRAST_DIRECTION.md` Part II (the Quake II note) | `textures.md` |
| `Baked_Lighting_Level_Generation_Blender_Godot_4_7.md` | `lighting.md` |

The reports' claims are theirs; a step taken on one re-reads its source first (CLAUDE.md, Verification).

## What they come to

- **None of it moves interventions-per-level**, which the sweeps already hold at 0. It moves frame cost on hardware
  nobody here has measured, and the "good" gate (roadmap 18): what a person playing would notice.
- **The factory has measured past two of the guides.** Frame time here follows draw calls, not triangles: removing
  30 % of the primitives moved the median frame by +0.018 ms against a control's +0.021 (`geometry.md`, row 15). And
  the big texture cut is already made: the reflection atlas was 257 of 516 MiB, and every level texture has shipped
  compressed since Level Factory 0.190.0 (`textures.md` §2). Both measurements are on one RTX 2060.
- **What the passes found wrong, which is the work worth doing first:**
  - The perf panel prints Godot's primitives monitor as "tris" (`debug_overlay.gd:511`). It counts vertices or indices
    across passes and moved 1.5-5.4x with the Lux tier alone; CLAUDE.md's own draw-call paragraph repeats the slip.
  - Models whose second UV set carries shader data -- tree crowns' sway, the ATM's shutter -- import as lightmap users,
    so that data serves as their lightmap UVs, and tree trunks get neither lightmap nor probes. This contradicts roadmap
    217's "trees are kept dynamic and cast none into a bake" (`lighting.md` §2, row 6).
  - Item 238's own "left" lever, compressing the level's ~30 MiB, is already spent. What fills that 30 MiB is
    duplication: 458 texture files in 9335's package are 118 images, every building shipping its own copies; one per
    content is about -10 to -12 MiB with no change to the look (`textures.md` §2).
- **What nothing measures yet, and the walker's own notes ask about:**
  - What a moving body receives from the bake. The walker on the street lights' shadows: "moving bodies shouldn't be
    dark, they will be important to see in the game". There are 126 automatic probes over a 120 x 90 m level, about
    11 m apart, and no frame has shown a body lit by them.
  - Whether light passes the baked glass panes.
  - What the walker's "you can tell where one texture stops and ends...needs 3d UV Tri stuff?" is seeing. World
    triplanar already ships on every kit wall, and triplanar "solves projection, not repetition". The suspects are the
    2 m wall tile repeating once per 2 m module, compression over fine grain, lightmap chart edges and relief seams.

## The order proposed

Each step is one change with a control, and none runs while a cold run is in flight.

1. **The panel's label** -- "prims (all passes)" -- with a test on its format string. Under an hour.
2. **The shader-UV2 classification** -- an A/B at `light_baking=3` with a no-change control, read off the lightmap's
   user count (1,434) and frames at a tree and an ATM.
3. **What a body receives** -- a grey capsule at every `light_check` station, dynamic against static (the no-probe
   control), sun on and off; then laid probes against the automatic ones.
4. **What the 238 verdict sees** -- arms at the review's two cameras, with an unchanged copy and a lossless arm that
   must move pixels; then **one texture per content per package** (-10 to -12 MiB).
5. **Glass in the bake** -- panes as shipped, out of the bake, out of shadow, against a no-change re-bake.
6. **The look moves, each to the walker's eye**:
   - one broad layer on the ground (asphalt's tile 3 -> 4 m, exactly 128 px/m);
   - a world-derived tint on merged walls (posterized to the palette: the Quake II note's "constraint");
   - inserts placed where a cause puts them.
7. **Later, each with its own control:**
   - R1 attributed by pass, with an import-LOD arm;
   - the dressing's shadows and partition;
   - shadow casting by size;
   - a second bake for a power cut;
   - the bake report and binding check;
   - the validation room built through the pipeline.

## Questions that block a step

| question | blocks | the factory's suggestion |
|---|---|---|
| Which hardware is low-end, and can a level be measured on one? | every frame-cost claim in all three guides | one run on it: as shipped twice, then the Compatibility tier |
| Tiled skins: stay pixel (nearest, 128 px/m, approved in Zoo 0.55.0) or follow the realism trial, and at what density? | 4 and 6 | decide after step 4's frames |
| May wall tiles stop repeating once per 2 m module? It reverses an approved look | 6 | show both |
| Doors: bake every doorway open (today), or exterior doors closed? A closed networked door then shows baked light past it | 3, 5 | keep open until a frame shows the cost |

The rest -- the Lux tier, dressing shadows, LOD pop-out, the power cut, sunlight through windows, baked crown shadows --
come with the frames of the step that raises them.
