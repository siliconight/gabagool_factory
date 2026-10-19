# Low-Poly Appearance, High Triangle Counts
## A Geometry Audit and Optimization Playbook for Blender → Godot 4.7

**Audience:** Procedural asset creator, level generator, rendering/optimization engineer, technical artist, QA/performance engineer  
**Applies to:** Blender-authored or script-generated assets; imported and procedurally generated Godot 4.7 3D scenes; stylized, low-poly-to-semi-realistic environments; repeated urban props and modular buildings  
**Status:** Engineering guidance and diagnostic plan. Numeric budgets are **starting hypotheses**, not proven project limits. Scripts below are intended as audit starting points and must be tested in the project's exact Blender/Godot versions.  
**Principle:** **Spend geometry on visible value, and measure what the GPU is actually asked to do.**

---

## 1. Problem statement

Our levels have a comparatively low-poly appearance: simple architectural silhouettes, modest surface detail, straightforward props, and an intentionally restrained geometric style. Yet their reported runtime geometry counts may be considerably higher than that appearance implies.

This mismatch does **not** by itself prove the assets are poorly made. It is a signal to investigate whether:

1. The source meshes contain more triangles than their silhouettes warrant.
2. Blender's modifiers or procedural operations inflate evaluated geometry.
3. Export and import change the apparent vertex layout or mesh structure.
4. Many individually inexpensive assets accumulate into an expensive scene.
5. Godot renders more geometry than is useful from the current camera.
6. Depth, shadow, and other rendering passes inflate runtime work statistics.
7. The number being called “triangles” is not actually a unique triangle count.

**Primary engineering question:** *For every meaningful category of geometry cost, can we identify where it originates, why it exists, whether a player can perceive its benefit, and whether removing it measurably helps runtime performance?*

**Desired outcome:** Better visual quality *per unit of rendering cost*, not the smallest possible poly count.

### A short articulation for the team

> The level looks simpler than its reported geometry cost. We need to determine whether we're generating excessive topology, repeating too much geometry, or submitting unnecessary geometry to the renderer. Start by separating source triangles, imported triangles, placed scene triangles, and frame-level rendering statistics. Then fix the largest costs that provide the least visible or gameplay value.

---

## 2. Terms that must not be confused

| Measure | What it actually means | Why it matters |
|---|---|---|
| **Blender polygons/faces** | Faces in the authored mesh; a face can be a triangle, quad, or n-gon | A count of 1,000 quads is generally **2,000 triangles**, not 1,000 |
| **Blender base triangles** | Triangulated equivalent of the unmodified mesh | Detects unnecessary topology present before modifiers |
| **Blender evaluated triangles** | Triangles after visible evaluated modifiers / mesh generation | Closer to the geometry exported, depending on export settings |
| **Imported mesh triangles** | Triangle primitives in Godot's imported mesh resource | Checks source-to-engine topology changes |
| **Packed/render vertices** | Vertices in GPU-facing attribute buffers, possibly duplicated at UV, normal, and material boundaries | Drives vertex memory and processing, **not necessarily triangle count** |
| **Per-instance geometry** | A mesh's triangles × number of placed copies | Finds repetition-driven costs |
| **Scene triangle inventory** | Sum of mesh triangles across loaded scene placements | An upper-level asset inventory; **not** a frame draw count |
| **Visible / submitted geometry** | Geometry selected for drawing from a given camera, after culling and LOD decisions | Approximates relevant per-view geometry demand |
| **Frame rendering primitives monitor** | Godot's monitor reporting vertices or indices submitted across render passes | May be much larger than source triangles; **do not label it literal unique triangles** |
| **Draw calls** | Render submissions, influenced by objects, mesh surfaces, materials, passes, and batching | Can bottleneck the CPU/driver even when triangles are low |
| **GPU / CPU frame time** | Actual time spent rendering / simulating | Determines whether a supposed optimization improves player experience |

### Why quad count misleads

- An ordinary cube has **6 quad faces** and **12 triangles**.
- A 40 × 20 rectangular grid of quads has **800 quads and 1,600 triangles** even though its outer silhouette is still a rectangle.
- A flat wall constructed as one quad takes **2 triangles**; the same wall subdivided into 40 × 20 grid cells takes **1,600 triangles**, unless that internal topology is required for deformation, vertex coloring, displacement, or another verified purpose.
- Triangulating an n-gon does not automatically indicate a bug. The relevant question is whether the original polygon contains more detail or complexity than necessary, and whether triangulation produces valid geometry.

### Why flat shading does not mean low geometry

A dense mesh can be flat-shaded and visually read as low-poly. Texture style, flat colors, and simple silhouettes are **aesthetic properties**; triangle count is **topological**. Style should not be treated as an optimization guarantee.

### A critical correction about normal/UV seams

Sharp normals, flat shading, UV seams, and material boundaries can cause **vertex duplication in exported GPU buffers**. They do **not inherently multiply the number of geometric triangles**. Audit **triangle count and imported vertex count independently**. A rising vertex count with stable triangle count points to a different issue from excessive subdivision.

---

## 3. The four measurements that settle most disputes

Track four different numbers, consistently named:

| ID | Name | Unit | Meaning |
|---|---|---|---|
| **G1** | `blender_evaluated_tris` | Triangles / asset | Geometry after evaluated Blender modifiers; before engine import |
| **G2** | `godot_mesh_tris_lod0` | Triangles / mesh resource | Base (highest-detail) imported mesh's triangle count, not camera-adjusted LOD |
| **G3** | `scene_placed_tris_lod0` | Triangles / loaded placements | G2 × counts of `MeshInstance3D` and `MultiMesh` placements; not view culled |
| **R1** | `runtime_render_primitives` | Godot monitor units / frame | Engine-reported vertices/indices across rendering passes; **not interchangeable with G1–G3** |

Alongside these, always capture `draw_calls`, rendered objects, CPU time, GPU time (when available), and frame-time percentiles. If GPU timing is unavailable on the current backend, mark it **unavailable**, not 0.

**Never report `R1/G3` as a scientific “triangle inflation ratio.”** G3 counts all loaded placements at LOD0, while R1 uses different units and includes rendering passes. Compare G1 ↔ G2 on the *same mesh* and use R1 only for *controlled runtime A/B measurements*.

### What each comparison can prove

