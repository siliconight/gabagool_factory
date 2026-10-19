# Baked Lighting for Procedural Levels
## A practical production guide for Blender and Godot 4.7

```yaml
document_type: technical_art_and_pipeline_guide
document_version: 1.0
target_engine: Godot 4.7
asset_authoring: Blender
primary_use: levels_generated_in_editor_or_during_content_production
game_context: four_player_cooperative_PvE_heists
visual_goal: readable_stylized_realism_with_economical_geometry
recommended_baseline: baked_static_environment_plus_selected_realtime_lights
runtime_lightmap_baking: unsupported_by_standard_Godot_LightmapGI
verification_status: documentation_checked_not_engine_executed
reference_check_date: 2026-10-19
```

**Production direction:** Give the level generator responsibility for lighting as well as geometry. Assemble a believable space, decide which parts can change during play, prepare the static surfaces, and bake their lighting in the completed layout. Keep the resulting lightmaps with that exact layout and lighting scenario.

This guide turns the Half-Life 2 lighting example into requirements for an asset creator, level assembler, lighting pass, and build validator. It proposes a workflow; it does not claim that the supplied settings have been benchmarked in your project. Numeric ranges are starting experiments, not engine limits or industry standards.

## 1. What the Half-Life 2 example teaches

Source uses a compilation stage called VRAD to calculate lighting and store lighting data in a compiled map. Its lightmapped surface materials combine a base texture with separately stored illumination. That separation lets the same brick or plaster image appear differently in a sunny courtyard, under an awning, or beside a colored wall. [S1–S2]

The useful lesson is that **lighting describes the relationships between surfaces**. A bright opening illuminates a floor. That floor returns some light toward the ceiling. An adjacent wall lends a little of its color to the light it reflects. Recesses become darker because less light reaches them. These relationships make simple architecture feel solid and connected. [S3]

Baked lighting is one contributor to Half-Life 2's appearance. Composition, coherent materials, restrained color, proportions, silhouettes, and purposeful set dressing also matter. A bake cannot correct arbitrary layouts or poor art direction.

### 1.1 Radiosity and lightmaps are different concepts

Radiosity describes diffuse light exchange between surfaces. A lightmap is a way to store precomputed lighting. Different baking algorithms can produce lightmaps; adopting Godot's LightmapGI does not mean reproducing Source's radiosity implementation.

For this pipeline, the important result is precomputed, spatially coherent indirect illumination rather than a particular historical solver.

### 1.2 Why a shadow survives when a texture is removed

Replacing a wall's patterned base texture with a neutral, **lit** material changes its appearance without deleting its lightmap or the geometry blocking the light. A window-frame shadow can remain visible.

Two qualifications matter:

- This is not proof by itself that lighting is baked. A real-time shadow also survives a base-texture replacement.
- Separate storage does not mean complete independence. Surface colors influence bounced light during the bake. Repainting a red wall white can leave stale red bounce on nearby surfaces until lighting is rebaked. [S3]

Deleting a baked occluder after the bake can also leave its old shadow behind. That is stale data, not successful dynamic lighting.

## 2. The lighting layers the tool must understand

| Layer | What it represents | Pipeline responsibility |
| --- | --- | --- |
| Base color / albedo | Surface color and pattern, such as painted plaster or brick | Keep reusable textures free of strong scene-specific directional shadows |
| Direct illumination | Light reaching a surface from a sun, lamp, or other source | Decide per source whether direct lighting must react during play |
| Indirect diffuse illumination | Light reflected between surfaces | Bake for fixed environments; choose another strategy when the environment changes substantially |
| Ambient occlusion | Reduced ambient accessibility around contacts and crevices | Use as restrained local grounding; it does not provide bounced light |
| Specular reflection | View-dependent highlights and reflected surroundings | Configure roughness and an appropriate reflection source |
| Emission | A surface's apparent self-illumination | Decide separately whether its light contribution is fixed or changes |
| Exposure / tone mapping | How scene brightness becomes a displayed image | Lock a reproducible baseline before judging lighting |

Useful conceptual approximation for a diffuse surface:

```text
surface appearance ≈ albedo × (direct illumination + indirect illumination)
                   + specular response + emission
```

This is an explanatory relationship, not Godot shader code. Actual rendering also involves material models, visibility, directional information, color space, and display processing.

**Do not compensate for missing indirect light by making every material emissive or flooding every room with uniform ambient light.** Those choices hide the geometry-dependent variation the bake is intended to create.

## 3. Choose the generation model before implementing the baker

Godot 4.7's standard LightmapGI baking is an editor feature. An exported game can display prepared lightmaps, but cannot calculate new LightmapGI bakes for arbitrary generated layouts. [S4]

| Generation model | Suitability | Required approach |
| --- | --- | --- |
| Generate a mission in the editor, then ship it | Strong fit | Assemble, validate, bake, package |
| Generate a finite catalogue of mission variants during production | Strong fit | Give each approved layout and lighting scenario its own bake |
| Select a finished, baked mission at runtime | Strong fit | Load the matching scene and lighting data together |
| Rearrange room modules at runtime | Conditional | Restrict to validated, lighting-isolated modules; otherwise choose a runtime lighting strategy |
| Generate an unrestricted new map when a match starts | No standard LightmapGI bake for the new layout | Use an explicitly supported alternative |
| Rebuild walls or change the sun continuously during play | Poor fit for a fixed bake | Use real-time lighting/GI, bounded authored states, or accept a documented approximation |

**Recommended baseline for a four-player heist:** Generate missions before shipping and keep time of day fixed for each mission variant. Spend dynamic lighting on players, enemies, flashlights, alarms, and selected interactive fixtures.

