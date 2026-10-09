<!--
Filed 2026-10-08 from the walker's `Blender_Modern_Low_Poly_Asset_Standard.docx`
(the original is beside this file). Rendered to Markdown from the document's
own paragraph styles by a script; the text is the document's, unedited,
except Addendum A (before section 16), added 2026-10-08 at the walker's
request and not in the .docx.
How it maps to Zoo's minting today: MODERN_LOW_POLY_IN_ZOO.md.
-->

# Modern Low Poly Asset Creation in Blender

*Production standard for Delco Dangerous*

For the 3D asset creator  •  Blender to Godot 4.7  •  8 October 2026

Create grounded 1990s Delco assets with simple, deliberate shapes and a more convincing modern finish. Keep broad planes, angular silhouettes, readable colors, and compact textures. Improve construction, edge shading, material separation, and lighting response while measuring the runtime cost.

This document is the working brief for a human artist or procedural asset tool. It covers mesh creation, Blender object structure, baking, textures, materials, export, collision, LODs, and the evidence required to approve an asset.

### The visual target

| Direction | Observable appearance |
|---|---|
| PSX inspired | Very simple forms, coarse textures, strong faceting; historical display artifacts are optional style choices. |
| Deliberate low poly | Accurate proportions and strong planes; selected geometry makes construction readable. |
| Modernized low poly | Small bevels, controlled normals, restrained materials, and stable lighting. This is the default target. |
| Stylized realism | Selected hero assets receive richer form and material detail while matching the same shape language. |

Terms such as modern low poly, mid poly, and stylized realism overlap. They do not define a universal triangle count. Treat the target as a set of visible qualities and measured budgets.

### What the creator must preserve

- Keep recognizable silhouettes and broad, intentional surface planes. Use smooth shading selectively.
- Model construction that makes sense: thickness, recesses, supports, joints, and attached parts.
- Spend detail where the player can see it. Keep decorative noise below the main forms.
- Use no automatic subdivision of the runtime mesh. Detailed baking sources may remain offline.
- Review the exported asset in Godot at gameplay distance and in motion.

Status of the numbers: Budgets, tolerances, bevel sizes, and material values in this document are proposed starting points. They are not measured performance results or universal engine limits. References [A1–A8] demonstrate published work; [T1–T14] explain technical behavior.

## 1 Asset budgets and working assumptions

Set the viewing distance, interaction, repetition, and target hardware before choosing an asset budget. The same object can justify different detail as handheld equipment, room dressing, or distant scenery.

| Asset class | LOD0 starting range | Spend detail on |
|---|---|---|
| Small clutter | 300–1500 triangles | Identity and exposed outline. Simple items may be far below this range. |
| Common medium prop | 1000–4000 triangles | Openings, handles, profile changes, and visible corners. |
| Selected hero prop | 3000–8000 triangles | Close interaction, silhouette, functional parts, and distinctive construction. |
| Enemy character | 6000–12000 triangles | Face, hands, clothing silhouette, equipment, and deformation. |
| Architecture | Budget by module and view | Entrances, rooflines, sills, frames, and places that reveal depth. |

Count evaluated, exported triangles after modifiers. Do not add detail to fill a range. Record exported vertices as well: UV and normal discontinuities can split vertices beyond the count shown on the editable mesh. [T11]

| Resource | Starting policy |
|---|---|
| Material surfaces | Aim for one opaque surface per simple static prop. Add surfaces only for a clear visual or functional reason; glass is a common separate case. |
| Unique textures | Usually 128–512 px. Review larger unique maps against viewing distance. |
| Shared trim atlas | Start at 1024 px. A larger atlas can be sensible if reused widely and its density is needed. |
| Ordinary environment density | Start around 128–256 texels per meter. |
| Close interaction density | Start around 256–512 texels per meter; prioritize labels that must be read. |
| Density consistency | Keep comparable surfaces within roughly 20 percent unless the difference is deliberate. |

### Frame time is the performance measure

The total frame interval is 33.33 ms at 30 FPS, 16.67 ms at 60 FPS, and 8.33 ms at 120 FPS.

These intervals cover the whole running game. There is no universal draw-call-to-FPS ratio. Record the GPU, CPU, renderer, resolution, quality preset, and representative gameplay load. CPU and GPU work can overlap; do not simply add their frame times. [T8]

The visual reference is older console art. This is not a claim that the asset or Godot project runs on original Xbox or PS2 hardware.

## 2 Viewing distance and visible detail

Review detail with the gameplay camera. A useful feature changes the outline, depth, motion, or a visible lighting response.

| Feature | Preferred representation |
|---|---|
| Silhouette or deep opening | Geometry. |
| Independent motion or interaction | Separate geometry with an appropriate pivot. |
| Small edge highlight | Selected bevel or a baked normal, depending on the view. |
| Shallow seam or screw recess | Normal map when it survives the texture resolution. |
| Gloss, grease, abrasion | Roughness. |
| Labels, discoloration, fading | Base color. |
| Broad repeated-object tint | Vertex color or a compatible variation parameter. |

### A practical pixel estimate

At 1080p and a 60 degree vertical field of view, a small feature facing the camera covers approximately 935 times its size in meters, divided by its distance in meters, in pixels. Contrast, motion, angle, and reflections also affect visibility.

