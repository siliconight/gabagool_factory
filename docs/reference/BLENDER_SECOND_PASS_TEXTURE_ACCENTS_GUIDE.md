---
title: "Second-Pass Texture Accents for Stylized Realism"
subtitle: "An optional Blender accent pass over an existing base coat or texture"
version: "1.0"
date: "2026-10-11"
audience: [environment_artist, technical_artist, procedural_asset_tool, game_engineer]
authoring_baseline: "Blender 4.5 LTS"
runtime_target: "Godot 4.7"
units: "meters; 1 Blender unit = 1 meter"
code_status: "Python syntax checked; not executed inside Blender"
parameter_status: "Suggested art-direction starting points, not measured material standards"
scope: "Second-pass accents only; retain the accepted base coat, textures, and material identity"
pipeline_stage: "after_base_material_review_before_final_bake"
base_material_policy: "preserve"
default_accent_coverage: "zero until an explicit accent mask is provided"
---

# Second-Pass Texture Accents for Stylized Realism

**Use this guide after the base coat or texture is already established and visually accepted.** It defines a second pass that adds selected accents over that base: richer local colors, controlled gradients, small graphics, localized wear, and changes in surface response.

The base material remains the source of the asset's main color, texture, and identity. This pass adds emphasis to chosen areas. It is not the stage for rebuilding the whole material, changing the art style, correcting the mesh, or covering every surface with detail.

“Second pass” describes the production stage. It can contain several editable accent layers; it does not mean exactly one additional image or a second transparent mesh over the whole object.

It is written for an artist or procedural tool working in Blender. The effects remain separately editable, with Python examples for inserting the pass into an existing material and baking the approved combination for the game.

The target is a relatively stylized, believable 3D world: clear shapes at gameplay distance, convincing materials up close, and enough restraint that important objects remain easy to read. Examples use ordinary painted metal, brick, concrete, wood, and signage suited to a 1990s Pennsylvania setting.

**Core rule:** the base carries the object; the second pass adds selected emphasis. Use medium marks and local color transitions to establish that emphasis, then small surface changes to support it up close.

### Where this pass belongs

1. Build the asset and establish its base coat/texture.
2. Review the base material at gameplay distance and accept its main read.
3. **Run this optional accent pass on explicitly chosen regions.**
4. Compare with the accepted base and remove accents that do not help.
5. Bake/export while retaining the editable base and accent layers.

If the asset is missing its main color design, material definition, UV quality, or required geometry, return it to the base-asset stage. Do not use accent noise or gradients to disguise those missing foundations.

## 1. Start here

For one already accepted base material:

1. Preserve its color, roughness, metallic value, and normal input.
2. Write a short accent brief: what should draw attention, where, and why.
3. Paint or generate an accent-permission mask, then choose one intentional effect: a local gradient, repaint patch, stripe, label, contact polish, or localized wear.
4. Use the same placement mask to change the affected material properties coherently.
5. Add small surface relief only inside the selected accent regions and only where the final texture can resolve it.
6. Inspect with moving light and at the actual gameplay camera distance.
7. Keep the authoring layers in the `.blend`; bake permanent effects into game textures.

For a first implementation, read Sections 2–8, copy the reusable script in Section 11, and use the worked example in Section 13. The baking helper follows in Section 15.

### What is supplied

- Specific node recipes and suggested numeric ranges.
- An optional layer group that wraps an existing Principled material.
- A script that generates meaningful placement masks for a door-front example.
- A limited, explicit baking helper for that material setup.
- A machine-readable recipe and integration rules for a procedural asset factory.
- Checks for close-range quality, layering errors, and game-engine export.

### Implementation status

The Python examples target Blender 4.5 LTS API conventions. Their syntax was checked outside Blender. Blender was not available in the authoring environment, so node creation, render appearance, and baking have **not** been runtime-validated here. Run the smoke checks in Section 17 on your installed Blender build before integrating the scripts into a factory. Later Blender releases require the same check; compatibility is not assumed from the version number alone.

## 2. Preserve the ability to add layers when wanted

Treat this as an optional post-base operation. A clean asset may receive a color band, a local gradient, or contact polish with no damage at all.

For an ordinary localized accent pass, a useful initial art-direction target is to leave roughly **70–90% of the visible surface without an obvious added accent**. This is a composition heuristic, not a required mask percentage or a physical rule. A large intentional mural or stripe can justify more coverage. Fine color drift must not make the whole asset look newly retextured.

Every request should specify:

- **Base to preserve:** material/texture identity and any protected graphics or colors.
- **Accent goal:** clearer handle, more readable entrance, a repair patch, a touch of local color, or another concrete purpose.
- **Allowed regions:** an explicit mask or semantic anchors.
- **Allowed channels:** color, roughness, shallow relief, or a justified combination.
- **Amount:** a restrained initial strength and coverage expectation.

Example: “Keep the blue door's base coat. Add a small worn/polished region around the pull handle and one muted faded patch above it. Keep the center panel calm. Preserve the delivery lettering.”

| Requirement | Implementation rule |
| --- | --- |
| Preserve an existing asset | Wrap existing material inputs; retain the original material data-block |
| Enable only on chosen assets | Explicit object and material-slot selection |
| Compare with the original | A master `Enable` value; `0` bypasses added effects |
| Restrict the second pass | An `Accent Mask` limits every added effect; black preserves the base |
| Adjust one effect | Separate strength and placement mask for each effect |
| Repeat a result | Save recipe version, seed, source maps, scale, and layer order |
| Make a new variant | Change a named control or seed without rebuilding the mesh |
| Export efficiently | Bake stable layers; retain runtime layers only when their independence is useful |

Do not silently clear a material, delete UVs, apply modifiers, replace every material slot, or alter all objects sharing the same mesh. The reference attachment function creates an object-local material copy and edits one slot.

With `Enable = 0`, or outside the accent mask, valid incoming color, roughness, metallic, and normal values should match the original material. The reference clamps scalar material values to their valid 0–1 range, so deliberately out-of-range input values are outside its bypass guarantee. The mask defaults to zero; enabling the group alone must not repaint the object.

## 3. What “more colors and gradients” means in practice

More detailed stylized materials benefit from related shades and gradual transitions. The colors should still belong to a material or a visible event.

Use these four kinds of variation separately, applying authored changes only where the accent brief permits them:

1. **Pigment variation:** slight changes within the same paint, brick, or wood.
2. **Condition variation:** fading, dirt, polishing, moisture, or oxidation.
3. **Material changes:** paint revealing primer, primer revealing metal, paper covering paint.
4. **Lighting response:** the renderer's highlights, shadows, and reflections.

The first three can be authored into texture layers. The fourth should respond to the game scene. A sun-facing gradient painted into albedo will remain there after the sun moves; a faded patch can legitimately remain there.

### Example palette for a faded blue-green painted door

These are illustrative sRGB swatches, not measured reflectance values:

| Purpose | Hex | Placement |
| --- | --- | --- |
| Cooler pigment | `#36545D` | Broad, low-contrast patches within intact paint |
| Main paint | `#456B70` | Most of the painted surface |
| Warmer pigment | `#607D78` | Small shifts within the same coating |
| Faded paint | `#849994` | Chosen exposure regions |
| Newer repair paint | `#31565C` | One bounded repaint patch |

In this pass, the existing base texture supplies the main paint. The table illustrates how to choose related accent colors around it; it is not an instruction to replace an established palette.

Start with three to five intentional ramp stops. Interpolation supplies the intermediate colors. A continuous ramp does not require hundreds of manually selected swatches.

For scripted RGB sockets, convert hex sRGB colors into scene-linear values. The reference `srgb_hex()` helper does this for Blender's default working-space assumptions. Do not apply this conversion to numeric masks, roughness, height, or RGB multiplier values. Blender distinguishes display colors from linear rendering and data textures. [B09, B10]

### Useful starting controls

| Effect | Starting control | Adjustment rule |
| --- | --- | --- |
| Broad pigment tint | Mix factor `0.15–0.35` | Reduce if separate patches look like different paint colors |
| Fading toward a related pale color | Mix factor `0.10–0.30`, restricted by a mask | Retain the original material identity |
| Local dirt coloration | Mix factor `0.15–0.45`, restricted by a mask | Raise only where a deposit should be obvious |
| Small roughness variation | About `±0.02–0.06` around the base | Look for a changing reflection, not glitter |
| Bright decorative stripe | Usually a near-opaque color replacement inside its mask | Use wear and fading separately |

These are recipe controls, not universal physical values. Color, light, exposure, and surrounding materials affect the result.

## 4. Separate detail by physical size and viewing distance

Specify the intended size of a mark in meters before choosing a noise scale or image resolution.