If unrestricted runtime generation is a requirement, evaluate SDFGI, VoxelGI, or deliberately authored ambient and fill lighting. They have different update behavior and costs; none is a drop-in version of LightmapGI. SDFGI and VoxelGI require Forward+ in the documented renderer matrix. Already baked LightmapGI can render in Compatibility; baking requires hardware with RenderingDevice support. [S5–S6]

## 4. Treat the completed layout as the lighting input

A mesh can be reusable. Its surrounding illumination usually is not.

A wall beside an open window needs different lighting from the same wall behind a tall building. A room with a red floor returns different light from one with dark asphalt. A module baked without its neighbor cannot predict that neighbor's shadows or bounce.

### 4.1 Proposed pipeline

1. **Plan the mission:** Establish routes, buildings, openings, time of day, and gameplay lighting changes.
2. **Generate assets in Blender:** Produce geometry, UV1, material slots, semantic roles, and optional UV2.
3. **Import into Godot:** Resolve materials, generate or preserve UV2, and apply lighting roles.
4. **Assemble the final scene:** Place static architecture, adjacent blockers, lights, and props that meaningfully affect illumination.
5. **Validate before baking:** Reject broken openings, unintended glass blockers, incorrect static roles, and missing lightmap inputs.
6. **Bake a preview:** Inspect lighting relationships with cheap settings.
7. **Resolve defects:** Correct geometry and classification before increasing bake quality.
8. **Bake the release candidate:** Use the approved quality and density profile.
9. **Validate the exported mission:** Check appearance, gameplay states, dependencies, memory, and frame time.
10. **Package the scene and bake as a matched result:** Store the recipe and input fingerprint with it.

The generator should not silently change architecture after step 8.

### 4.2 Assign ownership

| Component | Must produce | Must reject |
| --- | --- | --- |
| Asset creator | Clean geometry, material roles, correct scale, meaningful object separation | Opaque wall faces hidden behind intended windows; mixed movable/static geometry |
| Level assembler | Final transforms, opening connections, neighboring blockers, stable identities | Overlapping shells; large unclassified late changes |
| Lighting planner | Source placement, scenario, change policy, exposure baseline | Lamps that can switch off but leave important permanent baked illumination |
| Import adapter | Validated material mapping, UV policy, mesh GI roles | Unknown role values or ambiguous UV ownership |
| Bake manager | Bake outputs, input fingerprint, quality profile, failure report | Missing output, stale dependencies, unapproved preview bake |
| Runtime loader | Matched level package and gameplay state | Lighting data borrowed from a different generated layout |

## 5. Blender asset requirements

### 5.1 Make the space behave like architecture

Generate walls with intended thickness and close their junctions. Provide the ceiling or roof that should block outdoor light. Model the reveals around windows and doors. Ensure the visible opening is also an opening in the structural mesh.

For ordinary interiors, test shell thickness around **0.15–0.30 m** as an initial asset convention. Choose thickness from the building type and intended construction; this range is not a universal requirement for LightmapGI.

Validate the final evaluated mesh, including modifiers:

- Normals face the intended direction; mirrored transforms have not inverted surfaces.
- Floors and walls do not have accidental gaps.
- Duplicate coplanar faces and overlapping shells are removed.
- Decorative cuts have not produced sliver triangles or tiny disconnected fragments.
- Shadow-critical frames and mullions exist as geometry when their silhouettes matter.
- Large invisible backfaces are retained only when they serve a deliberate structural purpose.

Extra detail is useful when it changes silhouette, visible shading, an important shadow, or play. Increasing triangle counts without those benefits does not improve the bake.

### 5.2 Separate objects by lighting behavior

For a window asset, export separate objects for:

1. Structural frame and mullions.
2. Glass pane.
3. Blinds, shutters, or bars, if present.
4. An optional breakable or moving part.

For a door, separate the fixed frame from the moving leaf. For a fluorescent fixture, separate its body, visible diffuser/emission, and semantic light anchor.

One material slot for glass inside a combined frame-and-pane mesh is not enough for the baseline policy in this guide: the proposed GI classification operates at mesh-instance level.

### 5.3 Prefer a predictable export contract

Use `.glb` as the initial interchange format unless an established project pipeline requires something else. Pin the Blender version and exporter configuration. Export a known one-meter calibration object to confirm units and orientation.

Treat Blender's node graph as authoring data. Bake procedural color/roughness/normal textures to images or recreate the intended material in Godot. Do not assume arbitrary Cycles nodes, transmission, or area-light behavior will reproduce in Godot. Blender's glTF material model and UV mapping have a defined export scope. [S7]

Use stable object IDs and material IDs, with readable names for artists. Store semantic properties in a sidecar recipe, or transport them through glTF extras using a tested importer. Godot documents import customization and custom-property transport, but the project must implement the mapping. [S8]

## 6. UV1 and UV2 have different jobs

**UV1 is the reusable surface design. UV2 is the unique lighting address.**

UV1 can tile, mirror, overlap, or use a trim sheet. A lightmapped wall can therefore retain a repeating brick texture while its sunlight and bounce vary along the wall.

For baked surfaces, UV2 must give surface regions separate lightmap space without unintended overlap. Reserve it for the lightmap, rather than a second tiling-detail texture. Godot supports generating this channel during import, and its LightmapGI tutorial recommends that route for most assets. [S9]

### 6.1 Choose one UV2 owner

| Policy | Good use | Required validator |
| --- | --- | --- |
| Godot generates UV2 | Default modular architecture and ordinary props | Imported mesh has UV2 and a usable lightmap size hint |
| Blender authors UV2 | Assets needing deliberate seams or controlled chart layout | Export/import preserves the intended second channel; Godot does not overwrite it |

In Godot's import configuration, **Static Lightmaps** enables the static mesh GI role and UV2 generation. **Lightmap Texel Size** controls spatial density: smaller values increase resolution and resource cost. [S8]

