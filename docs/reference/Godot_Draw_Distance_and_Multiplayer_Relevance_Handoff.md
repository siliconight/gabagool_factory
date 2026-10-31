---
document_id: godot_draw_distance_multiplayer_relevance
title: Draw Distance and Multiplayer Relevance Handoff
version: 1.0.0
updated: 2026-10-30
status: proposed_implementation_standard
audience: [engineering, technical_art, level_design, gameplay, networking, qa]
engine_family: Godot_4.x
engine_build: null
renderer: null
game_type: multiplayer_cooperative_pve_shooter
reference_experience: Left_4_Dead_style_horde_combat
target_fps: [60, 120]
units: {distance: meters, duration: seconds, frame_time: milliseconds}
normative_keywords: [MUST, SHOULD, MAY]
configuration_status: illustrative_not_production_tuned
---

# Draw Distance and Multiplayer Relevance

## 1. Decision and intended outcome

**Reduce the cost of distant or irrelevant content while preserving a coherent world, readable combat, and consistent multiplayer behavior.**

Draw distance is one part of the solution. The team should coordinate mesh detail, object visibility, effects, animation, loading, network interest, and authoritative simulation. Each addresses a different cost and needs independent controls.

Players should notice a stable, responsive game. They should rarely notice the transitions that make it possible.

This handoff targets dense cooperative PvE combat, including a four-player test scenario. It defines implementation requirements and verification practices, not a guarantee that arbitrary hardware will sustain 60 or 120 FPS. Hardware, resolution, renderer, encounter limits, and the exact Godot build must be recorded before performance sign-off.

### Reading and automation conventions

- **MUST** means a required correctness or release condition.
- **SHOULD** means the default approach; exceptions require a documented reason and evidence.
- **MAY** means an optional technique justified by profiling.
- IDs such as `REQ-001` and `AC-001` are stable references for tickets and checks.
- YAML examples describe application-owned data contracts. They are not built-in Godot configuration files or executable implementations.
- Engine facts cite official documentation using `[S#]`. Project policies and sample budgets are recommendations made by this document.

## 2. Non-negotiable requirements

| ID | Requirement |
| --- | --- |
| REQ-001 | Graphics presets MUST preserve gameplay-relevant visibility: threats, cover, traversal boundaries, objectives, and required attack cues. A cheaper representation is acceptable. An invisible relevant object is not. |
| REQ-002 | Render visibility MUST NOT directly determine authoritative enemy activity, damage, collision, or encounter state. |
| REQ-003 | Authoritative activity MUST consider every affected player and active gameplay dependency, including projectiles and objectives. |
| REQ-004 | Network interest MUST be evaluated per receiving peer and include enough preparation time before an entity can matter. |
| REQ-005 | Entity reactivation or renewed replication MUST restore current state without duplication, resurrection, or replaying obsolete actions. |
| REQ-006 | Expensive activation, path queries, and content preparation SHOULD be scheduled across updates rather than released as one burst. |
| REQ-007 | Performance claims MUST identify hardware, resolution, renderer, build, encounter load, and measured frame-time distribution. |
| REQ-008 | Every optimization MUST be evaluated against the bottleneck it is intended to reduce. |

## 3. Separate the systems

| System | Decision | Ownership | Does not automatically accomplish |
| --- | --- | --- | --- |
| Rendering | What should this camera draw, and at what detail? | Each client | Stop scripts, physics, AI, or networking |
| Presentation | How much animation, sound, and cosmetic work is useful? | Each client, constrained by gameplay cues | Change damage or attack timing |
| Replication | What state does this peer need, and when? | Authority/network layer | Decide whether an entity exists on the authority |
| Simulation | What behavior and interactions must run? | Server or authoritative host | Depend on the host camera |
| Residency | What resources and instances must remain ready? | Each process | Follow a single camera radius safely |

Maintain separate state for these decisions. A hidden enemy can remain active, audible, and replicated. A far building can retain collision and a simple visible shell while its decorative contents are absent.

## 4. Apply the appropriate Godot tools

### 4.1 Rendering toolkit

