# Godot 4.7 Runtime Optimization Guide

**A practical production guide for 3D levels, assets, and procedural content**  
Version 1.0 • 3 October 2026 • Primary references: Godot 4.7 documentation

## Purpose and evidence

Optimization means reducing the resources required to deliver the intended player experience. The goals are stable frame delivery, responsive gameplay, predictable memory use, and transitions without disruptive stalls.

This guide focuses on the game while it runs. Editor responsiveness, shorter imports, smaller downloads, and faster builds are outside scope unless they change runtime behavior.

**Evidence boundary:** The engine mechanisms below were checked against official Godot 4.7 documentation. No game project, target hardware, or Godot executable was available for runtime benchmarking during preparation. Consequently, this document does not claim measured gains in your game. It provides documented techniques and reproducible experiments that turn a plausible optimization into a project-verified result. There are no invented benchmark results.

Labels used throughout:

- **Documented:** Godot describes the mechanism in the linked reference.
- **Project prescription:** A proposed authoring rule, workflow, or experiment; validate it against your game.
- **Verified in project:** A status earned only after completing the measurement and regression checks in Section 4.

Read Sections 1–4 first. Use Section 5 to diagnose a problem, Section 6 for implementation recipes, and Sections 7–11 as production requirements.

## 1. What optimization is—and what it is not

Optimization can mean doing less work, doing it less often, moving it outside interactive play, or representing the same experience more cheaply. A distant building may need a convincing silhouette and lit windows, without rooms, furniture, collision, or AI.

It is not synonymous with lower polygon counts, fewer nodes, smaller PNGs, fewer draw calls, or disabling every visual feature. Those are possible inputs to performance. The outcome is what happens on the target device.

Distinguish four activities:

| Activity | Example | Success evidence |
| --- | --- | --- |
| Efficient design | Design street corners that limit simultaneous visibility | Worst viewpoints meet the runtime budget |
| Optimization | Replace repeated independent visual props with spatially grouped instances | Repeatable reduction in the constrained runtime cost |
| Quality scaling | Reduce shadow distance on a lower hardware tier | That tier meets its target at accepted quality |
| Scope reduction | Reduce the number of simultaneous enemies | Explicit design approval and acceptable gameplay |

Quality scaling and scope changes are valid decisions. Record them honestly; they do not establish that equivalent content became cheaper.

**When to do it:** Plan visibility, lighting, simulation, and memory constraints during blockout. Benchmark representative content before mass production. Fix measured regressions continuously. Reserve low-level tuning for a demonstrated bottleneck. Godot explicitly recommends measurement and efficient design rather than speculative micro-optimization. [R1]

## 2. Understand the runtime costs

| Resource | What consumes it | What players experience when it is constrained |
| --- | --- | --- |
| CPU frame work | Scripts, AI, scene updates, rendering submission, animation, resource management | Low frame rate, delayed responses, spikes |
| GPU frame work | Geometry, pixel shading, lighting, shadows, transparency, post-processing | Low frame rate that often changes with resolution or viewpoint |
| Physics time | Active bodies, contacts, collision queries, complex shapes | Simulation overload, inconsistent motion or stalls |
| System RAM | Resources, scene instances, simulation state, caches, temporary allocations | Memory pressure, paging, instability |
| GPU memory | Textures, meshes, lightmaps, render targets and buffers | Residency pressure, stalls, allocation failure |
| Disk and resource loading | Reading, decompression, deserialization, resource construction | Hitches at doors, first encounters, or transitions |
| Network and host simulation | Replication, serialization, authoritative simulation | Delayed state, corrections, host-specific slowdown |

CPU and GPU execution overlap. Do not add their reported times and call that the frame time. The slower stage often limits throughput, with synchronization, presentation, and other stalls complicating the result. Reducing CPU work may leave FPS unchanged when the GPU remains the limiting stage. [R1]

Rendering visibility, simulation activity, and memory residency are separate controls:

- **Not rendered:** A mesh is culled or hidden. Its scripts, physics, and resources may remain active.
- **Not simulated:** A system stops updating. Its visuals and resources may remain present.
- **Not resident:** Unneeded instances and references are released. Verify that memory actually settles.

Use each control deliberately. A hidden room is not automatically an unloaded room.

## 3. Establish budgets before judging assets

### Frame-time targets

Frame budget in milliseconds = 1,000 / target FPS.

| Target | Frame budget | Proposed normal-play target with 20% reserve |
| --- | ---: | ---: |
| 30 FPS | 33.33 ms | 26.67 ms |
| 60 FPS | 16.67 ms | 13.33 ms |
| 120 FPS | 8.33 ms | 6.67 ms |