| Feature size | At 3 meters |
|---|---|
| 1 mm | 0.3 px |
| 5 mm | 1.6 px |
| 10 mm | 3.1 px |
| 50 mm | 15.6 px |

Below a couple of pixels at normal viewing distance, first test shading or textures. Retain geometry for meaningful outlines, openings, shadows, or interaction. Subpixel highlights can remain visible; this is not a universal deletion rule.

### Choose cylinder resolution by its outline

| Sides | Closed cylinder triangles | Outline error at 120 px diameter |
|---|---|---|
| 8 | 28 | 4.6 px |
| 12 | 44 | 2.0 px |
| 16 | 60 | 1.2 px |
| 24 | 92 | 0.5 px |
| 32 | 124 | 0.3 px |

Counts assume flat caps, one straight section, and no bevels. Error is the maximum radial gap between an inscribed polygon and a circle. This is an analytical example, not a benchmark. Choose faceting that matches the style.

Review views: use the closest permitted view, the normal gameplay view, and a distant view. A 1 m / 3 m / 10 m set is useful for room props; adapt it for handheld items and buildings.

## 3 Plan construction and object structure

Begin with reference showing dimensions, material, assembly, and wear. For a familiar 1990s object, identify the few features that establish its identity before adding generic detail. A telephone should read as a telephone in gray.

| Construction | Mesh requirement | Blender approach |
|---|---|---|
| Folded metal | Thin panels, lips, overlaps | Extruded profiles; thickness where visible. |
| Molded plastic | Shell seams, rounded corners, recessed controls | Box modeling, insets, selected bevels. |
| Wood furniture | Board thickness and supported parts | Separate simple pieces at consistent dimensions. |
| Masonry | Deep openings, sills, lintels | Extruded wall sections and attached architectural pieces. |
| Pipes and cables | Consistent diameter and deliberate bends | Low-resolution curves; inspect before conversion. |
| Fabric and padding | Large masses, compression, tension | Shape silhouette first; add local loops for form and motion. |

### Separate objects for a reason

A mesh contains geometry. An object places a mesh in the scene and carries transforms and modifiers. Several objects can share mesh data. Keep an editable source, baking sources and cutters, and an explicit export set.

| Part or use | Recommended structure |
|---|---|
| Cabinet body and fixed trim | May become one export object with disconnected mesh pieces. |
| Opening door or sliding drawer | Separate object with a hinge or slide pivot. |
| Pick-up handset or removable panel | Separate object when gameplay requires it. |
| Repeated chairs or cans | Reuse one mesh; use Alt+D for linked duplicates while authoring. |
| Large building | Divide into useful rooms, facade sections, or spatial chunks. |
| Collision | Separate, simpler geometry or engine primitives. |

Ctrl+J joins objects but does not weld their surfaces. Preserve the needed modifiers on export copies before joining; Blender does not combine every source modifier stack. One object can still contain several material surfaces and produce multiple draws. [T4]

Origins and scale: use a consistent ground placement origin for static props; hinge origins for doors; defined attachment points for interactive parts. Apply scale for static modeling before precise bevels and thickness. Preserve intentional rig transforms. Check a known one-meter reference in Godot.

## 4 Build and clean the mesh

### Construction order

1. Block in dimensions and large forms with simple primitives.

2. Establish the silhouette and major openings.

3. Add visible thickness, recesses, supports, joints, and attachments.

4. Distribute edges around curvature and deformation.

5. Add selected bevels and only the small geometry that survives the gameplay view.

6. Inspect the triangulated export in gray before texturing.

### Topology rules

Rigid props do not require all-quad topology. Use quads where they make editing and deformation easier, triangles where they represent the final shape efficiently, and n-gons as an editing convenience on suitable flat regions. Resolve nonplanar and concave faces deliberately in the export mesh.

Flat panels need few faces unless additional vertices support shape, UV boundaries, vertex colors, deformation, or another defined function. Straight cylinders need lengthwise rings only where radius, bends, or motion require them. [A6]

For animated assets, test elbows, knees, shoulders, mouths, and layered clothing through their actual motion. End loops away from heavily deforming regions when practical. A rigid prop and a bending character need different topology.

### Cleanup operations

| Problem | Operation | Check afterward |
|---|---|---|
| Accidental duplicate vertices | Merge by Distance | Intentional seams, gaps, and separate parts. |
| Redundant coplanar edges | Limited Dissolve | UVs, material boundaries, sharp edges, vertex attributes. |
| Loose unwanted geometry | Delete Loose | Small intentional pieces. |
| Near-zero edges and faces | Degenerate Dissolve | Thin geometry. |
| Reversed surfaces | Face Orientation and normal correction | Intentional inner surfaces and open shells. |
| Excess LOD detail | Manual removal or Decimate | Silhouette, normals, UVs, and material assignments. |

For a roughly one-meter prop, 0.1 mm can be a cautious Merge by Distance starting point when repairing selected accidental duplicates. Keep the threshold well below the smallest intentional gap. Do not use it as a global welding rule. [T3]

Keep simple backs and undersides on reusable props that can be rotated or knocked over. Remove trapped interior geometry that has no visual or gameplay use. Intended open surfaces are different from accidental holes; inspect both with backface culling enabled.

## 5 Use modifiers and controlled edge shading