| Tool | Use | Implementation and limit |
| --- | --- | --- |
| Frustum culling | Skip drawing outside the camera view | Automatic. Do not use being offscreen as permission to stop gameplay. [S1] |
| Mesh LOD | Reduce geometric complexity | Inspect imported LODs, especially skinned meshes. Fewer triangles do not inherently remove material, animation, or node costs. [S2] |
| Visibility ranges | Remove optional detail or select manual representations | Use `GeometryInstance3D.visibility_range_begin/end` and margins. Thresholds use the instance AABB center, so large assets need special care. [S3] |
| HLOD | Replace a collection with a simpler distant representation | Author a proxy and configure visibility dependencies. Useful for reducing object submissions and material surfaces as well as detail. [S3] |
| Occlusion culling | Avoid drawing geometry behind solid structures | Enable occlusion culling and supply simplified occluders. Profile the CPU overhead and visual correctness. [S4] |
| MultiMesh | Draw repeated meshes efficiently | Partition by room, lot, or street segment. Instances share a visibility unit; a map-wide batch can prevent useful culling. [S5] |

Start with ordinary mesh instances and imported LODs. Add manual proxies, batching, or special systems where measurement shows a benefit. In Forward+, shared meshes and suitable shared materials may already benefit from automatic instancing. [S1]

### 4.2 Transition practices

1. Preserve silhouettes, rooflines, cover outlines, dominant colors, and material response across representations.
2. Judge transitions at gameplay resolution, normal movement speed, and supported aiming magnification. Distance alone does not describe how much screen space an object occupies.
3. Use hysteresis to avoid repeated switching at a boundary. For custom logic, simplify beyond an exit distance and restore detail at a smaller enter distance.
4. Prefer matched representations and stable switching first. Godot's built-in visibility alpha fades add transparency cost and are Forward+-only; other renderers need a different transition policy. [S6]
5. MAY use a custom dithered transition after testing noise, temporal artifacts, shadow behavior, and overlap cost. It is custom shader work, not the built-in visibility-range fade.
6. Avoid a conspicuous ring where all clutter disappears. Small deterministic variation MAY be applied to cosmetic thresholds, while retaining author control.
7. Inspect animated and shader-displaced bounds. Incorrect bounds cause premature culling. Avoid oversized bounds that defeat culling. [S6]

Alpha fades temporarily draw overlapping representations and can make dense scenery more expensive. Do not enable them globally as an assumed optimization.

### 4.3 Occluders and level layout

Use room boundaries, building shells, street bends, elevation changes, and offset entrances to create natural visibility breaks. Preserve useful combat sightlines; do not turn every space into a narrow corridor for performance.

Occluders MUST respect openings. A closed-door occluder must not continue blocking the view after the door opens or is destroyed. Avoid treating transparent windows, fences, and foliage as solid walls. Godot's occlusion tests use object bounds, so enormous merged meshes are harder to cull effectively. [S4]

Atmospheric haze MAY reduce the visual contrast of distant proxies. Fog itself does not remove the underlying geometry or processing work.

## 5. Content policy

| Content class | Close presentation | Distant treatment | Safety condition |
| --- | --- | --- | --- |
| Decorative clutter | Authored detail | Simplify or remove | No gameplay collision, concealment, or required interaction |
| Cover and barriers | Readable surface and outline | Preserve a cheaper representation | Visible boundary agrees with authoritative collision |
| Building shell | Detailed exterior | Simplified shell or block proxy | Keep openings, navigation landmarks, and sightline boundaries consistent |
| Interior dressing | Detail in accessible/viewable rooms | Cull occluded rooms; simplify viewed interiors | Do not expose empty rooms through windows or doorways |
| Ordinary enemies | Readable silhouette and actions | Cheaper mesh, materials, effects, and cosmetic animation | Preserve targeting and attack cues |
| Special enemies | Strong identification | Retain identity and threat cues | Relevance can override distance |
| Teammates/objectives | Relevant presentation | Cheaper mesh or approved marker | Preserve required tactical information |
| Cosmetic corpses/debris | Bounded local detail | Shorter lifetime, pooling, simplified physics | Separate from loot, obstruction, or other authoritative state |
| Effects and decals | Budgeted local presentation | Reduce count, lifetime, complexity, and range | Preserve damage-area boundaries and critical telegraphs |
| Lights and shadows | Prioritized nearby detail | Separate range and quality limits | Preserve required stealth/readability behavior if applicable |

Distances MUST be tuned by content class. Start with representative assets and measure them; this document deliberately does not prescribe one universal cutoff in meters.

For a distant storefront, retain its shell, sign, windows, and recognizable lighting. Remove individual bottles, shelf contents, and door hardware only when their absence is unobtrusive. Keep the cover provided by a parked car visible even after replacing its wheels and trim with a simpler mesh.

