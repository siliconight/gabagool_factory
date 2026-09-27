# Draw Call Optimization in Godot 4.7

*A practical guide to batching, GPU instancing, visibility, and profiling for 3D scenes*

## The short version

Use fewer draw calls when profiling shows that CPU-side rendering submission is a bottleneck. For repeated copies of the same mesh, Godot's `MultiMeshInstance3D` can render many instances with far less submission overhead than thousands of independently submitted mesh nodes.

That gain is not free. Godot culls a MultiMesh as one object, not one instance at a time. A single world-sized MultiMesh may therefore send lots of invisible geometry to the GPU. Group instances into spatially coherent batches, preserve useful culling, and profile the result on target hardware.

**Working rule:** keep individually managed objects as `MeshInstance3D`; use MultiMesh for large populations of repeated, mostly static or similarly managed objects; split MultiMeshes by area and appearance; use LOD and visibility culling to limit the work each visible batch creates.

## What a draw call is

A draw call is a rendering command that asks the graphics pipeline to draw geometry with particular data and render state. Preparing and submitting many commands can consume CPU time, especially when a scene contains many small objects. The GPU still has to process the geometry, shade visible pixels, and handle any relevant shadow or depth passes.

A useful analogy is giving the kitchen one order for a tray of identical meals instead of sending a separate order for every plate. The tray reduces repeated instructions; it does not make the food disappear. The GPU still processes the instances that the batch makes visible.

Draw calls are only one part of frame time. A scene can instead be limited by gameplay scripts, physics, animation, vertex work, pixel shading, overdraw, shadows, memory bandwidth, or loading. A lower draw-call count is not itself proof of a faster frame.

## Batching and instancing are related, but different

- **Batching** groups compatible rendering work so the renderer can submit it more efficiently. Which objects can be grouped depends on the renderer and on shared mesh/material/render state.
- **GPU instancing** draws repeated copies of one mesh using a shared mesh plus per-instance data such as transforms and optional colors/custom values. `MultiMesh` is Godot's explicit 3D instancing resource.
- **Mesh merging** combines geometry into a larger mesh. It can reduce object or surface submissions, but may increase memory and remove per-object visibility and movement control.
- **Object pooling** reuses objects to reduce allocation and creation/destruction costs. It is not a draw-call optimization by itself. A pool full of visible `MeshInstance3D` nodes may still submit substantial rendering work.

Godot 4.7 also performs **automatic instancing** for identical opaque or alpha-tested `MeshInstance3D` objects in the Forward+ renderer. This is renderer-specific and has restrictions; it does not apply the same way in Mobile or Compatibility, and alpha-blended materials are not automatically instanced this way. Measure the renderer you ship with before replacing scene nodes manually.

## What MultiMesh saves—and what it does not

A MultiMesh stores one mesh and many instance transforms (and optionally per-instance colors or custom data). Godot can submit those copies using GPU instancing, reducing CPU/API submission overhead compared with sending every copy as an independent mesh object.

A MultiMesh does **not** mean:

- The instances have become one cheap polygon. Each visible instance still has geometry to process.
- Every MultiMesh always equals exactly one draw call in every circumstance. Meshes with multiple surfaces/materials and extra render passes can require additional work. Think in terms of substantially fewer instance submissions, not a universal fixed draw-call count.
- Invisible instances are individually removed from rendering. Godot uses the MultiMesh's shared visibility bounds; it cannot frustum-cull individual instances within it.
- Instance gameplay behavior, collision, navigation, or AI has been provided. Those systems still need their own design.

Godot's MultiMesh documentation also notes that the resource is treated as one object for the maximum-lights-per-object restriction. If the shared lighting limit is reached, later instances in that MultiMesh may not receive additional lights. Validate lighting and shadows when using MultiMesh for objects affected by many local lights.

## Good candidates

Use MultiMesh when you have many copies of the same mesh, in a reasonably localized area, with simple per-instance differences:

- Grass, flowers, rocks, debris, repeated architectural details
- Forests, crowds of simple background figures, flocks, or swarms
- Repeated static props placed by procedural generation
- Large populations whose transforms can be generated or updated as a group

It is usually a poor fit when objects need distinct scene-tree behavior, complex individual animation, different meshes/materials, frequent individual interaction, precise per-instance visibility, or independently controlled shadow/lighting behavior. A hybrid is common: nearby interactive objects are individual nodes; far background copies are instanced.

## The important tradeoff: batch size versus visibility