| Tool | Use | Constraint |
|---|---|---|
| Mirror | Symmetrical housings and furniture | Inspect the center seam; vary only meaningful parts. |
| Array | Shelves, rails, repeated components | Count evaluated geometry; copies still cost rendering. |
| Solidify | Visible shells, panels, rims | Apply scale; inspect thickness and tight corners. |
| Boolean | Openings and larger recesses | Clean tiny faces and inspect triangulation. |
| Bevel | Edge form and highlights | Selected edges; one segment by default. |
| Weighted Normal | Broad hard-surface panels | Keep intended planes and sharp boundaries. |
| Decimate | Suitable LOD or organic candidates | Review shape, attributes, and shading. |

Use closed, well-formed Boolean cutters where practical. Try the Exact solver when overlapping or coplanar geometry causes problems. Inspect the resulting topology before adding bevels. Solver quality does not remove the need for cleanup. [T2]

### Bevel sizes for testing

| Surface | Starting width | Segments |
|---|---|---|
| Painted metal cabinet edge | 1–3 mm | 1 |
| Molded plastic housing | 2–6 mm | 1–2 |
| Wood counter edge | 3–8 mm | 1–2 |
| Broad concrete corner treatment | 10–25 mm | 1; shape damage separately |

These are visual starting points. A folded lip, rolled edge, or rounded molding may need a real profile. Keep enough flat surface between adjacent bevels; if the bevel consumes a narrow panel, reduce it or change the construction.

### Normals and final topology

Apply smoothing intentionally. Smooth By Angle classifies edges by face angle; inspect marked sharp edges as well. Weighted Normal can bias shading toward broad faces. Try Face Area and Angle with Keep Sharp, then inspect the result rather than treating the settings as mandatory. [T13]

Keep shape-changing operations before final normal evaluation. On the export copy, establish the final bevels, triangulation, and normals before baking. Use that same result for export. Preserve custom normals; do not change smoothing afterward without checking or rebaking.

Pass condition: a moving light creates stable edge highlights while broad panels remain flat-looking. Reject swollen doors, unexplained triangular gradients, bevel overlap, and rounding that erases the low-poly planes.

## 6 Bake selected detail in Blender

Use baking for selected close props, equipment, shallow recesses, embossing, and surface features that would otherwise add unnecessary geometry. Common environment props may need only geometry normals and shared materials. Simon Fuchs demonstrates the full Blender workflow on his Drone project. [A3]

1. Keep an editable source and a separate runtime export mesh.

2. Finalize the export silhouette, UVs, triangulation, and normals.

3. Build a detailed source for shallow features. Keep it aligned to the export mesh.

4. Create a cage that encloses the intended source surfaces without collecting nearby unrelated parts.

5. In Cycles, select Normal baking, Tangent space, and Selected to Active.

6. Select the detailed source first and the export mesh last so the export mesh is active.

7. Make the destination Image Texture node active in each target material, then bake to that image.

8. Save the image, export, and inspect the result in Godot before adding more detail.

### Map and UV requirements

- Try 512×512 for a selected medium prop normal map. Increase only if the normal detail survives and needs more pixels.
- Use Non-Color for normal data and a Normal Map node in Blender. Godot expects OpenGL style tangent-space normals with positive Y. [T6]
- Try an 8-pixel bake margin at 512 px, leaving enough island separation for the padding. Inspect mip levels; padding alone cannot protect a poorly packed atlas.
- When baking tangent-space normals, split UV islands at hard-edge boundaries. UV seams do not all require hard edges. [T5]
- Match the final triangulation and normal basis between the bake and the exported mesh.

The Blender Bevel shader node is a Cycles feature. Bake its shading contribution when using it as an authoring shortcut; the node itself does not become a Godot runtime feature. A normal map changes surface lighting, not silhouette, deep openings, or geometric shadow shape. [T12, T14]

### Inspect the bake

Toggle the normal map while holding the mesh and lighting constant. Look for visible surface improvement, waviness around cylinders, seams, projection from nearby parts, and inverted dents. Fix the cage, UV layout, tangent convention, or source geometry before raising texture resolution.

Evidence: capture normal off and on, the final wireframe, and the map resolution. Record texture memory and frame cost separately. Baking saves geometric detail but adds texture and shading work.

## 7 Build reusable textures and trim sheets

A trim sheet contains reusable strips of surface detail. Map door frames, counters, shelf lips, signs, and similar meshes onto those strips. Use plain tiling materials for broad uninterrupted surfaces and unique textures for selected identities. This approach is demonstrated in Sunset Overdrive, Tor Frick’s Scifi Lab, and VALORANT environment production. [A1, A2, A5]

### Start with a deli and convenience store family

| Trim element | Use |
|---|---|
| Painted metal frame | Doors, cabinets, sign borders. |
| Aluminum edge | Countertops, shelving, window frames. |
| Rubber seal | Door and window surrounds. |
| Wood molding | Counters and interior trim. |
| Panel seam | Appliances and cabinet faces. |
| Shallow vent or rib | Equipment panels where openings need not be visible. |

1. Model the strips on a flat source sheet at consistent physical scales.

2. Bake the required maps onto a plane.

3. Map test meshes to the strips and preserve comparable texel density.

4. Create plain tiling companions for broad surfaces.

5. Build a complete storefront in Godot and inspect corners, junctions, and repeated details.

### UV and density rules

Texture dimensions and texel density are different. A 512-pixel strip spanning two meters supplies 256 texels/m; the same strip spanning eight meters supplies 64 texels/m. Use the density targets in section 1 and review surfaces at comparable distances.