For Blender-authored UV2:

1. Finish topology and transformations first.
2. Keep the material UV map as the first exported channel and lightmap UVs as the second.
3. Place seams at natural breaks and avoid unnecessary fragmentation.
4. Unwrap and pack with adequate separation.
5. Inspect the result after export and Godot import; names alone do not prove channel order.
6. Supply and verify the mesh's lightmap size hint through the pipeline.

Blender's Lightmap Pack operator places selected faces separately, while Pack Islands packs existing charts. These can assist the workflow, but a face-per-chart result can waste space and increase seams. [S10]

### 6.2 Padding must be evaluated in pixels

A normalized margin such as `0.01` has different pixel meaning at different chart resolutions. As a prototype target, test a **4–8 texel gap between islands** at the effective packed resolution, then inspect the engine result at distance and oblique angles. Filtering and mip levels can still require more separation.

Do not convert that recommendation into an unconditional Blender margin value. Define whether the exporter setting means a gap or a border and validate the actual packed output.

The same reusable mesh resource can appear several times without requiring every instance to occupy a different place in that mesh's UV2. Instance placement in the baked atlas is the baker's responsibility. Avoid manually stacking charts within one mesh merely because the base texture repeats.

## 7. Glass needs an explicit policy

Visible transparency, shadow casting, GI participation, reflection, and collision are separate decisions. A pane can look transparent while an unintended structural face or a different bake representation blocks the opening.

### 7.1 Baseline clear-window policy

For ordinary clear shopfront and house windows, use this deliberate approximation:

| Part | Proposed classification | Intended result |
| --- | --- | --- |
| Frame / mullions | Static bake participant; shadows enabled | Frame silhouette blocks light |
| Clear pane | Excluded from the static bake; runtime shadows off | Pane remains visible while light passes through its area |
| Fixed opaque shutter / blind | Static bake participant if permanently fixed | Produces its intended shadow |
| Moving blind / breakable obstruction | Excluded from static bake; runtime shadow policy | No permanent baked silhouette from a temporary state |
| Collision | Configured separately | Gameplay collision does not decide visual transmission |

The static-bake exclusion is the reliable baseline here. Do not depend solely on the pane's alpha value or a real-time shadow toggle to describe how the baker treats it.

This policy approximates unobstructed transmission. It does **not** simulate glass absorption, refraction, caustics, or physically correct colored transmission. Reject it for a window whose tint or opacity is central to the scene's lighting.

### 7.2 Godot mesh policy example

The following is an editor-tool integration fragment, not a complete importer or baker. The caller resolves semantic roles from the project recipe.

```gdscript
func apply_mesh_lighting_role(mesh: MeshInstance3D, role: String) -> void:
    match role:
        "static_opaque":
            mesh.gi_mode = GeometryInstance3D.GI_MODE_STATIC
            mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
        "clear_glass":
            mesh.gi_mode = GeometryInstance3D.GI_MODE_DISABLED
            mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
        "movable":
            mesh.gi_mode = GeometryInstance3D.GI_MODE_DISABLED
            mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
        _:
            push_error("Unknown mesh lighting role: %s" % role)
```

These are mesh GI and shadow settings, not light-node bake settings. Static GI geometry participates in LightmapGI; nonstatic moving geometry must receive its baked indirect illumination through probes rather than a surface lightmap. [S11]

An unknown role must also fail the calling validator; logging an error alone does not stop a production build.

### 7.3 Diagnose a dark window in this order

1. Temporarily remove the pane from the **bake input** and rebake the same test.
2. If light now enters, keep the pane excluded and verify its runtime material separately.
3. If it stays dark, inspect for an opaque face across the opening, hidden blinds, duplicate panes, incorrect normals, and an exterior blocker.
4. Confirm an actual light source and environment exist in the scene. An editor preview is not the scene's lighting setup.
5. Check the pane's role survived import and generation.
6. Inspect the affected receiver for UV2 and sufficient lighting resolution.
7. Only then adjust brightness or exposure.

Always rebake after a bake-input change. Merely hiding the pane while continuing to display an old bake does not test transmission.

### 7.4 Transparency modes are not interchangeable

Godot's alpha blending, alpha scissor, alpha hash, and depth-prepass modes differ in cost and shadow behavior. Alpha scissor represents a cutout rather than smoothly translucent glass. Do not replace glass with a cutout mode simply to obtain a different shadow result. [S12]

For tinted or dirty glass, choose and document one of these treatments:

- Keep the clear-window policy and accept simplified transmission.
- Make a genuinely opaque dirty region separate geometry where its shadow matters.
- Add a restrained, source-motivated colored fill as an authored approximation.
- Use a rendering method specifically validated for the desired transmission.

If a pane can break, design its before/after lighting expectations. With the baseline clear-glass policy, breaking it should not remove a permanent baked pane shadow because none was baked.

## 8. Classify lights by what gameplay can change

The dedicated Godot LightmapGI tutorial describes three per-light choices: Disabled excludes a source from the bake; Dynamic bakes indirect illumination while retaining real-time direct light/shadows; Static bakes direct and indirect illumination on static surfaces. Fully baked direct lighting has an important limitation: moving objects do not cast real-time shadows onto those baked surfaces from that source. [S9]

The general Light3D class reference describes bake enums across GI backends and differs from the LightmapGI tutorial in its discussion of Dynamic. Therefore, make a four-light calibration test in the exact installed 4.7 build a release requirement before automating the mapping. Do not infer behavior from enum names alone. [S13]

### 8.1 Proposed semantic source roles

