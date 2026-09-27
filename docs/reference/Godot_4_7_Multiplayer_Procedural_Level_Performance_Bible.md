# Godot 4.7 Multiplayer Level Performance Bible

## Purpose

A practical production standard for building attractive, playable 3D multiplayer levels in Godot 4.7, especially levels assembled or varied by a procedural tool. It covers the content the generator places: meshes, materials, lighting, collision, effects, audio, and networked gameplay objects.

The goal is not to chase one magic draw-call or polygon count. A level is performant when its worst representative play moment stays inside the frame, memory, and network budgets on the minimum supported hardware, with headroom for combat and player actions.

> **Budget note:** Godot documentation explains engine behavior, not universal per-level limits. Numeric values below are initial project budgets for a typical 3D multiplayer action game. Profile a representative build on the actual minimum target, then tune them. Keep the ratios and gates even when the absolute limits change.

## 1. Performance contract

The level creator must know these project inputs before generating content:

| Input | Required project setting | Why the generator needs it |
|---|---|---|
| Client frame target | 30, 60, or 120 FPS | Sets total frame time and content complexity |
| Minimum client hardware | GPU, CPU, RAM, VRAM, resolution, renderer | Determines what “passes” means |
| Maximum players in one view | Design maximum, including split-screen if applicable | Defines worst-case characters, shadows, animation, effects, and replication |
| Server model | Dedicated server, listen server, or peer hosted | Changes server CPU, physics, and bandwidth budgets |
| Network envelope | Tick/update rate, expected RTT/loss, bandwidth per client | Prevents level content from creating unbounded replicated state |
| Gameplay density | Maximum active NPCs, projectiles, breakables, lights, and effects | Defines the combat stress case |
| Streaming model | Whole-level load, chunks, or additive scenes | Determines how content and memory are partitioned |

### Frame-time targets

Frame time is the useful budget: 30 FPS allows 33.33 ms, 60 FPS allows 16.67 ms, and 120 FPS allows 8.33 ms for the entire frame. Do not allocate the whole frame to the level; gameplay, UI, networking, audio, and operating-system overhead also need time.

| Target | Whole-frame limit | Level content target (CPU and GPU) | Practical pass condition |
|---|---:|---:|---|
| 30 FPS | 33.33 ms | Aim for ≤24 ms each | 1% low remains near 30 FPS in worst-case play |
| 60 FPS | 16.67 ms | Aim for ≤12 ms each | 1% low remains near 60 FPS in worst-case play |
| 120 FPS | 8.33 ms | Aim for ≤6 ms each | 1% low remains near 120 FPS in worst-case play |

CPU and GPU work overlap, so do not add their timings together. The slower side is the immediate frame-rate ceiling. Treat the gap between the content target and whole-frame limit as room for the rest of the game and short spikes. Measure frame-time percentiles, not only average FPS.

**Starting quality tiers when the project has not set its own:** author a Baseline tier for the minimum supported device, a Default tier for common hardware, and an Enhanced tier for optional visual quality. Do not make level geometry or gameplay visibility depend on the tier.

## 2. Runtime budget matrix

Use this as a first-pass per-client budget for the busiest camera view. The counts are ceilings for initial profiling, not promises that a scene will run well at those counts.

| Cost area | 30 FPS starting point | 60 FPS starting point | 120 FPS starting point | Generator rule |
|---|---:|---:|---:|---|
| Visible opaque render submissions | ≤1,200 | ≤800 | ≤500 | Prefer shared materials and instancing; count actual passes, not only mesh nodes |
| Visible triangles, baseline camera | ≤1.5M | ≤1.0M | ≤700K | Use LODs; inspect close combat and long sightlines separately |
| Real-time shadow-casting lights affecting view | 1 sun + 2 local | 1 sun + 2 local | 1 sun + 1 local | Prefer baked/static lighting; local lights should have short ranges |
| Dynamic shadow casters | ≤100 | ≤60 | ≤40 | Disable shadows on small clutter and distant characters |
| Active physics bodies (all types) | ≤500 | ≤350 | ≤250 | Most scenery is static geometry; keep dynamic bodies rare |
| Active rigid bodies | ≤80 | ≤50 | ≤30 | Use only for objects with actual physical gameplay |
| Visible animated characters | Project specific | Project specific | Project specific | Budget rigs, bones, animation updates, and shadows together |
| Active particles | ≤10K simple particles | ≤7K | ≤4K | Prefer GPU particles for visual-only effects; cap emitters and lifetime |
| Unique materials in a visible area | ≤100 | ≤80 | ≤60 | Reuse material resources and atlases; reduce one-off variants |
| Networked stateful world objects per interest area | ≤ project cap | ≤ project cap | ≤ project cap | Replicate gameplay state only; derive visuals locally |