The reserve is a **project planning proposal**, not a Godot requirement or a guarantee. It leaves room for combat bursts and content growth. Meeting a median target alone is insufficient; track the slow tail and deadline misses.

Define the following before approval:

| Contract field | Required entry |
| --- | --- |
| Engine | Exact 4.7.x version and build identifier |
| Rendering | Forward+, Mobile, or Compatibility; graphics API |
| Hardware tier | CPU, GPU, RAM, available GPU memory, OS, driver, power mode |
| Display | Output resolution, internal scale, AA, fullscreen/window mode |
| Performance | Target FPS, p95/p99 limits, allowable deadline misses and hitch severity |
| Memory | Peak process memory and GPU allocation/residency limits; transition reserve |
| Gameplay load | Player count, enemies, active bodies, simultaneous effects |
| Content | Build commit, map, procedural seed, camera route, scenario |
| Loading | Allowed startup/transition time and maximum gameplay stall |

Renderer choice is an early architectural decision. Godot exposes different features and behavior across its three renderers. Compare a representative scene on the weakest supported device before committing; renderer switching can require visual changes. [R8]

### Derive asset budgets from a representative level

Do not invent a universal “500 draw calls = 60 FPS” rule. There is no fixed conversion between draw calls, triangles, and FPS.

Project prescription:

1. Build a small slice containing the actual material, light, collision, and enemy types.
2. Capture a quiet view, the longest sightline, and a full combat view.
3. Increase one content family at a time: props, characters, shadow lights, or effects.
4. Find the density where the target fails on minimum hardware.
5. Choose a lower authoring limit that preserves the agreed reserve.
6. Retest combinations. Independent per-category limits can fail when combined.

Record **simultaneously visible**, **simultaneously simulated**, and **simultaneously resident** counts. Total assets in a folder do not express any of these.

## 4. How to test and verify an optimization

### Tools and what they establish

| Tool/evidence | Use | Limitation |
| --- | --- | --- |
| Godot Debugger → Profiler | Find costly script and frame/physics activity | Instrumentation affects execution; not a complete GPU explanation |
| Godot Visual Profiler, where supported | Investigate rendering passes and CPU/GPU timing | Availability depends on renderer; GPU timing can differ from presentation |
| Debugger monitors | Track rendering counters, memory indicators, object counts and pipeline events | Counters are indicators, not full process or GPU-residency accounting |
| OS/vendor tools | Process memory, GPU pressure, CPU/GPU traces and presented-frame timing | Match tool support to API and platform |
| Matching screenshots and replay | Verify appearance, gameplay, and repeatability | A screenshot cannot verify motion artifacts or responsiveness |

Use the documented profiler and debugger tools to locate causes, then validate a release export on actual hardware. External CPU/GPU tools are useful when Godot's view is insufficient. [R1, R14, R15]

### Reproducible A/B protocol — project prescription

1. **Capture A:** Preserve the baseline commit and export. Record the contract from Section 3.
2. **Fix the workload:** Use the same route, seed, enemy schedule, player actions, camera/FOV, and settings. Seed equality alone does not ensure identical physics or network timing.
3. **Separate diagnostic and player tests:** Use uncapped/V-Sync-off captures to expose workload changes. Also test the shipping cap and V-Sync mode to judge actual delivery.
4. **Separate cold and warm tests:** Record first-use behavior separately from a repeat traversal. A warm driver/resource cache can hide first-use stalls. Describe the cache state; do not label a run “cold” without evidence.
5. **Make B a single change:** Keep output quality equivalent unless the test is explicitly about a quality tradeoff.
6. **Repeat:** As an initial protocol, run a fixed 120-second route five times per version, alternating A and B. Extend only if variation or rare events leave the result unclear.
7. **Record each run:** Median, p95, p99, maximum frame interval, count above the frame budget, and counts above agreed hitch thresholds. Include CPU/GPU timing, relevant counters, and peak memory.
8. **Inspect the mechanism:** If testing LOD, confirm that rendered geometry changed. If testing shadow cost, inspect the shadow pass. A faster run without the expected mechanism may be noise.
9. **Check regressions:** Replay doors, windows, crouch/jump viewpoints, gameplay interactions, combat, and transitions. Compare memory and loading as well as FPS.
10. **Confirm shipping conditions:** Release export, weakest supported tier, correct renderer/API, and supported multiplayer configuration.

Percentiles describe the sorted individual frame intervals: p99 is the interval at or below which 99% of the recorded frames fall. Define the tool's “1% low” convention if using it; different calculations are not interchangeable. Do not average FPS samples to substitute for a frame-time distribution.

A practical initial success rule is a repeatable improvement larger than baseline run-to-run variation, with no unapproved regression. A proposed 5% improvement threshold can be useful for triage, but it is not proof by itself. A smaller reliable change may still be valuable; a large noisy change may not be real.