Mirror or stack UVs where repeated detail is acceptable. Keep readable text, distinctive damage, and asymmetrical wear from accidentally mirroring. Lightmap UVs require a separate suitable layout; a repeated trim UV layout is not a valid unique lightmap layout.

Use a checker texture to inspect stretching and scale. Reserve enough padding for filtering and mipmaps. Select texture filtering deliberately: coarse texture art can remain stylistic while mipmaps and suitable filtering improve stability in motion.

A shared atlas reduces texture duplication but does not automatically turn separate objects into one draw. Keep material resources consistent and verify instancing or batching in the engine. [T8]

Pass condition: repeated assets look related without obvious stamp-like repetition, and material changes do not shift seams or edge details unpredictably.

## 8 Author materials and purposeful wear

Make paint, plastic, rubber, metal, wood, and masonry respond differently to light. Use broad readable color regions and restrained surface detail. PBR materials can support stylized art; consistent material behavior does not require photorealistic texture density. [A7]

| Surface | Metallic | Starting roughness |
|---|---|---|
| Painted steel | 0 | 0.45–0.70 |
| Exposed worn metal | 1 | 0.25–0.55 |
| Hard plastic | 0 | 0.35–0.60 |
| Rubber | 0 | 0.70–0.90 |
| Dry brick or concrete | 0 | 0.80–1.00 |
| Varnished wood | 0 | 0.35–0.60 |

These are art presets for initial testing, not laboratory measurements. Metalness describes the visible top layer: paint and rust are normally nonmetallic; a chip exposing bare metal changes the material. Inspect under a useful reflection environment before judging metal. [A7]

### Place wear where something caused it

| Cause | Placement and treatment |
|---|---|
| Handling | Handles, buttons, coin slots; local polish or grease. |
| Impact and contact | Exposed lower corners, kick plates, equipment contact. |
| Water | Streaks below leaks, seams, gutters, and fasteners. |
| Sunlight | Fading on exposed upper and outward surfaces. |
| Repair | Mismatched panel, fresh screws, different paint coverage. |

Choose two or three relevant conditions per asset. Use procedural masks as a starting point, then edit placement and strength. The same grunge across every surface obscures construction and makes repeated assets conspicuous.

### Keep the maps useful

Base color carries pigment and identity. Roughness controls reflection spread. Normals carry shallow surface orientation. Keep strong directional highlights and shadows out of base color when the asset must respond to changing light. Use AO separately for local occlusion; it does not replace contact shadows or lighting.

Bake Blender procedural materials to the outputs the game consumes. A complicated Blender node graph does not transfer as equivalent executable shading through GLB. Start with standard materials, then justify each extra layer or shader feature.

Pass condition: the material types remain distinguishable in neutral daylight and warm interior light. The asset still reads at gameplay distance without every scratch being visible.

## 9 Lighting and style consistency

Approve the asset under neutral lighting first, then in the game’s lighting. Improve form, contact, and material response while retaining the color and shape language of the world. Keep PSX-style wobble, snapping, dithering, and quantization as deliberate presentation options.

| Asset | Preserve | Modernize |
|---|---|---|
| Building | Broad wall and roof masses | Opening depth, frame highlights, contact lighting. |
| Vehicle | Angular body silhouette | Window recesses, wheel profiles, material separation. |
| Human | Facial planes and clothing masses | Deformation, selected smoothing, major folds. |
| Rock | Strong planar breaks | Grouped colors and restrained surface response. |
| Furniture | Simple construction and proportions | Thickness, joints, bevels, material differences. |

### Three lighting checks

1. Neutral scene: fixed camera, exposure, background, and a light that reveals surface shape.

2. Warm interior: inspect roughness, dark materials, labels, and recesses in the intended 1990s setting.

3. Outdoor or night scene: confirm the object remains readable in the project’s darker and brighter conditions.

Use the same lighting for mesh before-and-after comparisons. Make lighting changes a separate comparison so the cause of improvement remains clear. Disable distracting post effects during the basic asset review, then inspect the actual gameplay presentation.

### Lighting for levels

Use baked lighting for static arrangements when the level pipeline supports it. For procedurally assembled levels, bake the final assembly offline or establish a lighting approach that works after assembly. Independently baked modules can show seams or incompatible lighting; check the assembled result.

Limit shadow-casting lights and expensive screen effects to their demonstrated contribution. Use distance and quality controls where appropriate. Real-time shadows, transparency, lighting, and pixel shading can dominate cost even when meshes are small. [T8]

Keep detail and contrast from competing with enemies, objectives, and interactable items. VALORANT’s map-art process is a useful example of repeated gameplay review and controlled environmental noise; adopt the clarity principle at the mood appropriate to this game. [A5]

Pass condition: the asset remains recognizable, materially convincing, and consistent with neighboring assets at the lowest supported quality preset.

## 10 LODs repetition culling and collision

### Reduce what stops mattering

Use the closest version for visible shape and selected detail. At greater distances, remove small bevels, handles, cable bends, interior detail, and other features that no longer contribute. Choose transitions by screen size and visible change, not a universal distance.