## 6. Client and authority responsibilities

| Concern | Client responsibility | Authority responsibility |
| --- | --- | --- |
| Geometry and cosmetics | Local detail and effect quality | No dependency on graphics preset |
| Movement | Present snapshots; predict where designed | Own/validate movement and interactions according to netcode design |
| Combat | Display aim, attacks, impacts, and feedback | Validate hits; own damage, health, death, and action timing |
| Enemy animation | Evaluate visual animation according to relevance | Keep authoritative timing and hit shapes independent of cosmetic throttling |
| Enemy activity | Present relevant entities | Consider all players and ongoing interactions |
| World state | Present current state | Preserve doors, destruction, loot, and objectives |
| Collision/navigation | Maintain what local prediction needs | Maintain what authoritative simulation needs |

A dedicated server SHOULD avoid loading unnecessary presentation assets. A listen server must perform both roles, so test host performance with the worst encounter occurring away from the host camera.

### 6.1 Enemy simulation tiers

The following is a project policy to implement, not an automatic Godot feature.

| Tier | Entry condition | Work policy |
| --- | --- | --- |
| Combat | Threatening/engaged with any player, or needed by an active interaction | Responsive authoritative movement, collision, attacks, and damage; budget expensive perception and planning separately |
| Approaching | Traveling toward likely contact | Maintain coherent approach; stagger replanning and noncritical perception |
| Background | Currently uninvolved and cannot affect immediate combat | MAY use coarse decisions or abstract travel if transitions preserve state and timing |
| Dormant | Authored encounter has no active dependency | Retain encounter state and explicit wake conditions |

Promotion MUST occur early enough to avoid an enemy waking in place or attacking without preparation. Demotion SHOULD require a grace period and no outstanding combat, projectile, objective, or player dependency.

An offscreen enemy firing at a teammate stays combat-relevant. A distant sniper can require higher relevance than a nearby uninvolved enemy behind several rooms.

Do not reduce the global physics tick rate to implement these tiers. Schedule selected decisions less frequently while keeping required integration and collision behavior consistent. Reduced-frequency movement needs a deliberate collision-safe model; simply skipping movement ticks can break speed and collision.

### 6.2 Horde workload scheduling

- Recalculate paths when goals or route conditions meaningfully change, with bounded refresh intervals appropriate to behavior.
- Distribute perception, target selection, and path requests across updates.
- Queue and prioritize work by threat and time until contact, with a maximum wait to prevent starvation.
- Limit expensive avoidance to agents that need it; validate crowd flow and collision behavior before reducing it.
- Prefer simplified navigation source geometry and offline baking for static levels. Runtime parsing/baking is not a substitute for a properly prepared level. [S7]
- Keep cosmetic skeletal work separate from hit detection. Throttled visual animation MUST NOT delay attacks or change damage windows.

## 7. Network interest and lifecycle

Network interest means deciding what each receiving peer needs. It must account for sightlines, auditory information, movement, attacks, objectives, and imminent interactions. Camera frustum alone is insufficient.

Godot's `MultiplayerSynchronizer` provides `set_visibility_for()`, `add_visibility_filter()`, and `update_visibility()`. Its visibility can influence spawning through `MultiplayerSpawner`. These controls concern replication, not mesh visibility. [S8]

### Required behavior

1. Authority evaluates relevance per peer using spatial candidates plus gameplay overrides.
2. Begin replication before exposure or interaction. Maintain a surrounding interest area so a fast turn does not reveal an unspawned threat.
3. Supply a complete initial state: stable entity ID, lifecycle generation, transform, velocity where needed, health, action state/time, and relevant persistent flags.
4. Initialize presentation from that state. Avoid interpolating from an old pooled position or replaying a completed action.
5. Use wider leave thresholds and grace time to avoid spawn/despawn churn.
6. Preserve authoritative state when a peer loses interest. Return current state when interest resumes.
7. Route important sound and event information independently where the source entity is not replicated.

A lifecycle generation distinguishes a reused pooled identity from its previous occupant. Retain enough removal/version information to reject stale packets and avoid resurrection. Handle late join and reconnect using the same state-restoration principles.

Replication frequency and interest membership are separate controls. `replication_interval` is configured per synchronizer; it is not automatically a different frequency for every receiving peer. Per-peer frequency tiers require an explicit replication design. Keep critical state changes dependable and ordered as required by that design. [S8]