- **G1 high for a simple asset:** Source mesh density or Blender procedural construction is suspect.
- **Blender base triangles low, G1 high:** Evaluated modifiers or generators are adding topology.
- **G1 and G2 close, but G3 high:** Placement count and reuse are the primary explanation.
- **G3 high but camera R1 remains low:** Effective culling, LOD, and/or visibility may already be limiting submitted work.
- **R1 unexpectedly high in specific cameras:** Investigate culling, LOD, shadow-pass workload, depth pass, and visibility layout.
- **R1 improves but GPU milliseconds do not:** Triangle throughput may not be the actual bottleneck. Examine shaders, overdraw, draw calls, lighting, texture bandwidth, and CPU work.

---

## 4. Cause taxonomy and how to recognize it

| Cause | Distinctive signature | Owner | First action |
|---|---|---|---|
| **Unnecessary edge loops** | Flat surfaces have grid-like topology with no silhouette or shading purpose | Asset creator | Inspect wireframe, dissolve nonfunctional loops |
| **Overly fine Bevel / Subdivision** | `evaluated_tris / base_tris` grows dramatically | Asset creator | Compare modifier levels; reduce segments or replace with normal detail |
| **High radial segmentation** | Tiny pipes, cables, handles, bottles, and poles contain 24–64-sided round geometry | Asset creator | Set screen-size-aware radial sides |
| **High-density Boolean or remesh results** | Dense irregular triangulation remains after mesh operations | Asset creator | Retopologize or generate clean procedural topology |
| **Procedural grid over-tessellation** | Roads, lots, roofs, and walls use a dense grid for surfaces that are visually planar | Generator engineer | Separate shape boundaries from surface subdivision |
| **Unintended internal/back faces** | Inner surfaces exist under opaque walls, roofs, floors, terrain, or intersecting props | Asset creator | Remove only when not needed for interiors, damage, visibility, or two-sided use |
| **Duplicate/coincident objects** | Identical or overlapping meshes appear in the same location | Generator engineer | Add duplicate-placement checks |
| **Overlapping modular pieces** | Every module carries hidden end caps, overlapping floors, or unnecessary connection geometry | Asset creator + level generator | Define connector/adjacency rules |
| **Excessive repetition** | Modest asset tris × very high placement counts | Level generator | Rank `(mesh tris × count)`; introduce density rules and LOD |
| **Too many mesh surfaces/materials** | Triangle count modest but draw calls and material state changes high | Asset creator + optimizer | Reduce unnecessary material slots; share materials |
| **Unhelpful batching** | One huge mesh or widely scattered MultiMesh never culled in smaller parts | Optimizer | Partition by block, room, or visibility cell |
| **No useful LOD** | Distant detail remains high cost | Optimizer | Verify import LOD generation; use HLOD or manual LOD where useful |
| **Poor occlusion opportunities** | Most of town renders even when behind solid buildings | Level engineer + optimizer | Test occlusion culling and spatial organization |
| **Expensive shadow submission** | Large runtime-monitor change when shadows are toggled | Optimizer | Triage shadow casters, ranges, and light setup |
| **Metric misinterpretation** | Godot monitor appears far larger than imported triangle inventory | Optimizer | Verify monitor's units and passes before changing assets |

### Important exceptions

Do not delete geometry just because it is hidden *right now*. It may be intentionally needed for:

- Enterable interiors or doors and windows that can open.
- Destruction, damage states, and modular reassembly.
- Multiplayer cameras in different rooms and viewing angles.
- Silhouettes seen from elevated positions, balconies, roofs, and traversal routes.
- Mirror-like effects, reflections, shadow casting, or cinematic cameras where applicable.
- Physical or navigation semantics when a separate collision/navigation asset is not yet provided.

**Rule:** Label geometry `required`, `conditionally required`, or `removable` based on documented use cases. Never equate invisible *from the current camera* with globally unnecessary.

---

## 5. Blender asset-authoring rules

### 5.1 Build silhouette-first, not subdivision-first

1. Define the required player-facing silhouette, including close inspection distances.
2. Build the fewest segments that hold that silhouette at intended gameplay distances.
3. Spend extra geometry only where it changes shape, shading in a visibly important way, animation/deformation, collision-sensitive presentation, or a critical hero prop.
4. Move small grooves, scratches, seams, stickers, grout, wood grain, brick detail, and shallow panel boundaries to **textures, trim sheets, decals, normal maps, or vertex colors** where reasonable.
5. Keep separate the concepts of **visual mesh**, **collision mesh**, **navigation mesh**, and **occluder geometry**. They have different optimization goals.

**Use geometry when it changes silhouette, spatial depth, or parallax enough to matter. Use surface detail when it only changes the appearance of a surface.**

### 5.2 Source-generation safeguards

Procedural generators should explicitly declare:

- `asset_type` and `visual_importance`: background / normal / hero.
- `expected_viewing_distance_m`: expected near/far ranges.
- `silhouette_tolerance`: permissible deviation at target screen size.
- `radial_segments`, `bevel_segments`, `subdivision_levels`, `curve_resolution`, and `remesh_resolution` where relevant.
- `include_interior_geometry` and `is_enterable`.
- `occludes_others`, `casts_shadow`, and `receives_shadow` as intentional choices, not globally hard-coded true/false.
- `lod_strategy`: auto import / manual / HLOD / impostor / not warranted.
- `collision_strategy`: proxy primitives / convex decomposition / detailed mesh where justified.
- `instance_reuse_key` or mesh-sharing identifier.

If the generator cannot articulate the purpose of an expensive feature, default to the simpler version and flag it for a visual review.

### 5.3 Appropriate segmentation: start with view distance

| Asset/feature | Typical failure | Better starting strategy |
|---|---|---|
| Long straight wall | Grid subdivided every small interval | 2 tris per rectangular panel; add cuts only for real openings and geometry changes |
| Building roof plane | Dense tessellation over flat surface | Large planar faces; detail at eaves, ridges, openings, and silhouettes |
| Road / sidewalk | Regular high-resolution grid everywhere | Segmentation only for road shape, curb turns, terrain conformity, or deformation requirements |
| Telephone pole / pipe | 32–64-sided cylinder at normal gameplay distance | Try 6–12 sides where silhouette supports it; use more only for hero close-ups |
| Curved sign/frame | Excessive spline/curve resolution | Adaptive tessellation by curvature and on-screen error |
| Bottle / can / trash bin | Many rings not visible in profile | Remove redundant longitudinal and radial loops |
| Windows / door trim | Thick modeled subdivisions on every copy | Shared simple profiles, trim textures, limited hero variants |
| Trees / foliage | High-tri branches and leaves on hundreds of instances | Scale-aware geometry and foliage LOD; validate alpha overdraw as a separate cost |

These are **design heuristics**, not fixed asset triangle limits.