**Why submissions and triangles are not enough:** one material can have multiple passes; transparent surfaces, shadows, GI, screen-space effects, overdraw, shader cost, skinning, and physics can dominate. Use Godot’s profiler and rendering monitors on the project build to discover the actual bottleneck.

## 3. Asset authoring matrix

| Asset class | Model and import rule | Material / texture rule | Runtime rule |
|---|---|---|---|
| Hero / interactable prop | Silhouette first; keep detail in normal maps and trim sheets; author a simplified collision mesh | Reuse shared material families; avoid unique 4K maps for small props | A hero asset may have more detail, but it must have a tested distance LOD and a clear interaction range |
| Repeated prop (chairs, crates, lamps) | One reusable mesh where possible; consistent pivot and dimensions | Same material set across variants; use packed ORM maps where appropriate | Instance repeated meshes; use MultiMesh for dense, visually simple repetition, partitioned into local groups |
| Foliage / debris | Low silhouette complexity; avoid dense overlapping cards | Share atlas/material; avoid expensive translucency | Use MultiMesh for static clutter; set a correct custom AABB; split large fields so invisible areas can cull |
| Building / architecture | Modular pieces with clean seams; separate occluding walls from small trim | Use trim sheets and a small material palette | Separate interiors/rooms/chunks for culling and streaming; do not make an entire city one giant mesh |
| Character | LOD meshes, bounded material slots, simple distant rig | Share skin/hair/material variants where practical | Stop or reduce animation at distance; use simplified shadows/attachments for remote players |
| VFX | Prefer simple geometry and short lifetime | Minimize transparent full-screen coverage and layered alpha | Cap simultaneous emitters; gameplay-critical effects must remain readable at low quality |
| Collision | Author simple primitives or low-complexity static collision separate from render mesh | No render material needed | Do not use detailed render meshes as general collision; never give decorative clutter collision by default |

### Mesh LOD and visibility

- Author at least a near and far representation for large/high-silhouette assets. Add a middle LOD when profiling shows a benefit.
- Keep all LODs’ silhouette, pivot, and bounds aligned to avoid visible popping and bad culling.
- Use `GeometryInstance3D` visibility ranges for whole-object transitions and HLOD clusters; use mesh LOD for a single object’s geometry reduction.
- Set distant clutter to disappear before it becomes sub-pixel noise. Replace a cluster with a cheap silhouette or impostor only when it improves the actual camera view.
- Do not rely on occlusion culling in open sightlines. In interiors and dense streets, use simple opaque walls and occluders. Godot 4.7 occlusion culling is CPU-driven; avoid complex occluders that cost more to process than they save.

### Instancing and batching

- Use `MultiMeshInstance3D` for many identical, mostly static meshes such as grass clumps, rocks, rubble, or repeated lights without individual gameplay behavior.
- Keep each MultiMesh spatially compact. Godot culls a MultiMesh as a whole, not each contained instance; a huge field can draw when most of it is off-screen.
- Do not put objects requiring individual collision, interaction, replication, animation, or visibility decisions into a MultiMesh without a separate gameplay representation.
- Reuse mesh/material resources. Godot sorts by material/shader, but unique materials and state changes still add overhead.
- Batching is not a substitute for culling. One massive batch can reduce submissions while increasing invisible geometry and overdraw.

## 4. Level and environment rules

| Level feature | Authoring rule | Generator validation |
|---|---|---|
| Play space | Design combat rooms, lanes, and traversal around intended player count; preserve readable routes and cover | Validate navigation/connectivity, spawn spacing, and sightlines for all generated variants |
| Sightlines | Break very long views with turns, elevation, architecture, fog, or distant HLOD | Capture worst-case camera locations looking down the longest route |
| Occlusion | Use solid architecture as useful occluders; avoid relying on thin leaves, fences, or transparent curtains | Check that occluder volumes hide meaningful geometry and do not hide visible objects |
| Chunking | Divide large maps into rooms/sectors that align with natural visibility and streaming boundaries | Report per-sector visible objects, memory, lights, and network interest size |
| Set dressing | Place detail in clusters near player paths; leave low-value space visually quiet | Enforce density limits by distance band and region |
| Background world | Use low-cost skyline/backdrop meshes or impostors outside playable space | Background objects have no collision, scripts, navigation, or network replication |
| Destruction | Keep the number of simultaneously destructible items bounded; represent debris with pooled or cosmetic pieces | Stress-test simultaneous destruction and reset/cleanup |
| Navigation | Bake/author navigation for stable geometry; avoid runtime rebakes for ordinary procedural variation | Validate nav connectivity and cap active agents/path requests |