Start with a broad, conservative interest set for a small cooperative mission. Tighten it only when bandwidth, serialization cost, or client entity processing warrants the complexity. Account for long-range weapons, projectiles, explosions, and audio before removing state.

## 8. Loading and residency

Keep rendering distance, loading distance, simulation relevance, and network interest separate. Their relative sizes depend on the entity and interaction; there is no safe universal ordering for every object.

For an approaching boundary, estimate:

`preparation_buffer_m >= max_relative_approach_speed_mps * readiness_time_s + safety_margin_m`

Readiness time includes resource loading, instantiation, activation, required GPU preparation, state receipt, and presentation initialization. Use conservative measured values under load. Teleports and scripted spawns require explicit preparation, not this distance formula alone.

Godot offers threaded resource requests. Check `load_threaded_get_status()` before retrieving a resource: calling `load_threaded_get()` too early can block. Background resource loading does not guarantee cheap scene instantiation or activation. [S9]

For a bounded mission, first try keeping the level resident while controlling visibility and activity. Add streaming when measured memory or loading constraints justify it. A streaming implementation MUST preserve required collision/navigation for every relevant player and entity, and budget activation work on the main thread.

## 9. Performance budgets and presets

| Target | Frame deadline | Proposed steady-load CPU and GPU ceilings, each |
| --- | --- | --- |
| 60 FPS | 16.667 ms | 13.3 ms |
| 120 FPS | 8.333 ms | 6.6 ms |

The ceilings reserve roughly 20% headroom and are proposed project budgets, not Godot guarantees. CPU and GPU work overlap; do not simply add their durations. Also measure end-to-end frame pacing and synchronization stalls.

Physics, decision updates, snapshot transmission, and rendering are separate clocks. A 120 FPS presentation target does not require 120 Hz AI or networking. Godot supports fixed physics ticks with interpolated presentation. Network snapshot interpolation still needs an explicit design; avoid accidentally applying two smoothing layers and adding excess latency. [S10]

### Preset policy

The performance preset SHOULD first reduce decorative shadow range, optional light count, particle density, decal lifetime, clutter distance, and environmental detail. It MAY use internal resolution scaling if GPU pixel cost is the bottleneck. Preserve required combat cues and shared world boundaries.

Do not change enemy counts, authoritative tick rate, damage timing, or mission state according to an individual client's graphics preset. If adaptive visual quality is added, use stable thresholds and cooldowns so quality does not oscillate during combat.

### Diagnose before tuning

| Observation | Investigate first |
| --- | --- |
| Lowering resolution substantially improves FPS | GPU pixel cost, effects, transparency, lighting |
| Simplifying visible meshes helps | Geometry, materials, shadows, submissions |
| Horde size hurts even when enemies are hidden | AI, physics, navigation, animation, replication |
| Doorway or corner causes a spike | Instantiation, activation, shader/pipeline work, network spawn burst |
| Separated players hurt host performance | Combined simulation/residency workload and per-peer replication |

These are diagnostic hypotheses. Confirm them with CPU/GPU traces and controlled comparisons.

## 10. Machine-readable policy example

This is one illustrative application contract. Null values are unresolved decisions and MUST block release-profile validation. Example preparation and network conditions MUST be replaced or approved using project measurements. Distances use meters with the project scale explicitly verified.

```yaml
schema_version: 1
policy_id: cooperative_pve_relevance
status: illustrative
engine:
  version: null
  renderer: null
  meters_per_world_unit: 1.0
test_environment:
  cpu: null
  gpu: null
  ram_gib: null
  resolution_px: null
  player_count: 4
  max_active_enemies: null
  network_rtt_ms: 100
  network_jitter_ms: 20
  packet_loss_percent: 1
profiles:
  fps_60:
    target_fps: 60
    frame_deadline_ms: 16.667
    steady_cpu_ceiling_ms: 13.3
    steady_gpu_ceiling_ms: 13.3
  fps_120:
    target_fps: 120
    frame_deadline_ms: 8.333
    steady_cpu_ceiling_ms: 6.6
    steady_gpu_ceiling_ms: 6.6
content_policies:
  decorative_clutter:
    cosmetic_only: true
    distance_cull_allowed: true
    detail_restore_distance_m: null
    detail_remove_distance_m: null
    transition: hysteresis
  gameplay_cover:
    cosmetic_only: false
    distance_cull_allowed: false
    distant_representation_required: true
    collision_owner: authority
  enemy:
    cosmetic_only: false
    distance_cull_allowed: false
    relevance_overrides:
      - threatening_any_player
      - visible_target
      - audible_gameplay_cue
      - active_projectile_dependency
      - objective_dependency
      - imminent_contact
authority:
  activity_scope: all_players_and_gameplay_dependencies
  camera_controls_simulation: false
  graphics_preset_controls_gameplay: false
  physics_tick_hz: null
  expensive_decision_queue:
    per_tick_budget_ms: null
    maximum_wait_ms: null
network:
  interest_scope: per_peer
  frustum_only_interest: false
  enter_distance_m: null
  leave_distance_m: null
  leave_grace_s: null
  full_state_on_interest_entry: true
  stable_entity_ids: true
  lifecycle_generation_required: true
loading:
  threaded_resources: true
  verify_loaded_before_get: true
  main_thread_activation_budget_ms: null
  measured_readiness_p99_s: null
  preparation_safety_margin_m: null
```

