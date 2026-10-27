# The supermarket's gondola ends render black

Seen on 2026-10-27 in the walker's rebuilt Restaurant Row level (seed 9205; Deli Counter 0.277.0, Zoo 1.132.0,
Level Factory 0.259.0), frames `docs/findings/walk_2026-10-26_panel/frames/08_*` and `09_*`. From the aisle heads,
the end of supermarket_a01's 14 m gondolas renders pitch black above its end cap. So does a long box at the aisle
heads, read but not probed here. The block is in the control frames of 2026-10-26 too
(`docs/findings/selling_hall_lights/frames/02_*`, the centre of the left half), so it predates this week's changes.

## What it is: MEASURED

All probes ran on the walker's walk copy; the station is (3.5, 1.6, 13.0) looking at (3.5, 1.2, -8.0).

- **The mesh.**
  - `ray_probe.gd` (`ray_probe.out.txt`): the ray through the block enters `Level/Bake/Site/b1/MergedR_150` first,
    at 2.99 m. That is the gondola's merged painted steel, 5,544 verts, `M_Skin_metal_painted_delco_1997_ffffff`.
  - `paint_arm.py` (`paint_arm.out.json`): painting that mesh flat red turns the block red, and painting the bags'
    mesh green does not.
- **Its geometry and colour are right.**
  - `plane_normals_probe.gd` (`plane_normals.out.txt`): the end panel's outer face at z = 9.69 is 2.8 m2, its
    stored normal +z (toward the station), the winding agreeing.
  - Zoo builds it so. A Blender build of the 14 m module read its outer faces at x = +-6.68 with normals outward;
    that one-off script was not kept. The module GLB as Godot imports it reads the same (`module_normals_probe.gd`,
    `module_normals.out.txt`).
  - Its vertex colour is 0.65 grey (`vertex_probe.out.txt`).
  - Its own material set unshaded renders it light grey, (164, 166, 173) at the block's centre
    (`paint_arm_steel_own_unshaded.out.json`).
- **So it receives no light.**
  - Baked: black.
  - Every LuxLighting's baked lighting switched off at load, every static rig light then dynamic
    (`unbaked_arm.py`): still black.
  - Re-baked at LightmapGI `texel_scale` 2 (`tools/lux_rebake.py`): still (9, 10, 13).

## What it is not: REFUTED