**Density by distance:** spend detail where players can inspect it. A practical zoning model is: interaction zone (full detail and gameplay), combat zone (readable mid-detail), traversal/background zone (LOD and sparse collision), and horizon zone (static, noninteractive silhouettes). Distances should be tuned to the game’s camera, movement speed, and resolution.

## 5. Lighting and visual quality

| Lighting use | Preferred choice | Rules |
|---|---|---|
| Static interior / fixed time of day | `LightmapGI` | Bake static lighting; use probes for moving characters; reserve real-time lights for gameplay or deliberate accents |
| Large outdoor level | Directional sun + sky/ambient lighting; evaluate baked lighting or SDFGI against the target hardware | Keep local shadow lights rare and short-range; design the sky/ambient contribution before adding fill lights |
| Small moving accent (muzzle flash, spell, lamp) | Short-lived local light, usually without shadows | Pool or reuse; cap simultaneous lights; avoid making every emissive prop a real light |
| Dynamic global illumination | Use only if the visual requirement needs it and the minimum target sustains the cost | Test heavy combat, camera movement, and low-end hardware; provide a lower-cost tier |
| Reflections | Reflection probes or screen-space options as needed | Avoid many overlapping probes; baked lightmaps need an appropriate reflection strategy |

- Bake what does not need to change. Godot documents LightmapGI as a static approach with low runtime cost; dynamic lighting remains available for moving objects and gameplay accents.
- A level should have a deliberate light budget. A local light only earns its cost when it changes player decisions, readability, or mood.
- Prefer emissive materials for decorative glow; use real lights only when nearby surfaces or characters must be illuminated.
- Avoid large numbers of shadow-casting OmniLight3D/SpotLight3D nodes, overlapping shadow volumes, and long-range local shadows.
- Use light layers / cull masks deliberately if the game has effects or player-only lighting.
- Keep fog and volumetric effects purposeful. Test the worst view at native resolution; full-screen effects can be fill-rate bound.
- Quality settings should reduce expensive features cleanly: shadow resolution/distance, GI mode, volumetric fog, screen-space effects, and render scale.

## 6. Physics, interaction, and navigation

- Every visible object does not need collision. Decorative clutter should usually be visual-only.
- Prefer primitive collision shapes (box, capsule, sphere, cylinder) for gameplay props. Use simple static concave geometry only for fixed level architecture. Use simplified convex shapes for moving rigid bodies.
- Use one or a few shapes per object. Complex compound collision on thousands of props increases broad-phase and contact work.
- Assign collision layers and masks narrowly. A projectile should not test against UI-only, cosmetic, or irrelevant layers.
- Pool high-churn projectiles and transient effects where profiling shows creation/destruction spikes.
- Do not run per-frame raycasts or overlap scans for every prop. Query only when gameplay requires it; stagger or batch noncritical queries.
- Navigation agents should be limited to actual active actors. Use distance/visibility policies to reduce update frequency for distant AI, and cap concurrent path queries.
- For procedural geometry, generate gameplay collision from the simplified blockout/collision recipe, not from the final render mesh.
- Test physics with the maximum players, NPCs, projectiles, and destructible objects active together.

## 7. Multiplayer-aware level content

The rendering client and authoritative server have different budgets. A dedicated server normally does not need to instantiate or render visual meshes, materials, lights, particles, or audio. Keep server gameplay state separate from client presentation where the architecture permits.

