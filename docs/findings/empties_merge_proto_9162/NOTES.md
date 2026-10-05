# The Empties, merged one mesh a side per material: a prototype, priced

Measurement only. No tool changed. The walker's order for the Empties was
"finish them, then optimise them for runtime".

## The ceiling

From cold run 9161's notes, re-measured interleaved with cool-downs: hiding
all 25 Empties saves
- **816 draws and 1.87 ms** at the median view;
- up to **3,951 draws and 11.6 ms** at the worst.

That is the most any work on them could save.

## What an Empty submits

A three-storey Empty instances about 88 kit modules, one per Deli Counter
slot.
- **In Godot:** 95 MeshInstance3D, 161 surfaces, in 8 materials.
- **Its collision** is its base's 94 `-convcolonly` shapes plus each
  module's own collider.
- **Its covers** are already merged per side (roadmap 180).

## The prototype

`patches/lf_empties/merge_empties_proto.gd`, run headless on an imported
copy of cold run 9162's package, with every Empty scene saved back.
- Each slot child whose name gives a side (`ext_<storey>_<facing>_*`,
  `parapet_<facing>_*`, `roof_*`) is taken apart.
  - **Colliders:** its StaticBody3D colliders are copied out whole.
  - **Surfaces:** every surface is appended into one SurfaceTool per
    (side, material name, uv1 scale and triplanar flags, surface format).
    Each module GLB imports its own material instances, so the name is the
    identity.
- A three-storey Empty goes from 95 meshes and 161 surfaces to **13 merged
  meshes**, with all 86 colliders kept. The painted-block houses go to 9.

**The look:** `merged_across_the_street.png` against 9162's own frame from
the same camera.
- Brick, stone, windows, doors, AC units, bars and lintels are unchanged.
- The brick runs continuously across what were module seams: the worldskin
  projects from world position, so merging does not move it.
- The lamp pools on the merged facades are a little brighter. The merged
  meshes are not the baked lightmap's users (its users are node paths), so
  they draw without it.

## The price

A = 9162, B = merged, A2 = 9162: two-pass harness, 60 s cool-downs
(`price_robust.txt`, `price.txt`). The control had 0 headings more than
1 ms apart, median +0.026 ms.

| | merged | ceiling (all hidden, on 9161) |
|---|---|---|
| draws, median view | -686 | -816 |
| draws, mean / most | -913 / -3,015 | -1,212 / -3,951 |
| median frame, median view | -0.88 ms | -1.87 ms |
| median frame, mean / most | -1.53 / -6.94 ms | -2.85 / -11.6 ms |
| p95, median view | -1.07 ms | -2.23 ms |

- **The merge recovers about 84 % of the Empties' draws** and about half of
  their frame time. The rest is what drawing the Empties' pixels costs,
  which no merge touches.
- The ceiling was measured on 9161's row and the merge on 9162's, which
  differ in which houses stand where. The ratios are approximate.
- **Not established:** whether lightmapped merged meshes cost more or less
  than these unbaked ones. A real merge happens before the bake, so its
  meshes would be lightmapped as today's modules are.

## What a real merge has to carry

These come from mapping the code (subagent survey, 2026-10-05) and from the
prototype.
- **Where.** In Level Factory's export, after the package is imported and
  before the light bake.
  - The composer is plain Python and computes each slot's final transform.
    `_fit_rotation` and a 4 mm sink mean `slots.json` alone does not
    reproduce placement. Only the imported scene has the transforms.
  - The bake keys lightmap users by node path, and Godot generates UV2 at
    import for a mesh without it. A merged mesh needs `lightmap_unwrap`
    before the bake.
- **Materials:** the imported instances. The worldskin's world projection
  and the lit pane faces (`M_Window_pane_Face`, UV-mapped) are already on
  them, and the prototype shows both survive.
- **Collision:** keep each module's collider as it is. A doorway's jambs
  come from the module, not the base.
- **Occluders:** `bake_occluders.gd` classifies by module file name, and
  Empties supply 1,002 of the package's 1,316 occluders. The merged sides
  need a rule of their own.
- **Gates:** Deli Counter's z-fight and placement gates run inside compose,
  before any merge, so they are unaffected.
- **CLAUDE.md, "never across modules".** The rule's reason is the culling
  unit: merge the largest thing that enters and leaves view as one. A side
  of a sealed Empty is that thing, as a side of a building's covers was
  for roadmap 180. Its kit modules are parts of that unit, not separate
  buildings, and a street of them merged into one mesh would still be
  wrong.