**Example:** A capped 32-sided cylinder with one row of side quads typically triangulates into **124 triangles** (64 side + 60 cap triangles). A similarly capped 12-sided cylinder is **44 triangles**. That's **80 triangles per object**, or **80,000 triangles across 1,000 placements** before LOD/culling. Exact output varies with cap topology and generators.

### 5.4 Modifiers to inspect before export

| Modifier/process | Risk | Audit rule |
|---|---|---|
| Subdivision Surface | Multiplicative topology growth | Record base vs evaluated; prohibit accidental export/render levels |
| Bevel | Excess rings around edges | Limit bevel segments based on intended screen-space benefit |
| Solidify | Duplicates surface shell; may be appropriate | Confirm the asset actually needs thickness or double-sided construction |
| Boolean | Dense/dirty output or sliver triangles | Audit evaluated result, degenerates, and topology |
| Remesh / Voxel Remesh | Adds uniform detail unrelated to shape | Use the coarsest resolution that preserves necessary form; clean output |
| Array / Mirror | Expands geometry as intended, sometimes unnecessarily | Distinguish deliberate repeats from duplicated final meshes |
| Geometry Nodes | Can realize huge numbers of instances or geometry | Inspect evaluated output **and** actual instances; preserve instancing where practical |
| Curves / bevel depth | Small tubes become heavily tessellated | Enforce radial and path-resolution budgets |
| Triangulate | Exposes final triangles | Useful for controlled diagnosis; not a substitute for decimation |

**Do not indiscriminately apply Decimate.** It can ruin silhouette, UVs, normals, material boundaries, and small hero details. First remove avoidable generated topology, then evaluate selective simplification.

### 5.5 Material, UV, and normal discipline

- Prefer shared reusable materials, palettes, atlases, and trim sheets when they preserve the look.
- Remove accidental extra material slots and split surfaces.
- Inspect UV islands and sharp edges for **packed vertex inflation**, not assume they increase geometric triangle count.
- Do not use extra geometry just to give every tiny surface a unique color if vertex colors or textures can deliver the same effect.
- Preserve intentional hard-edged lighting and stylization; optimization should not turn the project into featureless smooth shading.

### 5.6 Blender acceptance checks

An asset should ship with:

- Base and evaluated triangle counts.
- Evaluated/base ratio.
- Modifier inventory and any geometry-changing operations.
- Intended near/far viewing distances.
- Unique material/surface count and expected placements.
- Whether geometry is required for interiors, destruction, silhouette, or gameplay.
- At least one close-up and one intended-distance visual comparison against a simpler variant.
- A brief justification if it exceeds its asset-category baseline.

---

## 6. Godot 4.7 scene-construction rules

### 6.1 Verify import before blaming runtime

Use Blender's **evaluated** counts as the source reference. After import to Godot, measure base mesh `ArrayMesh` indices and vertices for each surface. Check for unexpected differences in primitive topology, split mesh parts, or duplicate imported objects.

Godot's automatic mesh LOD generation normally applies to imported **3D scenes** such as glTF and `.blend`. The 4.7 documentation notes different behavior for OBJ imported as a simple mesh resource; verify the actual importer settings for each asset type. [Godot mesh LOD]

A **higher imported vertex count** can be legitimate because UV/normal/material boundaries require distinct attributes; the imported **triangle count** may still match Blender.

### 6.2 Prefer visibility-aware geometry organization

For a town or heist level, group static geometry into sensible spatial chunks:

- Street segments and intersections.
- Individual buildings or a few adjacent facades.
- Rooms, floors, interiors, courtyards, and occlusion zones.
- Distant background blocks and skyline geometry.

**Bad:** One giant combined city mesh, where seeing one curb forces the entire mesh to remain a culling candidate.  
**Also bad:** Every piece of trim or brick becomes a separate tiny draw submission.  
**Preferred:** A measured middle ground: combine predictable nearby static details where useful, but retain enough partitions for culling and LOD.

Batching reduces submissions, **not automatically triangle count**. A bigger combined object can reduce draw calls while making visibility culling worse. Profile both directions. [Godot GPU optimization]

### 6.3 MultiMesh is a batching tool, not free geometry

`MultiMeshInstance3D` is useful for repeated poles, shrubs, fencing, bins, small clutter, and similar reusable pieces. It can greatly reduce draw-call overhead. However, the 4.7 documentation warns that a MultiMesh is spatially treated as one object, so instances spread too widely can undermine culling. [Godot MultiMesh]

**Do:** Partition repeated placements into spatial MultiMeshes (per block, room, or street) when justified.  
**Don't:** Put every piece of town clutter, from end to end of the map, into one enormous MultiMesh without comparing runtime performance.

### 6.4 LOD choices

| Situation | First candidate | Reason |
|---|---|---|
| Typical imported mesh with meaningful distance variation | Automatic mesh LOD | Lowest authoring overhead; inspect simplification quality |
| House/building visible across large distances | HLOD / simplified building shell | Can replace many detailed objects with a coarse grouped representation |
| Dense repeated foliage / props | Mesh LOD + local MultiMesh partitions | Addresses both geometric detail and submissions |
| Far-away skyline | Purpose-built distant mesh / impostor | Full playable geometry rarely warranted |
| Room never visible from the active area | Spatial partition / occlusion / selective visibility | Avoids unnecessary submission |
| Hero item viewed very near camera | Intentionally higher LOD0 detail | Visual benefit may justify cost |

**Caution:** A static audit that sums all loaded LOD nodes overstates what the camera may render if alternate HLOD nodes coexist. Record both the authored inventory and the runtime-visible result.

### 6.5 Occlusion culling

Godot already frustum-culls out-of-view objects. Occlusion culling is different: it can avoid drawing objects behind other geometry. It is especially promising for tightly packed streets, interiors, courtyards, walls, and block layouts with interrupted sightlines. It requires setup and has CPU cost, so test rather than assuming universal gains. [Godot occlusion culling]

For the level generator:

- Use believable opaque building volumes to interrupt lines of sight where appropriate.
- Partition individual occludees rather than combining many distant objects into one huge mesh.
- Keep occluder geometry simple; expensive occluders can defeat the benefit.
- Confirm buildings, roofs, and walls that should occlude are represented appropriately in the occluder setup.
- Test from rooftops, long avenues, elevated vantage points, and open intersections—where occlusion opportunities are weaker.
- Never make the level less believable or less fun solely to optimize a culling statistic.

### 6.6 Shadows and multiple rendering passes

**Godot's `Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME` is explicitly described in the 4.7 reference as the number of vertices or indices rendered in the last frame, not unique mesh triangles.** The count excludes culled objects and can rise because of depth and shadow passes. The docs mention values commonly around two or three times the underlying vertex count in typical configurations; that is an explanation, **not a universal conversion formula**. [Godot Performance]

