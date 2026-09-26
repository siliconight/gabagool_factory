# Backdrop World Generator

**Technical Design Document · Draft 1 · 26 September 2026**  
**Target:** Godot 4.7, 3D procedural heist levels  
**Owner:** Level toolchain

## 1. Purpose

Generate a convincing, non-playable surrounding world from a playable level's geometry and semantic recipe. A small heist site should read as part of a larger, geographically coherent place when viewed from streets, windows, roofs, and other reachable positions. The generator must preserve routes and landmarks at the map edge, fit the level's atmosphere, and impose a measurable rendering and memory cost.

**Success:** A designer can compile a playable map plus a regional profile and receive a deterministic backdrop scene, debug visualization, and validation report without hand-authoring a surrounding city. The backdrop must make the setting legible while keeping threats, objectives, entrances and silhouettes in the playable area easy to read.

## 2. Scope and boundaries

**MVP:** One contiguous level, one regional profile, static daylight or night lighting, fixed playable bounds, ground and rooftop cameras, facade shells, roads, vegetation, utility infrastructure, distant silhouettes, and sky/environment integration. Compile in editor or headless build; load the compiled artifact at runtime.

**Later:** Water and rail corridors, multiple height strata, artist-authored landmark libraries, weather variants, automated impostor baking, streamed districts, moving ambient silhouettes, and editor painting tools.

Generated scenery has no interiors, AI, navigation, loot, or ordinary physics collision. Player containment belongs to the playable level; visual continuity should hide the boundary without relying on an obvious wall. Do not assume a full 360-degree vista is needed.

## 3. Inputs and outputs

The compiler consumes the level recipe and evaluated scene geometry. Coordinates are meters in the level's local space; +Y is up. Bearings are degrees clockwise from geographic north and must be converted once into local coordinates using `north_yaw_degrees`. Any missing or incompatible coordinate metadata is a build error.

```yaml
schema_version: 1
level_id: flappahs_01
seed: 42107
world:
  north_yaw_degrees: 0
  region_profile: delco_1998_v1
  environment_profile: humid_late_summer_1730
playable:
  footprint_source: playable_bounds # validated polygon from compiled level
  height_min_m: -2
  height_max_m: 18
  player_eye_min_m: 1.3
  player_eye_max_m: 2.0
  reachable_camera_sources: [navmesh, authored_vantage_points]
  camera_fov_degrees: 90
  exclusions: [roof_inaccessible_02]
connections:
  - id: east_arterial
    type: road
    edge_marker: road_exit_east
    width_m: 14
    lanes: 4
    continuation: arterial_commercial
  - id: west_power
    type: overhead_utility
    edge_marker: pole_run_west
    continuation: residential
context:
  density: medium
  era: 1998
  visual_story_tags: [working_commercial_strip, aging_infrastructure]
  play_readability_zones: [store_entrance, police_approach_east]
  anchors:
    - asset: water_tower_generic
      bearing_deg: 310
      distance_band: far
      priority: preferred
  forbidden_features: [modern_glass_tower, mountains]
budget_profile: desktop_60fps_reference
```

Required: schema version, ID, seed, north orientation, valid footprint, region/environment profiles, camera sources, and budget profile. Connections and anchors are optional. Asset names resolve through a versioned regional catalog, never unchecked paths in recipes. Validate markers against the compiled scene; a connection whose marker is absent fails rather than silently placing unrelated scenery. Validate that camera origins are actually reachable; authored roof positions may supplement navigation samples. Permit per-level designer overrides with explicit provenance.

**Output package** (`res://generated/backdrops/<level_id>/`):

| File | Contents |
| --- | --- |
| `backdrop.tscn` | Generated scene rooted under `BackdropRoot`, with stable sector names and no gameplay ownership |
| `manifest.json` | Schema/compiler/catalog versions, input hashes, seed, bounds, assets, sector metadata and output hash |
| `visibility.bin` | Compressed camera samples and angular coverage, for editor inspection and incremental builds |
| `report.json` | Validation results, estimated costs, benchmark deltas and omissions |

The level loader attaches the scene at the level origin. Game code must not search this scene for objectives or interactables. Rebuilds are atomic: validate a temporary output, then replace the previous generated package. Build output should be byte-identical for equal inputs, compiler version, asset catalog, and generation settings; exclude timestamps from hashed content.

## 4. Architecture

