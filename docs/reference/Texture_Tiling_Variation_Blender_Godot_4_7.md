# Hiding Repeated Texture Tiles in Blender and Godot 4.7

**Purpose:** A practical material and level-building guide for large, reused surfaces in a stylized realistic 3D game. Examples use roads, pavement, walls, and floors, but the same principles apply to terrain and props.

## The problem

A seamless texture can still look repetitive. Its edges may join perfectly, while an identifiable crack, stain, bright stone, or color patch appears every few meters. Increasing resolution does not remove that pattern. Adding undirected noise can merely replace one obvious pattern with another.

Build variation at several scales:

1. **Small scale:** The repeating material supplies grain, aggregate, pores, and small cracks.
2. **Medium scale:** Alternate compatible tile variants or change UV orientation and offset.
3. **Large scale:** A broad, irregular mask changes color, wear, roughness, or material over several meters.
4. **Placed scale:** Decals, painted masks, geometry, and props describe what happened at that location.

For example, a Delco road can reuse one asphalt family across the level while showing tire wear in lanes, darker pavement near a repair cut, oil in a parking bay, faded markings, and dirt along the curb. Those features should follow road use and drainage, not random placement.

## What each technique actually does

| Technique | Use it for | Limitation and cost |
| --- | --- | --- |
| Better source tiles | Removing a conspicuous feature before it repeats | Requires editing or authoring the tile |
| UV offset and 90-degree rotation | Keeping neighboring modular pieces from lining up identically | Does not hide repetition within one large mesh; directional textures may be rotated incorrectly |
| Multiple tile variants | Changing recognizable cracks and stains | Additional textures and samples; variants must have compatible color and scale |
| Broad material mask | Creating patches of wear, dirt, dampness, or repair | Needs art direction; an obvious Voronoi cell pattern can be as distracting as tiling |
| Vertex paint | Putting variation where a human would expect it | Resolution depends on mesh vertex density |
| Decals or small overlay meshes | Placing distinctive events such as leaks, patches, stripes, and scuffs | Draw calls and overdraw can accumulate |
| Triplanar mapping | Projecting onto awkward shapes without stretched UVs | It solves projection, not repetition; several axis samples can increase shader cost |
| Near/far material treatment | Keeping close detail crisp while reducing visible repetition at distance | Requires testing transitions and shader cost |

The Unity tool described in the video combines several of these methods. Its 32-layer capacity is a feature ceiling, not a target for every Godot material. Build a small, measurable material family first.

## 1. Audit the tile in Blender

### Make a repeat test

1. Place the material on a broad plane or wall in Blender.
2. Display at least an 8 × 8 grid of repeats at the intended in-game scale.
3. Inspect it from walking height, from farther away, and in the lighting expected in the level.
4. Mark any feature you can find repeatedly within a second: a dark blotch, a uniquely shaped crack, a bright pebble, an edge gradient, or a strong diagonal line.
5. Fix the source texture or prepare variants before building a sophisticated runtime shader.

**Source-tile rules:** Keep the average color fairly even across opposite edges; avoid one hero crack or isolated stain in the base tile; keep directional structure intentional; check the normal and roughness maps as well as albedo. Repetition can remain visible in highlights even when color variation conceals it.

### Make a small material family

For a common surface, start with two or three variants:

- **A:** Ordinary or cleaner surface.
- **B:** Similar material with a different crack or aggregate distribution.
- **C, if needed:** More worn version, still recognizably the same material.

Variants should match in physical scale, approximate average brightness, and material identity. A blend between asphalt and mud is a different design decision from a blend between two asphalt variants.

Choose a real-world coverage convention for the tile and keep it consistent. As an initial art target, test one asphalt tile over roughly **1–3 m**, then adjust after seeing it at player height. This is a starting range, not a required texel-density standard.

### Plan authoring data separately from runtime shading

Blender can generate procedural noise, masks, vertex colors, and box-projected previews. Bake procedural results to images when Godot needs those exact results, or implement the behavior again in a Godot material. Do not assume an arbitrary Blender node graph will survive glTF import unchanged. Godot's import documentation specifically cautions that procedural Blender materials may not work correctly.

Useful exported data includes:

- UVs for the small repeating material.
- A second UV channel where an object-specific broad mask is more appropriate than world coordinates.
- Vertex colors for hand-painted wear or variation.
- Separate textures for albedo, normal, roughness, and masks as needed.

Godot can import vertex colors, but `StandardMaterial3D` ignores them until **Vertex Color > Use as Albedo** is enabled. For custom blend weights, use a `ShaderMaterial` and read the vertex color deliberately. Godot's native triplanar option is under the material's UV settings; Blender box projection is useful as an authoring preview but is not itself a portable shader.

## 2. Start with Godot's built-in material features

Before writing a custom shader, test a `StandardMaterial3D` on the actual scene:

1. Assign the base albedo, normal, and roughness textures.
2. Adjust **UV1 > Scale** until the texture has believable real-world size.
3. Enable **Detail** and use its secondary albedo or normal input and **Mask** for a controlled accent layer.
4. Try **UV1 > Triplanar** on geometry whose UVs stretch. Enable **World Triplanar** only where continuity across stationary neighboring pieces helps.
5. Inspect the result in motion at near, middle, and far camera distances.

Godot supports detail-mask blending and local or world triplanar mapping in its standard 3D materials. Its **Distance Fade** setting fades the visibility of a material with camera distance; it is not the near/far *texture blending* technique described in the video.

**Do not use world projection indiscriminately on movable props.** If an object moves through world coordinates while its texture stays fixed in the world, the texture can appear to slide across it. Local triplanar or ordinary UVs are usually better there.

## 3. Build a simple broad-scale blend shader

This example is for **horizontal, stationary surfaces** such as a road or large floor. It blends two compatible albedo variants using an irregular mask projected in world space. World coordinates allow a broad stain to continue across separate road meshes; the small texture still uses the meshes' UVs.

```glsl
shader_type spatial;

uniform sampler2D surface_a : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D surface_b : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D broad_mask : filter_linear_mipmap, repeat_enable;

uniform float repeats_per_uv = 4.0;
uniform float mask_size_meters = 12.0;

varying vec3 world_position;

void vertex() {
    world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
    vec2 detail_uv = UV * repeats_per_uv;

    vec3 a = texture(surface_a, detail_uv).rgb;
    vec3 b = texture(surface_b, detail_uv + vec2(0.37, 0.19)).rgb;

    float mask_value = texture(
        broad_mask,
        world_position.xz / mask_size_meters
    ).r;
    float blend_amount = smoothstep(0.3, 0.7, mask_value);

    ALBEDO = mix(a, b, blend_amount);
    ROUGHNESS = mix(0.78, 0.88, blend_amount);
}
```

**What to supply:** `surface_a` and `surface_b` are different seamless variants of the same surface. `broad_mask` is a grayscale, soft-edged, irregular texture with little recognizable structure. `repeats_per_uv` assumes the mesh UVs span roughly 0–1 across the relevant surface; change the UV layout or parameter to achieve a consistent physical tile size. `mask_size_meters` controls the large-scale pattern in Godot world units, assuming the level uses meters.

**Important limitations:** This example blends albedo and simple roughness values only. In production, sample and blend the matching roughness maps and normal maps with the *same* mask, keeping tangent-space handling consistent. A color blend alone will look wrong if the reflected light and surface relief still describe only one material. On walls, `world_position.xz` is the wrong projection: use an appropriate plane, a separate broad-mask UV, or triplanar logic. The shader's three texture samples are a starting cost, not a promise of performance on every target GPU.

## 4. Make the mask follow the place

Use procedural masks for broad distribution, then constrain them with authored or generated context. A useful placement rule is **surface state = base material + environmental cause + local event**.

| Surface | Broad variation | Local event |
| --- | --- | --- |
| Road | Different paving ages and lane wear | Utility repair, pothole patch, faded paint |
| Sidewalk | Dust, damp sections, older concrete | Cracked slab, chewing gum, curb staining |
| Brick wall | Weathering and uneven fading | Drain streak, painted-over sign, repaired mortar |
| Store floor | Traffic wear near entrances and counters | Spill, replacement tile, dragged furniture mark |
| Parking lot | Sun fading and tire wear | Oil near a parked car, painted line, patched trench |

Voronoi noise can divide a surface into irregular regions, but use it as one input to a soft mask. Warp its boundaries, vary region size, and avoid a uniform cell outline. Prefer fewer, meaningful differences over maximal variation everywhere.