| Project role | Intended behavior | Typical use |
| --- | --- | --- |
| `fixed_full_bake` | Bake direct and indirect; accept actor-shadow limitation | Small fixed decorative lamps away from important combat contact |
| `fixed_indirect_bake` | Bake indirect; keep direct light/shadows real time | Fixed sun and important combat-room illumination |
| `realtime_only` | Exclude source from bake; calculate direct light in play | Flashlights, muzzle flashes, alarms, meaningful switches |
| `scenario_variant` | Load an approved package with a matching bake | Separate day/night or powered/unpowered missions |

These strings are **proposed project metadata**, not Godot properties.

### 8.2 Do not bake a permanent consequence of a temporary state

- A shootable lamp should not leave strong illumination on a wall after it is destroyed.
- A moving door should not leave its closed silhouette on the floor when opened.
- A red rotating alarm should not leave a stationary red patch behind it.
- A flashlight should not contribute to the room's permanent bake.

Indirect-only baking does not solve large lighting changes: the indirect contribution is still frozen. For an important power-cut mechanic, keep the affected sources out of the bake, prepare bounded scenario variants, or choose a suitable runtime GI solution.

To exclude a light, set its bake policy. The Light3D reference warns that hiding a light alone does not exclude it from a LightmapGI bake. [S13]

### 8.3 Suggested hybrid for a heist mission

Use baked bounce to establish the fixed architectural space. Retain real-time direct lighting where player shadows, moving doors, or enemy silhouettes matter. Fully bake less important fixed fixtures only after viewing their actor-shadow tradeoff in context.

Keep changing emergency lights separate from the fixed environmental lighting. Where no runtime GI is used, accept that their light does not automatically bounce around the room; add a modest controlled fill only if gameplay and art review justify it.

## 9. Moving characters need sampled environmental light

Characters and movable props cannot carry a wall's surface lightmap as they move. LightmapGI supports probe-based indirect lighting for dynamic objects, with automatic probe generation and optional LightmapProbe nodes. [S14]

### 9.1 Place additional samples around meaningful transitions

The lighting planner should nominate test positions at:

- Exterior-to-interior thresholds.
- Window-lit areas and their adjacent shade.
- Stair landings and vertical route changes.
- Under awnings and deep shelving.
- Combat cover and objective interaction positions.
- Narrow rooms where bright and dark spaces are close together.

Use an initial test spacing of **1–2 m near abrupt transitions** and coarser sampling in open, uniform areas. This is a proposed placement experiment, not a guarantee of interpolation quality. More probes do not inherently prevent interpolation across a thin wall.

Walk a neutral gray character proxy through the level. Inspect sudden brightness changes, outside light appearing inside, and disagreement between the floor and the character. Correct placement or level partitioning before increasing every probe count.

Do not promise baked indirect shadowing from the moving actor. Probe lighting gives the actor an approximation of the static environment; real-time lights and other contact-shadow treatments handle its changing relationship to nearby geometry.

## 10. Reflections remain a separate task

A diffuse bake does not by itself provide convincing sharp reflections for glass, chrome, wet flooring, or polished counters. Godot's directional lightmaps can add approximate rough reflections; they are not a complete replacement for a deliberate reflection setup. [S4]

ReflectionProbe can complement LightmapGI. Fit probes to meaningful room volumes, keep their capture origins out of walls, and test box projection for roughly rectangular interiors. Prefer the cheaper Once update policy until a changing reflection is actually needed. [S15]

For the generator, define reflection volumes from rooms and architectural openings rather than distributing identical probes on a uniform world grid. Check that an interior does not read as if it were reflecting the outdoor sky from every surface.

## 11. Density and quality are different controls

More samples reduce integration noise. More lightmap texels improve spatial resolution. Increasing one does not automatically fix problems caused by the other.

Use these proposed initial density tiers, assuming one Godot unit represents one meter:

| Receiver / lighting need | Initial world-space texel size | Approximate texels per meter |
| --- | --- | --- |
| Indirect-only ordinary architecture | 0.20 m | 5 |
| Important interior receivers | 0.10 m | 10 |
| Local receiver under a recognizable baked frame shadow | 0.025–0.05 m | 20–40 |
| Large background architecture with broad gradients | 0.40 m | 2.5 |

These are project experiments. Start with the coarsest tier that survives the intended player view. High-resolution base textures do not require equally high-resolution lighting.

For a shadow feature of width `w`, a rough diagnostic target is several lightmap texels across the feature. A 0.05 m mullion projecting an important shadow might need around 0.0125–0.025 m sampling locally, or the direct shadow should remain real time. Projection angle changes the width on the receiver, so test the actual shadow.

### 11.1 Understand the area cost

Ignoring padding and packing losses:

```text
approximate lightmap texels = receiving surface area / (texel size × texel size)
```

A 100 m² surface at 0.20 m needs roughly 2,500 texels. At 0.10 m, it needs roughly 10,000. Halving texel size increases this area cost by four.

Do not confuse world-space texel size with density multipliers. A smaller import texel size raises density; a larger density multiplier can also raise density. The tool's UI should expose one clear concept and translate it into the selected Godot settings.

### 11.2 Memory must include all textures and slices

For an illustrative uncompressed RGBA16F texture:

```text
4096 × 4096 × 8 bytes = 128 MiB before mipmaps
full mip chain ≈ another one-third = about 171 MiB total
```

This is arithmetic for a hypothetical format, not a claim about Godot's final import format. Measure the actual texture formats, dimensions, slices, directional data, and shadowmask data in your build. Compressed file size is not resident GPU memory.

The maximum atlas dimension is not a total memory budget. Several smaller atlases can still consume more memory than expected. The bake report must enumerate everything the bake created. LightmapGIData exposes arrays of lighting and shadowmask textures, so tooling must not assume a single texture. [S16]

### 11.3 Proposed iteration profiles

