# The modern low-poly standard, and where Zoo's minting stands

**What this is.** The walker's production standard
(`MODERN_LOW_POLY_ASSET_STANDARD.md`, the original `.docx` beside it, 8
October 2026) is written "for a human artist or procedural asset tool". For
props, Zoo is that tool. This note maps the standard onto how Zoo mints a
species today, measured where it could be, so the next species starts from
it.

**How the two weigh against each other.** The standard calls its own numbers
"proposed starting points", not measured limits. Where it meets a rule this
factory measured, the measurement decides, and the rule is cited below.
Where it fills a blank, it is the brief.

Measured 2026-10-08 on Zoo 1.86.0, from the genomes, the recipes and one
real `meta.json` (the cruiser's).

## What Zoo already does

| The standard asks (section) | Zoo today |
|---|---|
| One opaque surface per simple prop; repeated-object tint in vertex colour (1, 2) | Colour rides `Wear`, the vertex colour, on one material per part family (`geometry.tint_wear`, `tint_wear_by`). The export packs parts by family and material (`bpylayer/merge.py`). CLAUDE.md: "Never express colour-only variation as a new material". |
| Small selected bevels, one segment (5) | Genome styles carry `bevel`: 588 of 733 style rows set one above 0, and 97 of 122 species bevel in some style. Most recipes apply it through `bevel_edges`, one segment. Some choose their chamfers instead: `simple_car` models the ones a car reads by into its sections and builds every part at 0, because bevelling every edge took 12-triangle boxes to 44 (its own comment, measured on walk 9048's car). That is the standard's "selected" in practice, but its genome's style bevels (0.01-0.014) then do nothing. Four recipes pass only a literal 0: cruiser, glass_shard, step_van, vault_door. How many shipped parts carry a bevel was not measured here. |
| Controlled normals, smooth by angle, sharp edges kept (5) | `geometry.shade_by_angle` at 50 degrees on the bmesh. Bevels roll off as highlights; box corners stay hard. Since 1.87.0 the export weighs each part's normals by face area (`core/normals.py`), so a bevelled face reads flat; before, every bevelled part at 50 degrees was a dome (`docs/findings/weighted_normals/`). |
| No automatic subdivision of the runtime mesh (preserve) | None. Every face is built. |
| Count exported triangles against a budget (1) | `budgets.tris_lod0` in every genome, checked as `tri_budget` (a warning) at every build. |
| Collision separate and simple (10) | `-colonly` boxes from a recipe's `collision_boxes`. |
| Consistent origins, scale and transforms (3, 11) | `build._recentre` enforces the centre pivot. Validation checks `fit_pivot` and `transforms`; `ATT_*` empties mark attachment points. |
| Clean topology, no accidental overlaps (4) | `tools/coplanar_census.py` builds every species at three genome corners; `tests/test_coincident_faces.py` holds the count. Pairs are fixed at their source. |
| Wear placed by cause (8) | `tint_wear_by` paints per corner: the getaway van's sun-chalked top, dusty sills, rust at the arches. `HUMAN_AUTHORSHIP_GUIDE.md` asks for cause and specificity. |
| Texel density for readable labels, 256-512 /m close (1, 7) | Set per species where a label must read. The cruiser's livery is 380 px/m (`cruiser_forms.ART_PPM`). |
| Cylinder sides by outline (2) | Genome params: `wheel_segments` 10-24 on cars, the van's tyre 28. |
| An asset record with the mesh (15) | `meta.json`: module (dims, fit, pivot, style, theme), genome, license, plan, and validation. Validation covers dimensions, fit, triangle budget, UVs, wear colours, materials, named parts, collision and applied transforms. |

## Gaps: what minting should add

**1. The record's missing fields** (section 15, "Supply this record").
`meta.json` lacks:
- viewing conditions (closest and normal distance, expected repetition);
- the recognizable features the construction serves;
- exported vertices per LOD, after UV and normal splits;
- the material surface count;
- texture dimensions and texel density;
- LOD versions;
- evidence: comparison frames and the conditions they were taken under.

The standard's tool instructions say "Emit the asset record with the mesh".

**2. Budgets by asset class** (section 1). A genome carries one number.
Across 122 species the median budget is 900:

| budget | species |
|---|---|
| 1,500 or under | 78 |
| 1,501 to 4,000 | 25 |
| 4,001 to 8,000 | 12 |
| over 8,000 | 7 |

**The seven over the hero range:**
- snack_gondola, 22,000;
- cubicle_bank, 24,000;
- video_rack, 15,000;
- coffee_island, 12,000;
- vault_door, 9,000;
- back_bar, 8,500;
- step_van, 16,000.

Most are whole assemblies, a bay full of stock, rather than one prop. The
van is the walker's hero.
- **The gap.** A genome could name its class (clutter, medium, hero,
  assembly), so that a budget outside the class's range is a stated
  exception.
- **What the standard rejects:** "silent budget overruns".
- **What a budget is here:** CLAUDE.md calls a triangle budget a regression
  detector, not a frame cost. The class says what the number is for.

**3. LODs** (section 10). `bpylayer/lods.py` makes optional Decimate copies
at 0.5 and 0.25, off by default.
- **The standard's caution:** Decimate output needs review for silhouette,
  normals and seams, and a transition is chosen by screen size.
- **No species ships LODs.** The measured cost here is submissions, not
  triangles (CLAUDE.md, "Draw calls are the budget"). So an LOD that keeps
  its draw count buys little, and distance hiding (visibility ranges,
  occlusion) buys more.

**4. Weighted normals** (section 5). Not used. A trial is a look, so it is
priced: on/off frames at fixed stations under the three lighting checks.
The standard asks for the same comparison in section 14. Addendum A.4 puts
it first of four trials: it costs no texture and no triangles.
- *Shipped, Zoo 1.87.0 (2026-10-09).* Census of 121 species: vertices,
  triangles, primitives and bytes identical; big-face corners over 10
  degrees 15,114 to 5,498. No measurable frame cost against two controls.
  The walker: "yeah looks better". `docs/findings/weighted_normals/`.

**5. Baked normal maps** (section 6). Zoo bakes none. The standard expects
them only for selected close props and says common props "may need only
geometry normals and shared materials". A bake adds texture memory and
sampling, so it is priced before it ships.
- **Where a source would come from.** Addendum A.1 and A.4 (subdivision
  modeling) say how Zoo could make its own bake source.
- **How.** A second build of the same recipe, its hard edges creased or
  support-looped under a Subdivision Surface modifier, baked Selected to
  Active onto the game mesh.
- **What it buys.** Rounded, light-catching edges without a triangle more.

**6. Trim sheets** (section 7). These belong to Pixelcoat (skins) and
Patina (the facade covers' trim atlas), not Zoo. The standard's deli and
convenience-store trim family is a brief for those two.

**7. The three approval assets** (sections 12 and 13). Each has a
counterpart:

| the standard's asset | the factory's counterpart |
|---|---|
| the deli cabinet | Zoo's `deli_case` and `counter` |
| the payphone | Zoo's `payphone`; comps in `PAYPHONE_COMPS.md`, roadmap 210 |
| the storefront | Deli Counter's storefronts, dressed by Zoo and Pixelcoat |

The standard's A/B/C comparison (basic boxes; construction; bevels and
normals) under identical neutral light has never been run on any of them.

**8. Wear by shape on exposed edges** (section 8, and Addendum A.2's cavity
masking). `geometry.wear_colors` darkens concave vertices by their average
edge angle and adds seeded grime. It does not lighten or chip convex edges,
which is where impact and handling put wear. The change is in vertex colour
only, so it needs no texture: Addendum A.4's second trial.

**9. Sculpted and human-made assets** (Addendum A.2 and A.3). Characters,
food and sculpted damage are made by sculpt, retopology and multires, by a
person. They enter through Zoo's ingest and meet this standard there. Zoo
does not sculpt.

## Where a measured house rule decides

- **Draw calls are the budget** (CLAUDE.md). The standard says frame time
  is the measure and "follow the measured bottleneck". Here that
  measurement was taken, and submission dominates.
- **Performance over look.** The game is online and multiplayer. Every
  look the standard proposes (bevel geometry, normal maps, extra surfaces)
  is priced before it ships, and the cheap version ships with what the
  expensive one would have bought said aloud.
- **References fill blanks.** A shipped look the walker approved stays
  unless the walker says otherwise.

## Minting a species against the standard

From section 15's instructions for procedural tools, in Zoo's terms:
1. **Inputs.**
   - The genome's dimensions and their range.
   - The construction type: folded metal, molded plastic, wood, masonry,
     pipe or fabric (section 3).
   - The viewing distance and repetition.
   - Moving parts, with their pivots.
   - The silhouette features that make it read, to begin with.
   - The material family, and the class budget.
2. **Build.**
   - Geometry for silhouette and deep openings, and visible thickness and
     joints.
   - Selected one-segment bevels.
   - No subdivision.
   - One part family per material, so the export merges it.
   - Primitive collision.
3. **Check.**
   - The census (no coincident faces).
   - The budget, stated against the class.
   - Frames at close, normal and far distances, in neutral, warm interior
     and night light.
   - Before and after under identical lighting.
4. **Emit the record** with the mesh.
5. **Reject**, in the standard's words: "silent budget overruns, hidden
   dense sources in exports, unexplained global smoothing, unsupported
   material graphs, and claims of equivalent performance without a
   comparison".

Then the brief the authorship guide asks for, and the comps where the
walker gave some.