| Detail band | Example physical sizes | Job | Typical technique |
| --- | --- | --- | --- |
| Broad | `0.3–2 m` | Gentle variation within a selected large patch | Low-frequency noise, gradients, painted masks |
| Medium | `2–30 cm` | Chips, repairs, stains, labels, scuffs | Authored shapes with limited procedural breakup |
| Fine | `4–12 mm` initially | Paint grain, small pits, chipped boundaries | Low-amplitude bump and roughness variation |
| Very fine | Below the reliable texel footprint | Surface impression | Fold into average roughness or a dedicated detail-texture system |

“Fine” is relative to the asset and final sampling. A camera-close prop can support detail that a background facade cannot.

### Convert feature size into texels

`feature_width_in_texels = feature_width_in_meters × texels_per_meter`

At `512 texels/m`, a `4 mm` scratch is only about `2 texels` wide. At `1024 texels/m`, it is about `4 texels` wide. These are source texture widths; distance, mipmaps, viewing angle, compression, and screen resolution reduce their visible contribution further.

Suggested starting budgets for this style:

- General environment surfaces: try approximately `512 texels/m`.
- Surfaces inspected closely: try approximately `1024 texels/m`, then check the actual camera.
- Small signs or readable labels: allocate resolution for their projected size and text, separately if necessary.
- A roughly `0.9 × 2.1 m` door: `1024 × 2048` can be a useful initial unique texture, with UV packing checked for consistent density. It is not a promise that all close-up detail will survive.

Do not add texture resolution until you have checked whether the missing effect is actually a bevel, a roughness difference, a better mask, or a stronger medium-sized shape.

## 5. Build a layer from properties, not only a color image

A useful layer carries a mask and whichever channels it needs:

| Channel | Meaning | Example |
| --- | --- | --- |
| Base color / albedo | Surface color without scene lighting | Blue paint or cream paper |
| Roughness | How broadly reflections spread | Dust broader; a worn handle narrower |
| Metallic | Metal versus dielectric material response | Bare steel `1`; paint, rust, paper `0` |
| Height or normal detail | Small surface orientation changes | Shallow paint edge or small pit |
| Emission | Self-emitting surface | A lit sign element only when appropriate |
| Mask | Where the layer exists | Scuff region around a handle |

Paint covering a steel door is a dielectric coating: its exposed appearance should generally use metallic `0`. A bare-metal chip can use metallic `1`. Rust is not bare metal. Intermediate values can occur at filtered boundaries; do not set an entire mixed paint-and-metal surface to `0.5` as a shortcut.

### Basic blend operation

For a scalar or color channel:

`result = previous × (1 − mask × strength) + layer × (mask × strength)`

Clamp the effective mask to `0–1`. In Blender, use **Mix** for replacement, or **Multiply** for a controlled tint or darkening operation. A color mix changes material inputs; it does not require making the final mesh transparent. The reference uses `ShaderNodeMix` with explicitly selected color sockets. [B02]

### Suggested roughness targets

These are appearance presets to tune under your lighting, not measurements:

| Surface | Starting roughness |
| --- | --- |
| Satin painted metal | `0.40–0.65` |
| Weathered matte paint | `0.65–0.85` |
| Primer or dry rust | `0.75–0.95` |
| Matte paper | `0.70–0.90` |
| Smooth worn metal | `0.20–0.40` |
| Dry concrete or brick | `0.75–0.95` |
| Thin wet region | `0.10–0.30`, adjusted for the surface beneath |

### Keep normals and heights coherent

- Combine related shallow height fields, then convert them through a **Bump** node.
- Feed the existing shader normal into that Bump node's `Normal` input.
- An existing tangent-space normal image must pass through **Normal Map** first.
- Do not average encoded RGB normal maps using an ordinary color mix and assume the result is correct. Use a normal-combination method designed for vectors if combining runtime normal maps.
- Use geometry for visible silhouette changes, lifted sign corners, thick trim, door recesses, and major chips.

Bump perturbs the shading normal; it does not create actual silhouette thickness. A tangent normal image needs the correct UV basis and Non-Color interpretation. [B05, B11]

## 6. Choose coordinates deliberately

| Coordinate system | Use it for | Main concern |
| --- | --- | --- |
| UV | Signs, labels, unique paint damage, baked maps | UV distortion, overlap, and texel density |
| Object space at known scale | Consistent-size grain and local procedural variation | Applied object scale and parent transforms |
| An Empty as mapping reference | Artist-positioned gradients or stamps | Keep its transform stable and record it |
| World space | Continuous variation across static modules | Moving an object can move it through the pattern |
| Generated | Quick normalized previews | A 1 m and 10 m object can receive the same number of features |

Blender's Generated coordinates span an object's undeformed bounds. Use an explicit UV Map node when a particular UV set is required. [B04]

For the reference script:

- One Blender unit represents one meter.
- Apply object scale before attaching the group.
- Avoid scaled parents and deformation for this first implementation.
- Local Object coordinates drive procedural grain; UV coordinates drive image masks.
- A Noise `Scale` is an approximate spatial-frequency control, not an exact feature-count or millimeter guarantee.

Use a stable per-asset seed. Python's built-in `hash()` is not suitable as a durable cross-process asset seed. A repeatable choice is:

```python
import hashlib

def stable_material_seed(asset_id):
    number = int.from_bytes(hashlib.sha256(asset_id.encode("utf-8")).digest()[:4], "big")
    return (number % 100000) / 100.0
```

Save the seed and recipe version. A seed alone does not guarantee identical procedural noise across different Blender versions.

## 7. Specific Blender node recipes

The sequences below describe node connections. All strengths and dimensions are starting suggestions for a meter-scale asset.

### 7.1 Broad pigment variation

**Use when:** an accepted material needs a local area of richer pigment variation. If the whole asset lacks its main color design, address that in the base pass first.

1. Connect **Texture Coordinate: Object** to **Noise Texture: Vector**.
2. Set a broad Noise Scale around `0.5–3`; start Detail at `1–2`, Distortion at `0`.
3. Connect `Fac` to a **Color Ramp** with three related colors or restrained tint ratios.
4. Use `EASE` interpolation for gradual changes.
5. Mix the result with the base color at a low strength.
6. Intersect it with the explicit accent mask. Do not automatically apply it across the complete material.

Use the scalar noise output to control chosen colors. Avoid using unconstrained random RGB noise as the final color source. Color Ramp maps a scalar field into controlled color transitions. [B03]

**Success:** the paint keeps its accepted base identity; the selected area has useful variation, and unselected areas retain their original appearance.

### 7.2 Directional fading or a broad gradient

**Use when:** a surface should have a deliberate, gradual transition.

1. Establish a mapping frame using Object coordinates or an Empty.
2. Use **Separate XYZ** to select the relevant axis.
3. Use **Map Range** with clamping to map the chosen extent to `0–1`.
4. Shape it with a Color Ramp or Float Curve.
5. Multiply by an exposure mask.
6. Mix toward a related faded color, optionally increasing roughness slightly.

For example, a gradient might run from no fading below `0.6 m` to maximum fading above `1.8 m`. This is an authored exposure approximation. It does not infer which parts were sheltered or how sunlight accumulated over years. Add those decisions to the exposure mask.

Add a small broad disturbance to the gradient if it looks mechanically perfect. Keep the overall direction readable.

### 7.3 Paint bands, stencils, and repaint patches

**Use when:** the environment needs identity, wayfinding, or evidence of maintenance.

- Paint a mask or generate a bounded rectangle/polygon.
- Use a crisp interior with a slightly irregular boundary.
- Mix a deliberate color inside the mask.
- Adjust its roughness separately: newer satin paint can contrast with older matte paint.
- Decide whether underlying texture relief remains visible. Paint follows brick and wood relief; a thick panel can cover it.
- Place old wear below a new repair layer; add later damage above the repair only when the object's history calls for it.

For scripted horizontal bands on a planar surface, threshold the local height between two limits, then perturb the limits by a few millimeters. Use that mask for color and roughness. Avoid displacing the whole band like a thick rubber strip.

### 7.4 Chipped paint with primer and exposed substrate

**Use when:** damage needs to look layered and hold up near the camera.

1. Author a broad **wear candidate mask** near likely contact areas.
2. Multiply that mask by a remapped noise field to break up the boundaries.
3. Create a lower threshold for the larger primer region.
4. Create a higher threshold for the smaller substrate region.
5. Blend paint to primer, then primer to substrate.
6. Use the corresponding masks for roughness and metallic changes.
7. Add a shallow negative height change at each boundary.

Suggested chip widths: roughly `5–40 mm` for visible clustered damage, adjusted for texel density. Suggested combined shading-height range: about `0.05–0.30 mm`, with modest exaggeration if necessary. Those heights are art settings, not a claim about real paint thickness.

The exposed region must remain inside the primer/wear region. A clearly visible bright rim around every chip will look embossed; keep relief restrained and let light determine which edges catch it.

### 7.5 Directional scratches and contact scuffs

**Use when:** a handle, loading edge, or moving part has a clear contact direction.