| Profile | Purpose | Proposed starting controls |
| --- | --- | --- |
| Layout preview | Find classification errors and obvious leaks | Low quality, coarse density, 1–2 bounces |
| Lighting review | Judge bounce, color, and actor integration | Medium quality, selected density tiers, 3 bounces |
| Release candidate | Validate final appearance and budget | High quality, locally justified density, 3 bounces initially |

Godot exposes bounce count, denoising, and optional directional lightmaps. More bounces and directional data add bake work; directional data also adds storage and runtime work. Leave bounce-energy amplification neutral initially. [S4]

Increase bounce count when a controlled comparison shows a useful improvement. Increase sampling when noise remains. Increase density when important spatial features are unresolved. Fix UVs, geometry, or roles when the defect comes from those inputs.

Do not switch to Ultra merely because it is available. Every quality increase needs a visible reason and a measured cost.

## 12. Partition bakes around lighting boundaries

### 12.1 Start with one coherent bake domain

For an initial mission, bake the complete participating environment together. Include the nearby exterior geometry responsible for blocking or reflecting light into the playable space.

Do not bake every wall or room independently just because generation produces independent modules. That loses cross-boundary lighting relationships.

### 12.2 Split when there is a production reason

Good candidates for separation include disconnected interiors, distinct mission scenes, and areas separated by a transition where the player cannot inspect a continuous lighting surface.

Open doorways, continuous corridors, stairwells, and large shopfront openings are poor automatic boundaries. If separate bake domains are necessary, define the neighboring geometry each domain must see and inspect both sides of the connection.

Godot's LightmapGI operates within a scene hierarchy scope. Place a single bake node under the mission root as a sibling of the participating geometry hierarchy for the initial implementation. Verify domain membership rather than relying on physical distance alone. [S4]

### 12.3 Runtime modules need a restricted contract

If selecting pre-baked room modules at runtime:

- Keep modules together with their bake data and internal node relationships.
- Validate which transforms and instancing arrangements the installed engine handles.
- Use transitions that conceal lighting discontinuities where appropriate.
- Prevent arbitrary windows or openings into unknown surroundings.
- Do not claim that neighboring modules will cast new baked shadows or contribute new baked bounce.
- Test probe lighting across every allowed connection.

Treat this as an authored lighting-isolation system. It is not a substitute for baking an unrestricted assembled layout.

## 13. Build lighting into level planning

The generator should reason about sources, openings, receivers, and blockers before scattering fixtures.

| Architectural situation | Planner question | Possible design response |
| --- | --- | --- |
| Narrow rowhouse street | What blocks direct sun and what receives skylight? | Differentiate exposed street, stoop, and recessed entry |
| Convenience store | Which openings reveal daylight and where do fixtures serve work? | Windows plus ceiling illumination organized around aisles and counter |
| Dive bar | What motivates each readable pool of light? | Bar fixtures, entrance spill, signs, and task lights |
| Service alley | Which adjoining building owns the light? | Back-door fixtures and partial spill, with darker stretches between |
| Warehouse | Which routes and work areas need illumination? | Doors, high windows, workbench sources, and overhead fixture groups |

For a 1990s Pennsylvania setting, choose the fixture family, installation pattern, and color according to the building's use and maintenance history. Avoid a default rainbow of differently colored lamps.

### 13.1 A simple room-lighting recipe

Each generated room should specify:

1. Its primary source or daylight opening.
2. The surfaces expected to receive direct light.
3. The surfaces expected to provide substantial bounce.
4. Its intentionally shaded area.
5. Player routes and interactions that must remain readable.
6. Any source or blocker that changes during gameplay.

Example: an old shop has a bright front window, pale plaster walls, darker shelving, and a fluorescent-lit counter. Daylight should be strongest near the front and diminish toward the back. The counter's task lighting can establish a second local focus. A global ambient increase should not erase that progression.

### 13.2 Readability is part of the validation

Evaluate enemy silhouettes, cover edges, pickups, door handles, and escape routes from actual gameplay positions. Do not brighten every dark corner equally. Improve the source placement, surface separation, or local composition that causes a specific readability failure.

For co-op, test four players with their expected effects active. A successful empty-room beauty view does not establish combat readability or runtime cost.

## 14. Proposed machine-readable data contract

The following is **example project JSON**, not a built-in Godot schema. Its role is to make the generator's decisions explicit. Store asset IDs and transforms in the wider level recipe; the lighting record references those stable IDs.

```json
{
  "schema_version": "1.0",
  "level_id": "delco_corner_shop_001",
  "generation_seed": 48271,
  "generation_stage": "editor",
  "engine_target": "4.7",
  "lighting_scenario": "late_afternoon_fixed",
  "lighting_strategy": "baked_environment_hybrid_direct",
  "time_of_day_changes_in_play": false,
  "uv2_policy": "godot_import",
  "exposure_profile": "mission_review_fixed_v1",
  "bake_profile": {
    "quality": "high",
    "bounces": 3,
    "bounce_indirect_energy": 1.0,
    "directional_lightmaps": false,
    "default_import_texel_size_m": 0.2,
    "important_receiver_texel_size_m": 0.1
  },
  "mesh_roles": [
    {
      "instance_id": "shop_shell_01",
      "role": "static_opaque",
      "must_have_uv2": true
    },
    {
      "instance_id": "front_window_frame_01",
      "role": "static_opaque",
      "must_have_uv2": true
    },
    {
      "instance_id": "front_window_pane_01",
      "role": "clear_glass",
      "must_have_uv2": false,
      "transmission_approximation": "pane_omitted_from_bake"
    },
    {
      "instance_id": "rear_door_leaf_01",
      "role": "movable",
      "must_have_uv2": false
    }
  ],
  "light_roles": [
    {
      "instance_id": "sun_01",
      "role": "fixed_indirect_bake"
    },
    {
      "instance_id": "counter_fixture_01",
      "role": "fixed_indirect_bake"
    },
    {
      "instance_id": "alarm_01",
      "role": "realtime_only"
    }
  ],
  "probe_review_routes": [
    "street_to_front_counter",
    "counter_to_stockroom",
    "stockroom_to_rear_alley"
  ],
  "required_tests": [
    "clear_pane_transmission",
    "frame_shadow",
    "door_open_closed",
    "actor_lighting_routes",
    "alarm_off_has_no_baked_red_patch",
    "exported_build_dependencies"
  ],
  "approval_state": "needs_preview_bake"
}
```