Shadow-pass work can be substantial for many objects and lights. Test whether low-value tiny clutter needs to cast shadows, whether shadow ranges are justified, and whether LOD can reduce distant shadow casters. Preserve necessary gameplay visibility and art direction.

### 6.7 Don't chase triangles when a different bottleneck dominates

A scene can have moderate triangle counts and still be slow because of:

- Too many draw calls or different material surfaces.
- Expensive lights/shadows or large transparent surfaces.
- Alpha overdraw in foliage, decals, smoke, or glass.
- Complex shaders and high fill-rate cost at target resolution.
- CPU-heavy gameplay/AI, physics, navigation, procedural spawning, or scripting.
- Resource streaming and memory pressure.

**Optimization is proven by sustained frame-time improvement and acceptable visual quality, not merely by a lower triangle number.**

---

## 7. Mandatory investigative workflow

### Phase 0 — Reproduce and preserve a baseline

1. Select one **representative urban level**: roads, sidewalks, buildings, enterable interiors, ordinary props, distant backdrop, and lights.
2. Lock the **Godot version, renderer** (Forward+/Mobile/Compatibility), resolution, quality settings, render scale, hardware, and build.
3. Define repeatable camera positions: tight interior; view through doorway; dense sidewalk; long avenue; cross-street; rooftop/elevated; open lot; worst known FPS location.
4. Capture stationary samples and a repeated walkthrough. Warm up shaders and streaming before measuring.
5. Run at least three trials per configuration; record median and lower-tail frame times, not just an isolated FPS peak.
6. On the four-player co-op project, also capture a controlled active encounter with four players/enemies/effects **separately from the geometry-only baseline**.
7. Save captures and build identifiers. Do not change multiple variables at once.

**Baseline data:** frame-time median/p95 or p99, FPS, CPU frame time, GPU frame time if supported, draw calls, runtime primitives monitor, objects in frame, memory, camera, quality preset, shadow state, loaded region, and asset inventory version.

### Phase 1 — Isolate the number being called “triangles”

Ask the person reporting the figure:

- Is it Blender's **Faces**, **Triangles**, or **Vertices** overlay?
- Is it Godot's **Performance → Rendering → Primitives in Frame** monitor?
- Is it an imported Mesh Inspector value, custom counter, or external GPU capture?
- Is it a **static asset inventory**, a **currently loaded scene inventory**, or a **per-frame** renderer statistic?
- Are shadows, depth prepass, and geometry LOD included or excluded?

Record the exact source and units. **Stop comparing numbers until they use compatible definitions.**

### Phase 2 — Source-mesh audit in Blender

1. Generate a CSV for every authored or generated mesh.
2. Rank by **evaluated triangles** and **evaluated/base ratio**.
3. Inspect the worst 20 for waste: edge loops, caps, subdivisions, curves, modifiers, overlap, and degenerate geometry.
4. Identify the worst mesh generators or recipe parameters—not just individual bad assets.
5. Check whether Geometry Nodes/collection instances expand geometry beyond the basic mesh-object audit.
6. Produce a simplified comparison version for each major offender.

### Phase 3 — Godot import audit

1. Count `godot_mesh_tris_lod0` from each imported mesh surface.
2. Match imported meshes to Blender source asset IDs.
3. Compare G1 and G2 for the **same asset and exported variant**.
4. Investigate unexpectedly high imported vertex counts separately from triangle counts.
5. Verify which assets have LODs generated and whether they're used at intended distances.
6. Confirm imported scene structure does not contain duplicate objects, unintended hidden meshes, or unwanted physics collision resources.

### Phase 4 — Placement and repetition audit

1. Sort scene instances by `(triangles per mesh × number of placements)`.
2. Identify assets with medium individual cost but high total contribution.
3. Find duplicate and near-overlapping placements, accidental wall/floor caps, and repeated hidden backside meshes.
4. Split results into **playable geometry**, **set dressing**, **filler buildings**, **background**, and **hero assets**.
5. Test reducing density **without removing environmental credibility**; concentrate props where humans would actually place them.

### Phase 5 — Controlled runtime ablation

At the *same fixed camera, loaded state, hardware, and settings*, compare:

| Test | Change one thing | Diagnostic inference (not proof by itself) |
|---|---|---|
| A | Hide small set-dressing category | Large runtime improvement → repetition/clutter may matter |
| B | Hide distant buildings/backdrop | Improvement → visibility/LOD/large scene contributions |
| C | Disable shadows for a test build | Major primitive or GPU-time drop → investigate shadow workload |
| D | Enable/disable occlusion culling, when correctly configured | Improvement → hidden scene geometry was a meaningful cost |
| E | Swap 32-side small cylindrical props for 8–12-side versions | Improvement proportional to count → radial topology waste |
| F | Enable LOD or swap far buildings to HLOD | Improvement with unchanged apparent scene → distance complexity |
| G | Partition one giant repeated MultiMesh into local groups | Improvement → culling granularity was poor |
| H | Merge local static trim meshes/material surfaces | Fewer draw calls with stable GPU frame time → submission overhead |
| I | Replace high-subdivision walls/roads with simple surfaces | Improvement → planar topology was wasted |

Do **not** infer that a technique is good from the primitive monitor alone. Record **GPU ms, CPU ms, frame time, and visual impact**.

### Phase 6 — Fix root causes, then rerun

Prioritize systemic causes: a single corrected pipe recipe or lot-grid rule could improve hundreds of assets. After each optimization:

1. Re-export and reimport.
2. Compare source count, imported count, placement count, and runtime monitor **without conflating them**.
3. Run the same camera path and hardware profile.
4. Check image comparisons from gameplay distance and close inspection.
5. Verify no broken lighting, silhouettes, interior views, collision, navigation, cover, or multiplayer behavior.
6. Record what changed, with an explanation of why it helped or did not help.

---

## 8. Diagnostic decision tree

