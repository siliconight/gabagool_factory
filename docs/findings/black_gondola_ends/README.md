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

## Open

Two different absences give the same black, and neither is measured:

- **Live**: a mesh renders at most `max_lights_per_object` (8) lights, the nearest to it. A 14 m gondola's merged
  steel is one object whose middle is 7 m from its ends.
- **Baked**: the lightmapper should see every static lamp. That the end face bakes black needs its UV2 chart and its
  texels read off `bake.exr`, which no probe here does yet.

Whatever the cause, it is downstream of Zoo, which builds the faces right, and of the material. The next probe reads
the face's lightmap texels.