### 14.1 Contract rules

- `instance_id` must resolve to exactly one intended instance in the assembled level.
- `quality`, mesh roles, light roles, and stage must come from explicit supported enum lists.
- Units must be unambiguous; reject zero or negative texel sizes.
- Conflicting classifications are errors, not opportunities for a last-write-wins fallback.
- The engine adapter translates semantic roles into actual settings and records the result.
- Shader and imported-material exceptions must be visible in a validation report.
- A changed recipe, adapter version, or bake-affecting input invalidates the approval state.
- If `generation_stage` becomes `runtime` with unrestricted assembly, reject this LightmapGI strategy instead of attempting an unsupported bake.

## 15. Bake invalidation and reproducibility

Store an input fingerprint with each approved bake. At minimum, include:

- Generator and lighting-adapter versions, seed, and resolved level recipe.
- Engine build and renderer/bake configuration.
- Static mesh content, evaluated topology, UV2, transforms, and stable instance paths.
- Bake-participating materials, textures, shader versions, color, and emission.
- Light properties and the resolved bake role of every source.
- Sky/environment and any bake-relevant exposure settings.
- Probe configuration, domain membership, density settings, and quality profile.

Use a canonical serialization before hashing. A seed alone is insufficient when assets or generator code change.

### 15.1 Invalidation examples

| Change | Proposed response |
| --- | --- |
| Move or resize a static wall | Invalidate affected domain and dependent domains |
| Repaint a major bounce surface | Invalidate affected lighting |
| Change the fixed sun angle or sky | Invalidate the scenario |
| Change an included emissive sign | Invalidate the affected domain |
| Alter UV2 or merge/split a mesh | Invalidate receiver bindings and bake |
| Rename or reparent baked instances | Revalidate bindings; conservative policy is rebake |
| Change probe placement | Rebuild the relevant baked probe data |
| Move an explicitly excluded character | No static bake invalidation |
| Tune a realtime-only flashlight | No static bake invalidation; rerun runtime checks |
| Change display exposure only | Rerun appearance checks; rebake if bake exposure also changed |

LightmapGIData stores baked users by node path and texture mapping. Preserve scene relationships and all output dependencies when packaging; do not retain just an image of the lightmap. [S16]

Keep original generator inputs, `.import` configuration, and needed unwrap cache files under version control. Treat an input fingerprint as reproducibility evidence, not a promise that different GPU/driver combinations produce bit-identical bake images.

For multiplayer, load the same approved level package on all clients. Synchronize gameplay state such as doors and alarms; do not send a new lighting bake over the network for each match.

## 16. Bake automation requirements

Implement automation as an editor-side production tool. Do not invent a `godot --bake-lightmaps` command or assume a headless worker has the GPU backend required by the lightmapper.

Begin with the editor's documented **Bake Lightmaps** action, then automate through a version-tested editor integration. If direct automation is unavailable in the project's build, a generated scene plus a manual bake remains a valid production stage. Do not replace it with a fake completed status.

### 16.1 Required bake report

Record:

- Level ID, scenario, input fingerprint, engine build, and selected renderer.
- Mesh/light role counts and exclusions.
- Bake domain, receiver count, and UV validation result.
- Start/end time, completion status, and error messages.
- Every generated resource and texture dependency.
- Atlas dimensions, slice counts, formats, file sizes, and measured resident memory where available.
- Probe configuration and review-route results.
- Review capture names and approval status.
- Baseline versus candidate GPU/CPU timing from the exported mission.

Bake a small level first. Add queueing, cancellation, caching, and multi-machine workers only after one end-to-end job reliably produces a usable exported scene.

### 16.2 Suggested tool backlog

| Priority | Tool capability | Completion evidence |
| --- | --- | --- |
| P0 | Asset and light-role classifier | Glass, frames, doors, actors, and changing lights receive correct roles |
| P0 | Static-mesh preflight | Missing UV2, broken roles, and structural opening errors produce actionable failures |
| P0 | Editor bake workflow | Generated mission saves and exports with its lighting |
| P0 | Lighting regression room | The tests in section 17 pass in the installed engine |
| P1 | Input fingerprint and stale-bake detector | Moving a wall or changing major albedo reliably invalidates output |
| P1 | Budget and dependency report | All bake textures are counted and packaged |
| P1 | Probe route reviewer | Actor lighting can be inspected along generated traversal paths |
| P2 | Domain partitioning and scenario catalogue | Multiple approved packages preserve transitions and budgets |

## 17. A small validation room that proves the concept

Create a reusable test scene before applying the workflow to a full mission.

### 17.1 Fixture

Use a room approximately **6 × 4 × 3 m**, with:

- A window opening about 2 × 1.5 m and a recognizable frame/mullion.
- A separate clear pane.
- Pale neutral walls and one red or green test panel.
- A floor with visible tiling in UV1 and unique UV2.
- An opaque interior blocker and a moving door.
- A fixed source entering through the opening.
- A separate switchable lamp.
- A gray movable character proxy, a rough sphere, and a reflective sphere.
- A real WorldEnvironment, fixed camera exposure, and named camera positions.