### Verification record

```text
Change ID / owner:
Status: proposed | documented | measured | verified in project
Baseline / candidate commits:
Godot version / renderer / graphics API:
Hardware / OS / driver / power mode:
Resolution / scale / AA / cap / V-Sync:
Map / seed / route / scenario / duration:
Cold or warm state and how established:
Hypothesis and expected mechanism:
Single change:
A and B per-run median / p95 / p99 / worst frame:
A and B deadline misses / hitch counts:
A and B CPU / GPU / physics timings:
A and B relevant rendering or simulation counters:
A and B peak process memory / GPU memory:
Visual and gameplay regression results:
Multiplayer/host results, if applicable:
Evidence paths: captures, CSV, screenshots, replay:
Decision / limitations / rollback commit:
```

**Never mark a technique project-verified merely because it is documented, appears in a demo, or reduces a counter.**

## 5. Diagnose before choosing a technique

These are experiments, not automatic diagnoses. Restore temporary changes afterward.

| Symptom | First isolation test | Investigate if the result supports it |
| --- | --- | --- |
| Slow when looking across a street | Compare closed view and long view with simulation held constant | Visibility, draw submission, LOD, shadows |
| Slow near smoke, windows, or foliage | Disable that visual family; separately reduce internal resolution | Transparent coverage, overlap, shader cost |
| Slow even facing a wall | Pause selected AI/physics work in a controlled test | Simulation, scripts, submission, background work |
| Lower resolution substantially helps | Compare GPU pass timings | Pixel shading, effects, transparency, bandwidth |
| Lower resolution barely helps | Inspect CPU and GPU traces rather than guessing | CPU work, geometry, synchronization, fixed GPU costs |
| First explosion or material appearance hitches | Track pipeline events during first and repeat use | Pipeline creation or resource loading |
| Entering a room hitches every time | Time load, instantiate, scene insertion, activation separately | Main-thread work or repeated initialization |
| Performance worsens over repeated missions | Compare settled memory/object counts after each cycle | Retained resources, unbounded caches, duplicated state |
| Slow only during enemy waves | Separate navigation, physics, animation, effects, replication | Peak simulation and rendering workload |
| Host is slower than remote clients | Compare host simulation and network serialization traces | Authority workload, not just scene visuals |

## 6. Actionable runtime techniques

Each recipe includes a documented mechanism where available and a project-specific validation experiment. Improvements remain conditional on the actual bottleneck.

### 6.1 Design levels for bounded visibility

**Use when:** Expensive views expose many rooms or street blocks at once.

**Action:** During blockout, test bends, substantial buildings, elevation, and interior walls as sightline breaks. Keep gameplay routes legible. Split near geometry at room/building boundaries so it can be culled independently. Test rooftops and elevated viewpoints; they often defeat ground-level assumptions.

**Verify:** Compare the worst route before and after layout changes at equivalent gameplay load. Inspect visible geometry, CPU/GPU time, and combat readability. A redesigned route needs design approval.

**Trap:** Fog and darkness can conceal detail visually without stopping its rendering. A giant joined mesh can cross several visibility zones and remain submitted. [R2, R16]

### 6.2 Add occlusion culling to substantial blockers

**Documented mechanism:** Godot tests object bounds against explicit occluders; enabling the setting alone does not supply them. [R5]

**Action:** Enable `Rendering > Occlusion Culling > Use Occlusion Culling`. Add `OccluderInstance3D` and use **Bake Occluders**, then inspect the result. Represent opaque walls/buildings, leaving openings intact. Do not bake an openable doorway shut. Rebuild or update the occlusion representation when generated layouts change.

**Verify:** A/B culling on/off along the same route. Confirm hidden geometry is culled; measure the net CPU and GPU result. Test open doors, windows, destructible walls and oblique views.

**Trap:** Occlusion costs CPU time and can lose in open scenes. Large bounds are harder to fully hide. The bake does not automatically include every rendering node type; inspect generated content explicitly.

### 6.3 Use imported mesh LOD

**Documented mechanism:** Imported 3D scenes can generate automatic mesh LOD. Mesh LOD reduces distant geometry; it does not inherently consolidate material surfaces. [R3]

**Action:** Inspect **Generate LODs** in the 3D import configuration and reimport when necessary. Compare wireframe views. Adjust the root viewport's `mesh_lod_threshold` only after inspecting silhouettes at real gameplay distances. OBJ imports require scene import mode for this workflow.

**Verify:** Compare LOD enabled/disabled with the same camera. Confirm fewer rendered primitives, then measure GPU/frame time. Inspect thin objects, signs, faces, and animated deformation.

**Trap:** LOD does little for a pixel-bound or simulation-bound scene. Runtime-generated meshes should not be assumed to receive the imported-scene LOD treatment automatically.

