# Trees: the walker's reference tree, its method, and god rays

The walker, 2026-10-09: "On the roadmap, improving Trees". With it:
- **The file.** `one tree hill_gumroad.blend`: "The cc0 tree to use as a
  reference for how to make better looking trees". It is CC0, by the
  walker's word.
- **The video it comes from,** "How I Made a Game-Ready Tree in Blender +
  Project Files", as a transcript. Read for method only; it is summarized
  below in this repo's words, not reproduced.
- **A note on god rays** through trees, and a photograph: a low sun behind a
  canopy, with shafts of light fanning down through haze. It was shown in
  chat and is not stored.

Roadmap 216 tracks the work.

## The file

- **The binary is not tracked.** It is 74,678,794 bytes, saved by Blender
  4.4, sha256 `12bc6c12f8818b4dd452ddd18276bfa3037d045821f165afdfc49a649ecf77e7`.
  Too large for the coordination repo, so it lives at
  `_archive/reference/one_tree_hill_gumroad.blend` (ignored), and the
  video's Gumroad page is its source (`docs/FILING.md`, the reference-asset
  row).
- **How it was read.** `docs/findings/trees_reference/inspect_blend.py`,
  with Blender's auto-exec off; output `inspect_blend.json`. It holds no
  scripts.

## What it is made of (measured)

One stylized hero tree on a hill, about 18 x 16.5 x 21 m. 828 objects,
every one a mesh.

| part | objects | triangles | material and maps |
|---|---|---|---|
| the trunk, `HillTree`: one connected mesh, roots, trunk and main limbs | 1 | 7,030 | `HillTree`: 2048 colour, 2048 normal, opaque |
| its sculpt, `HillTree_high`: the same base under a Multires modifier | 1 | 7,030 base | (the bake source) |
| large branch cards, `Plane` | 12 | 100 each | `Branch`: 2048 colour with alpha, 2048 normal |
| small leafy cards, three variants, `BranchSmallLeaves_01/02/03` | about 800 | about 28 each | `BranchSmallLeaves`: 2048 colour with alpha, 2048 normal |
| bare twig cards, `BranchSmall_01/02/03` | 3 | 6 to 28 | `BranchSmall`: 2048 colour with alpha, 2048 normal |

- **The game tree** is the trunk plus about 500 small cards and the 12
  large ones: about 21,000 triangles in 3 materials.
  - `ManualBranches` holds another 302 small cards (9,400 triangles), the
    hand-placed set.
  - `HillTree_particles` is a second copy of the trunk, the video's
    particle-scattered version.
- **Every card material is alpha-tested and two-sided.** Blender reads them
  as dithered with a 0.5 threshold and no backface culling. Each has its
  Principled Alpha input linked, and reads only two images, a colour map
  and a normal map. Which channel feeds the alpha was not read.
- **The placed cards are bent.** A placed copy is about 0.7 m deep in its
  own axes; the source variants are flat. Each is a few faces, about 14
  quads, not one.

## The method (the video, in this repo's words)

**The trunk.**
1. A skeleton of extruded vertices under a Skin modifier, one radius per
   vertex, smoothed by a Subdivision Surface.
2. Applied, then thinned by dissolving every second edge loop. The
   silhouette stays and the loops go.
3. Sculpted: bent and rotated limbs to break symmetry, then bark under a
   Multires modifier.
4. The low mesh is matched to the sculpt ("apply base"), unwrapped, and the
   sculpt baked onto it.

That is Addendum A.2 and A.3 of the modern low-poly standard, in use.

**The crown is cards.**
1. Real 3D branches, bare and leafy, in several variants, baked (colour and
   normal) onto a plane.
2. The plane is cut to the branch's outline, given a few loop cuts, and bent.
   The origin goes at the branch's base, so wind and growth pivot there.
3. Small cards are snapped onto large ones, and the large ones onto the
   trunk. The more variants, the more natural the crown.
4. Cards are merged as far as possible to cut draw calls, and alpha-clipped
   by a mask.

**The trunk stays still; the cards carry the wind.**

## God rays (the walker's note, and what this renderer allows)

The note lists three ways: volumetric fog lit by the sun; screen-space light
shafts; and fake shafts, which are semi-transparent cones or quads placed
under the trees. The note calls the last the performance-friendly one.

Here:
- **Volumetric fog does not render** on GL Compatibility, the renderer
  packages ship on. Lux measured it: "frame unchanged, engine warning"
  (`lux/CHANGELOG.md`, the weather probe).
- **Screen-space shafts** are the class of full-screen post-process that
  CLAUDE.md lists as refused or deferred on cost.
- **Fake shafts already exist for streetlights.**
  `lux/shaders/spatial/lux_light_cone.gdshader` is an additive cone with a
  flat apex-to-ground alpha gradient, faded to nothing as the camera walks
  under it. It is off by default. A shaft under a canopy, angled along the
  sun, is the same kind of object.
- **When they apply.** Only in the daylight slots with a low sun: morning,
  afternoon and evening of the walker's five times of day. Never at
  midnight.

## Zoo's trees today (measured 2026-10-09)

Six species from one recipe, `zoo/zoo_keeper/recipes/street_tree.py`:
`street_tree`, `red_maple` (the default form), `pin_oak`, `honey_locust`,
`london_plane` and `callery_pear`.
- **How one is built.** Grown from a skeleton: a tapered six-sided trunk
  and leader, primary branches at the species' angles
  (`core/tree_forms.py`), box twigs, and a faceted box "leaf cluster" at
  every tip. That is the low-poly retro read the walker kept on 2026-09-13.
- **What one costs** (`docs/findings/weighted_normals/census.json`):
  2,220 to 3,564 triangles, 4 primitives and 203 to 320 KB, on 3 to 5 m
  slots, 5.5 to 6.5 m tall.
- **Wind exists.** The crown carries a `Sway` UV layer, weighted by height
  and phased per cluster (Zoo 1.56.0).
- **Cards were tried.** `params.crown = "cards"` keeps 0.69.2's four crossed
  cutout planes, "judged not ready" on cold run 9032.
- **In a level at night:**
  `docs/findings/weighted_normals/level_extraction_pair.png` shows a trunk
  under a few square green masses.