Keep the test focused. Disable optional AO and screen-space indirect effects initially so they do not conceal what the bake contributes.

### 17.2 Required comparisons

| Test | Procedure | Passing evidence |
| --- | --- | --- |
| Bounce contribution | Compare no baked GI against a bake with identical real-time direct light, camera, and ambient setup | Shaded receiving surfaces gain coherent illumination rather than a uniform screen brightening |
| Surface color transfer | Bake with a colored panel, then change only that panel to neutral and rebake | Nearby bounce changes in the expected area |
| Separate texture and lighting | After a bake, replace receiver base texture with a neutral lit material without rebaking | Existing illumination pattern remains; note that this alone does not prove baking |
| Clear pane | Compare pane omitted from bake with visible pane classified as `clear_glass` | Comparable daylight reaches the interior in both cases |
| Frame shadow | Keep frame static and pane excluded | Frame blocks light while pane does not produce a solid rectangular blocker |
| Moving door | Open and close a nonstatic door | No permanent baked door silhouette; runtime direct-shadow behavior matches design |
| Actor lighting | Move gray proxy from outside to window to back of room | No unexplained bright flashes, blackouts, or severe mismatch with the environment |
| Switchable source | Turn the realtime-only lamp off after baking | No baked pool of light attributable to that source remains |
| Fully baked tradeoff | Compare an actor under fully baked direct light with indirect-baked/realtime direct light | Team sees and records the difference in actor shadows on static surfaces |
| Reflection setup | Inspect rough and reflective spheres with and without the reflection setup | Expected reflection source is present without claiming a sharp diffuse-lightmap reflection |
| Export round trip | Close editor and run exported scene | Lighting, dependencies, and object bindings remain correct |

### 17.3 Four-light mode calibration

Use isolated copies of the fixture so sources cannot contaminate each other's test:

1. A source intended for full baking.
2. A source intended for indirect-only baking.
3. A source excluded from baking.
4. A deliberately hidden source to check the visibility/bake distinction.

Bake, then move an actor, move an occluder, and change each source's energy in play. Record what changes on static receivers and what remains frozen. Save the confirmed mapping between project roles, Inspector values, and enum values for the exact engine build.

Repeat this calibration after an engine upgrade or a material-pipeline change that affects light transport. It resolves the documentation ambiguity identified in section 8 with observable behavior.

### 17.4 Optional automated measurements

Measure stable, named sample regions rather than comparing arbitrary screenshots:

- Window receiver brightness in the open-window versus clear-pane cases.
- Brightness of a deliberately shaded patch with bounce enabled versus disabled.
- Color change on a neutral receiver after the test panel is repainted and rebaked.
- Brightness steps along a fixed actor route.
- Differences at intended continuous architectural joins.

If numerical image comparison is implemented, use fixed exposure, camera, resolution, and render settings; prefer linear values for lighting analysis. A first clear-pane target might be **less than 10% average luminance difference** from the no-pane reference in a selected interior patch. This is a proposed tolerance, not a physical law or measured result. Review composition and individual defects as well as averages.

## 18. Common failures and first fixes

| Symptom | Likely cause | First useful action |
| --- | --- | --- |
| Bright exterior but black interior | Opaque pane/hidden blocker; absent bounce; unlit material | Remove pane from bake, inspect opening, confirm material and scene sources |
| Window light remains blocked after pane removal | Old bake still loaded or structural face remains | Rebuild the bake from the changed scene, then inspect shell geometry |
| Light leaks at wall joints | Gap, thin/misclassified geometry, bad UVs, inappropriate bias | Inspect geometry and UVs before increasing samples |
| Blotchy gradients | Insufficient sampling or problematic charts | Inspect UV layout, then compare quality/denoising locally |
| Recognizable shadows are blurry | Lightmap density too low on receiver | Raise local density or keep direct shadows real time |
| Bright seams between modules | Independent bakes, inconsistent materials/density, bad charts | Review in a shared lighting context and fix the actual boundary |
| Character looks detached from room | Sparse/bad probe sampling or missing direct-light relationship | Walk a proxy route and inspect probes and source policies |
| Switch-off leaves a lit wall | Direct or indirect contribution is baked | Remove that changing source from bake or use approved scenario states |
| Removed prop leaves a dark mark | Prop was included as a fixed occluder | Exclude movable prop and rebake |
| Clear window renders poorly | Runtime transparency/reflection issue | Debug material and ordering separately from bake transmission |
| Scene feels uniformly gray | Excess ambient fill, weak source hierarchy, similar material values | Reestablish source motivation and lit/shaded structure |
| Metal/glass looks dull | Missing or wrong reflection context | Inspect roughness, reflection probe, sky, and material mapping |
| Bake uses excessive memory | Excess density/fragmentation, too many receivers or slices | Enumerate outputs and reduce unimportant allocation |
| Lighting disappears in exported build | Missing dependencies or broken scene bindings | Inspect packaged resources and load the approved scene/bake pair |

Bias controls for baked and real-time shadows are different. Do not use a large blanket bias increase as a substitute for repairing geometry. [S4]

## 19. Release acceptance checklist

### Asset acceptance

- [ ] Glass, frames, and moving parts are separable and classified.
- [ ] Structural openings are genuinely open in evaluated meshes.
- [ ] Units, normals, transforms, and material mappings survive export.
- [ ] Static receivers have validated UV2 and usable lightmap sizing.
- [ ] Lighting-specific shadows are not painted into reusable albedo.

### Lighting acceptance

- [ ] Scene contains its actual environment and sources.
- [ ] Fixed and changing light roles match gameplay.
- [ ] Clear-glass and frame-shadow tests pass.
- [ ] Major bounce colors have been reviewed after the final material pass.
- [ ] Moving actors and doors have been reviewed on gameplay routes.
- [ ] Reflections have a deliberate, budgeted source.
- [ ] Exposure and gameplay readability are reviewed together.