### 6.4 Replace distant assemblies with HLOD

**Documented mechanism:** Visibility ranges can swap many nearby objects for a cheaper distant representation. [R4]

**Action:** Make a simplified combined street frontage or building proxy. Configure `GeometryInstance3D` Visibility Range Begin/End and margins; use visibility parents for hierarchical setups. Start with hard transitions plus hysteresis, then assess whether fading is worth its cost.

**Verify:** Walk repeatedly across the boundary and test different approach angles. Measure draws and frame time. Ensure the detailed version and proxy do not both remain active unnecessarily.

**Trap:** Alpha fades add rendering cost. Hiding the detailed model does not release its memory or disable gameplay. Author distances from screen size and visibility, not arbitrary universal meters.

### 6.5 Reuse mesh and material resources

**Documented mechanism:** Forward+ can automatically instance compatible objects sharing the same mesh and material. Its documented eligibility differs from Mobile/Compatibility and excludes some transparency modes. [R2]

**Action:** Use shared resources for repeated chairs, lamps, bins, or shelves. Audit generator output for unnecessary material duplication. Introduce variation through a tested shared-material approach rather than creating a unique resource for every prop.

**Verify:** Compare the repeated-prop scene before/after resource reuse. Inspect submission and frame time in the actual renderer.

**Trap:** Sharing a material does not universally collapse arbitrary meshes into one draw. Surfaces, passes, shadow rendering and instance eligibility still matter.

### 6.6 Group repeated visuals with MultiMesh

**Documented mechanism:** `MultiMesh` instances a shared mesh efficiently but uses group-level visibility bounds. It does not individually cull every member. [R6]

**Action:** Use `MultiMeshInstance3D` for repeated decorative meshes. Partition by spatial cell or visibility zone. Compare several cell sizes; populate correct bounds that include shader motion. Keep interactive behavior/collision as separate systems where needed.

**Verify:** Compare ordinary instances, one global MultiMesh, and spatially partitioned MultiMeshes. Use both open and heavily occluded views. Measure frame time, submission cost, rendered geometry, and update cost.

**Trap:** A global grass or prop group can render large hidden areas. MultiMesh is a rendering representation, not automatic physics or gameplay optimization. Lighting limits apply to the group; validate the chosen renderer.

### 6.7 Merge static geometry selectively

**Action:** Combine small static meshes that share materials and are normally visible together, such as one inaccessible storefront assembly. Perform the combination ahead of play. Preserve separate doors, moving pieces and independently hidden rooms.

**Verify:** Compare open views and views where most of the assembly is hidden. Keep the merge only if submission savings outweigh lost culling and any memory growth.

**Trap:** Joining meshes while retaining many material surfaces may retain many draws. Joining an entire map sacrifices culling. Use spatial grouping, not “merge everything.” [R16]

### 6.8 Give textures a runtime memory budget

**Documented mechanism:** Texture import compression affects GPU memory; smaller source files alone do not establish smaller GPU allocations. Mipmaps are appropriate for most 3D textures. [R9]

**Action:** Inspect imported texture dimensions, compression mode, and mipmap settings. Try a half-resolution variant of low-priority textures. Reuse tiling materials/trim sheets where suitable. Check fine text and normal maps independently rather than applying one setting blindly.

**Verify:** Compare peak GPU memory and camera-motion quality after reimport. Test the closest legitimate viewing distance and an oblique surface. Measure frame time if bandwidth or memory pressure is suspected.

**Trap:** Disabling mipmaps to save memory can worsen distant sampling quality. Huge atlases can retain unrelated content together. PNG/JPEG file size is not runtime texture cost.

**Arithmetic illustration, not a measurement:** An uncompressed 2048×2048 RGBA8 image is 16 MiB at its base level, about 21.33 MiB with a full mip chain. At 1024×1024 it is 4 MiB, about 5.33 MiB with mips. Halving both dimensions quarters texel count. Actual compressed allocations depend on format, block alignment and engine/driver overhead.

### 6.9 Budget transparent screen coverage

**Action:** Treat smoke, glass, layered foliage and large blended effects as a screen-coverage problem. Use opaque materials where possible. Test alpha scissor/hash for suitable cutouts; trim empty transparent areas and reduce overlapping particle layers. Separate a small transparent part from an otherwise opaque asset when beneficial.

**Verify:** Test the closest camera position with the maximum permitted simultaneous effects. Compare GPU time, including at different internal resolutions. Inspect edges and sorting in motion.

**Trap:** A low-triangle particle can be expensive when it covers most of the screen repeatedly. Cutouts and extra surfaces also have costs; the replacement must be measured. [R2]

### 6.10 Spend dynamic shadows deliberately