```text
START: "The level looks low-poly, but the count is unexpectedly high"
 |
 +-- Is the number a direct triangle count?
 |    |
 |    +-- NO / UNKNOWN --> Identify monitor, unit, scope, camera, and passes.
 |    |                   Record it separately; do not call it mesh triangles.
 |    |
 |    +-- YES ----------> Continue.
 |
 +-- Does Blender evaluated geometry have unexpectedly high triangles?
 |    |
 |    +-- YES --> Compare base vs evaluated.
 |    |           |
 |    |           +-- Large increase --> Modifiers / Geometry Nodes / generator.
 |    |           +-- Already high --> Excess grid, cylinders, caps, mesh design.
 |    |
 |    +-- NO --> Compare evaluated Blender asset vs Godot imported mesh.
 |                 |
 |                 +-- Godot mesh tris rise --> Export/import topology issue.
 |                 +-- Similar --> Check placement counts.
 |
 +-- Are placed scene triangles high due to repetition?
 |    |
 |    +-- YES --> Fix reusable asset cost, prop density, and LOD.
 |    +-- NO ---> Examine runtime submissions and other systems.
 |
 +-- Does the problem change significantly with viewpoint?
 |    |
 |    +-- YES --> Inspect frustum/occlusion, HLOD, distance, chunk size.
 |    +-- NO ---> Look at globally visible geometry and rendering passes.
 |
 +-- Does turning off shadows sharply improve monitor/GPU time?
 |    |
 |    +-- YES --> Optimize shadow casting and lighting configuration.
 |    +-- NO ---> Inspect materials, passes, batches, and GPU workload.
 |
 +-- Does FPS/frame time improve after removing geometry?
      |
      +-- YES --> Validate visual parity and keep the cheapest acceptable fix.
      +-- NO ---> The bottleneck may be elsewhere; stop optimizing tris alone.
```

---

## 9. Practical scripts

### 9.1 Blender: base vs evaluated topology CSV

**Purpose:** Audit source assets to identify modifier or generator inflation. Run from **Blender → Scripting**, with the relevant `.blend` file open. It writes a CSV next to the saved `.blend` or into Blender's temporary directory if unsaved.

**Scope:** Mesh objects directly present in the active scene. Counts each scene mesh object, but **does not fully expand Geometry Nodes' unrealized instances, collection-instance hierarchies, or export-specific object filtering**. For those, use the evaluated dependency graph or an exported glTF round-trip audit before certifying geometry.

```python
import bpy
import csv
import os


def triangles(mesh):
    mesh.calc_loop_triangles()
    return len(mesh.loop_triangles)


def audit_scene():
    dg = bpy.context.evaluated_depsgraph_get()
    rows = []

    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            continue

        source = obj.data
        base_tris = triangles(source)
        base_verts = len(source.vertices)

        obj_eval = obj.evaluated_get(dg)
        mesh_eval = obj_eval.to_mesh(
            preserve_all_data_layers=False,
            depsgraph=dg,
        )
        if mesh_eval is None:
            continue

        try:
            eval_tris = triangles(mesh_eval)
            eval_verts = len(mesh_eval.vertices)
            ngons = sum(1 for face in mesh_eval.polygons if len(face.vertices) > 4)
            ratio = round(eval_tris / base_tris, 3) if base_tris else 0.0
            mods = ';'.join(f'{m.name}:{m.type}' for m in obj.modifiers)

            rows.append({
                'object': obj.name,
                'mesh_data': source.name,
                'base_tris': base_tris,
                'evaluated_tris': eval_tris,
                'delta_tris': eval_tris - base_tris,
                'eval_over_base': ratio,
                'base_vertices': base_verts,
                'evaluated_vertices': eval_verts,
                'evaluated_ngons': ngons,
                'material_slots': len(obj.material_slots),
                'modifiers': mods,
            })
        finally:
            obj_eval.to_mesh_clear()

    rows.sort(key=lambda x: x['evaluated_tris'], reverse=True)
    folder = (bpy.path.abspath('//') if bpy.data.filepath else bpy.app.tempdir)
    path = os.path.join(folder, 'blender_geometry_audit.csv')
    if not rows:
        print('No mesh objects found in the active scene.')
        return

    with open(path, 'w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f'Wrote {len(rows)} mesh-object records to: {path}')
    print('Top evaluated triangle offenders:')
    for item in rows[:20]:
        print(item['object'], item['evaluated_tris'], item['eval_over_base'])


audit_scene()
```

**Interpretation:**

- `evaluated_tris` high, ratio ~1: dense source mesh or intentional authored detail.
- Ratio >>1: evaluate geometry-changing modifiers/operations.
- Ratio 0 because base is 0: generated-only geometry or an unusual source; investigate explicitly.
- Same `mesh_data` on many objects: Blender may share mesh data in memory, but each visible placement still contributes geometry to scene rendering.
- This script intentionally does **not** claim that it measures final engine draw calls or Godot imported GPU vertices.

**Quick correctness check:** Run the script on a default cube alone. Expect **12 base triangles**; with one level of ordinary quad Subdivision Surface, expect **48 evaluated triangles** (subject to modifier settings). If the values do not match, stop and investigate the audit setup.

### 9.2 Godot 4.7: placed-mesh geometry inventory

**Purpose:** Calculate `lod0_triangles × number_of_placements` for `MeshInstance3D` and `MultiMeshInstance3D` nodes in a loaded scene, and write a CSV. Attach this script to a `Node` inside a test scene (or equivalent audit harness). It writes to `user://scene_geometry_audit.csv`.

**Scope and limits:** This is a **static loaded-scene inventory**, not visible-camera geometry. It includes hidden/HLOD-alternate mesh nodes if loaded. It does not inspect particles, CSG-generated triangles, engine passes, automatically selected runtime LODs, or meshes generated later. It assumes normal triangle-list surfaces on non-`ArrayMesh` mesh types; non-triangle `ArrayMesh` surfaces are skipped. This tool is diagnostic and should be validated with a known cube and known repeated mesh before adopting its numbers.