### Build acceptance

- [ ] No unknown lighting roles or unresolved validation errors.
- [ ] Bake input fingerprint matches the shipped geometry and scenario.
- [ ] Preview output cannot be mistaken for approved release output.
- [ ] All bake resources and texture slices are included and counted.
- [ ] Exported-build appearance and performance meet the project's budgets.
- [ ] Four-player combat and effects have been profiled on target hardware.
- [ ] Known approximations, such as clear-glass transmission or static indirect light, are recorded.

## 20. Instruction block for an AI-assisted level generator

```text
Treat lighting as an authored relationship between geometry, sources,
materials, openings, and gameplay states.

For production-generated levels, assemble the final lighting context in
Godot before baking. Blender prepares geometry and material inputs;
Godot LightmapGI produces the project's static lighting result.

Keep reusable base textures separate from scene lighting. Use UV1 for
surface design and validated UV2 for baked receivers.

Classify every mesh and source. Separate clear panes from opaque frames,
moving doors from fixed architecture, and temporary lights from fixed
environmental sources. Unknown roles fail validation.

Do not assume that visible transparency gives correct bake transmission.
Use the approved clear-window approximation or a separately validated
transmission workflow. Keep collision decisions independent.

Do not bake strong permanent effects from objects or lights that change
during play. Provide probe sampling for moving actors and real-time direct
lighting where moving shadows matter.

Do not attempt standard LightmapGI baking in an exported game. Select a
compatible strategy before promising unrestricted runtime generation.

Invalidate lighting when its inputs change. Package the scene, bake,
probes, textures, scenario, and input fingerprint as a matched result.

Prove the workflow in the validation room, then check actual gameplay
routes, exported-build dependencies, memory, and frame time.
```

## 21. References and verification boundaries

Godot references below use the **4.7 documentation branch**. Blender references explain the relevant authoring operations and export scope; this guide does not require a particular Blender major version. Pin and validate the version used by the project.

| ID | Official / first-party reference | Used for |
| --- | --- | --- |
| S1 | [Valve Developer Community: VRAD](https://developer.valvesoftware.com/wiki/VRAD) | Source compilation and stored lighting |
| S2 | [Valve Developer Community: LightmappedGeneric](https://developer.valvesoftware.com/wiki/LightmappedGeneric) | Source lightmapped surface materials |
| S3 | [Godot 4.7: Introduction to global illumination](https://docs.godotengine.org/en/4.7/tutorials/3d/global_illumination/introduction_to_global_illumination.html) | Indirect diffuse light, surface color transfer, GI alternatives |
| S4 | [Godot 4.7: LightmapGI](https://docs.godotengine.org/en/4.7/classes/class_lightmapgi.html) | Editor-only baking, configuration, directional information, bias |
| S5 | [Godot 4.7: Overview of renderers](https://docs.godotengine.org/en/4.7/tutorials/rendering/renderers.html) | Renderer support and baking hardware requirements |
| S6 | [Godot 4.7: LightmapperRD](https://docs.godotengine.org/en/4.7/classes/class_lightmapperrd.html) | GPU-based lightmapper and RenderingDevice |
| S7 | [Blender: glTF 2.0 export manual](https://docs.blender.org/manual/en/5.0/addons/import_export/scene_gltf2.html) | Material export scope and UV mapping |
| S8 | [Godot 4.7: Import configuration](https://docs.godotengine.org/en/4.7/tutorials/assets_pipeline/importing_3d_scenes/import_configuration.html) | Static Lightmaps, texel size, import automation and custom properties |
| S9 | [Godot 4.7: Using Lightmap global illumination](https://docs.godotengine.org/en/4.7/tutorials/3d/global_illumination/using_lightmap_gi.html) | UV workflow, scene scope, per-light modes and dynamic shadow limitation |
| S10 | [Blender: UV Operators](https://docs.blender.org/manual/en/latest/modeling/meshes/editing/uv.html) and [Editing UVs](https://docs.blender.org/manual/en/latest/modeling/meshes/uv/editing.html) | Lightmap Pack and Pack Islands |
| S11 | [Godot 4.7: GeometryInstance3D](https://docs.godotengine.org/en/4.7/classes/class_geometryinstance3d.html) | Mesh GI roles and shadow settings |
| S12 | [Godot 4.7: BaseMaterial3D](https://docs.godotengine.org/en/4.7/classes/class_basematerial3d.html) | Transparency and unshaded-material behavior |
| S13 | [Godot 4.7: Light3D](https://docs.godotengine.org/en/4.7/classes/class_light3d.html) | Light bake enums and hidden-light baking behavior |
| S14 | [Godot 4.7: LightmapProbe](https://docs.godotengine.org/en/4.7/classes/class_lightmapprobe.html) | Additional indirect-light samples for moving objects |
| S15 | [Godot 4.7: Reflection probes](https://docs.godotengine.org/en/4.7/tutorials/3d/global_illumination/reflection_probes.html) | Reflection setup and update policies |
| S16 | [Godot 4.7: LightmapGIData](https://docs.godotengine.org/en/4.7/classes/class_lightmapgidata.html) | Baked resource dependencies, texture arrays, and user bindings |

Documentation and retrieved official-source excerpts were checked for this guide. The Godot pages were available directly; Valve and Blender details also relied on indexed official-source excerpts where direct page retrieval was blocked. No Blender or Godot executable was available in the authoring environment, so the example fragment and proposed settings were not engine-tested here. The calibration scene and exported-build checks are implementation acceptance work, not claimed completed tests.

The pipeline roles, data contract, example level, density tiers, tolerances, and backlog are original recommendations for this use case. They should be adjusted from measured results in the actual project.