**Project prescription:** Inventory every shadow-casting light and caster visible in a worst-case room. Identify which shadows communicate movement, threat, or spatial depth. Trial disabling shadows on tiny decorative casters, shortening useful shadow range, reducing oversized light coverage, and lowering shadow quality one setting at a time.

**Verify:** Measure shadow-pass and total GPU time. Test four simultaneous flashlights if supported, moving characters, doorways, and outdoor long shadows. Check that disabling a caster does not remove a gameplay cue.

**Trap:** Counting light nodes is insufficient; coverage, caster population, shadow rendering and overlapping influence change the cost. Lower-resolution shadows do not remove all shadow work.

### 6.11 Bake stable lighting

**Documented mechanism:** `LightmapGI` stores precomputed lighting and requires suitable UV2 data for baked geometry. [R7]

**Action:** For fixed layouts, prepare UV2, select appropriate static lightmap import settings, add `LightmapGI`, and bake the final arrangement. Compare static and dynamic light bake modes against gameplay needs. Preserve dynamic lighting where moving actors or changing lights require it.

**Verify:** Compare GPU time, lightmap memory, seams, actor integration and door behavior. Review lighting at the lowest supported texture/quality tier.

**Trap:** The lightmap represents the baked arrangement. Arbitrarily rearranging procedural rooms does not preserve cross-room lighting. For generated levels, use prevalidated configurations, carefully constrained module lighting, or a measured runtime alternative. Do not assume runtime rebaking is a cheap fix.

### 6.12 Isolate expensive environment effects

**Project prescription:** Add runtime debug toggles for supported GI, reflections, ambient occlusion, fog, volumetrics, and post effects. Toggle one family at a time. Compare a cheaper environment against the intended mood and navigation readability.

**Verify:** Use matched day, night, indoor and outdoor views. Attribute savings to GPU passes rather than assuming every enabled feature is expensive in the same way.

**Trap:** Renderer feature support differs. A quality preset that silently drops effects needs an intentional visual treatment. Avoid making “Low” too dark to play. [R8]

### 6.13 Simplify collision independently of art

**Documented mechanism:** Primitive shapes are generally suitable for dynamic bodies; convex and concave shapes have different uses and costs. [R13]

**Action:** Start with boxes/capsules/spheres. Use a small convex decomposition where needed. Use appropriately simplified static concave collision for complex environment surfaces instead of thousands of needless convex pieces. Remove collision from unreachable decoration and review layers/masks.

**Verify:** Capture physics time during peak contacts and query load. Test stairs, doors, cover, projectiles, thrown objects and moving platforms. Verify the selected physics backend.

**Trap:** Render LOD does not automatically simplify collision. Too many simple shapes can also be costly. Never sacrifice a collision silhouette required for reliable gameplay simply to reduce triangles.

### 6.14 Control active physics and debris

**Project prescription:** Cap persistent debris, allow suitable bodies to sleep, and replace cosmetic destruction with visuals that do not require full physical simulation. Give debris a lifetime or recycling rule. Limit expensive continuous collision detection to cases that need it.

**Verify:** Test simultaneous explosions and the settled aftermath. Compare active-body/contact counts and physics time. Ensure deletion or recycling does not remove valuable loot or break interactions.

**Trap:** One explosion is not the peak workload. Thousands of objects left behind can turn a brief effect into a permanent simulation cost.

### 6.15 Avoid unnecessary navigation work

**Documented mechanism:** Repeated path resets, synchronized queries, complex source geometry and runtime baking can create spikes. [R12]

**Action:** Request paths when goals materially change, rather than resetting every agent each frame. Stagger eligible requests while preserving response needs. Bake from simple traversal geometry; where runtime baking is necessary, follow the background-baking workflow and separately measure source parsing and map synchronization.

**Verify:** Use a crowd chasing moving targets, a blocked doorway, and an unreachable target. Record query counts and navigation/CPU spikes. Confirm agents still react quickly enough.

**Trap:** “Threaded bake” does not make every surrounding operation free. Do not reduce controller responsiveness or required movement updates just to lower query count.

### 6.16 Reduce optional update frequency

**Project prescription:** Classify behavior by urgency. Player movement and combat-critical decisions require timely updates. Ambient decisions, decorative motion and distant nonessential sensing may tolerate less frequent work. Prefer events over polling unchanged state. Spread optional updates across frames.

**Verify:** Compare CPU profiles at peak populations; test detection delay, animation transitions, audio cues and multiplayer state. Record the maximum added response latency explicitly.

**Trap:** Camera visibility is not gameplay relevance. An offscreen enemy can still shoot, hear, navigate or affect another player. Rendering culling alone is not permission to suspend authoritative simulation.

### 6.17 Move resource loading ahead of need