### Configuration validation rules

| ID | Rule |
| --- | --- |
| VAL-001 | Release profiles MUST resolve engine, renderer, hardware, resolution, encounter limit, tick rate, and operational budget fields. |
| VAL-002 | For cosmetic distance hysteresis, `detail_restore_distance_m < detail_remove_distance_m`. |
| VAL-003 | For distance-based network hysteresis, `enter_distance_m < leave_distance_m`; grace time must be nonnegative. Gameplay overrides may retain interest beyond these distances. |
| VAL-004 | Gameplay cover MUST retain a visible representation wherever it can block an interaction. |
| VAL-005 | Every content policy must resolve to an implemented adapter and a valid representation or culling behavior. |
| VAL-006 | Reject unknown enum values, negative distances, invalid frame targets, and unsupported fade modes for the selected renderer. |
| VAL-007 | Preparation buffers MUST cover measured readiness at the supported relative approach speed, including stress conditions. |

## 11. Implementation sequence and ownership

| Order | Owner | Work | Reviewable output |
| --- | --- | --- | --- |
| 1 | Engineering + QA | Pin build, renderer, hardware, resolution, enemy limit, and baseline scenarios | Baseline traces and completed performance profile |
| 2 | Technical art + level design | Classify representative content; inspect LODs and bounds; author occluders | One representative room-to-street route with visual comparisons |
| 3 | Rendering engineering | Apply measured visibility ranges, HLOD, effect budgets, and spatial batching | Before/after CPU/GPU capture; transition review |
| 4 | Gameplay engineering | Separate cosmetic presentation from simulation; stagger expensive horde work | All-player activity tests and per-system timings |
| 5 | Network engineering | Implement conservative interest lifecycle only where justified | Spawn/re-entry, packet-loss, late-join, and bandwidth evidence |
| 6 | Engineering + QA | Add residency/streaming only if baseline requires it | Memory and activation-spike evidence |
| 7 | QA + discipline owners | Validate both presets and correct regressions | Completed acceptance matrix with evidence links |

Use a central or spatially partitioned relevance scheduler where appropriate. Avoid adding full-scene searches and expensive visibility checks to every entity every frame. Debug views SHOULD expose render tier, simulation tier, per-peer interest, loading state, and the reason for each override.

## 12. Acceptance and test protocol

Run exported builds, using a reproducible route or scenario seed. Capture three warm runs of at least five minutes per target profile, plus a cold traversal for loading behavior. Keep benchmark mode uncapped to expose headroom; separately validate intended V-Sync/frame-cap presentation.

Report median, p95, p99, maximum, and count/duration of frames above the deadline. Proposed performance gate: p99 frame time within the target deadline in every required warm scenario, with all larger spikes individually reviewed. This is a project acceptance proposal; it does not imply every single frame meets the deadline.

| ID | Scenario | Required result |
| --- | --- | --- |
| AC-001 | Sprint, strafe at thresholds, turn 180 degrees, and use supported zoom | No repeated LOD flicker, conspicuous disappearance of cover, or unprepared threats |
| AC-002 | Maximum approved horde with simultaneous effects | Meets the selected frame-time gate; preserves attack cues |
| AC-003 | Players separate across areas, with combat away from host | Required simulation continues; host and clients meet their budgets |
| AC-004 | Long sightline, rooftop, window, open/destroyed door | Correct silhouettes and openings; no false occlusion or empty proxy interiors |
| AC-005 | Low and high graphics peers attack the same distant target | Matching gameplay state; relevant enemy and cover remain readable |
| AC-006 | Enemy/projectile approaches from outside the view | State and presentation ready before impact or exposure |
| AC-007 | Leave and re-enter interest; late join; reconnect | Correct health, death, doors, loot, actions, and lifecycle identity |
| AC-008 | Configured latency/jitter/loss and a worse supported network case | No duplicate entities or stale-state resurrection; degradation recorded |
| AC-009 | Cold traversal and burst activation | Activation work stays within approved budgets; no unexplained stalls |
| AC-010 | Repeated encounter resets and traversal | No growing entity count, unbounded cosmetic accumulation, or memory trend |