- Specify the contact location and direction first.
- Build a small set of line segments or elongated masks around that location.
- Vary length more than orientation.
- Group several marks into one scuffed area, with intact material between groups.
- Use a slight color change and/or roughness change; not every scratch needs to reveal metal.
- Keep major scratches wide enough to survive the final texture and mip levels.

A stretched noise field can suggest brushing or grain. For individual scratches, explicit strokes are easier to place and inspect than a global high-frequency noise texture.

### 7.6 Runoff, deposits, and ground grime

**Use when:** an edge, fastener, pipe, splash zone, or puddle provides an origin.

For each runoff source, store an anchor, downward direction, width, and maximum length. Use a narrow cross-streak falloff and a softer fade along its length. Break the shape gently, while keeping it connected to the source.

For ground grime, use a height mask confined to the lower region and intersect it with material/contact rules. A universal dark band at the base of every object quickly becomes repetitive.

Dry deposits usually broaden reflections. Wet grime can narrow them. Choose the material state explicitly rather than routing all dirt into the same roughness value.

### 7.7 Fine paint grain and small pores

**Use when:** broad and medium detail already read well, but close-up material response is too smooth.

1. Use a separate higher-frequency scalar Noise field.
2. Center it around zero by subtracting `0.5`.
3. Apply a small roughness offset.
4. Apply a smaller height amplitude through Bump.
5. Suppress this particular paint grain wherever paint has been removed or thickly covered.

Start with features around `4–12 mm` and apparent relief around `0.02–0.15 mm` for an environment test. True microscopic structure is primarily represented by roughness; do not try to individually resolve every real pore.

**Success:** a grazing light reveals texture, while the front-lit color view stays calm. If it looks like hammered foil or sandpaper, reduce amplitude, frequency, or both.

### 7.8 Paper, signs, stickers, and adhesive remnants

**Use when:** a surface needs human activity or a readable focal feature.

- Use UV placement or an explicit projection transform.
- Feed the image color into a material-color mix and its alpha into the layer mask.
- Match that mask in roughness; a paper sticker should not inherit polished-metal reflection everywhere.
- Decide whether a label conforms to the base relief or covers it with a flatter surface.
- For a thin painted stencil, retain the underlying bump almost entirely.
- For a paper label, reduce the underlying grain where the paper covers it and add subtle paper detail.
- For a lifted corner or a thick sign plate, use a small mesh with real thickness or curvature.

Texture alpha used as a mask inside an opaque shader does not require making the entire door transparent. Geometry cards require a deliberate transparency/cutout choice and careful placement to avoid depth fighting.

### 7.9 Brick, plaster, and concrete variation

- Assign subtle color differences by individual brick, repair patch, or construction section.
- Keep mortar separate from brick color and roughness.
- Add broad aging variation across several bricks, independent of per-brick variation.
- Keep small pores weak enough to avoid turning the facade into speckle.
- Place larger chips at selected edges; use geometry when they affect silhouette.
- Let construction explain boundaries: a repaired square, an old sign footprint, patched cracks, or a different mortar batch.

For a mesh-built brick wall, choose a seeded color per brick/object, then use the same shared material where practical. For a texture-built wall, use a per-cell selector plus a separate broad mask. Do not generate independently random color at every surface point.

### 7.10 Wood and brushed surfaces

- Align grain with the plank or manufacturing direction.
- Use separate mapping transforms for separate boards or parts.
- Combine broad board-to-board color differences with much weaker within-board grain.
- Put worn polish where hands, feet, or objects repeatedly touch.
- Reserve strong knots, splits, and dark stains for selected places.

Anisotropic or elongated texture coordinates can create directionality, but the object's construction determines the direction. One world-space grain orientation for every rotated board is incorrect.

### 7.11 Clean accents that add punch without adding damage

Use these when the asset already looks appropriately maintained:

| Accent | Blender setup | Useful starting point |
| --- | --- | --- |
| Local warm/cool color shift | Bounded mask × broad Noise → controlled Color Ramp → color Mix | `0.10–0.25` mix inside the chosen patch |
| Painted trim or stripe | Geometric/painted mask → color Mix; optional roughness Mix | Keep the interior readable and the color deliberate |
| Contact polish | Soft contact mask → roughness Mix | Lower local roughness by about `0.05–0.15`; inspect reflections |
| Small decorative stencil | Image color + alpha mask → base-color Mix | Preserve the base material's relief beneath the paint |
| Selective edge emphasis | Short authored mask near a chosen bevel → weak color/roughness accent | Keep it broken and subtle; real lighting still creates the highlight |
| Slight local finish change | Mask → roughness-only Mix | Start around `0.05` difference and inspect under moving light |

The reference group implements a subset. Contact-polish and graphic layers are small additional mixes in the copied material; they do not require rebuilding the base shader. Place every extra mix behind the same accent-permission mask. If an extra node sits after the supplied group, also multiply its factor by the master `Enable`, so the complete second pass still has a true bypass.

## 8. Masks: decide the cause before adding breakup

`final_effect_mask = surface_permission × meaningful_placement × shape_breakup × strength`

The meaningful placement mask should do most of the work. Noise should alter shape and variation inside a permitted region.

| Mask source | Best use | Limitation |
| --- | --- | --- |
| Painted grayscale UV image | Exact locations and medium/fine shapes | Requires a useful UV layout |
| Vertex/color attribute | Broad art direction across large meshes | Limited by vertex density and interpolation |
| Distance to tagged anchor | Handles, feet, impacts, fasteners | Requires named semantic anchors |
| Local height/slope | Splash zones, ledges, ground contact | Does not know the object's history |
| Baked curvature/AO | Candidate edges and recesses | Candidate information, not proof of dirt or damage |
| Noise | Shape breakup and low-level variation | Has no knowledge of construction or use |

Useful factory tags include `painted_surface`, `bare_metal`, `hand_contact`, `kick_zone`, `water_origin`, `ground_contact`, `repair_patch`, and `protected_surface`.

Do not assume a curvature or Pointiness result will identify convincing wear on every low-poly mesh. Mesh density, topology, bevels, and render-engine support influence such inputs. Explicit masks are more predictable for this workflow.

### Layer order is part of the asset's history

Example: original paint, fading, damage revealing primer/metal, a new repair patch, a label, then accumulated dust. A different asset may need its sticker underneath a later paint coat.

The supplied group uses this fixed order: base → pigment variation → fading → primer/substrate wear → dirt → fine relief. Its fine paint grain is suppressed on exposed substrate and deposited dirt. Graphics and repairs can be inserted at the appropriate point or handled separately.

## 9. Manual Blender workflow before scripting

1. Confirm the base material is accepted; record its appearance and the accent brief. Check dimensions, units, UV needs, and the intended camera distance.
2. Make a material copy for the chosen asset or slot.
3. Preserve the existing Principled inputs; identify whether they are constants or linked nodes.
4. Build one color mix behind an explicit accent mask. Test the layer at strengths `0`, `0.5`, and `1`, then choose an appropriate strength.
5. Add the corresponding roughness/metallic changes where the effect changes material.
6. Add shallow relief and check it under a large moving light.
7. Add another layer only after the previous one has a clear purpose.
8. Name nodes by effect and expose useful controls in a group.
9. Save the source material, masks, seed, and recipe version before baking.

Use an unlit color inspection to judge palette and placement, then a normally lit inspection to judge surface response. Do not compensate for an overexposed preview by permanently darkening all texture colors.

## 10. Reference group behavior and limits

The script below:

- Preserves incoming color, roughness, metallic, and normal connections.
- Adds broad pigment tint, masked fading, layered paint loss, dirt, and fine paint grain.
- Uses one global switch plus individual controls.
- Defaults all semantic placement masks to zero, so damage and dirt do not appear globally.
- Keeps `Accent Mask = 0` until a mask is supplied, preventing unrequested whole-material changes.
- Copies one material to object-local ownership and starts with `Enable = 0`.
- Reuses its own named group and returns an existing attached group on a repeat call.

It deliberately supports a direct **Principled BSDF → Material Output** surface graph. Mixed shaders, clearcoat-heavy stacks, glass, transmission, subsurface surfaces, and complex layered BSDF trees need a material-specific integration. The example is intended for ordinary opaque metalness/roughness materials.

This is a second-pass accent system. It requires an existing base material and does not automatically infer exposure, generate typography, unwrap a model, find physical contact history, or export arbitrary Blender shader graphs.

## 11. Python: reusable optional surface layers

Save this block as `surface_layers_reference.py`, or paste it into Blender's Text Editor. Running the block defines functions; it does not attach anything until `attach_accent_pass()` is called.

The current group-interface API uses `node_tree.interface.new_socket()`. Socket names are explicitly matched by type for the Mix node because it has separate hidden inputs for different data types. [B01, B02]