**Documented mechanism:** `ResourceLoader.load_threaded_request()` starts background loading; poll `load_threaded_get_status()` and retrieve only when ready. Calling `load_threaded_get()` too early can block. [R11]

**Action:** Request the next room before entry. Handle failed requests. Separately budget instantiation, scene insertion and initialization. Prewarm likely encounter resources where memory permits.

**Verify:** Record time for each stage, first-entry and repeat-entry stalls, and peak memory while old and new content overlap.

**Trap:** Background resource loading is not a guarantee of hitch-free scene activation. A large `instantiate()` or `_ready()` workload still needs restructuring, staging or a loading boundary. Do not mutate an active scene tree from arbitrary worker threads.

### 6.18 Prevent first-use pipeline surprises

**Documented mechanism:** Godot precompilation depends on seeing relevant meshes, materials and rendering features. Pipeline monitors reveal when new compilation occurs. [R10]

**Action:** Establish required rendering features during loading. Exercise representative actual material/mesh combinations, including overrides and effects, before combat. Avoid unnecessary runtime shader-source generation and feature changes; reuse a bounded set of tested variants.

**Verify:** Capture first fire, first enemy, first explosion, first reflection and first UI use. Correlate spikes with pipeline events and repeat the test on a clean documented environment where practical.

**Trap:** A warm developer machine can conceal the problem. Pipeline categories differ; background specialization is not equivalent to an on-demand draw compilation. Do not assume copying one computer's driver cache solves deployment.

### 6.19 Manage resource lifetime and transition peaks

**Project prescription:** Define which assets are mission-local and which persist. Release obsolete references after transitions. Bound caches and object pools. Compare memory after repeated load/play/unload cycles, allowing delayed cleanup to settle.

**Verify:** Record both transient peaks and settled baselines for at least ten cycles initially. Investigate continued growth; distinguish intentional cache growth from retained scenes/resources.

**Trap:** A pool may reduce spawn spikes while consuming excessive memory. Unchanged OS process memory alone does not prove a leak or prove correct cleanup; inspect live objects/resources and allocation behavior as well.

### 6.20 Cap secondary workloads

**Project prescription:** Treat mirrors, security cameras and other SubViewports as additional rendering workloads. Reduce their resolution/update frequency or suspend them when irrelevant. Cap particle emitters, overlapping audio voices, expensive audio effects and looping decorative systems.

**Verify:** Test a room with all screens, alarms and combat effects active. Compare CPU/GPU/audio workload and perceptual quality. Test reactivation so a paused screen or emitter does not resume incorrectly.

**Trap:** A small screen in the world can still render an expensive full scene. A looping cosmetic system can continue working long after the player leaves.

## 7. Apply the techniques during asset production

### Asset handoff contract — project prescription

Every reusable asset family should declare:

| Field | Required information |
| --- | --- |
| Role | Hero, interactive prop, repeated decoration, architecture, backdrop |
| Viewing conditions | Closest distance, expected screen coverage, silhouette priority |
| Geometry | Imported triangles/vertices, surfaces, LOD behavior |
| Materials | Shared resource IDs, shader features, transparency mode |
| Textures | Dimensions, imported formats, mips, expected residency |
| Lighting | Shadow policy, baked/dynamic role, UV2 if required |
| Collision | Shapes, layers, masks, intended interactions |
| Behavior | Scripts, animation, physics, audio, update frequency |
| Multiplicity | Expected visible, active and resident counts |
| Evidence | Representative scene, capture, hardware, result status |

**Artist workflow:** Author the silhouette first; spend detail where players can see it. Remove permanently inaccessible geometry only after checking shadows, reflections and future gameplay use. Reuse material families. Import into the actual game early. Review at actual resolution and motion speed, not only in a close-up modeling viewport.

**Approval workflow:** Test one instance for correctness, then the intended repeated population for runtime cost. A cheap isolated prop can become expensive when it adds a unique material, collision body and script to every shelf slot.

For an intentionally older-console visual style, use simpler silhouettes, deliberate textures, restrained material features and baked detail where suitable. The style itself is not a performance guarantee; modern lights, transparency and simulation can dominate a low-poly scene.

## 8. Apply the techniques during level production

| Stage | Required runtime work | Exit evidence |
| --- | --- | --- |
| Blockout | Establish worst sightlines, traversal routes, gameplay density and inactive backdrop boundaries | Baseline route and target-hardware capture |
| First art slice | Prove representative geometry, lighting, materials, enemies and effects together | Measured asset-family budgets |
| Content expansion | Recheck peak visible/active/resident populations | Regression results at each meaningful addition |
| Lighting pass | Compare shadow and environment alternatives | Approved quality/performance tradeoffs |
| Gameplay complete | Stress waves, destruction, doors, traversal and host workload | Worst-case captures and corrected bottlenecks |
| Release candidate | Test exported builds, first-use behavior, transitions and long sessions | Acceptance record on supported tiers |