- **The albedo** (Zoo's `snack_gondola` paints its end panels steel 0.72): unshaded it is grey.
- **Inverted normals.** RETRACTED: `vertex_probe.gd` chose triangles by centroid within a radius, and read the
  panel's INNER face, 2 cm behind, for the outer one. `plane_normals_probe.gd` picks by plane and is the reading
  that stands.
- **A normal map with no tangents.** `tangent_probe.out.txt`: `normal_enabled` false, 5,544 tangents, none zero.
- **Lightmap resolution.** Texel scale 2 changes nothing.
- **A metal finish.** `material_probe.out.txt`: metallic 0.000.

## The bake, read further (2026-10-27)

- **It is a lightmap user.** `lightmap_users_probe.gd` (`lightmap_users.out.txt`): `MergedR_150` is user 1,769 of the
  LightmapGI's 2,807, gi_mode static.
- **Its end face's UV2 is its own.** `uv2_overlap_probe.gd` (`uv2_overlap.out.txt`):
  - the face's chart is about 13 x 9 texels of the mesh's 270 x 266;
  - no other triangle of the mesh overlaps it.

  So the bake computed that face dark; it did not borrow a hidden face's texels.
- **It receives the room's fill and almost no lamp.** Re-baked with `bake_room_fill` 0.1, four times Blue Hour's
  0.025:
  - the frame's mean doubled, 39.8 -> 79.0 (p50 104);
  - the block rose only 9 -> 25.

  The fill reaches it and the lamps barely do.
- **The lead, not measured.** The lamps are downward cones whose RANGE is drop + 0.75 m (Lux's
  `lux_light_loader.gd`, written against realtime per-object light claims). Under this store's 4.1 m ceiling that
  floors a pool about 2.6 m across, and the face looks toward the storefront. The only row on its side (Godot
  z 12.8) is about 4.0 m from it, against a 4.85 m range, in the attenuation's tail.

  Every steady fluorescent here is BAKED, so the range the realtime rule protects is not what the bake needs. A
  bake-only range, or a broader emitter, would light vertical faces the way a ceiling of troffers does. That is a
  Lux change to every interior, to be priced, and the walker's to see.

## The range arm, first attempt: NULL, KNOB NOT READ

`range_arm_loader.py` (`range_arm_loader.out.*`) scaled `fluorescent_range` in the walk copy's own
`runtime/lux/runtime/lux_light_loader.gd` by 1.6 and 2.0 and re-baked. All three arms read identically (to_cooler
38.5, walker_sales 47.6, the block (1, 1, 7)).

That is evidence about the wiring, not the lead. The range is computed once when Lux applies the rig (Level Factory's
`assets/godot/run_lux_apply.gd`) and saved as a literal in `presentation/lux.applied.tscn`. There, the supermarket's
50 lamps read `spot_range = 4.85`, `spot_angle = 89.0`, `spot_attenuation = 2.0`, hung at y 4.1 over x -16..22,
z -15..13. `tools/lux_rebake.py` loads that scene as saved and never calls the function.

A second draft scaled only the saved lamps' `spot_range`, and was stopped before it ran. That would have been a
second dead knob: `lux_fluorescent_rig.gd` is `@tool`, and its `_rebuild()` frees every saved lamp at `_ready` and
builds it again from the rig resource's `light_range`, in the editor's bake as in the game. `range_arm.py` scales
`light_range = 4.85` on the 50 rig resources, and the saved `spot_range` with it.

By the window Lux prices with (`range_window`, `(1 - (d/r)^4)^2`), a lamp 4.0 m from the face at a 4.85 m range
passes 0.29 of its light before the inverse square. At 7.76 m (x 1.6) it passes 0.92.

## The range arm: MEASURED (`range_arm.py`, `range_arm.out.txt`)

The supermarket's 50 rigs' `light_range` scaled, re-baked, shot. The control reproduces the shipped frame to the
digit, so the instrument is the shipped build:

| arm | to_cooler mean / p50 | walker_sales mean / p50 | the block's RGB |
|---|---|---|---|
| control (4.85 m) | 38.5 / 41 | 47.6 / 44 | (1, 1, 7) |
| x 1.6 (7.76 m) | 61.5 / 72 | 73.4 / 77 | (34, 32, 25) |
| x 2.0 (9.7 m) | 68.9 / 82 | 81.9 / 89 | (43, 38, 32) |

Frames: `_scratch/range_arm/cmp_to_cooler.png` (control, x 1.6, x 2.0) and `cmp_walker.png`.

- The range is the dial for the block, and for the whole store. At x 1.6 the frame's mean rises 60 % and the comps'
  "bright lights" read.
- It is NOT the whole answer for the block. At x 2.0 the gondola end is still the darkest surface in the view, a
  dim brown-grey where its sides are lit. A vertical face that looks toward the storefront takes its lamp light
  from the one row in front of it, at a grazing angle.

The range in `lux.applied.tscn` is also the realtime claim each lamp makes on every dynamic object it reaches (the
per-object 8). A bake-only range, laid before Bake is pressed and restored before the save (the way
`add_bake_fills` lays the rooms' fill), would buy the lightmap's light at no runtime price. That is the candidate,
and it is a Lux change to every interior's look, so it is the walker's to see.

## Shipped: a bake-only range for a supermarket's rows (2026-10-27)

A chain of four releases (`rebuild_1027_versions.txt` names each repo's commit):

- **Deli Counter 0.279.0** stamps a supermarket's sales-floor rows with `bake_reach`, their lamp spacing.
- **Zoo 1.134.0** carries it to each lamp's marker as `lux_bake_reach`.
- **Lux 0.80.0** derives the rig's `bake_range`, `hypot(drop, bake_reach) + 0.75`: 7.61 m here.
- **Level Factory 0.261.0**'s bake lends that range to the static lamps before Bake is pressed, and gives it back
  before the save.

The walker's level, rebuilt on that chain and on Zoo 1.133.0 / Deli Counter 0.278.0's grocery shelves:

- **The bake:** `light_bake.json` reads ok, 228 room fills, `bake_ranges_lent` 39. 40 rigs carry 7.61 m; the one not
  lent is a rig that is not static.
- **The live scene:** 50 lamps at `spot_range = 4.85`, the drop rule, as before. The realtime claim is unchanged.
- **The frames** (`frames/04_rebuilt_on_the_chain.png`): to_cooler 38.5 -> 60.3 mean (p50 41 -> 70), the block
  (1, 1, 7) -> (35, 32, 26); walker_sales 47.6 -> 72.5. These agree with the x 1.6 arm (61.5, (34, 32, 25)), so the
  shipped path does what the arm measured. Down lane 2 the frame reads 87.8 mean, down lane 3 91.1.

NOT PRICED in frame time, and why that is the claim: the shipped scene's live lights are byte-for-byte the ranges they
were, and the lightmap's resolution is unchanged, so nothing the frame submits moved. A price run would measure that
zero. It was not run, and the grocery shelves (Zoo 1.133.0: still two submissions a gondola, about 30,600 triangles
at 14 m against the snack form's 21,660) were not priced either.

## Left

- **The end of a gondola is still the darkest surface in the view.** Now dim grey, and a blank steel panel 2 m tall
  above a 1.5 m end cap. Real stores carry the end display to full height or hang a header there. That is Zoo
  geometry (`snack_gondola_forms`' end cap), not light.
- **The walker's station** (24.4, 1.6, -6.8) has a near object filling the right of its frame, in the control as
  well. It is not this finding's.

## Open

Two different absences give the same black, and neither is measured:

- **Live**: a mesh renders at most `max_lights_per_object` (8) lights, the nearest to it. A 14 m gondola's merged
  steel is one object whose middle is 7 m from its ends.
- **Baked**: the lightmapper should see every static lamp. That the end face bakes black needs its UV2 chart and its
  texels read off `bake.exr`, which no probe here does yet.

Whatever the cause, it is downstream of Zoo, which builds the faces right, and of the material. Superseded by the
section above: the bake reached the face with its fill and not its lamps.