A MultiMesh's bounds describe the whole instance collection. If any part of those bounds is visible, the renderer may render instances that are outside the camera view. A forest spread across the whole level can remain active when the camera sees only a tiny corner of it.

**Prefer several local MultiMeshes over one enormous one.** Split by a meaningful spatial unit such as room, building, terrain tile, forest patch, or streaming cell. This gives the renderer better all-or-none visibility decisions. Avoid making every patch so tiny that submission overhead climbs again; tune the granularity with a representative camera path and profiler.

Set the visibility bounds correctly. For procedurally placed instances, compute or assign a `custom_aabb` that encloses the full possible instance extent. An undersized bound can make the batch disappear or clip unexpectedly; a needlessly huge bound weakens culling. Recompute bounds if the collection can move beyond the original extent.

Godot also offers `visible_instance_count` to draw only the active prefix of an allocated MultiMesh. This is useful when population size changes. It is not individual frustum culling and does not select arbitrary visible indices unless the instance data/order is managed accordingly.

## Choosing the right tool

| Situation | Start with | Why |
|---|---|---|
| A modest number of unique/interactable props | `MeshInstance3D` | Simple per-object behavior and visibility; avoid extra machinery without measured need. |
| Repeated identical opaque props in Forward+ | Regular nodes first; profile automatic instancing | Godot may already instance compatible objects automatically. |
| Thousands of repeated copies with transforms generated as a set | `MultiMeshInstance3D` | Explicit GPU instancing with low submission overhead. |
| Repeated props spread over a large area | Several spatially partitioned MultiMeshes | Preserves coarse visibility culling instead of one giant all-or-none bound. |
| Many different objects that can be baked into static geometry | Mesh combine/merge or authored HLOD | Useful for static scenery; check memory, occlusion, and per-object needs. |
| Distant objects need less detail | Automatic mesh LOD or visibility-range HLOD | Reduces geometry or swaps whole groups for simpler representations. |
| Indoor rooms hide large portions of the level | Occlusion culling and/or room/visibility logic | Avoids rendering geometry hidden by walls when the scene offers useful occlusion. |
| Objects are expensive to create/destroy but not especially costly to draw | Object pool | Helps lifecycle/allocation spikes, not inherently draw calls. |

## Minimal GDScript example

This example creates one local batch of simple repeated meshes. In production, fill the transforms from authored placement data or a deterministic placement generator, and create one node/resource per spatial cell as needed.

```gdscript
extends MultiMeshInstance3D

@export var mesh_to_instance: Mesh
@export_range(1, 100_000) var count := 1000
@export var area_size := Vector2(40.0, 40.0)

func _ready() -> void:
    var batch := MultiMesh.new()
    batch.transform_format = MultiMesh.TRANSFORM_3D
    batch.mesh = mesh_to_instance
    batch.instance_count = count

    for i in range(count):
        var x := randf_range(-area_size.x * 0.5, area_size.x * 0.5)
        var z := randf_range(-area_size.y * 0.5, area_size.y * 0.5)
        var position := Vector3(x, 0.0, z)
        var rotation := Basis(Vector3.UP, randf_range(0.0, TAU))
        var scale := Vector3.ONE * randf_range(0.85, 1.15)
        batch.set_instance_transform(i, Transform3D(rotation.scaled(scale), position))

    # Set conservative local bounds covering all generated instances and mesh size.
    # Tune this for your actual mesh and placement rules.
    batch.custom_aabb = AABB(
        Vector3(-area_size.x * 0.5 - 2.0, -2.0, -area_size.y * 0.5 - 2.0),
        Vector3(area_size.x + 4.0, 8.0, area_size.y + 4.0)
    )
    multimesh = batch
```

For reproducible procedural scenes, seed the random number generator or, preferably, derive placements from saved seed/data. For visible variations, `use_colors` and `use_custom_data` can pass per-instance values to supported materials/shaders. Those features add flexibility; they do not remove the need to test shader cost and renderer compatibility.

### Setup in the editor

1. Add a `MultiMeshInstance3D` to the scene.
2. Create a `MultiMesh` resource and assign its mesh.
3. Set its transform format, instance count, and per-instance transforms (through code, editor tooling, or imported data).
4. Set the `custom_aabb` to cover all possible instance positions and mesh extents.
5. Divide large populations into separate instances grouped by spatial cell and, where useful, by mesh/material/behavior.
6. Test visibility, shadows, lighting, and any per-instance material variation on the target renderer.