```text
Level recipe + compiled geometry + region catalog
                 ↓
       Schema and semantic validation
                 ↓
       Reachable-view sampling
                 ↓
       Edge connection planning
                 ↓
       Visibility-aware sector layout
                 ↓
       Facade / midground / horizon assembly
                 ↓
       Render packaging and QA gates
                 ↓
       Scene + manifest + report
```

The region catalog describes *constraints* and weighted assets: rooflines, setbacks, street widths, facade modules, vegetation, utility patterns, signs, material palettes, skyline anchors, and exclusion rules. Separate architectural identity from environmental lighting; the same region can have multiple times of day. A placement solver first continues explicit edges, then fills visible gaps with appropriate parcels, then adds distant silhouettes. Preserve a consistent directional layout so a landmark remains in the same bearing from all vantage points.

Before detailing, render a low-cost composition pass from the sampled cameras. Check foreground/midground/horizon silhouette rhythm and reserve high-contrast regions around combat targets, entrances, UI overlays and likely threat approach lines. Use a shared palette and color key with the playable level. `visual_story_tags` select contextual evidence (for example worn shop signs and old utility infrastructure) from the approved catalog; they must not generate misleading objectives, fake traversal affordances or conspicuous repeated motifs. The articles on game backgrounds emphasize scene readability, layered depth, coherent art direction and environmental storytelling; this converts those broad principles into generator inputs and QA checks. [300Mind](https://300mind.studio/blog/game-background-design/) · [SunStrike Studios](https://sunstrikestudios.com/en/blog/video-game-backgrounds-guide/) · [Stepico](https://stepico.com/blog/3d-environment-design-for-games-how-visual-worlds-drive-revenue/).

## 5. Visibility analysis

The analysis decides *which directions and heights require scenery*, before generation.

1. **Sample viewpoints.** Stratify reachable pedestrian navigation space by cells and add authored roof/window/perch positions. Include likely extreme points and edge-facing routes. At each point sample standing and any permitted crouched eye height. Sample relevant yaw directions at camera FOV; weight player-facing windows and routes more heavily. Deduplicate positions that produce similar views.
2. **Build an occlusion proxy.** Use opaque structural geometry from the compiled playable level: terrain, exterior walls, large roofs, and static neighboring shells. Exclude glass, foliage, temporary doors, destructible cover, and small props. Add conditional visibility cases for doors that can open or structures that can be destroyed. A build should not rely on an occluder that gameplay can remove.
3. **Cast coverage rays.** Across horizontal and vertical angular bins, trace from each viewpoint to the backdrop planning limit. Record first opaque hit, open-sky interval, visible edge segments, ground/horizon elevation, and distance to interruption. Use a coarse first pass and refine around windows, streets, roof edges, and connection markers. Numerical defaults (cell size, angle steps, ray limit) are tunable build settings, not promises of visual fidelity.
4. **Aggregate a visibility envelope.** Union visible azimuth/elevation intervals by sector. Keep camera source IDs, coverage weights, and confidence. Mark intervals with uncertain dynamic occlusion as visible. Prioritize large, frequently viewed openings. Flag any playable camera outside the sampled envelope at QA time.
5. **Review.** Editor overlay shows sample cameras, ray hits, visibility heatmap, unresolved horizons, edge continuations, and excluded sectors. Designers may pin a required sightline and rebuild.

Ray-based analysis is an optimization hint, not a visibility guarantee: test actual camera sweeps after assembly. Thin openings, changing doors, high FOV, and unusual roof climbs can reveal missed gaps.

## 6. World construction

| Layer | Intent | Representation |
| --- | --- | --- |
| Edge continuation | Make roads, sidewalks, rail/power runs, shorelines and terrain cross bounds coherently | Matched mesh segments and near facade shells; no traversable interior |
| Near backdrop | Provide recognizable streetscape and parallax from moving cameras | Shallow 3D facades, block-scale roofs, poles, walls, vegetation |
| Midground | Establish neighborhood rhythm and silhouettes | Grouped low-detail blocks, clustered instancing, shared materials |
| Far vista | Place large regional anchors in plausible bearings | Low-poly silhouettes or view-dependent cards with bounded view angles |
| Sky and haze | Unify depth, time, weather and horizon | Shared `WorldEnvironment`/sky settings with level; atmospheric fade |

Band distances are *derived from viewing conditions* and tunable profile settings, not fixed world rules. A roof with a long view needs different detail than a street hemmed in by buildings. Avoid nearby camera-facing cards when lateral motion exposes them. Multi-angle impostors may work at distance; if they show rotation artifacts during camera sweeps, use silhouette meshes.

Start every explicit road/rail/utility connection with matched width, grade, heading and material at the boundary. Continue it until it turns behind an occluder or naturally leaves the visible region. Keep parcels and buildings out of its right of way. Require anchor bearings and skyline scale to be consistent with the level's north orientation; if specified anchors conflict, report the conflict instead of shifting one invisibly. Derived profiles should evoke a region without requiring exact real street topology.

Use a single environment profile for sun direction, ambient contribution, exposure, fog/haze and color. Backdrop materials may simplify shading but must match the foreground's apparent light direction and value range. Make fog and distant colors legible under all supported renderer/weather variants. Reference real signage or trademarks only through cleared assets.

**Readability priority:** Maintain a value/contrast separation between background and playable targets. Avoid a bright sign or facade edge directly behind a likely enemy silhouette. Preserve depth through actual near/midground parallax and atmospheric falloff; depth of field or blur is an optional camera/art decision and should not be imposed by the generator during an FPS fight. Do not make distant landmarks so conspicuous that they imply an inaccessible objective. A screenshot can look attractive while damaging target recognition, so test in motion during actual combat.

## 7. Godot implementation

Implement a headless-capable **EditorPlugin/compiler** in the toolchain; generate PackedScenes/resources ahead of play. Keep runtime work to loading, optional coarse sector switching, and existing renderer culling. Building arbitrary geometry each frame is out of scope.

- Use `MeshInstance3D` for distinct near structures and grouped low-detail blocks. Reuse meshes/materials and combine static compatible surfaces only when that improves measured results.
- Use `MultiMeshInstance3D` for repeated objects such as trees or poles, partitioned into modest spatial sectors. A MultiMesh is culled as a unit rather than per instance, so one giant city-wide MultiMesh can waste GPU time.
- Use visibility ranges/HLOD for group replacement when profiling warrants it. Account for camera FOV and resolution during visual QA; automatic mesh LOD and manually selected group LOD serve different purposes.
- Use authored `OccluderInstance3D` only for large, reliable opaque blockers after measuring CPU and GPU impact. Godot occlusion culling has platform and scene-dependent costs; open vistas may benefit more from LOD and range limits.
- Set conservative geometry bounds, cull masks, material settings and shadow policies. Near silhouettes that visibly cast shadows may need them; far instances should usually avoid shadow maps. Verify transparency overdraw and fog costs in GPU captures.
- Share the playable level's `WorldEnvironment` and directional lighting where feasible. Avoid a second conflicting sky or light rig.

The engine version is pinned to **4.7 for integration verification**. Confirm imported assets, rendering methods and 4.7 API behavior in the actual project before selecting an implementation detail; documentation from another branch is only design guidance.

## 8. Performance contract

Measure on the team's reference hardware and release graphics presets. Record the *incremental* cost of enabling the backdrop in an otherwise identical replay, after shader warmup and with a stable camera path. Report median and 95th-percentile frame times, CPU main/render times, GPU frame time when available, rendered objects/draw calls, triangles, VRAM and system RAM, load time, and packaged disk size. Draw calls are diagnostic, not the sole pass/fail criterion. Track shader/material variants and streaming spikes.

**Provisional acceptance budgets (must be calibrated against a representative vertical slice):** at the desktop 60 FPS preset, backdrop contribution ≤0.5 ms p95 GPU and ≤0.2 ms p95 CPU on agreed stress cameras; ≤128 MiB incremental resident VRAM, ≤64 MiB incremental RAM, and zero gameplay physics bodies, navigation meshes, AI, or per-frame generator work. These are targets rather than guarantees or engine constants. Record limits by hardware/preset; a build that exceeds a target reports the offending sector/assets, then reduces lower-priority content or fails the configured gate. No silent quality reduction of required road continuations or pinned landmarks.

Benchmark at least: street-level long view, broad rooftop panorama, fast turn near level edge, night or high-contrast lighting, and worst-case open connections. Compare captured image pairs as well as counters. Include low settings and the supported renderer(s) in the compatibility matrix. The performance suite in the repository should own machine details, measurement procedure, regression thresholds and trend history.

## 9. Validation and acceptance

**Build checks:** schema and asset resolution; seed determinism; footprint and camera sample integrity; no forbidden features; explicit connections align within profile tolerances; no generated geometry overlaps playable traversal or critical sightlines; no gameplay nodes/physics/nav; required landmarks placed at valid bearings; package stays inside budgets or gives actionable errors.

**Visual checks:** an automated camera sweep visits sampled views and boundary extremes, saves comparison frames, and detects empty horizon gaps, obvious card rotations, texture discontinuities and lighting mismatches. Record grayscale/value thumbnails for canonical combat views with enemies, interactables and UI present; flag background highlights and edges that obscure targets or falsely resemble traversable routes. Detection can flag frames for human review; it cannot certify artistic quality. Designer approval uses a shortlist of canonical images plus free movement and combat through the compiled level.

**MVP acceptance scenarios:**

1. A corner-store level with two road exits generates continuous roads, matching sidewalks and a coherent neighborhood from street and roof.
2. A level with a tall playable roof reveals additional far scenery without exposed empty sectors.
3. Rebuilding the same inputs and catalog produces the same output hash; changing the seed changes optional placement without moving pinned connections or anchors.
4. A missing connection marker or contradictory required anchor produces a specific build error.
5. Adding the backdrop respects the calibrated profile budgets on the reference device and logs baseline/delta evidence.
6. Runtime scene inspection confirms no generated collision, navigation, AI, or objective hooks.

## 10. Failure handling and designer controls

Provide three controls: `pin_view` (must cover this camera/direction), `pin_asset` (required location/bearing), and `exclude_zone` (no placement). Each override records author and reason and remains deterministic. A failed compile preserves the last valid package for editor preview but marks it stale and blocks release packaging. Unsupported asset combinations or unresolvable road grades fail with a message naming the source markers. If a low-priority sector exceeds cost, the report lists the removed assets and the visible coverage they represented.

## 11. Delivery sequence

1. **Contract and fixture:** versioned schema, region catalog, one hand-built corner-store input, reproducible headless build.
2. **Visibility MVP:** reachable samples, static occlusion proxy, heatmap and pinned-view support; validate with roof and window cases.
3. **Construction MVP:** edge-matched roads, facades, midground blocks, trees/poles and horizon silhouettes; stable seeds and manifests.
4. **Integration:** Godot PackedScene packaging, shared environment, editor overlay, automated sweeps and baseline profiling.
5. **Production gate:** second contrasting level, calibrated budgets, regression thresholds, and documented artist overrides.

**Key risk:** visibility analysis can miss rare angles, and aggressive instancing can increase overdraw despite fewer draw calls. Address both with free-camera review, sector-sized batches, and before/after GPU captures. The first milestone should establish whether generated backdrops look geographically coherent on one actual level before expanding the catalog.

**Ambient motion follow-up:** If distant traffic, birds, wires or trees are later animated, use plausible paths and acceleration and measure their screen-space distraction and runtime cost. The supplied [animation arcs article](https://gamedevservice.com/blog/what-are-arcs-in-animation-a-complete-guide-to-the-principle-of-arcs) concerns motion design, so it is a reference for that later pass rather than evidence for static backdrop placement.

## References

- [Godot: Visibility ranges (HLOD)](https://docs.godotengine.org/en/4.7/tutorials/3d/visibility_ranges.html)
- [Godot: Using MultiMeshInstance3D](https://docs.godotengine.org/en/4.7/tutorials/3d/using_multi_mesh_instance.html)
- [Godot: Occlusion culling](https://docs.godotengine.org/en/4.7/tutorials/3d/occlusion_culling.html)
- [Godot: Optimizing 3D performance](https://docs.godotengine.org/en/4.7/tutorials/performance/optimizing_3d_performance.html)
- [300Mind: Game background design](https://300mind.studio/blog/game-background-design/)
- [SunStrike Studios: Video game backgrounds guide](https://sunstrikestudios.com/en/blog/video-game-backgrounds-guide/)
- [Stepico: 3D environment design for games](https://stepico.com/blog/3d-environment-design-for-games-how-visual-worlds-drive-revenue/)
- [GameDevService: Arcs in animation](https://gamedevservice.com/blog/what-are-arcs-in-animation-a-complete-guide-to-the-principle-of-arcs) (future ambient-motion reference)

The Godot references are implementation background. Verify their 4.7 pages and the project's chosen renderer during integration.