For a procedural level builder, save a **stable per-piece seed** and material profile. A road segment can select variant B, a modest UV offset, and a repair-mask location from its seed. Rebuilding the level should produce the same result. Author rules that keep continuity at seams and that place context marks in plausible positions.

## 5. Add a second accent pass

Keep distinctive marks outside the endlessly repeating base texture:

- Use a vertex-color channel or painted mask for broad, soft wear.
- Use a decal or small overlay mesh for a specific patch, spill, stripe, poster residue, or leak.
- Use geometry when the silhouette, edge, or depth should change.
- Keep marks sparse enough that each retains a reason for being there.

For large, frequently visible surfaces, a small mask texture or vertex paint may be cheaper than many overlapping transparent decals. Verify in the target scene; overlapping translucent surfaces can increase GPU work and cause sorting problems. Godot's opaque material path is generally preferable when transparency is unnecessary.

## 6. Treat distance as a separate design problem

At close range, small texture detail is useful. At a distance, repeated bright and dark features can merge into a conspicuous grid. First inspect the texture's mipmapped appearance and ensure its average value is even. Then, if needed, make broad color and material variation carry the distant view while fine detail becomes less prominent.

A custom camera-distance blend can use two **opaque material appearances** within one shader: near detail and a broader far treatment. Fade their contribution smoothly over a tested distance interval. Avoid enabling Godot's transparency-based Distance Fade merely to accomplish this; that setting controls material visibility and can put the material on a more costly transparent path.

## Runtime cost and selection rules

Every added layer can mean more texture reads and shader work. Triplanar projection may require sampling multiple axes for each texture. A many-layer material applied to an entire city block may cost far more than a few authored decals or two compatible tile variants. Actual impact depends on screen coverage, texture size and compression, renderer, hardware, and how many maps each layer samples.

Use this escalation order:

1. Improve the base tile and consistent UV scale.
2. Add stable per-piece variant, rotation where valid, and offset.
3. Add one broad mask blending two material variants.
4. Add selectively placed paint, decals, or mesh detail.
5. Add triplanar mapping where projection is genuinely difficult.
6. Consider texture bombing or more layers only if repetition remains visible and profiling shows room.

Do not assume a 32-layer design is appropriate for a four-player level. Start with a material used in a representative street or interior, measure it on target hardware, and expand only for a visible gain.

## Visual and technical acceptance test

Create a representative test scene: a long road, curb and sidewalk, wall, modular seams, several lights, and a moving player camera. Capture comparable views at walking distance, across the street, and from a high vantage point.

- **Tile test:** A viewer cannot quickly trace the same crack or stain across the large surface.
- **Continuity test:** Physical texture scale stays consistent across adjacent modules; broad world-space variation does not visibly reset at seams.
- **Placement test:** Wear and stains correspond to traffic, water, maintenance, or occupancy rather than arbitrary scatter.
- **Material test:** Albedo, normal, and roughness changes tell the same story under day and night lighting.
- **Motion test:** No obvious texture sliding, shimmering, or abrupt near/far transition.
- **Performance test:** Compare frame time and GPU cost against a one-layer baseline in the same camera views; keep the simpler version when the visual change is negligible.

## References

- [Godot 4.7: Standard Material 3D and ORM Material 3D](https://docs.godotengine.org/en/4.7/tutorials/3d/standard_material_3d.html) — detail masks, UV scaling, triplanar mapping, distance fade, and transparency behavior.
- [Godot 4.7: Spatial shaders](https://docs.godotengine.org/en/4.7/tutorials/shaders/shader_reference/spatial_shader.html) — UVs, vertex color, model transform, and fragment outputs.
- [Godot 4.7: Shading language](https://docs.godotengine.org/en/4.7/tutorials/shaders/shader_reference/shading_language.html) — sampler declarations and texture filtering hints.
- [Godot: Import configuration](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/import_configuration.html) — imported materials and procedural Blender material limitations.
- [Godot: Available 3D formats](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html) — vertex color import behavior.
- [Blender Manual: Image Texture node](https://docs.blender.org/manual/en/4.5/render/shader_nodes/textures/image.html) — box projection and blending between projected sides.