## Frame-rate targets and draw-call budgets

Set a frame-time target first. Draw-call count is a diagnostic measure, not a universal budget. The target frame rates below give the total time available for all game work in each frame:

| Target frame rate | Total frame-time budget |
|---|---:|
| 30 FPS | 33.3 ms |
| 60 FPS | 16.7 ms |
| 120 FPS | 8.3 ms |

These are whole-frame budgets shared by gameplay, rendering, physics, audio, and other work. They are not time budgets reserved for draw calls. There is no dependable rule such as “X draw calls for 60 FPS”: the cost varies with hardware, renderer, materials, visibility, and GPU workload.

Profile a representative scene on target hardware, then set a project-specific draw-call guardrail that leaves room for other work and frame-time spikes. Recheck after changes. Fewer draw calls help when CPU-side rendering submission is a real bottleneck; they may have little effect when the GPU or another system is limiting performance.

## A practical optimization workflow

### 1. Define the actual target

Record the target platform, renderer (Forward+, Mobile, or Compatibility), resolution, frame-rate target, and a representative gameplay view. A benchmark on a desktop with a fixed camera is not enough to establish performance on a lower-power target or in a different renderer.

### 2. Capture a baseline

Use a repeatable scene and camera path. Record frame time in milliseconds, not only average FPS. Capture CPU and GPU frame timing where possible, visible object/primitive counts, draw calls or render statistics, and stutters during movement. Run a release build when validating the result; the editor and debug build add overhead.

### 3. Confirm the bottleneck

Use Godot's Profiler and Performance monitors, then use an external GPU profiler when the built-in view cannot distinguish the issue. Look for evidence that CPU-side rendering/submission is expensive before focusing on draw calls. If GPU time is the constraint, reducing draw-call count alone may not help; investigate pixel cost, overdraw, geometry, shadows, resolution, and shader complexity.

Change one factor at a time. Compare the same camera positions, visibility, settings, and hardware. A scene may become CPU-bound after a draw-call reduction, revealing a different bottleneck.

### 4. Apply the least complex effective change

- Reuse compatible materials and meshes where it helps automatic instancing and state sorting.
- Use MultiMesh for repeated geometry when a real population justifies it.
- Partition batches spatially so culling still rejects unseen areas.
- Use mesh LOD, visibility-range HLOD, or occlusion culling for the work those tools are designed to remove.
- Reduce expensive shadow casting and dynamic lighting where profiling points to them.
- Keep interactive objects as individual nodes when individual control matters.

### 5. Recheck the result and visuals

Compare median and worst-case frame times, CPU/GPU timing, draw work, and visible geometry. Walk through rooms, look through windows, view batch boundaries, and test camera angles that expose partial batches. Check popping, disappearing bounds, lighting limits, shadow behavior, and overdraw. Keep the change only if it improves the target experience without unacceptable visual or authoring costs.

## Common mistakes to avoid

- **Optimizing a draw-call number without a measured problem.** A lower count can coexist with the same frame time or worse GPU load.
- **Making one MultiMesh for the whole level.** Large shared bounds weaken culling and can keep off-screen instances rendering.
- **Assuming one MultiMesh equals one total draw call.** Multiple mesh surfaces/materials and render passes add work.
- **Confusing pooling with rendering optimization.** Pooling helps reuse and allocation; visibility and rendering submission still matter.
- **Assuming every repeated object requires manual MultiMesh.** Forward+ may automatically instance compatible opaque/alpha-tested meshes.
- **Making every asset share one material at any cost.** Atlases and shared materials can help, but can increase texture size, complexity, or memory pressure. Profile the whole frame.
- **Ignoring shadows, transparency, and lighting.** These can multiply rendering work or change which optimizations apply.
- **Using a benchmark that only shows an empty test scene.** Test representative level content, camera movement, and target hardware.
- **Using FPS alone.** Frame time and CPU/GPU measurements explain why performance changed; FPS can hide variance and becomes capped by V-Sync/refresh rate.

## Corrections to the supplied video explanation

The video gives a useful intuition for repeated placement, but a few details need tightening for Godot 4.7:

1. GPU instancing sends shared mesh data with per-instance data; it does not literally eliminate all per-object information or all GPU work.
2. “Draw 1,000 even if only two are visible” is a useful warning, but the precise issue is that Godot culls a MultiMesh as one overall object. If its overall bounds are visible, individual instances are not frustum-culled separately. Spatially splitting the MultiMesh is the standard mitigation.
3. Object pooling is not the main fix for this visibility tradeoff. Pooling controls object lifetime and allocation; spatial partitioning, culling, and LOD control rendering work.
4. A one-draw-call claim is a simplification. A MultiMesh can sharply reduce instance submission overhead, but surfaces/materials and render passes can still generate multiple draws.
5. The example's reported FPS difference is specific to its test machine, scene, renderer, and setup. Treat it as an illustration, not an expected speedup or benchmark target.
6. Godot 3.5-era batching documentation describes older renderer behavior. Godot 4.7 has renderer-specific automatic instancing in Forward+, so the current version's documentation and your project's renderer settings take precedence.

## Recommended team standard

- Profile before optimizing, and record the scene, camera, renderer, and target hardware.
- Prefer the simplest representation that meets the measured frame-time target.
- Use MultiMesh for repeated geometry that benefits from GPU instancing; partition by local area to keep useful culling.
- Keep `custom_aabb` valid and as tight as practical.
- Recheck visibility, lighting, shadows, and performance on the target renderer after changes.
- Treat draw-call count as a diagnostic metric, not a universal performance budget; derive a project guardrail from target hardware and profiling.

## Sources and further reading

### Godot 4.7 documentation

- [Optimization using MultiMeshes](https://docs.godotengine.org/en/4.7/tutorials/performance/using_multimesh.html) — benefits, per-MultiMesh culling limitation, custom visibility, and visible-instance count. The page currently flags some content as not yet updated for 4.7; use it alongside the current class reference.
- [MultiMesh class reference](https://docs.godotengine.org/en/4.7/classes/class_multimesh.html) — GPU instancing, shared visibility bounds, custom AABB, lighting limit, and instance properties.
- [Optimizing 3D performance](https://docs.godotengine.org/en/4.7/tutorials/performance/optimizing_3d_performance.html) — automatic instancing and manual MultiMesh guidance.
- [General optimization tips](https://docs.godotengine.org/en/4.7/tutorials/performance/general_optimization.html) — profiling, measurement, and bottleneck identification.
- [GPU optimization](https://docs.godotengine.org/en/4.7/tutorials/performance/gpu_optimization.html) — GPU bottlenecks, overdraw, and 2D batching context.
- [Mesh level of detail](https://docs.godotengine.org/en/4.7/tutorials/3d/mesh_lod.html) — automatic mesh LOD and validation.
- [Visibility ranges (HLOD)](https://docs.godotengine.org/en/4.7/tutorials/3d/visibility_ranges.html) — replacing groups with simpler representations while preserving close-range culling.
- [Occlusion culling](https://docs.godotengine.org/en/4.7/tutorials/3d/occlusion_culling.html) — where occlusion helps and how Godot's implementation works.
- [Internal rendering architecture](https://docs.godotengine.org/en/4.7/engine_details/architecture/internal_rendering_architecture.html) — renderer architecture and occlusion-culling context.

### Graphics background

- NVIDIA, [GPU Gems 3: Animated Crowd Rendering](https://developer.nvidia.com/gpugems/gpugems3/part-i-geometry/chapter-2-animated-crowd-rendering) — hardware instancing's CPU-submission benefit and the continued importance of LOD and frustum culling. It is an older Direct3D example, so use it for concepts rather than Godot API details.

### User-supplied links

- [GDQuest: Optimizing a 3D scene](https://www.gdquest.com/tutorial/godot/3d/optimization-3d/) — helpful concepts and profiler context, but published in 2020 for Godot 3.2; some renderer and lighting details are outdated for Godot 4.7.
- [Bugnet: Optimizing draw calls for better game performance](https://bugnet.io/blog/optimizing-draw-calls-for-better-game-performance) — broad overview, but its batching instructions mix Unity and Unreal concepts with Godot. Do not use its exact counts, material rules, or workflow as Godot-specific requirements.
- [Godot 3.5: Optimization using batching](https://docs.godotengine.org/en/3.5/tutorials/performance/batching.html) — legacy renderer-specific explanation; useful background only.
- [Godot 3.5: GPU optimization](https://docs.godotengine.org/en/3.5/tutorials/performance/gpu_optimization.html) — legacy context; prefer the Godot 4.7 GPU optimization page.
- [The Gamedev Guru: Unity draw-call optimization](https://thegamedev.guru/unity-performance/draw-call-optimization/) — Unity-specific; useful only for general profiling concepts, not for Godot feature instructions.