```gdscript
extends Node

@export var root_to_scan: Node3D

func _ready() -> void:
    call_deferred("_run_audit")


func _run_audit() -> void:
    var root: Node = root_to_scan
    if root == null:
        root = get_tree().current_scene
    if root == null:
        push_warning("No scene root available for geometry audit")
        return

    var records: Array[Dictionary] = []
    _walk(root, records)

    records.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
        return int(a["placed_tris"]) > int(b["placed_tris"])
    )

    var total_tris: int = 0
    var total_placements: int = 0
    for entry in records:
        total_tris += int(entry["placed_tris"])
        total_placements += int(entry["placements"])

    var file := FileAccess.open("user://scene_geometry_audit.csv", FileAccess.WRITE)
    if file != null:
        file.store_csv_line(PackedStringArray([
            "node_path", "mesh_name", "mesh_tris_lod0",
            "placements", "placed_tris", "surfaces"
        ]))
        for entry in records:
            file.store_csv_line(PackedStringArray([
                str(entry["node_path"]), str(entry["mesh_name"]),
                str(entry["mesh_tris_lod0"]), str(entry["placements"]),
                str(entry["placed_tris"]), str(entry["surfaces"])
            ]))
        file.close()

    print("GEOMETRY AUDIT | scene placements:", total_placements,
        " | authored LOD0 triangles:", total_tris,
        " | mesh nodes:", records.size())
    for i in range(mini(20, records.size())):
        print(records[i])
    print("CSV location: ", ProjectSettings.globalize_path(
        "user://scene_geometry_audit.csv"))


func _walk(node: Node, records: Array[Dictionary]) -> void:
    if node is MeshInstance3D:
        var mi := node as MeshInstance3D
        if mi.mesh != null:
            _add_record(mi, mi.mesh, 1, records)

    elif node is MultiMeshInstance3D:
        var mmi := node as MultiMeshInstance3D
        if mmi.multimesh != null and mmi.multimesh.mesh != null:
            var mm := mmi.multimesh
            var copies: int = mm.instance_count
            if mm.visible_instance_count >= 0:
                copies = mini(copies, mm.visible_instance_count)
            _add_record(mmi, mm.mesh, copies, records)

    for child in node.get_children():
        _walk(child, records)


func _add_record(
    node: Node, mesh: Mesh, placements: int,
    records: Array[Dictionary]
) -> void:
    var per_mesh: int = 0
    var included_surfaces: int = 0

    for surface in range(mesh.get_surface_count()):
        if mesh is ArrayMesh:
            var am := mesh as ArrayMesh
            if am.surface_get_primitive_type(surface) != Mesh.PRIMITIVE_TRIANGLES:
                continue

        var arrays: Array = mesh.surface_get_arrays(surface)
        if arrays.is_empty():
            continue
        var index_array: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
        var vertex_array: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
        var elements: int = index_array.size()
        if elements == 0:
            elements = vertex_array.size()

        per_mesh += int(elements / 3)
        included_surfaces += 1

    records.append({
        "node_path": str(node.get_path()),
        "mesh_name": mesh.resource_name,
        "mesh_tris_lod0": per_mesh,
        "placements": placements,
        "placed_tris": per_mesh * placements,
        "surfaces": included_surfaces,
    })
```

**Validation:**

- A standard cube mesh should report **12 mesh triangles**.
- Ten copies of that cube should report **120 placed triangles**, whether ten nodes or one MultiMesh with ten enabled instances.
- If custom generators use triangle strips, nonstandard surfaces, or procedural meshes updated after `_ready`, extend the auditor rather than trusting its count.
- For large scenes, this one-shot script allocates surface-array data to inspect resources. Run it as an intentional audit, **not every frame**.

### 9.3 Godot: log runtime metrics without mislabeling them

Attach this to a node in a **debug/test build**. It samples Godot's standard monitors once per second. The exact cadence is only for easy comparison: some engine monitors themselves update less frequently than frames.

```gdscript
extends Node

var sample_elapsed := 0.0

func _process(delta: float) -> void:
    sample_elapsed += delta
    if sample_elapsed < 1.0:
        return
    sample_elapsed = 0.0

    var primitives: float = Performance.get_monitor(
        Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)
    var draws: float = Performance.get_monitor(
        Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
    var objects: float = Performance.get_monitor(
        Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)
    var fps: float = Performance.get_monitor(Performance.TIME_FPS)

    print("fps=", fps,
        " render_primitives_monitor=", primitives,
        " draw_calls=", draws,
        " rendered_objects=", objects)
```

**The label `render_primitives_monitor` is deliberate.** Never rename this value `unique_scene_triangles`. Use the engine profiler and, when needed, a platform GPU capture to investigate specific passes.

---

## 10. Example: diagnosing a deceptively simple suburban block

The following are **illustrative numbers**, not measurements from this project.

| Geometry family | Triangles each | Instances | Placed LOD0 tris |
|---|---:|---:|---:|
| Basic buildings and facades | 2,500 | 24 | 60,000 |
| Trim, doors, and window details | 500 | 240 | 120,000 |
| Poles, pipes, posts | 300 | 300 | 90,000 |
| Curb/road/sidewalk segments | 1,200 | 150 | 180,000 |
| Signs, boxes, bins, and small clutter | 250 | 500 | 125,000 |
| **Total placed LOD0 triangle inventory** | | | **575,000** |

Despite simple buildings, most of the inventory is **small repeated details and unnecessarily subdivided surfaces**, not architectural silhouettes.

Possible next experiment:

- Reduce each basic curb/road segment from 1,200 to 300 triangles where curvature and cracks do not demand subdivisions: save **135,000 placed LOD0 triangles**.
- Reduce pole/pipe meshes from 300 to 120 without visible silhouette loss: save **54,000**.
- Replace repeated modeled trim with lower-cost meshes or textures while preserving visual character.

That would reduce the **static inventory**, but it would **not guarantee** a proportionate change in runtime frame time. Godot may cull many copies or draw LODs, and other bottlenecks may dominate. Only the camera-controlled performance test validates value.

### A more realistic success criterion than “just lower poly count”

> Our street still reads as the same believable 1990s Pennsylvania environment from player-relevant distances, while the evaluated meshes and placed instances are measurably simpler; the production renderer also shows a repeatable frame-time improvement in at least the scenarios where geometry was identified as a bottleneck.

---

## 11. Prioritization and triage

For each opportunity, record:

- **Scale**: triangles unnecessarily spent per asset × expected placements.
- **Visibility**: percentage of test cameras/frames in which it is active or submitted.
- **Pass amplification**: shadow/depth participation and cost.
- **Visual risk**: risk of noticeable silhouette, shading, or realism loss.
- **Gameplay risk**: collision, cover, readability, traversal, and four-player visibility.
- **Engineering leverage**: one generator-rule fix versus hundreds of manual edits.
- **Measured benefit**: median and tail frame time improvement, not just triangle removal.

| Priority | Definition | Typical example |
|---|---|---|
| **P0: Correctness** | Wrong monitor interpretation, duplicate meshes, extreme unexpected generation | Repeated object placed twice; modifier accidentally multiplies meshes |
| **P1: High leverage** | Systemic, frequently used asset with no visual benefit from excess triangles | Curve recipe uses 48 radial sides for every utility pole |
| **P2: Scene-level issue** | Visibility granularity, heavy backdrop, ineffective LOD/culling | One entire town in one huge mesh or MultiMesh |
| **P3: Incremental** | Moderate savings with little risk | Remove unnecessary caps on a frequently repeated modular piece |
| **Defer** | Expensive change with little measured runtime benefit or significant art risk | Destroying hero-object form to save a small number of triangles |

Start with **highest aggregate impact with the clearest proof of avoidable cost**. If the project is draw-call-bound, material-sharing and chunking may outrank triangle reduction.

---

## 12. Working budgets: how to establish them honestly