Evidence MUST include build/configuration ID, hardware, scenario, player/enemy counts, render resolution, frame-time distribution, CPU/GPU timing, authority tick cost, active AI count, path-query volume, replication traffic, memory, and transition video where visual behavior is assessed. Record visible geometry/draw submissions and animation cost when relevant to the change.

## 13. Common failure modes

| Failure | Consequence | Correction |
| --- | --- | --- |
| Hide mesh and assume enemy is cheap | AI and animation still dominate | Measure and budget systems independently |
| Disable a whole entity because it is offscreen | Broken threats, audio, damage, or multiplayer | Separate presentation and authoritative activity |
| Use host camera as activity source | Other players experience frozen enemies | Aggregate all gameplay dependencies |
| Cull cover while preserving its collision | Invisible obstruction | Keep an inexpensive visible representation |
| Fade all objects | Transparency and overlap become expensive | Use selective transitions and compare measured cost |
| Merge an entire level | Poor occlusion and visibility granularity | Partition using meaningful spatial boundaries |
| Wake the horde simultaneously | CPU and replication spike | Prepare early; stagger noncritical work |
| Stream by nearest camera only | Missing state or collision for other players | Track residency requirements per process and dependency |
| Ship average-FPS results only | Hitches remain hidden | Review distributions, over-budget events, and visual recordings |

## 14. Sources and evidence boundaries

Official Godot documentation was consulted on 2026-10-30. The `stable` URLs below are moving references. Implementation owners MUST pin the project's exact engine build and confirm the relevant behavior against that version before merging. No game source, runtime capture, or hardware benchmark was available for this handoff.

Engine behavior is sourced below. The workload tiers, contracts, sequencing, budgets, and acceptance gates are project recommendations derived from those capabilities and the game's stated requirements. They require implementation and measurement.

| ID | Primary source | Supports |
| --- | --- | --- |
| S1 | [Godot: Optimizing 3D performance](https://docs.godotengine.org/en/stable/tutorials/performance/optimizing_3d_performance.html) | Frustum culling, transparency cost, rendering techniques, automatic instancing |
| S2 | [Godot: Mesh level of detail](https://docs.godotengine.org/en/stable/tutorials/3d/mesh_lod.html) | Imported mesh LOD and asset inspection caveats |
| S3 | [Godot: Visibility ranges / HLOD](https://docs.godotengine.org/en/stable/tutorials/3d/visibility_ranges.html) | Visibility ranges, margins, proxies, visibility dependencies |
| S4 | [Godot: Occlusion culling](https://docs.godotengine.org/en/stable/tutorials/3d/occlusion_culling.html) | Simplified occluders, bounds-based tests, performance tradeoffs |
| S5 | [Godot: MultiMesh](https://docs.godotengine.org/en/stable/classes/class_multimesh.html) | Instancing and shared spatial visibility limitations |
| S6 | [Godot: GeometryInstance3D](https://docs.godotengine.org/en/stable/classes/class_geometryinstance3d.html) | Fade renderer support, range properties, bounds controls |
| S7 | [Godot: Optimizing navigation performance](https://docs.godotengine.org/en/stable/tutorials/navigation/navigation_optimizing_performance.html) | Navigation bottlenecks and simplified bake inputs |
| S8 | [Godot: MultiplayerSynchronizer](https://docs.godotengine.org/en/stable/classes/class_multiplayersynchronizer.html) | Per-peer visibility, spawner interaction, synchronization intervals |
| S9 | [Godot: Background loading](https://docs.godotengine.org/en/stable/tutorials/io/background_loading.html) | Threaded resource loading and potentially blocking retrieval |
| S10 | [Godot: Physics interpolation introduction](https://docs.godotengine.org/en/stable/tutorials/physics/interpolation/physics_interpolation_introduction.html) | Fixed simulation ticks and interpolated rendering |