```python
"""Second-pass accent reference for Blender 4.5 LTS; run in Blender's Text Editor.
Defines functions only. Call attach_accent_pass() explicitly on the chosen object.
Syntax-checked outside Blender; Blender execution still requires validation.
"""
import math
from pathlib import Path
import bpy

GROUP_NAME = "GF_AccentPass_v1"
OWNER = "gf_accent_pass_v1"


def srgb_hex(value):
    """Hex sRGB to scene-linear RGBA, assuming Blender's default working space."""
    value = value.lstrip("#")
    if len(value) != 6:
        raise ValueError("Expected six hex digits")
    channels = [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + .055) / 1.055) ** 2.4
              for c in channels]
    return (*linear, 1.0)


def build_accent_group():
    existing = bpy.data.node_groups.get(GROUP_NAME)
    if existing:
        if existing.get("owner") != OWNER:
            raise RuntimeError("Group name is already used by unrelated data")
        return existing
    g = bpy.data.node_groups.new(GROUP_NAME, "ShaderNodeTree")
    g["owner"] = OWNER
    specs = [
        ("Base Color", "NodeSocketColor", (.12, .20, .24, 1)),
        ("Base Roughness", "NodeSocketFloat", .65),
        ("Base Metallic", "NodeSocketFloat", 0),
        ("Base Normal", "NodeSocketVector", (0, 0, 1)),
        ("Coordinates", "NodeSocketVector", (0, 0, 0)),
        ("Enable", "NodeSocketFloat", 0),
        ("Accent Mask", "NodeSocketFloat", 0),
        ("Fade Mask", "NodeSocketFloat", 0),
        ("Wear Mask", "NodeSocketFloat", 0),
        ("Dirt Mask", "NodeSocketFloat", 0),
        ("Variation", "NodeSocketFloat", .30),
        ("Fade", "NodeSocketFloat", .20),
        ("Wear", "NodeSocketFloat", 1),
        ("Dirt", "NodeSocketFloat", .35),
        ("Micro", "NodeSocketFloat", .30),
        ("Seed", "NodeSocketFloat", 0),
        ("Macro Scale", "NodeSocketFloat", 2),
        ("Chip Scale", "NodeSocketFloat", 80),
        ("Micro Scale", "NodeSocketFloat", 140),
        ("Fade Color", "NodeSocketColor", srgb_hex("849994")),
        ("Primer Color", "NodeSocketColor", srgb_hex("77756B")),
        ("Substrate Color", "NodeSocketColor", srgb_hex("A4A8AA")),
        ("Substrate Metallic", "NodeSocketFloat", 1),
        ("Dirt Color", "NodeSocketColor", srgb_hex("625849")),
    ]
    unrestricted = {"Seed", "Macro Scale", "Chip Scale", "Micro Scale"}
    for name, kind, default in specs:
        s = g.interface.new_socket(name=name, in_out="INPUT", socket_type=kind)
        s.default_value = default
        if kind == "NodeSocketFloat" and name not in unrestricted:
            s.min_value, s.max_value = 0, 1
        elif name.endswith("Scale"):
            s.min_value, s.max_value = .001, 10000
    for name, kind in [
        ("Color", "NodeSocketColor"), ("Roughness", "NodeSocketFloat"),
        ("Metallic", "NodeSocketFloat"), ("Normal", "NodeSocketVector"),
        ("Exposed Mask", "NodeSocketFloat"),
    ]:
        g.interface.new_socket(name=name, in_out="OUTPUT", socket_type=kind)
    nodes, links = g.nodes, g.links
    gi = nodes.new("NodeGroupInput")
    go = nodes.new("NodeGroupOutput")
    gi.location, go.location = (-1200, 0), (1800, 0)
    sequence = [0]

    def node(kind, label):
        n = nodes.new(kind)
        n.name = n.label = label
        i = sequence[0]
        n.location = (-950 + (i // 7) * 260, 450 - (i % 7) * 210)
        sequence[0] += 1
        return n

    def wire(value, target):
        if hasattr(value, "is_output"):
            links.new(value, target)
        else:
            target.default_value = value

    def calc(operation, a, b=0, label=None, clamp=False):
        n = node("ShaderNodeMath", label or operation)
        n.operation, n.use_clamp = operation, clamp
        wire(a, n.inputs[0])
        wire(b, n.inputs[1])
        return n.outputs[0]

    def product(*values):
        out = values[0]
        for value in values[1:]:
            out = calc("MULTIPLY", out, value)
        return out

    def scalar_mix(a, b, t):
        return calc("ADD", a, product(calc("SUBTRACT", b, a), t))

    def color_mix(a, b, t, mode="MIX", label="Color layer"):
        n = node("ShaderNodeMix", label)
        n.data_type, n.blend_type = "RGBA", mode
        n.factor_mode, n.clamp_factor, n.clamp_result = "UNIFORM", True, False
        # Mix has several hidden A/B sockets. Select by name AND socket type.
        socket = lambda name, kind: next(s for s in n.inputs
                                        if s.name == name and s.type == kind)
        wire(t, socket("Factor", "VALUE"))
        wire(a, socket("A", "RGBA"))
        wire(b, socket("B", "RGBA"))
        return next(s for s in n.outputs if s.type == "RGBA")

    def ramp(value, stops, label, interpolation="EASE"):
        n = node("ShaderNodeValToRGB", label)
        r = n.color_ramp
        r.interpolation = interpolation
        while len(r.elements) > 2:
            r.elements.remove(r.elements[-1])
        r.elements[0].position, r.elements[0].color = stops[0]
        r.elements[1].position, r.elements[1].color = stops[-1]
        for pos, color in stops[1:-1]:
            r.elements.new(pos).color = color
        wire(value, n.inputs["Fac"])
        return n.outputs["Color"]

    def threshold(value, start, end, label):
        return ramp(value, [(start, (0, 0, 0, 1)), (end, (1, 1, 1, 1))], label)

    def noise(scale_name, seed_offset, label):
        n = node("ShaderNodeTexNoise", label)
        n.noise_dimensions = "4D"
        wire(gi.outputs["Coordinates"], n.inputs["Vector"])
        wire(gi.outputs[scale_name], n.inputs["Scale"])
        wire(calc("ADD", gi.outputs["Seed"], seed_offset), n.inputs["W"])
        n.inputs["Detail"].default_value = 2
        n.inputs["Roughness"].default_value = .55
        n.inputs["Distortion"].default_value = 0
        return n.outputs["Fac"]

    i = gi.outputs
    enabled = calc("MULTIPLY", i["Enable"], i["Accent Mask"], clamp=True)
    macro = noise("Macro Scale", 0, "Broad pigment variation")
    chips = noise("Chip Scale", 11.73, "Chip boundary breakup")
    micro = noise("Micro Scale", 29.41, "Fine paint grain")
    # These are scene-linear RGB multipliers, not sRGB color swatches.
    tint = ramp(macro, [(.2, (.68, .88, 1.12, 1)),
                        (.5, (1, 1, 1, 1)),
                        (.8, (1.18, 1.0, .80, 1))], "Restrained tint ratios")
    color = color_mix(i["Base Color"], tint, product(enabled, i["Variation"]),
                      "MULTIPLY", "01 Pigment variation")
    fade = product(enabled, i["Fade"], i["Fade Mask"])
    color = color_mix(color, i["Fade Color"], fade, label="02 Faded paint")
    rough = calc("ADD", i["Base Roughness"], product(fade, .08))
    metallic = i["Base Metallic"]

    # A semantic wear mask sets LOCATION; noise only shapes its boundaries.
    field = product(i["Wear Mask"], calc("ADD", .55, product(chips, .45)))
    primer = product(enabled, i["Wear"], threshold(field, .50, .62, "Primer mask"))
    exposed = product(enabled, i["Wear"], threshold(field, .66, .78, "Metal mask"))
    color = color_mix(color, i["Primer Color"], primer, label="03 Primer")
    color = color_mix(color, i["Substrate Color"], exposed, label="04 Substrate")
    rough = scalar_mix(scalar_mix(rough, .80, primer), .38, exposed)
    metallic = scalar_mix(scalar_mix(metallic, 0, primer),
                          i["Substrate Metallic"], exposed)

    dirt = product(enabled, i["Dirt"], i["Dirt Mask"])
    color = color_mix(color, i["Dirt Color"], dirt, label="05 Deposited dirt")
    rough = scalar_mix(rough, .88, dirt)
    metallic = scalar_mix(metallic, 0, dirt)

    grain_weight = product(enabled, i["Micro"],
                           calc("SUBTRACT", 1, exposed),
                           calc("SUBTRACT", 1, dirt))
    centered_grain = calc("SUBTRACT", micro, .5)
    rough = calc("ADD", rough, product(centered_grain, .12, grain_weight))
    rough = calc("ADD", rough, 0, clamp=True)
    metallic = calc("ADD", metallic, 0, clamp=True)

    # Approximate authoring heights in meters at 1 Blender unit = 1 meter.
    # Bump changes normals; it does not create real silhouette thickness.
    height = calc("ADD", product(primer, -.00018), product(exposed, -.00010))
    height = calc("ADD", height, product(dirt, .00005))
    height = calc("ADD", height, product(centered_grain, .00025, grain_weight))
    bump = node("ShaderNodeBump", "06 Combined shallow relief")
    bump.inputs["Strength"].default_value = 1
    bump.inputs["Distance"].default_value = 1
    wire(height, bump.inputs["Height"])
    wire(i["Base Normal"], bump.inputs["Normal"])
    for name, source in [("Color", color), ("Roughness", rough),
                         ("Metallic", metallic), ("Normal", bump.outputs["Normal"]),
                         ("Exposed Mask", exposed)]:
        links.new(source, go.inputs[name])
    return g


def attach_accent_pass(obj, slot_index=None):
    """Attach to one existing, directly connected Principled material slot.
    Makes an object-local material copy; Enable = 0 and Accent Mask = 0.
    Explicitly provide an accent mask before enabling selected effects.
    """
    if bpy.app.version < (4, 5, 0):
        raise RuntimeError("This reference targets Blender 4.5 or newer")
    if obj is None or obj.type != "MESH" or obj.mode != "OBJECT":
        raise ValueError("Choose a mesh in Object Mode")
    if any(abs(v - 1) > 1e-5 for v in obj.scale):
        raise ValueError("Apply object scale first, or adapt coordinate scaling")
    if not math.isclose(bpy.context.scene.unit_settings.scale_length, 1.0):
        raise ValueError("Reference assumes one Blender unit equals one meter")
    index = obj.active_material_index if slot_index is None else slot_index
    if not (0 <= index < len(obj.material_slots)):
        raise ValueError("An existing material slot is required")
    source = obj.material_slots[index].material
    if source is None or not source.use_nodes:
        raise ValueError("The material must use nodes")
    if source.get("owner") == OWNER:
        found = source.node_tree.nodes.get("GF Accent Pass")
        if found and found.type == "GROUP" and found.node_tree.get("owner") == OWNER:
            return found
        raise RuntimeError("Existing layer material is incomplete; inspect it")
    outs = [n for n in source.node_tree.nodes
            if n.type == "OUTPUT_MATERIAL" and n.is_active_output]
    if len(outs) != 1 or not outs[0].inputs["Surface"].is_linked:
        raise ValueError("Need one active, connected Material Output")
    source_bsdf = outs[0].inputs["Surface"].links[0].from_node
    if source_bsdf.type != "BSDF_PRINCIPLED":
        raise ValueError("Reference supports a direct Principled-to-Output graph")
    group_tree = build_accent_group()
    mat = source.copy()
    mat.name, mat["owner"] = source.name + "_layers", OWNER
    tree = mat.node_tree
    bsdf = tree.nodes[source_bsdf.name]
    group = tree.nodes.new("ShaderNodeGroup")
    group.node_tree, group.name, group.label = group_tree, "GF Accent Pass", "Second-pass surface accents"
    group.location = (bsdf.location.x - 340, bsdf.location.y)
    group.width = 280
    for bsdf_name, input_name, output_name in [
        ("Base Color", "Base Color", "Color"),
        ("Roughness", "Base Roughness", "Roughness"),
        ("Metallic", "Base Metallic", "Metallic"),
        ("Normal", "Base Normal", "Normal"),
    ]:
        target = bsdf.inputs[bsdf_name]
        if target.is_linked:
            old_link = target.links[0]
            tree.links.new(old_link.from_socket, group.inputs[input_name])
            tree.links.remove(old_link)
        elif bsdf_name == "Normal":
            geo = tree.nodes.new("ShaderNodeNewGeometry")
            geo.label = "Preserve original geometric normal"
            tree.links.new(geo.outputs["Normal"], group.inputs[input_name])
        else:
            group.inputs[input_name].default_value = target.default_value
        tree.links.new(group.outputs[output_name], target)
    coords = tree.nodes.new("ShaderNodeTexCoord")
    coords.name = "GF Coordinates"
    coords.location = (group.location.x - 240, group.location.y - 220)
    tree.links.new(coords.outputs["Object"], group.inputs["Coordinates"])
    # OBJECT linking prevents changing materials on other users of the mesh.
    slot = obj.material_slots[index]
    slot.link, slot.material = "OBJECT", mat
    return group


def connect_mask(group, input_name, image_path, uv_name="UVMap"):
    """Connect a separate grayscale, non-color image to a mask input."""
    if input_name not in {"Accent Mask", "Fade Mask", "Wear Mask", "Dirt Mask"}:
        raise ValueError("Unsupported mask input")
    path = Path(bpy.path.abspath(str(image_path)))
    if not path.is_file():
        raise FileNotFoundError(path)
    tree = group.id_data
    uv = tree.nodes.get("GF Mask UV") or tree.nodes.new("ShaderNodeUVMap")
    uv.name, uv.uv_map = "GF Mask UV", uv_name
    name = "GF " + input_name
    tex = tree.nodes.get(name) or tree.nodes.new("ShaderNodeTexImage")
    tex.name = name
    tex.image = bpy.data.images.load(str(path), check_existing=False)
    tex.image.colorspace_settings.name = "Non-Color"
    tex.interpolation, tex.extension = "Linear", "EXTEND"
    tree.links.new(uv.outputs["UV"], tex.inputs["Vector"])
    tree.links.new(tex.outputs["Color"], group.inputs[input_name])
    return tex
```