**Do not publish arbitrary universal triangle ceilings.** A close-up player-facing object can legitimately cost more than a thousand distant filler props. Instead:

1. Build a representative asset library and profile it on target hardware.
2. Assign role and intended screen size to each asset.
3. Record median and p90/p95 triangles by archetype **from the project's best-looking efficient examples**.
4. Define a **soft budget** for each category; exceeding it requests review, not automatic rejection.
5. Define an **aggregate placement budget** for each level zone and camera exposure condition.
6. Recalibrate budgets when the team changes rendering backend, targets, view distance, shadows, or art style.

### Proposed starting gates (policy candidates, not hardware guarantees)

| Gate | Trigger | Response |
|---|---|---|
| Evaluated topology expansion | `evaluated/base > 1.25` on a simple static prop with no justified modifier | Review modifier intent; not automatic fail |
| Large unexplained import triangle delta | `abs(G2-G1)/max(G1,1) > 0.02` for same LOD0 mesh and export variant | Check source/export/import assumptions |
| High instance-weighted contribution | Asset archetype is in the top 10 placed-triangle contributors | Inspect silhouette and placement counts |
| Large geometry reduction but no frame-time benefit | Consistent camera tests show no meaningful GPU/frame-time change | Deprioritize triangles; inspect different bottleneck |
| High draw calls with moderate triangles | Draw calls drop when local static meshes/materials are combined | Consider batching or shared materials, check culling regression |
| Visual regression | Noticeable silhouette or gameplay readability loss at tested distance | Reject or revise optimization |
| Culling regression | Chunking/merging increases off-screen submissions materially | Restore more effective spatial partitions |

**These percentages are team workflow triggers, not engineering truths.** A legitimate bevel or mirror can exceed 1.25×; an asset legitimately transformed on import can exceed 2%; and a GPU-limited scene may need a different threshold entirely.

---

## 13. Automated pipeline requirements for the asset creator and optimizer

### 13.1 Required output per asset and level

Store one report per artifact/build with these fields (or equivalent columns):

```json
{
  "schema_version": "1.0",
  "asset_id": "prop.utility_pole.variant_a",
  "source_file": "art/props/utility_pole_a.blend",
  "generator_recipe": "utility_pole_v3",
  "mesh_role": "background_repeated",
  "view_distance_m": {"near": 5, "far": 80},
  "source": {
    "base_triangles": 240,
    "evaluated_triangles": 640,
    "vertices_evaluated": 420,
    "modifiers": ["BEVEL"]
  },
  "engine": {
    "imported_lod0_triangles": 640,
    "imported_vertex_count": 704,
    "mesh_surfaces": 1,
    "lod_policy": "auto_import"
  },
  "placements": {
    "count_in_level": 180,
    "placed_lod0_triangles": 115200
  },
  "review": {
    "excess_geometry_suspected": true,
    "reason": "bevel segments beyond silhouette value",
    "action": "compare 1-segment and 2-segment bevel at 5m",
    "owner": "asset_generator",
    "status": "open"
  }
}
```

**Example values only.** `source evaluated triangles`, `imported vertices`, and `placed LOD0 triangles` are **different fields by design**. Do not write runtime primitives into any of them.

### 13.2 Automated validations

**Blender-stage checks**

- Unexplained evaluated/base triangle growth.
- Degenerate/zero-area triangles and non-manifold geometry where disallowed.
- Duplicate object transforms and coincident exported duplicates.
- Unexpected high side counts, bevel levels, subdivision levels, curve resolution.
- Dense planar topology with no declared displacement/deformation need (heuristic flag, not automatic deletion).
- Duplicate hidden caps at modular connectors.
- Excess material slots and repeated same-material splits.
- Geometry Nodes/instances not accounted for in flat object audits.

**Godot-stage checks**

- Imported LOD0 triangle totals reconcile with expected evaluated source variant.
- Imported vertices and mesh surfaces reported independently.
- MeshInstance/MultiMesh instance counts and spatial distribution.
- LOD availability and HLOD overlap rules.
- Render visibility groups and chunk sizes.
- Shadow casting policy by category; test variants for cost.
- Scene object count, draw-call and runtime monitor deltas by camera scenario.

**QA checks**

- Gameplay-distance A/B screenshots and wireframes.
- Night/day and indoor/outdoor lighting parity.
- Doors, windows, roofs, cover edges, and vertical traversal preserved.
- Four-player coop tests, enemies, effects, and streaming behavior preserved.
- No new light leaks, shading cracks, texture stretching, z-fighting, or degenerate meshes.

### 13.3 Regression dashboard proposal

Each generated level gets a compact baseline comparison:

| Dimension | Baseline | Candidate | Delta | Pass rule |
|---|---:|---:|---:|---|
| Source evaluated triangles | — | — | — | No unjustified rise |
| Total placed LOD0 triangles | — | — | — | Lower or intentional |
| Runtime primitive monitor (same camera) | — | — | — | Explain change; no fixed ratio |
| Draw calls (same camera) | — | — | — | Explain change |
| GPU frame time p95 | — | — | — | Improve if GPU bottleneck |
| Total frame time p95 | — | — | — | No statistically meaningful regression |
| Visual acceptance | — | — | — | Art and gameplay sign-off |

**Regression gate:** Candidate is accepted if the visual/gameplay contract remains intact and the test demonstrates improved performance, reduced future scaling risk, or removal of objectively dead geometry—without a new bottleneck.

---

## 14. Owners and requested deliverables

### Asset creator / procedural Blender author

**Deliver:**

1. A CSV of base vs evaluated triangles and top 20 offenders.
2. Findings organized by generator operation: bevel, subdivision, remesh, curves, grids, booleans, duplicates.
3. Two or three revised procedural recipes that remove the highest-value waste without changing art direction.
4. Per-archetype mesh-generation rules for segment counts and allowable modifier growth.
5. Before/after images from target gameplay distances, not just Blender wireframe.

**Definition of done:** A source asset's geometry cost is deliberate, auditable, and proportional to visible/gameplay value.

### Godot optimizer / scene-generation engineer

**Deliver:**

1. A reproducible scene-geometry inventory with correct units and explicit audit limitations.
2. Profile captures for the representative camera matrix and hardware profiles.
3. A ranked list of mesh-placement contributors, oversized chunks, material-surface offenders, and weak culling opportunities.
4. Controlled A/B data for LOD, occlusion, shadow participation, MultiMesh partitioning, and geometry reductions.
5. A recommended spatial chunking strategy and asset/level performance dashboard.

**Definition of done:** Scene building, import, visibility, and drawing behavior have demonstrably controlled costs at target hardware/settings.

### Joint sign-off