| Technique | Benefit | What must be checked |
|---|---|---|
| Imported mesh LOD | Reduces geometry at distance | Normals, silhouette, seams, and transition appearance. |
| Visibility ranges and HLOD | Replaces or hides whole objects or groups | Popping, culling, and loss of needed interaction cues. |
| Occlusion culling | Avoids drawing objects hidden behind geometry | Correct occluders and corner cases near the camera. |
| Instancing or MultiMesh | Reduces repeated submission work | Shared resources and visibility granularity. |
| Distance fades for lights and effects | Removes distant work | No distracting appearance changes. |

Godot supports complementary LOD and visibility approaches. Its documented automatic instancing is renderer dependent. MultiMesh visibility is managed as a batch rather than by ordinary individual-instance frustum culling, so divide repeated props into useful spatial groups and verify behavior in the selected renderer. [T8]

### Use transparent surfaces selectively

Keep opaque surfaces opaque. Isolate the portion that actually needs transparency. Thin foliage cards, glass, and particles can become expensive when many layers cover the same screen area. A low triangle count does not eliminate that pixel work. [T8]

### Collision follows gameplay

Use boxes, spheres, capsules, or other simple shapes when they represent gameplay adequately. A cabinet collider rarely needs handles, bevels, hinges, or panel gaps. An opening door needs collision that follows its motion.

Use a small number of convex shapes when primitives cannot describe a dynamic object. Reserve appropriate concave triangle collision for static geometry that needs it. Inspect walkable openings and ledges deliberately; decorative detail should not snag movement. [T9]

Keep collision separate from render geometry and review the two together. A complex visible model can have simple collision; a visually simple archway still needs collision that leaves the opening usable.

Pass condition: the worst expected gameplay view remains within the frame target, LODs remain visually acceptable, and collision permits the intended movement and interactions.

## 11 Export Blender assets to Godot

Keep the editable source as a .blend file. Use .glb for the normal game handoff unless the project specifies another supported route. Godot recommends glTF; direct .blend import also uses a Blender-to-glTF conversion. [T7]

| File or component | Purpose |
|---|---|
| .blend source | Editable objects, modifiers, source textures, and clearly separated baking/cutter collections. |
| .glb asset | Runtime geometry, node transforms, materials, and supported animation data. |
| Texture files | Source and runtime maps when required by the project; identify shared atlases. |
| Collision and LOD definitions | Simple shapes or source meshes and documented engine settings. |
| Asset record | Budgets, dimensions, pivots, use, and review evidence. |

### Export checks

- Export only the intended asset set. Keep cutters and dense baking sources out.
- Evaluate the intended modifiers and inspect the final triangle count.
- Preserve UVs and normals. Check tangents for normal-mapped assets in the imported result.
- Verify scale, upright direction, forward direction, origins, and attachment points.
- Check backface culling so closed opaque objects do not become unintentionally double-sided.
- Reimport into a clean scene and inspect materials, object separation, and animation.
- Inspect the same file in Godot; a correct Blender viewport is not sufficient.
### When an OBJ file is required

OBJ is suitable for basic static geometry exchange. It does not preserve an editable Blender modifier stack. Godot documents limitations for pivots, skeletons, animation, UV2, and PBR materials. Plan to rebuild any missing setup at the destination. [T7]

| OBJ setting | Requirement |
|---|---|
| Selection and modifiers | Only intended objects; export the evaluated result. |
| UVs and normals | Enable both. Preserve custom shading where supported. |
| Triangulation | Match the mesh used for baking. |
| Materials and textures | Include .mtl and referenced textures if needed; inspect the destination materials. |
| Axes and scale | Use the destination conversion and verify a known one-meter dimension and forward marker. |

Blender’s OBJ exporter supports evaluated geometry, UVs, normals, and triangulation. OBJ file size and Blender object count do not establish runtime cost. Measure the imported asset. [T10]

## 12 Worked example for a deli cabinet

Use this as the first common-prop prototype. It tests construction, object separation, thickness, selected bevels, normals, and simple collision. The dimensions are an illustrative game-asset specification.

Overall size: 1.2 m wide × 0.65 m deep × 0.9 m high.

| Part | Proposed construction | Mesh treatment |
|---|---|---|
| Carcass | About 18 mm boards | Simple panels; interior only where visible. |
| Countertop | About 30 mm thick | Solid slab with selected edge treatment. |
| Two doors | About 18 mm thick | Separate objects if they open. |
| Door reveals | About 3 mm | Actual spacing, reviewed at the camera distance. |
| Toe kick | 100 mm high; 50 mm setback | Simple recessed base. |
| Handles | Recognizable manufactured profile | Low-sided geometry with usable visual clearance. |
| Hinges | Only as exposed or needed | Represent visible operation; simplify concealed parts. |

1. Make a box at the overall dimensions and compare it with the player reference.

2. Block in countertop, doors, and recessed base.

3. Add visible board thickness, reveals, and handle clearance.

4. Place door origins at hinge axes if the doors open.

5. Add small selected bevels and inspect smoothing on broad faces.

6. Finalize and triangulate an export copy, then add simple collision.

7. Test the result in Godot at close, normal, and distant views.

Initial triangle target: 400–900 for a simple static version. An opening version may need more for interior surfaces and hardware. Keep the result simpler if it already works; do not fill the budget.

| Version | Change | What the comparison answers |
|---|---|---|
| A | Basic boxes | Are the proportions correct? |
| B | Thickness, gaps, recesses, attachments | Does construction improve believability? |
| C | Selected bevels and corrected normals | Does edge shading justify the added geometry? |