### Controls worth exposing in a factory UI

| Artist-facing control | Reference input | Meaning |
| --- | --- | --- |
| Enable surface detail | `Enable` | Master blend; zero returns to the base |
| Where accents may appear | `Accent Mask` | Required permission mask; zero preserves the base |
| Color richness | `Variation` | Strength of broad related color shifts |
| Fade amount | `Fade` | Mix toward the chosen faded color |
| Fade location | `Fade Mask` | Authored exposure region |
| Paint loss | `Wear` | Strength of primer/substrate appearance |
| Wear location | `Wear Mask` | Candidate contact/damage region |
| Deposit amount/location | `Dirt`, `Dirt Mask` | Dry deposit appearance in the starter |
| Fine surface texture | `Micro` | Linked small roughness and bump changes |
| Variation seed | `Seed` | Repeatable procedural variation |
| Broad/chip/fine size | Three `Scale` inputs | Approximate procedural frequencies |
| What lies under paint | `Substrate Color`, `Substrate Metallic` | Material-specific exposed surface |

`Wear` changes the strength of an existing pattern; it is not a physical percentage of paint removed. Adjust the placement mask and thresholds when coverage must change. A material-replacement mask usually needs values close to one inside real exposed patches.

## 12. Python: meaningful door masks

This example generates an overall accent mask plus effect masks for a door front approximately `0.9 m` wide and `2.1 m` tall. It selects a handle region, part of the lower edge, a bounded faded patch, and downward streaks beneath hinge locations. The material group adds smaller breakup only inside those permitted regions.

**UV contract:** one rectangular door-front island fills `0–1`; U runs left to right and V runs bottom to top. Use this only on that front material/face layout. It is not a general solution for a packed atlas, multiple door sides, or arbitrary geometry. For a production atlas, rasterize these fields through the asset's actual UV mapping and add island padding.

Mask strengths are deliberately separate from final material strength. The faded patch is an artist-selected example; edit or disable it where the asset's history makes it inappropriate. Remove any unwanted effect from both its effect mask and the overall accent mask so unrelated variation is not left behind in that region.