### Example: a convenience-store mission

This is a test plan, not a benchmark result.

- **Exterior:** Look diagonally across the parking lot into the store. Check distant frontage proxies, long shadows, glass and visible interior detail together.
- **Interior:** Stand where the most shelf products are visible. Compare shared resources and spatial instancing while preserving independent culling between aisles.
- **Doorway:** Open and close the entrance while crossing it. Catch incorrect occluders, lighting transitions and resource-activation stalls.
- **Combat:** Trigger the maximum supported enemies, weapon effects, flashlights, glass/debris and alarms simultaneously.
- **Back room:** Check that unseen exterior detail is culled without stopping gameplay that remains relevant elsewhere.
- **Exit/restart:** Repeat the mission to expose retained state, growing memory and repeat initialization cost.

For distant unplayable neighborhoods, author the views actually exposed by the playable camera. Prefer shells/proxies without room contents, collision or scripts unless a system requires them. Verify rooftops, balconies and alternate sightlines before removing detail.

## 9. Requirements for procedural level and asset tools

Project prescriptions for a generator that must continue producing performant content:

1. **Stable reproduction:** Save seed, generator version, asset catalog version, settings and engine version for every failing output.
2. **Shared resources:** Reuse mesh/material/texture resources; avoid accidental per-placement duplication.
3. **Separate representations:** Generate visual geometry, collision, navigation source, occlusion and backdrop proxies according to their different needs.
4. **Spatial organization:** Partition render groups by visibility/streaming zones rather than one global batch.
5. **Bounded variability:** Declare maximum enemies, lights, effects, physics bodies and unique material variants, including their combined peak.
6. **Activation policy:** Distinguish loaded, visually active and simulation-active content. In multiplayer, account for every relevant player.
7. **Generation timing:** Place heavy construction before play where possible. Profile runtime generation, activation and upload stages separately if unavoidable.
8. **Validation output:** Emit counts, texture estimates, resource uniqueness, missing LOD/occluder flags, collision complexity and suspicious unbounded systems.
9. **Stress seeds:** Maintain known difficult seeds: long sightlines, dense shelves, narrow navigation bottlenecks, many doorways, and simultaneous effects.
10. **Runtime gate:** Treat static reports as warnings. Approve generator versions only after benchmark routes on actual exports.

A generator should fail or flag invalid content early, with a useful reason: “this seed exceeds the validated simultaneous shadow-light policy” is actionable. “too many polygons” without a measured context is not.

## 10. Multiplayer runtime considerations

Apply this section if the game supports co-op or a listen server. These are project design prescriptions, not a claim that Godot automatically supplies relevance management.

- Test clients and the host separately. A listen server also pays authoritative simulation and serialization costs.
- Use several physical devices for representative network performance; multiple local clients contend for the same hardware.
- Render optimization is local to each camera. Simulation relevance may be the union of several players' areas.
- Keep persistent mission state independent from visual representation. A hidden loot object still needs correct ownership/state.
- Replicate required gameplay state at an appropriate rate; do not transmit every decorative transform by default.
- Test dispersed players as well as grouped players, including one outside and another inside the same building.
- Measure bandwidth, serialization time, tick stability and correction behavior alongside frame timing.
- Preserve hit registration, enemy awareness and interaction responsiveness when reducing update frequency.

Changing physics or network tick rates is a gameplay/network design change. It requires its own validation and is not a first-line fix for expensive art.

## 11. Acceptance checklist and maintenance

### Asset accepted

- [ ] Tested at intended screen size and repeated population.
- [ ] LOD/proxy transitions preserve required silhouette and readability.
- [ ] Materials and texture imports meet the measured family policy.
- [ ] Shadow, collision and behavior costs are intentional.
- [ ] No unnecessary unique resources or persistent update loops.
- [ ] Runtime evidence identifies the export, device and settings.

### Level accepted

- [ ] Worst sightline and combat route meet frame-time/tail requirements.
- [ ] First-use and repeat-use stalls are tested separately.
- [ ] Doors, windows and destructible blockers do not produce culling errors.
- [ ] Peak transition memory fits the agreed tier.
- [ ] Repeated missions do not show unexplained growing resource use.
- [ ] Minimum quality remains playable and visually coherent.
- [ ] Multiplayer host and dispersed-player scenarios pass when applicable.

### Optimization accepted

- [ ] A/B evidence exceeds expected run-to-run noise.
- [ ] The expected mechanism is observable.
- [ ] Visual/gameplay regressions are absent or explicitly approved.
- [ ] Memory, load time and responsiveness tradeoffs are recorded.
- [ ] The improvement survives a release export on target hardware.
- [ ] A regression scenario and rollback path exist.