| Content | Replicate? | Recommended representation |
|---|---|---|
| Static level geometry and dressing | No, if every peer loads the same deterministic level/version | Share a level seed and generation/version data when appropriate; verify identical gameplay collision/navigation |
| Player transforms and gameplay state | Yes, within the project’s chosen authority model | Synchronize only required state at an intentional tick/update rate; interpolate presentation on clients |
| Cosmetic animation, dust, sparks, local audio | Usually no | Trigger locally from replicated gameplay events or deterministic local presentation |
| Projectile | Replicate gameplay-relevant spawn/state/hit outcome | Avoid syncing every visual particle or trail segment |
| Destructible object | Replicate authoritative state change, not its full visual simulation | Send stable object ID + state/event; construct debris locally |
| Doors, switches, pickups | Yes, if they affect play | Send compact state transitions; avoid continuously synchronizing unchanged values |
| AI | Authoritative gameplay state only | Client visuals interpolate; do not replicate every internal AI variable |
| Background crowds / ambient wildlife | No, unless gameplay interacts with them | Local cosmetic simulation with strict caps |

### Network rules for the level generator

- Treat network traffic as a gameplay budget, not an art-asset budget. A crate is cheap until it has a unique network identity, frequent updates, collision, and replicated destruction state.
- Static map pieces should not each become networked nodes. Keep them local and deterministic where possible.
- Every networked object type must declare: authority, spawn/despawn rule, fields replicated, update/event conditions, relevance range, and maximum simultaneous count.
- Use interest management so clients do not receive distant or irrelevant state. Godot’s high-level multiplayer supports visibility concepts through multiplayer synchronizers/spawners; validate the project’s exact behavior and architecture.
- Prefer event/state-change messages to frequent unchanged property replication. Do not broadcast decorative changes to all peers.
- Make procedural seeds/versioning explicit. A seed alone is insufficient if engine version, content set, or generation rules can differ; include a generation version and validate critical collision/nav results.
- Test packet rate and bytes per client at maximum players in a worst-case encounter. Add latency and packet loss; local LAN testing alone is not acceptance.

## 8. Procedural generation contract

Every generated level must carry measurable metadata. The generator should fail, warn, or down-tier a layout before runtime when a limit is exceeded.

### Required generated report

| Metric | Report by | Gate |
|---|---|---|
| Mesh instances, unique meshes, unique materials | Level and sector | Alert on budget excess; identify top contributors |
| Estimated visible triangles / draw submissions | Camera test point and sector | Run from spawn, central combat, longest sightline, and highest vantage point |
| Lights and shadow casters | Level and sector | Hard-cap real-time shadow lights; report overlap hotspots |
| Collision objects and shapes | Level and sector | Exclude cosmetic-only objects; report complex or high-shape-count bodies |
| Navigation regions, agents, path requests | Level | Validate connectivity and runtime agent cap |
| Texture memory and render-target cost | Asset and level | Identify high-resolution outliers and duplicated textures |
| Networked object counts and expected update rates | Object type and interest area | Must fit project’s per-client/server envelope |
| Chunk/sector load size and activation time | Sector | No large synchronous spawn spike during play |

### Generation-time gates

1. **Validate source recipe:** references resolve, object dimensions/pivots are sane, LODs and collision variants exist where required.
2. **Build gameplay shell first:** navigation, collision, spawns, traversal, cover, and combat flow pass before detail dressing.
3. **Place by density zone:** apply object caps by sector and distance band; reject duplicate clutter filling the same visual role.
4. **Assign render and gameplay roles:** every object is tagged as gameplay-critical, visual-only, background, replicated, static, or dynamic.
5. **Apply optimization metadata:** material family, LOD/range, occluder eligibility, shadow policy, collision policy, network policy, and streaming sector.
6. **Compile a stress level:** combine the maximum supported players with maximum planned AI, effects, projectiles, lights, and destruction.
7. **Run camera probes:** test spawn, combat center, long corridor/sightline, elevated view, and an intentionally clutter-heavy view.
8. **Profile on target:** compare CPU/GPU frame time, memory, draw calls, physics, and network counters against the project baseline.
9. **Store the report with the level seed and generation version** so regressions can be reproduced.

## 9. Profiling and acceptance checklist

### Before optimizing

- Record the exact Godot version, renderer, resolution, hardware, player count, level seed, and graphics tier.
- Use a release/export build for final measurements; editor overhead can distort results.
- Profile a repeatable worst-case scenario, not an empty spawn room.
- Determine whether the bottleneck is CPU, GPU, physics, memory, loading, or network before changing content.

### Pass criteria