Use identical neutral lighting for A, B, and C. After selecting the mesh, add the shared counter materials and deliberate wear. The countertop should feel thick, the doors should fit their frame, and the handles should look graspable before textures carry the result.

## 13 Worked examples for a payphone and storefront

### Payphone as a selected close prop

A payphone tests recognizable construction, several materials, readable text, curves, and close inspection. Keep its broad housing angular enough to match the environment.

| Component | Treatment |
|---|---|
| Housing | Simple mesh with selected one-segment bevels. |
| Handset | Enough geometry for the grip and recognizable outline. |
| Cable | Low-sided tube; reduce small bends in distant versions. |
| Coin return | Real recess if the permitted camera can see into it. |
| Screw slots and shallow seams | Baked normals where they remain legible. |
| Instructions and brand | Base color with UV space for readable information. |
| Wear | Local roughness at contact areas; small paint chips with material changes. |

Initial targets: 1500–2500 triangles; one opaque material where practical; 512 px base color; optional 512 px normal map; a smaller packed mask map if it survives inspection. Separate the handset if interactive. These are proposed experiment limits, not measured results.

Compare the original low-poly version, the construction-and-normal revision, and the material revision under fixed lighting. Toggle the normal map separately. Check that labels, material separation, and highlights improve at normal viewing distance.

### Storefront as the reusable environment test

Build one storefront containing a recessed doorway, projecting sign, sill, window frame, awning or canopy, and a few repeated fixtures. Use a small trim family with plain tiling companions. Model the parts that reveal depth; keep brick pores and ordinary surface scratches in textures.

- Prove that straight sections, corners, and junctions assemble without gaps or accidental overlaps.
- Confirm consistent texel density and alignment across shared trims.
- Place repeated modules together to expose obvious texture repetition.
- Separate opaque and transparent surfaces deliberately; test the combined scene cost.
- Check interior/exterior junctions, collision openings, LODs, and any baked-lighting seams.

Approve the cabinet, payphone, and storefront before expanding the asset library. Together they exercise the common-prop, close-prop, and modular-environment workflows.

## 14 Prove visual improvement and runtime cost

Published work demonstrates that the techniques can produce convincing results. It does not establish their cost in this project. Use controlled comparisons of exported assets and record the conditions.

| Review | Capture | Acceptance condition |
|---|---|---|
| Silhouette | Black shape at three relevant distances | Identity and intended faceting remain clear. |
| Construction | Gray material, neutral view | Thickness, joints, openings, and attachments make sense. |
| Shading | Moving light on a neutral material | Stable highlights; no swollen panels or unexplained gradients. |
| Materials | Daylight and warm interior | Material types remain distinct and fit the style. |
| Motion and distance | Approach, orbit, retreat, animation | No distracting shimmer, seams, LOD collapse, or deformation. |
| Export | Clean import plus Godot view | Scale, UVs, normals, materials, pivots, and separation survive. |
| Runtime | Identical representative gameplay route | Cost fits the project target and any change is reported. |

### A repeatable performance comparison

1. Record hardware, renderer, resolution, quality settings, build, camera route, and visible population.

2. Warm shaders and the scene before steady-state comparisons; report loading or compilation hitches separately.

3. Run the same route at least three times for the baseline and revision. Keep unrelated effects and simulation load comparable.

4. Capture CPU and GPU frame times, typical and slow frames, draw calls, visible geometry, texture memory, and shadow-casting lights.

5. Test a representative worst view with enemies, effects, and the expected repeated assets. Include the lowest supported quality preset.

Use uncapped or otherwise non-limited profiling when diagnosing cost so a frame cap does not hide changes; also test the actual shipping settings. Compare distributions or percentiles as well as averages. Investigate repeatable spikes.

Performance-neutral means the observed difference falls within repeat-run variation under those conditions. Otherwise report the measured increase and the visible improvement. There is no tested millisecond saving asserted by this document.

If a scene is pixel-, shadow-, or transparency-limited, reducing triangle count may not solve it. If submission dominates, resource reuse, instancing, and culling may matter more. Follow the measured bottleneck. [T8]

## 15 Creator handoff and acceptance checklist

### Supply this record for each asset

| Field | Required information |
|---|---|
| Identity | Asset ID, category, revision, and intended use. |
| Scale and placement | Dimensions in meters, pivot, forward direction, attachment points. |
| Viewing conditions | Closest and normal distances, camera settings, expected repetition. |
| Construction | Reference, recognizable features, separate moving parts. |
| Mesh counts | Evaluated/exported triangles and vertices for each LOD. |
| Materials and textures | Surface count, shared resources, map dimensions, texel density. |
| Collision | Shape types, moving parts, and intended interaction boundaries. |
| LOD and visibility | Versions, transitions, spatial grouping, and exceptions. |
| Evidence | Comparison images, short motion capture, test conditions and performance result. |
| Files | Editable source, export, required textures, and import/setup notes. |

### Accept when all of these hold

- The gray mesh reads correctly at gameplay distance and fits the approved style.
- Every added edge supports visible form, construction, shading, deformation, or a required vertex attribute.
- Thickness, joints, recesses, attachment, and motion are plausible.
- Exported topology and normals are clean; baking and runtime meshes agree.
- Texture detail is stable and materials remain consistent under the required lighting.
- Collision, pivots, and LODs work in the engine.
- Budgets and performance results are recorded, including any justified exceptions.
### Instructions for procedural asset tools