```python
"""Optional mask generator for ONE rectangular door-front UV island.
U: left to right. V: bottom to top. Island fills 0..1. Units: meters.
This is a placement recipe, not a sun/weather simulator.
"""
import math
from array import array
from pathlib import Path
import bpy


def smoothstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


def door_fields(u, v, width_m=.9, height_m=2.1):
    x, z = u * width_m, v * height_m
    handle = math.exp(-1.8 * (((x - .13) / .10) ** 2
                              + ((z - 1.05) / .19) ** 2))
    lower_edge = 1 - smoothstep(.005, .028, z)
    kick = math.exp(-2 * (((x - .38) / .31) ** 2
                          + ((z - .18) / .12) ** 2))
    wear = max(.98 * handle, .90 * lower_edge, .68 * kick)

    def streak(anchor_x, anchor_z, length=.38, width=.009):
        down = anchor_z - z
        if down < 0 or down > length:
            return 0.0
        return math.exp(-((x - anchor_x) / width) ** 2) * \
            (1 - smoothstep(0, length, down))

    runoff = max(streak(width_m - .035, 1.75),
                  streak(width_m - .035, .55, .32))
    dirt = max(.72 * (1 - smoothstep(.015, .22, z)), .70 * runoff)
    # A deliberately selected faded patch; does not recolor the whole door.
    patch = math.exp(-2 * (((x - .56) / .23) ** 2 + ((z - 1.55) / .33) ** 2))
    fade = .80 * smoothstep(.10, .65, patch)
    accent = max(smoothstep(.04, .22, wear),
                 smoothstep(.05, .25, dirt), smoothstep(.05, .25, fade))
    return {"accent": accent, "wear": wear, "dirt": dirt, "fade": fade}


def write_door_masks(directory, width_px=512, height_px=1024):
    folder = Path(bpy.path.abspath(str(directory)))
    folder.mkdir(parents=True, exist_ok=True)
    paths = {name: folder / ("door_" + name + ".png")
             for name in ("accent", "wear", "dirt", "fade")}
    if any(path.exists() for path in paths.values()):
        raise FileExistsError("Choose a fresh directory; existing masks are preserved")
    buffers = {name: array("f", [0.0]) * (width_px * height_px * 4)
               for name in paths}
    for y in range(height_px):
        for x in range(width_px):
            # Blender image buffers use a bottom-left origin, matching these UVs.
            fields = door_fields((x + .5) / width_px, (y + .5) / height_px)
            offset = 4 * (y * width_px + x)
            for name, value in fields.items():
                buffers[name][offset:offset + 4] = array("f", [value, value, value, 1])
    for name, path in paths.items():
        image = bpy.data.images.new("GF_Door_" + name, width_px, height_px,
                                    alpha=False, float_buffer=False)
        try:
            image.colorspace_settings.name = "Non-Color"
            image.pixels.foreach_set(buffers[name])
            image.update()
            image.filepath_raw, image.file_format = str(path), "PNG"
            image.save()
        finally:
            bpy.data.images.remove(image)
    return {name: str(path) for name, path in paths.items()}
```

For other assets, replace `door_fields()` with the asset's local coordinates and semantic anchors. A tabletop needs hand/plate/edge regions; a loading dock needs pallet paths and impact edges; a concrete wall needs runoff sources and ground conditions.

## 13. Worked example: add detail to an existing painted door

Preparation:

1. Save the `.blend` file.
2. Select the intended door-front mesh in Object Mode.
3. Apply object scale intentionally; use one Blender unit per meter and no scaled parent.
4. Use a direct Principled material for the painted front. Give hardware its own material/mesh.
5. Prepare the UV layout described in Section 12 and name it `UVMap`.
6. In Blender's Scripting workspace, create a new Text block. Paste the Section 11 script, then the Section 12 script, then the invocation below into that same Text block, in that order. Run it once.

```python
if not bpy.data.filepath:
    raise RuntimeError("Save the .blend file before using // relative paths")

door = bpy.context.object
layer = attach_accent_pass(door)
mask_paths = write_door_masks("//texture_layers/door_variant_01/masks")
connect_mask(layer, "Accent Mask", mask_paths["accent"], "UVMap")
connect_mask(layer, "Wear Mask", mask_paths["wear"], "UVMap")
connect_mask(layer, "Dirt Mask", mask_paths["dirt"], "UVMap")
connect_mask(layer, "Fade Mask", mask_paths["fade"], "UVMap")

layer.inputs["Seed"].default_value = 52.25
layer.inputs["Variation"].default_value = .30
layer.inputs["Fade"].default_value = .20
layer.inputs["Wear"].default_value = 1.0
layer.inputs["Dirt"].default_value = .35
layer.inputs["Micro"].default_value = .30
layer.inputs["Enable"].default_value = 1.0

# Compare the complete stack against the preserved base:
# layer.inputs["Enable"].default_value = 0.0
```

Choose a new mask directory for another variant; the generator refuses to overwrite existing masks. To revise an existing variant, edit its masks deliberately or reconnect replacement images.

For later parameter tweaks, use the already attached group's inputs or call `attach_accent_pass(door)` to retrieve it. Do not rerun mask generation into the same folder unless you have deliberately changed the generator's overwrite policy.

### Adjust in this order

1. Set `Micro = 0` and temporarily set `Wear = Dirt = 0`.
2. Adjust local variation and fading until the intended accent reads while the base remains recognizable.
3. Enable wear and inspect its location. Edit the mask before increasing detail.
4. Enable dirt and check that it follows contact and runoff.
5. Add a stripe or graphic using its own mask and material properties.
6. Restore fine grain and keep it weak enough to support the larger design.
7. Compare at gameplay distance and near the handle.

To keep a particular area clean, paint black into `Accent Mask`. To preserve broad variation while protecting only against damage, edit `Wear Mask` instead.

## 14. Bake layers without losing the authoring system

Maintain two representations:

- **Authoring:** the editable material group, source masks, graphics, settings, and recipe in the `.blend`.
- **Runtime:** the smallest suitable set of maps/material operations for the game.

Baking a final map does not require deleting its source layers. You can return to the source, change a mask, and rebake.

### Baking contract

1. Use a deliberate UV layout with no unintended overlaps.
2. Finalize the exported mesh topology, smoothing, UVs, and triangulation before the final tangent-normal bake.
3. Keep the topology and tangent basis consistent when importing into the engine.
4. Make the intended Image Texture node active in each material being baked.
5. Bake color without lighting; store roughness and metallic as linear scalar data.
6. Bake normals in tangent space with the orientation expected by the target engine.
7. Use padding around islands and inspect the result at lower mip levels.

Blender's bake destination is the active image texture node (or the configured color attribute target). Cycles supports emission and normal baking; emission routing is useful for extracting a specific shader input without scene lighting. [B06, B07]

### Why this helper uses an emission pass for color and scalar maps

It temporarily connects the final Principled color or scalar input to an Emission shader in a disposable material copy. That extracts the selected property, including later color/roughness accent mixes, without the lighting contribution or metalness-dependent diffuse behavior. The exposed-mask debug output comes from the group. Normal baking restores the actual surface shader first.

Do not bake the beauty render or Combined pass into albedo for this workflow. That would commit the preview's light, shadows, and reflections to the texture.

### Recommended output interpretation

| Output | Color-space interpretation | Use |
| --- | --- | --- |
| `base_color.png` | sRGB color | Final painted color, no intentional scene-light bake |
| `roughness.png` | Non-Color / linear data | Inspection and repacking |
| `metallic.png` | Non-Color / linear data | Inspection and repacking |
| `normal.png` | Non-Color / normal map | Tangent-space surface orientation |
| `exposed_mask.png` | Non-Color / linear data | Debugging or selected runtime variation |
| `orm.png` | Non-Color / linear data | R: AO; G: roughness; B: metallic |

The helper writes `R = 1` in ORM, meaning **no additional AO contribution**. It does not claim to bake ambient occlusion. Bake AO separately if required and pack that result into red; inspect for double-darkening with other occlusion systems.

Use image saving that preserves the intended color/data interpretation. The helper uses `image.save()`, not a deliberately view-transformed beauty export. Check a known scalar swatch such as `0.5` after export/import to catch color-space mistakes. [B09, B10]

The examples use 8-bit image buffers for a straightforward initial game-texture workflow. If a broad gradient bands, first inspect lighting, compression, and color interpretation. Use a higher-precision intermediate/export route when needed, and recheck the final runtime format.

## 15. Python: limited baking helper

This helper handles one material slot, one active UV layout, no live render modifiers, and the supplied layer group. It creates a disposable object/mesh/material copy, restores the original selection and render settings, and refuses to overwrite an existing output directory.

It does **not** perform high-poly-to-low-poly projection. For that workflow, set up selected-to-active baking, cage/ray distances, and a tangent-compatible export mesh explicitly. Multi-material assets require a baker that selects a target node in every participating material.

If a bake fails, the new output folder may contain partial files. Treat that folder as incomplete and use a fresh output folder for the next attempt.