- [ ] 1% low frame rate meets the project target in worst-case combat on minimum client hardware.
- [ ] CPU and GPU frame-time targets retain planned headroom; no recurring spikes from generation, spawn/despawn, shader compilation, or scene loading.
- [ ] Peak RAM/VRAM stay below project limits with the largest supported level and session duration.
- [ ] No unbounded node, physics body, light, particle, or network-object growth over a full match.
- [ ] No decorative/background object has accidental collision, script processing, navigation, or replication.
- [ ] LOD, visibility ranges, occlusion, shadows, and MultiMesh bounds are visually correct from all probe cameras.
- [ ] Server CPU and network bandwidth pass at maximum players and worst-case gameplay activity.
- [ ] Multiplayer clients see matching gameplay collision, traversal, and interactable states across generated versions.
- [ ] Baseline and enhanced visual tiers preserve gameplay readability and map navigation.
- [ ] The generation report and profiler capture are saved with the level seed/version.

## 10. Triage order when a level misses budget

1. **Measure first.** Identify whether CPU, GPU, physics, memory, loading, or network is over budget.
2. **GPU-bound:** reduce shadowed lights and shadow distance, transparent overdraw, expensive screen effects, and overly dense visible geometry; verify LOD/HLOD and occlusion.
3. **CPU/render-bound:** reduce unique submissions/material variants, per-frame scripts, scene-tree churn, and unnecessary visibility/processing; instance static repetition.
4. **Physics-bound:** remove decorative collision, simplify shapes, narrow collision masks, reduce active rigid bodies and query frequency.
5. **Network-bound:** reduce replicated object counts and update frequency, send state changes, and tighten interest management.
6. **Memory-bound:** reduce texture sizes/duplication, stream or unload sectors, and cap simultaneous assets/effects.
7. **Stutter-bound:** move expensive generation/loading off the gameplay critical path where safe, prewarm shaders/assets, and pool high-churn objects after profiling confirms the source.
8. Re-run the same seed, cameras, player count, and scenario. Keep a before/after measurement.

## 11. Godot 4.7 implementation notes

- `MultiMesh` reduces per-instance submission overhead, but its instances are culled together and its visibility bounds must be correct.
- Godot’s occlusion culling uses CPU work and currently does not provide general dynamic-occluder behavior; use simple, stable occluders and profile them.
- Environment quality controls are largely project settings, allowing graphics tiers to be managed centrally.
- LightmapGI suits mostly static scenes and has low runtime cost; dynamic lights still cost runtime work.
- Multiplayer performance depends on the game’s authority and replication design. The level generator should declare object policies and expose counts rather than assume engine synchronization makes content free.
- A dedicated-server export should omit visual-only work wherever possible; confirm this in the project architecture and server build rather than relying on visibility alone.

## Official Godot references

- [Godot 4.7 Performance documentation](https://docs.godotengine.org/en/4.7/tutorials/performance/index.html)
- [Godot 4.7 Optimizing 3D performance](https://docs.godotengine.org/en/4.7/tutorials/performance/optimizing_3d_performance.html)
- [Godot 4.7 MultiMesh optimization](https://docs.godotengine.org/en/4.7/tutorials/performance/using_multimesh.html)
- [Godot 4.7 MultiMesh class reference](https://docs.godotengine.org/en/4.7/classes/class_multimesh.html)
- [Godot 4.7 Mesh LOD](https://docs.godotengine.org/en/4.7/tutorials/3d/mesh_lod.html)
- [Godot 4.7 Visibility ranges (HLOD)](https://docs.godotengine.org/en/4.7/tutorials/3d/visibility_ranges.html)
- [Godot 4.7 Occlusion culling](https://docs.godotengine.org/en/4.7/tutorials/3d/occlusion_culling.html)
- [Godot 4.7 Environment and post-processing](https://docs.godotengine.org/en/4.7/tutorials/3d/environment_and_post_processing.html)
- [Godot 4.7 Using LightmapGI](https://docs.godotengine.org/en/4.7/tutorials/3d/global_illumination/using_lightmap_gi.html)
- [Godot 4.7 3D collision shapes](https://docs.godotengine.org/en/4.7/tutorials/physics/collision_shapes_3d.html)
- [Godot 4.7 High-level multiplayer](https://docs.godotengine.org/en/4.7/tutorials/networking/high_level_multiplayer.html)
- [Godot 4.7 MultiplayerSynchronizer](https://docs.godotengine.org/en/4.7/classes/class_multiplayersynchronizer.html)

---

**Working rule:** Build to the project’s measured worst case. If a level cannot pass with the maximum players, combat density, and camera view active, it is not finished, even if it looks good in an empty editor viewport.