The asset creator and optimizer should answer, for each accepted change:

- **Where did the extra cost originate?**
- **Why was it unnecessary?**
- **What exactly did we change?**
- **How did appearance, gameplay, and performance change?**
- **Can the generator prevent the same problem in future assets/levels?**

---

## 15. Failure modes / anti-patterns

**Do not:**

- Call a frame-level index/vertex-submission monitor a unique triangle count.
- Compare Blender polygon count directly against Godot render primitives.
- Assume that because a model *looks* low-poly, its evaluated mesh is low-poly.
- Treat UV/normal seams as proof of additional *triangles* when they may only add GPU vertices.
- Merge an entire playable city into a single object just to reduce draw calls.
- Replace every small static object with one citywide MultiMesh.
- Trust automatic LOD without testing distance, silhouettes, and import settings.
- Apply Decimate indiscriminately across procedural assets.
- Delete interior geometry that may become visible in gameplay.
- Optimize decorative triangle count while ignoring a GPU-heavy shader, expensive shadows, or a CPU bottleneck.
- Assume fewer triangles necessarily yield higher FPS.
- Invent a platform triangle budget without test-scene evidence.
- Change renderer settings, camera position, and art assets simultaneously during an A/B test.

**Do:**

- Separate authored topology from runtime submission and frame time.
- Make optimizations systematic at the asset-recipe level.
- Preserve the project's stylized-realistic, lived-in environment.
- Distinguish density of believable set dressing from unnecessary topology inside each prop.
- Keep metrics machine-readable so later procedural tools can enforce good defaults.

---

## 16. First sprint: proposed execution plan

| Order | Work | Owner | Output |
|---|---|---|---|
| 1 | Reproduce high reported “tri” count and identify monitor/units | Optimizer | Verified metric definition |
| 2 | Capture a representative scene baseline and 8 fixed camera cases | Optimizer | Profile pack |
| 3 | Run Blender CSV and rank top 20 meshes by evaluated triangles + expansion | Asset creator | Source offender list |
| 4 | Run Godot placement audit; rank highest scene contributors | Optimizer | Instance offender list |
| 5 | Cross-check 10 same-asset source/import triangle counts | Both | Export/import reconciliation |
| 6 | Fix 2–3 systemic mesh recipes (e.g., pipes, facades, sidewalk grids) | Asset creator | Simplified candidates |
| 7 | Test occlusion, shadows, and spatial MultiMesh partitions individually | Optimizer | A/B impact table |
| 8 | Validate visuals and gameplay on target cameras and 4-player scenario | Both | Accepted/rejected decisions |
| 9 | Add audit metrics and soft gates to level/asset pipeline | Both | Repeatable generation guardrails |

**Expected output of the sprint is a diagnosis, not an arbitrary triangle target.** It should identify the dominant source of excess cost, prove a fix, and prevent the error from recurring in procedural generation.

---

## 17. References and primary documentation

All links below are public technical references; version-specific Godot references target **4.7**.

1. **Godot 4.7 — Performance monitors.** Clarifies the rendering primitive monitor, objects, draw calls, and update timing.  
   https://docs.godotengine.org/en/4.7/classes/class_performance.html
2. **Godot 4.7 — Mesh.** Explains mesh surfaces, index/vertex arrays, triangles, and how distinct vertex attributes can require duplicate vertices.  
   https://docs.godotengine.org/en/4.7/classes/class_mesh.html
3. **Godot 4.7 — ArrayMesh.** API for triangle-list surface type, index-array length, and vertex-array length.  
   https://docs.godotengine.org/en/4.7/classes/class_arraymesh.html
4. **Godot 4.7 — Mesh LOD.** Automatic imported-scene LOD generation, use, and caveats.  
   https://docs.godotengine.org/en/4.7/tutorials/3d/mesh_lod.html
5. **Godot 4.7 — Visibility ranges / HLOD.** Manual visibility ranges and hierarchical simplification.  
   https://docs.godotengine.org/en/4.7/tutorials/3d/visibility_ranges.html
6. **Godot 4.7 — Occlusion culling.** Use cases, setup, measurement, and limits.  
   https://docs.godotengine.org/en/4.7/tutorials/3d/occlusion_culling.html
7. **Godot 4.7 — MultiMesh.** GPU instancing tradeoffs and culling limitations.  
   https://docs.godotengine.org/en/4.7/classes/class_multimesh.html
8. **Godot 4.7 — Optimizing 3D performance.** Overall visibility, LOD, batching, and geometry guidance.  
   https://docs.godotengine.org/en/4.7/tutorials/performance/optimizing_3d_performance.html
9. **Godot 4.7 — GPU optimization.** Draw-call/material-state cost and batching pitfalls.  
   https://docs.godotengine.org/en/4.7/tutorials/performance/gpu_optimization.html
10. **Blender Python API — Mesh.** `calc_loop_triangles()` and topology information.  
    https://docs.blender.org/api/current/bpy.types.Mesh.html
11. **Blender Python API — Object.** Evaluated objects, temporary mesh extraction, modifier-aware inspection.  
    https://docs.blender.org/api/current/bpy.types.Object.html

**Verification note:** This guide was assembled against published Blender and Godot 4.7 API documentation. The included scripts have **not** been executed against the project's actual assets, build, renderer, or target hardware. Validate them on the test meshes described above and adapt them to the project's procedural/instance architecture before making them CI gates.

---

## Final recommendation

**First establish whether the apparent excess exists in the meshes or only in the runtime metric.** Then:

1. Fix unexpected evaluated mesh density at the Blender/generator source.
2. Reduce repeated asset cost where instance-weighted totals are high.
3. Ensure Godot can make good visibility and LOD decisions with reasonable spatial partitions.
4. Investigate depth/shadow/multi-pass work and draw-call overhead separately.
5. Accept changes only when measured performance and visual/gameplay outcomes justify them.

The target is not merely “a lower triangle count.” The target is **believable, fun, high-quality levels where the geometry and runtime rendering cost are deliberate, visible in reports, and justified by what the player experiences.**

<!-- Reference-style links used in technical sections -->
[Godot mesh LOD]: https://docs.godotengine.org/en/4.7/tutorials/3d/mesh_lod.html
[Godot GPU optimization]: https://docs.godotengine.org/en/4.7/tutorials/performance/gpu_optimization.html
[Godot MultiMesh]: https://docs.godotengine.org/en/4.7/classes/class_multimesh.html
[Godot occlusion culling]: https://docs.godotengine.org/en/4.7/tutorials/3d/occlusion_culling.html
[Godot Performance]: https://docs.godotengine.org/en/4.7/classes/class_performance.html