```python
"""Bake the reference layer group from a disposable duplicate in Blender.
Deliberately limited to one material, one non-overlapping active UV layout,
and evaluated geometry already prepared for export. Does not export glTF.
"""
from array import array
from pathlib import Path
import bpy


def bake_accent_maps(obj, output_dir, width=1024, height=2048, margin=16):
    if obj is None or obj.type != "MESH" or obj.mode != "OBJECT":
        raise ValueError("Choose one mesh in Object Mode")
    if len(obj.material_slots) != 1 or obj.active_material is None:
        raise ValueError("Reference baker supports exactly one material slot")
    if not obj.data.uv_layers.active:
        raise ValueError("An active, non-overlapping UV map is required")
    if any(mod.show_render for mod in obj.modifiers):
        raise ValueError("Use an export duplicate with modifiers evaluated/applied first")
    source = obj.active_material
    if not source.use_nodes or source.node_tree.nodes.get("GF Accent Pass") is None:
        raise ValueError("Attach the reference GF Accent Pass group first")
    folder = Path(bpy.path.abspath(str(output_dir)))
    folder.mkdir(parents=True, exist_ok=False)
    scene = bpy.context.scene
    old_engine, old_samples = scene.render.engine, scene.cycles.samples
    old_active = bpy.context.view_layer.objects.active
    old_selected = list(bpy.context.selected_objects)
    temp = mesh = material = None
    images, files = {}, {}
    try:
        # Copy before touching nodes, UV flags, or material slots.
        temp = obj.copy()
        mesh = obj.data.copy()
        temp.data = mesh
        material = source.copy()
        # Link early so cleanup can always remove the temporary object.
        scene.collection.objects.link(temp)
        temp.name = "GF_BakeTemporary"
        temp.hide_render = False
        temp.hide_viewport = False
        temp.hide_set(False)
        temp.hide_select = False
        temp.material_slots[0].link = "OBJECT"
        temp.material_slots[0].material = material
        mesh.uv_layers.active.active_render = True
        for selected in list(bpy.context.selected_objects):
            selected.select_set(False)
        temp.select_set(True)
        bpy.context.view_layer.objects.active = temp
        scene.render.engine, scene.cycles.samples = "CYCLES", 32
        tree = material.node_tree
        layer = tree.nodes["GF Accent Pass"]
        output = next(n for n in tree.nodes
                      if n.type == "OUTPUT_MATERIAL" and n.is_active_output)
        original_surface = output.inputs["Surface"].links[0].from_socket
        bsdf = output.inputs["Surface"].links[0].from_node
        if bsdf.type != "BSDF_PRINCIPLED":
            raise ValueError("Baker expects a direct Principled surface output")
        emit = tree.nodes.new("ShaderNodeEmission")
        emit.inputs["Strength"].default_value = 1
        target = tree.nodes.new("ShaderNodeTexImage")
        target.label = "Temporary bake destination; never sampled"

        def destination(name, color=False):
            image = bpy.data.images.new("GF_Bake_" + name, width, height,
                                        alpha=False, float_buffer=False)
            image.colorspace_settings.name = "sRGB" if color else "Non-Color"
            images[name] = image
            target.image = image
            for node in tree.nodes:
                node.select = False
            target.select, tree.nodes.active = True, target
            return image

        def save(name):
            image = images[name]
            path = folder / (name + ".png")
            image.filepath_raw, image.file_format = str(path), "PNG"
            # save(), not save_render(): no deliberate display-look baking.
            image.save()
            files[name] = str(path)

        for name, socket_name in [("base_color", "Base Color"),
                                  ("roughness", "Roughness"),
                                  ("metallic", "Metallic"),
                                  ("exposed_mask", None)]:
            destination(name, color=(name == "base_color"))
            for link in list(emit.inputs["Color"].links):
                tree.links.remove(link)
            if socket_name is None:
                tree.links.new(layer.outputs["Exposed Mask"], emit.inputs["Color"])
            else:
                # Read final Principled inputs, including any later accent nodes.
                incoming = bsdf.inputs[socket_name]
                if incoming.is_linked:
                    tree.links.new(incoming.links[0].from_socket, emit.inputs["Color"])
                else:
                    value = incoming.default_value
                    emit.inputs["Color"].default_value = \
                        (value, value, value, 1) if isinstance(value, (int, float)) else value
            tree.links.new(emit.outputs[0], output.inputs["Surface"])
            result = bpy.ops.object.bake(type="EMIT", margin=margin,
                                         use_clear=True, use_selected_to_active=False,
                                         target="IMAGE_TEXTURES")
            if "FINISHED" not in result:
                raise RuntimeError("Bake did not finish: " + name)
            save(name)

        tree.links.new(original_surface, output.inputs["Surface"])
        destination("normal")
        result = bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT",
                                     normal_r="POS_X", normal_g="POS_Y", normal_b="POS_Z",
                                     margin=margin, use_clear=True,
                                     use_selected_to_active=False, target="IMAGE_TEXTURES")
        if "FINISHED" not in result:
            raise RuntimeError("Normal bake did not finish")
        save("normal")

        # ORM uses linear scalar data: R = no extra AO, G = roughness, B = metallic.
        count = width * height * 4
        rough = array("f", [0.0]) * count
        metal = array("f", [0.0]) * count
        packed = array("f", [0.0]) * count
        images["roughness"].pixels.foreach_get(rough)
        images["metallic"].pixels.foreach_get(metal)
        for index in range(0, count, 4):
            packed[index:index + 4] = array("f", [1, rough[index], metal[index], 1])
        orm = destination("orm")
        orm.pixels.foreach_set(packed)
        orm.update()
        save("orm")
        return files
    finally:
        scene.render.engine, scene.cycles.samples = old_engine, old_samples
        if temp is not None:
            bpy.data.objects.remove(temp, do_unlink=True)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)
        if material is not None and material.users == 0:
            bpy.data.materials.remove(material)
        for image in images.values():
            if image.users == 0:
                bpy.data.images.remove(image)
        for selected in old_selected:
            if bpy.context.view_layer.objects.get(selected.name) is selected:
                selected.select_set(True)
        bpy.context.view_layer.objects.active = old_active
```

After loading the helper, select the prepared one-material bake object and run:

```python
files = bake_accent_maps(
    bpy.context.object,
    "//texture_layers/door_variant_01/baked_v01",
    width=1024,
    height=2048,
    margin=16,
)
print(files)
```

Sixteen pixels is a starting padding amount for this example, not a universal mip-safe value. Island spacing, target mip levels, texture size, and compression determine the necessary padding. A bake margin cannot repair overlapping islands or insufficient space between them.

## 16. Export and use in Godot

Blender shader-node graphs do not transfer wholesale into glTF or Godot. The glTF exporter constructs supported materials from node patterns it recognizes. Bake the procedural stack, then make a straightforward export material from the resulting images, or rebuild the desired live operations in Godot. [B08]

### Stable surfaces

For frequently reused environment assets:

1. Preserve the authoring `.blend`.
2. Create a simple export material using the baked base color, normal, roughness, and metallic data.
3. In Godot, use the correct color/normal/data interpretation for each map.
4. If using `ORMMaterial3D`, supply the packed ORM map.
5. Use Godot's expected OpenGL-style tangent normals: X+, Y+, Z+.

Godot documents normal mapping as a shading-detail operation and defines ORM channel packing. Its normal convention matters when exchanging maps with other tools. [G01]

### Layers that remain independent in the level

| Need | Runtime option |
| --- | --- |
| Independently placed labels, stains, or marks | Decals or suitable small meshes |
| One extra color/normal detail layer | `StandardMaterial3D` Detail with a mask |
| Multiple independent property layers | A purpose-built `ShaderMaterial` |
| Different colors on many instances | A constrained runtime tint/parameter scheme |
| Large stable combinations | Bake to a shared texture/material where appropriate |

Godot's standard Detail feature supplies secondary albedo/normal detail and a mask; it is not an arbitrary authoring layer stack. [G01]

Decals can override selected PBR properties, but have renderer and performance constraints. Godot 4.7 documentation lists Forward+ and Mobile support; Compatibility needs an alternative for this use. Keep decal projection volumes tight and use distance fading where appropriate. [G02]

### Performance decisions

- Authoring layer count does not need to equal runtime shader layer count.
- Many unique baked variants increase texture memory and can fragment material reuse.
- Multiple transparent sheets covering a whole wall create overdraw and sorting problems.
- Bake permanent small marks together where their independent placement is no longer useful.
- Retain unique signs or event-driven marks separately when that flexibility is valuable.
- Keep repeatable grain in shared detail textures if that suits the rendering budget.
- Profile the actual scene; do not assign a universal “free decal” or “free layer” allowance.

For scale, three uncompressed `1024 × 2048` RGBA8 textures with a complete mip chain occupy roughly `32 MiB` together. This is a planning example before compression, not a claim about Godot's final formats or actual allocation.

## 17. Validation that proves the layers are useful

### Blender script smoke check

Run this once on a duplicate test asset in the installed Blender version:

1. Record `bpy.app.version_string` and the recipe version.
2. Attach the group; confirm the original material remains available.
3. Set `Enable = 0`; compare color, roughness, metallic, and normal response with the base.
4. Set `Enable = 1` while `Accent Mask = 0`: the appearance should remain unchanged. Then supply a bounded accent mask; broad/fine changes should occur only inside it.
5. Feed a simple black/white image to one mask; confirm that effect follows the correct UV region.
6. Set `Accent Mask = 0`; all added effects should disappear there.
7. Run `attach_accent_pass()` again; confirm no second layer group is inserted.
8. Confirm an unrelated object sharing the original mesh/material did not change.
9. Bake the simple test asset; inspect each map independently before importing.

### Visual acceptance