Require inputs for dimensions, construction type, viewing distance, repetition, interaction, silhouette features, resource limits, and material family. Choose geometry from those inputs. Preserve separate moving parts and spatial grouping. Emit the asset record with the mesh.

Reject silent budget overruns, hidden dense sources in exports, unexplained global smoothing, unsupported material graphs, and claims of equivalent performance without a comparison. When a feature fails review, revise the specific cause rather than increasing detail across the asset.

## Addendum A: subdivision, sculpt and retopology, multires -- and where each fits here

*Added 2026-10-08 from the walker's notes, a sculpt-and-retopology
walkthrough and a Blender retopology tutorial. It is not in the original
`.docx`. Written for this project, not transcribed.*

**Why it is here.** The default target is modernized low poly, and section
6 bakes selected detail. Three Blender workflows decide how good a hard
prop's edges and an organic piece's forms can look:
- **subdivision modeling**, for hard surfaces;
- **sculpt and retopology**, for organic forms;
- **multires**, for detail sculpted on a clean mesh.

**None of them puts a subdivided or sculpted mesh in the game.** The rule
above stands: "Use no automatic subdivision of the runtime mesh." What they
make is a better bake source, a cleaner game mesh, or both.

### A.1 Subdivision modeling and the topology that goes with it

**What it is.** A coarse cage, smoothed by a Subdivision Surface modifier.
Where an edge must stay hard, something holds it:
- **support loops** (holding or control edges) run parallel and close to
  it; the closer, the tighter the curve;
- **edge crease** weights;
- **a bevel** of two or three segments, applied before the subdivision.

**The topology that goes with it:**
- **Quads where the surface curves.** Triangles and n-gons only on flat
  regions: a flat n-gon subdivides cleanly, a curved one pinches.
- **Poles off the highlights.** A pole is a vertex with three edges, or five
  or more. Put them on flat areas, never where a highlight runs.
- **Support loops evenly spaced.** Keep them parallel and evenly spaced, and
  as few as hold the shape.

**Edge reduction.** These keep the cage light by stopping a loop from
running across the whole model:
- 2-to-1 and 3-to-1 reductions;
- a loop ended in a triangle or a pole on a flat area;
- a loop routed round a cut-out;
- Limited Dissolve on coplanar edges.

**Where it fits here.**
- **As a bake source.** The subdivided high-poly's rounded edges bake into
  the game mesh's normal map (section 6, Selected to Active). The game mesh
  keeps its triangles, and its edges catch light like a casting's.
- **As a hero mesh,** subdivision level 1 applied, and only for the
  "selected hero" tier, priced. Each level multiplies the faces by four.
- **Never as a runtime modifier.**

**Its cheaper cousin is already in Zoo:** one-segment bevels, smooth-by-angle
shading, and weighted normals (the one not yet used). Choose between them:
- **bevels and normals** when the radius shows at gameplay distance and
  geometry is cheap;
- **a subdivided bake source** when the edges are small and many (a
  payphone's housing, a register's keys) and a texture is affordable.

### A.2 Sculpt and retopology

**The workflow,** for characters, food, fabric and padding, rocks, dents and
damage:
1. **Block the shape** by any means: a voxel remesh of joined pieces,
   booleans, Dyntopo sculpting. Ignore the topology.
2. **Sculpt only the forms that change the silhouette.** Keep the
   resolution as low as the shape allows; more only slows the work.
3. **Retopologize.** Build the game mesh on top of the sculpt, snapped to
   its surface. The sculpt is a mold, not the model.
4. **Discard the sculpt,** keeping a copy.
5. **Put multires on the clean mesh,** and sculpt the fine detail that does
   not change the silhouette.
6. **UV unwrap, then bake from multires:** normals for a game mesh,
   displacement for a film one.
7. **Apply the maps and remove multires,** keeping a backup.
8. **Colour,** by one of:
   - vertex paint on the detailed mesh in Sculpt Mode (multires applied on a
     copy), baked to an image, with cavity masking to tell bumps from
     crevices;
   - a cavity or curvature map recoloured as the base of the texture;
   - an external painting application.

   Texture Paint mode is the weakest of these: old and slow.

**Retopology practice.**
- **Snapping.** Snap to the sculpt's surface (Face Project, projecting
  individual elements).
- **A Shrinkwrap modifier,** Above Surface with a small offset, and On Cage,
  so the new vertices show above the sculpt.
- **Mirror with Clipping** on a symmetric piece. Hide the mirror while
  working near its plane, so a click does not take a vertex on the far
  side.
- **Quads of even size,** smaller where detail lives. A few triangles where
  they hide; n-gons avoided.
- **Loops follow the form's flow:** round the eyes and the mouth, along
  creases and folds. Then the shape holds with few faces.
- **Tools.** Loop Cut adds resolution where a region is too coarse; Edge
  Slide evens the spacing; F fills.
- **Back up before applying** the Mirror and the Shrinkwrap.