Stop tuning when the agreed performance contract is met with appropriate reserve and further complexity is not justified. Reopen the work when content, hardware targets, renderer, drivers or engine versions change materially. Rebaseline after engine upgrades; results belong to a specific configuration.

## 12. Common mistakes to reject in review

| Claim or shortcut | Correction |
| --- | --- |
| “It has fewer triangles, so it is optimized.” | Show the limiting runtime cost and measured outcome. |
| “It is one mesh, so it is one draw.” | Materials/surfaces and rendering passes still matter. |
| “MultiMesh is always faster.” | Test visibility granularity and update cost. |
| “It is behind a wall, so it is free.” | Confirm occlusion, simulation policy and residency independently. |
| “The PNG is smaller, so VRAM is lower.” | Inspect imported format, dimensions and actual GPU memory. |
| “Async loading removes the hitch.” | Time instantiation, insertion, initialization and pipelines too. |
| “The average is 60 FPS.” | Inspect p95/p99, deadline misses and hitch severity. |
| “It runs well on the developer PC.” | Validate minimum supported hardware and shipping settings. |
| “A demo proves our level will be faster.” | A demo proves a mechanism in its own conditions. Run the project experiment. |
| “We will optimize after all the levels are done.” | Validate architecture and content families before multiplying them. |

## 13. Primary references and reusable demonstrations

All links below were consulted for this guide on 3 October 2026. The documentation is pinned to **4.7** rather than the moving `stable` alias. The recipes combine the documented mechanisms with explicitly identified project prescriptions; references do not imply published benchmark gains for this project.

- **[R1] General optimization tips:** measurement, bottlenecks, efficient design, and external profilers. https://docs.godotengine.org/en/4.7/tutorials/performance/general_optimization.html
- **[R2] Optimizing 3D performance:** culling, instancing eligibility, transparency and related 3D tradeoffs. https://docs.godotengine.org/en/4.7/tutorials/performance/optimizing_3d_performance.html
- **[R3] Mesh level of detail:** import workflow, debug comparisons and LOD thresholds. https://docs.godotengine.org/en/4.7/tutorials/3d/mesh_lod.html
- **[R4] Visibility ranges:** HLOD, visibility parents, margins and fade behavior. https://docs.godotengine.org/en/4.7/tutorials/3d/visibility_ranges.html
- **[R5] Occlusion culling:** setup, baking, bounds and runtime tradeoffs. https://docs.godotengine.org/en/4.7/tutorials/3d/occlusion_culling.html
- **[R6] MultiMesh API:** group bounds, instance rendering and limitations. https://docs.godotengine.org/en/4.7/classes/class_multimesh.html
- **[R7] LightmapGI:** UV2 requirements, setup and baked-lighting constraints. https://docs.godotengine.org/en/4.7/tutorials/3d/global_illumination/using_lightmap_gi.html
- **[R8] Renderer overview:** features, platform suitability and switching limitations. https://docs.godotengine.org/en/4.7/tutorials/rendering/renderers.html
- **[R9] Importing images:** texture compression modes, mipmaps and 3D import behavior. https://docs.godotengine.org/en/4.7/tutorials/assets_pipeline/importing_images.html
- **[R10] Pipeline compilation stutter:** precompilation, feature detection and compilation monitors. https://docs.godotengine.org/en/4.7/tutorials/performance/pipeline_compilations.html
- **[R11] Background loading:** request, status and retrieval semantics. https://docs.godotengine.org/en/4.7/tutorials/io/background_loading.html
- **[R12] Navigation optimization:** path query behavior, source parsing and baking. https://docs.godotengine.org/en/4.7/tutorials/navigation/navigation_optimizing_performance.html
- **[R13] Collision shapes:** primitive, convex and concave shape tradeoffs. https://docs.godotengine.org/en/4.7/tutorials/physics/collision_shapes_3d.html
- **[R14] The Profiler:** interpreting Godot profiling information. https://docs.godotengine.org/en/4.7/tutorials/scripting/debug/the_profiler.html
- **[R15] Debugger panel:** monitors, profiling and debugging tools. https://docs.godotengine.org/en/4.7/tutorials/scripting/debug/debugger_panel.html
- **[R16] GPU optimization:** rendering submission, material reuse and static-merge tradeoffs. https://docs.godotengine.org/en/4.7/tutorials/performance/gpu_optimization.html

**Practical demonstration:** R3 and R5 link to Godot's official **Occlusion Culling and Mesh LOD demo project**. Use the linked compatible revision to inspect the mechanism, then repeat the same on/off comparison in your level. This guide did not execute that demo. Record the revision and engine version if using its results as supporting evidence.