| Check | Pass condition |
| --- | --- |
| Across the room | Main color, graphic, and silhouette remain clear |
| Normal gameplay distance | Medium wear and repairs read as intentional shapes |
| Close inspection | Material changes and shallow relief support the color detail |
| Moving light | Highlights and apparent relief respond to light direction |
| Quiet areas | Intact material occupies enough space for accents to stand out |
| Wear placement | Contact marks, runoff, and deposits have identifiable causes |
| Layer boundaries | Color, roughness, metallic, and relief agree about what material is present |
| Camera movement | Fine patterns remain stable enough for gameplay |
| Bypass comparison | Each enabled effect provides a useful improvement |
| Engine import | No unexpected inverted normals, washed masks, stretched graphics, or bake seams |

Check at the game's actual resolution, field of view, antialiasing, texture filtering, and compression settings. A close Blender render alone does not establish runtime quality.

### Troubleshooting

| Symptom | Likely cause | First correction |
| --- | --- | --- |
| Surface looks dusty everywhere | Global mask or excessive fine contrast | Restrict placement; lower micro strength |
| Every edge is equally damaged | Curvature/edge mask used as a final result | Add contact/history masks and quiet regions |
| Material looks like plastic | Roughness, metalness, normal strength, or lighting mismatch | Inspect each channel independently |
| Chips look like raised stickers | Height sign or amplitude is wrong | Lower/remove relief; verify negative paint-loss height |
| Paint looks metallic | Metallic map follows the object substrate globally | Set intact paint to zero; expose metal only through wear |
| Colors change badly on import | Color-space, tone-mapping, or lighting mismatch | Verify sRGB versus data maps under neutral lighting |
| Gradient bands | Precision, compression, or excessive grading | Check source precision and final import settings |
| Scratches shimmer | Features are too small or strong for their projection | Widen/reduce them; use mipmaps and appropriate filtering |
| Lettering is stretched | UV aspect or projection mismatch | Correct placement in world dimensions |
| Wear floats away from the handle | Wrong UV layout or coordinate space | Visualize the mask and verify the anchor contract |
| Grain changes size per object | Generated coordinates or unapplied scale | Use a consistent measured coordinate scheme |
| Bake is black/incorrect | Wrong active target, wrong surface connection, missing UV | Verify the minimal bake setup before adding complexity |
| Normals have seams | UV/tangent/topology mismatch or inadequate padding | Align bake and export mesh; inspect tangent convention |

## 18. Machine-readable recipe for a procedural tool

This is an example input contract. A factory adapter must implement the mapping to the supplied functions; pasting JSON alone does not execute it.

```json
{
  "schema": "surface_accents_recipe_v1",
  "pass_type": "post_base_material_accent",
  "base_material_policy": "preserve",
  "base_review_state": "accepted",
  "accent_goal": "Local handle emphasis and one muted faded patch; retain the blue base coat",
  "protected_regions": ["delivery lettering", "separate handle hardware"],
  "asset_id": "delco_service_door_01",
  "recipe_version": "1.0",
  "blender_baseline": "4.5",
  "enabled": true,
  "material_slot": 0,
  "style": "stylized_realism",
  "coordinates": {
    "procedural_space": "object",
    "meters_per_blender_unit": 1.0,
    "require_applied_scale": true,
    "mask_uv": "UVMap"
  },
  "group": "GF_AccentPass_v1",
  "group_inputs": {
    "Enable": 1.0,
    "Seed": 52.25,
    "Variation": 0.30,
    "Fade": 0.20,
    "Wear": 1.0,
    "Dirt": 0.35,
    "Micro": 0.30,
    "Macro Scale": 2.0,
    "Chip Scale": 80.0,
    "Micro Scale": 140.0,
    "Substrate Metallic": 1.0
  },
  "mask_images": {
    "Accent Mask": "masks/door_accent.png",
    "Fade Mask": "masks/door_fade.png",
    "Wear Mask": "masks/door_wear.png",
    "Dirt Mask": "masks/door_dirt.png"
  },
  "export": {
    "mode": "baked_pbr",
    "size_px": [1024, 2048],
    "normal_convention": "opengl_tangent",
    "orm_channels": ["ao_or_one", "roughness", "metallic"],
    "preserve_authoring_layers": true
  }
}
```

### Factory validation rules

- Reject unknown group inputs; do not silently ignore misspellings.
- Resolve paths relative to the recipe's own directory.
- Require matching UV and coordinate assumptions.
- Require an accepted base material and an explicit accent goal before enabling the pass.
- Require an accent-permission mask; do not silently substitute a full-white mask.
- Clamp artist strength controls to `0–1`; validate positive texture frequencies separately.
- Require nonzero placement masks before applying wear, dirt, or localized fading.
- Record the actual Blender build and bake settings alongside outputs.
- Include source-image hashes and the layer-group version in rebuild/cache keys.
- Invalidate a bake when topology, UVs, tangents, material settings, masks, or relevant transforms change.
- Do not rebuild or overwrite the author's original material for a variation request.
- If `enabled` is false, leave the asset untouched or set an already attached group's `Enable` to zero.
- Treat missing assets or unsupported material graphs as explicit errors, not permission to replace them with generic materials.

## 19. Recommended presets by material

Use these as different recipes, not one universal noise setup:

| Material | Prioritize | Keep restrained |
| --- | --- | --- |
| Painted metal door | Broad pigment shifts, handle wear, separate substrate response | Whole-surface rust and high-frequency pitting |
| Brick wall | Per-brick palette, mortar separation, broad stains and repairs | Random saturated bricks and strong pore contrast |
| Concrete | Large tonal variation, form/repair history, selected chips | Uniform dark cracks and noisy normal maps |
| Painted wood | Directional grain, coat wear, board boundaries | Grain visible equally through every coating |
| Plastic machine casing | Subtle color variation, contact polish, labels | Metallic response and stone-like roughness |
| Paper/enamel signage | Readable graphics, print fading, correct matte/satin response | Damage that competes with the message |

For an initially clean asset, start with a selected local color or material-response accent. Add history layers only when the accent brief calls for them. The accepted base coat stays dominant, and an asset can pass review with no second-pass accents at all.

## 20. Primary references

Checked on 2026-10-11. These establish node/API behavior and pipeline requirements. The suggested palettes, masks, strengths, physical feature sizes, acceptance checks, and Python integration are original implementation guidance, not vendor-prescribed presets. Some retrieved Blender manual pages use a localized URL while retaining the relevant English technical content.

- **B01 — Blender 4.5 Python API: NodeTreeInterface.** Group input/output socket creation. https://docs.blender.org/api/4.5/bpy.types.NodeTreeInterface.html
- **B02 — Blender 4.5 Python API: ShaderNodeMix.** Data types, blend mode, and clamping. https://docs.blender.org/api/4.5/bpy.types.ShaderNodeMix.html
- **B03 — Blender 4.5 Manual: Color Ramp.** Mapping scalar values to colors. https://docs.blender.org/manual/uk/4.5/render/shader_nodes/converter/color_ramp.html
- **B04 — Blender 4.5 Manual: Texture Coordinate.** Object, Generated, and UV coordinate behavior. https://docs.blender.org/manual/en/4.5/render/shader_nodes/input/texture_coordinate.html
- **B05 — Blender 4.5 Manual: Bump.** Height, distance, strength, and normal input. https://docs.blender.org/manual/sr/4.5/render/shader_nodes/vector/bump.html
- **B06 — Blender 4.5 Manual: Render Baking.** Targets, passes, normals, and selected-to-active workflow. https://docs.blender.org/UATEST/manual/en/4.5/render/cycles/baking.html
- **B07 — Blender 4.5 Python API: BakeSettings.** Bake configuration and normal-space settings. https://docs.blender.org/api/4.5/bpy.types.BakeSettings.html
- **B08 — Blender Manual: glTF 2.0.** Supported node patterns and texture export. https://docs.blender.org/manual/en/4.4/addons/import_export/scene_gltf2.html and https://docs.blender.org/manual/sl/4.5/addons/import_export/scene_gltf2.html
- **B09 — Blender 4.5 Manual: Color Management.** Linear rendering and display transforms. https://docs.blender.org/manual/sr/4.5/render/color_management.html
- **B10 — Blender 4.5 Manual: Image Settings.** Color/data interpretation. https://docs.blender.org/manual/id/4.5/editors/image/image_settings.html
- **B11 — Blender 4.5 Manual: Normal Map.** Tangent-space normals and Non-Color input. https://docs.blender.org/manual/id/4.5/render/shader_nodes/vector/normal_map.html
- **B12 — Blender 4.5 Manual: Shader Nodes Introduction.** Procedural nodes and reusable groups. https://docs.blender.org/manual/en/4.5/render/shader_nodes/introduction.html
- **G01 — Godot 4.7: Standard Material 3D and ORM Material 3D.** Material channels, normal convention, and Detail layer. https://docs.godotengine.org/en/4.7/tutorials/3d/standard_material_3d.html
- **G02 — Godot 4.7: Using Decals.** Placement, material properties, renderer support, and cost considerations. https://docs.godotengine.org/en/4.7/tutorials/3d/using_decals.html