**Where it fits here.** Human-made assets:
- enemy characters (section 1's 6,000-12,000 triangle range);
- food, padded seating, sculpted damage.

Zoo does not sculpt. A human-made asset enters the factory through Zoo's
ingest (Zoo's README, "Adopting external assets") and is held to this
standard.

### A.3 Multires

Subdivision that can be sculpted at several levels over a fixed base mesh.
Blender bakes normal or displacement maps from it ("Bake from Multires"),
the only way it bakes displacement.

**Here: normal maps only.** Displacement needs a subdivided render mesh,
which the runtime rule forbids.

### A.4 What procedural props can take from this

These are ways for Zoo's hard models to look better than today. Each is a
look, so each is a trial priced on and off at fixed stations before it
ships:
1. **Weighted normals on bevelled parts.** The cheapest: no textures, no
   triangles.
2. **Convex-edge wear in vertex colour.** Zoo's `wear_colors` darkens
   concave vertices and adds grime; it does not lighten or chip exposed
   edges. Wear by shape is the cavity mask above, at no texture cost.
3. **A procedural bake source.**
   - A second build of the same recipe, its hard edges creased or
     support-looped under a Subdivision Surface modifier, is the high-poly.
   - Cycles bakes a tangent-space normal map from it onto the game mesh
     (Selected to Active).
   - The cost: one texture per species (section 6's 512 px start), no
     triangles.
   - Zoo bakes nothing today.
4. **Procedural detail on the bake source only:** noise, dents, weld seams,
   panel lines.

### A.5 What does not change

- **No subdivided or sculpted mesh in a runtime export.**
- **A normal map is a texture,** in the part family's one material, not a
  new material. Draw calls are this project's budget.
- **Triangles are counted on the game mesh,** after any of this. The bake
  source's are not counted.

## 16 Artist and production references

These references supply visible results and workflows. The proposed numbers in this standard are not attributed to these projects. Older tutorials may use different interface labels or software; carry across the method and verify the current export.

[A1] Morten Olsen   The Ultimate Trim for Sunset Overdrive

Shipped-game production presentation. Study the standardized trim layouts, normal-map edge treatment, and comparisons with and without normal detail. Use for storefronts, frames, counters, and building kits.

[A2] Tor Frick   Scifi Lab

Finished artist experiment. Frick reports two 256×512 textures for diffuse/masks and normals. Study UV reuse and variety from limited texture resources; the experiment is not a benchmark for this project.

[A3] Simon Fuchs   Blender Drone

Blender game-asset demonstration covering modeling, UVs, baking, and finish. Study construction, Boolean workflow, and baking at a lower detail target. The full course is paid and uses an older Blender interface.

[A4] Adam Idris   Environment breakdown

Completed portfolio environment. Study limited bevels, weighted normals, and trim use for older industrial equipment. Treat it as an artist example, not proof of a shipped runtime budget.

[A5] Lydia Zanotti   The Art of VALORANT Map Environments

Shipped-game process from an environment artist. Study blockout progression, reuse of tiling textures and trims, selected unique props, visual clarity, and engine reviews.

[A6] Frozenbyte   Retopology and blockset production

Studio workflow with wireframes. Study density, viewing distance, rigid versus deforming topology, and reuse. Follow the Blocksets link in the workflow for assembly guidance; examples use Modo.

[A7] Joe Wilson   Physically Based Rendering And You Can Too

Material guide with artist examples. Study material separation, paint versus exposed metal, roughness, and consistency across lighting conditions.

[A8] Josh Gambrell   Blender Boolean Cleanup Topology Study 1

Focused Blender topology exercise. Use for cleanup practice alongside export testing; a modeling tutorial is not an engine performance benchmark.

## 17 Technical references

Sources consulted for the guidance in this document on 8 October 2026. Use the documentation for the installed Blender and Godot versions when menu labels or import behavior differ.

[T1] Blender   Bevel modifier

Edge selection, widths, segments, overlap handling, and hardened normals.

[T2] Blender   Boolean modifier

Boolean solver behavior, overlapping geometry, and manifold restrictions.

[T3] Blender   Mesh cleanup

Cleanup operations including degenerate and limited dissolve. Merge by Distance is a distinct operation and should be scoped to the intended vertices.

[T4] Blender   Join objects

Object joining behavior and modifier limitations. Related: Duplicate Linked for shared mesh data.

[T5] Marmoset   Baking Tips and Tricks

Triangulation, hard edges, UV boundaries, and normal-map troubleshooting. Blender execution steps use Cycles baking.

[T6] Godot   Importing images

Normal-map convention, texture import, and compression. Use positive-Y OpenGL style tangent-space normal maps.

[T7] Godot   Available 3D formats

Recommended glTF workflow, direct Blender import, OBJ limitations, and material culling.

[T8] Godot   Optimizing 3D performance

LOD, visibility, instancing, transparency, and baked lighting. Follow its GPU optimization and MultiMesh links for bottlenecks and batch visibility limits.

[T9] Godot   Collision shapes in 3D

Primitive, convex, and concave collision choices and their intended use.

[T10] Blender   Wavefront OBJ

Evaluated modifiers, UV coordinates, normals, triangulation, axes, and material export.

[T11] Blender   glTF export

Exported vertex splits, mesh attributes, material support, and export settings.

[T12] Blender   Cycles render baking

Selected to Active, tangent-space normals, cages, target images, and margins.

[T13] Blender   Weighted Normal modifier

Face weighting, Keep Sharp, and custom normal behavior.

[T14] Blender   Bevel shader node

Cycles bevel shading and the distinction between shader appearance and geometry.
