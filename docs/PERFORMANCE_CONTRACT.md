# Procedural Level Performance Contract

**Target:** Godot 4.7, 3D
**Applies to:** Level generators, asset substitution tools, encounter placement,
navigation builders, streaming systems, and every feature that adds content to
generated levels.

> **Status: proposed project policy, not yet enforced anywhere.** Nothing in
> this repo gates on it today. It is written down so that the budgets,
> telemetry schema, gates and runtime responses below can be argued with,
> adopted piecemeal, or refused — rather than each tool inventing its own.
>
> Where it meets what this repo has already measured:
>
> - §7's "a mesh is not necessarily one draw call" is the rule
>   `CLAUDE.md` states as a hard one: **draw calls are the budget, not
>   triangles**, measured 2026-09-16 — 1,730 draws read 9.49 ms and 6,376 read
>   25.59 ms while the primitive count sat flat at ~1.4M throughout.
> - §4's "never report an unavailable metric as zero" and §3's insistence on
>   naming the scenario are the same discipline that caught a wet `next_pass`
>   measurement being withdrawn in LF 0.115.0: the pass was submitted and never
>   drawn, and the control could not tell submission from shading.
> - §10's permanent benchmark set does not exist yet. `tools/cold_run.py`
>   measures interventions, not frames; `tools/wet_ab.gd` and
>   `tools/occlusion_ab.gd` measure frames at fixed stations on one package.
>
> Verify specific monitor names and renderer support against the exact Godot
> 4.7 build this project uses.

---

## 1. Purpose

A generated level is only valid if it plays well on the target hardware. Every
tool in the pipeline must know what it adds to the level, measure its actual
runtime cost, and respond when that cost exceeds a budget.

This contract protects us from a common failure: each tool produces a
reasonable result in isolation, while their combined output exhausts memory,
overloads the CPU or GPU, or stalls during play.

**Core rule:** the generator may vary the level's appearance and layout. It may
not vary its performance without bounds.

---

## 2. Define the target before setting limits

Maintain one performance profile per supported hardware and graphics setting.
Each profile specifies:

| Item | Record |
|---|---|
| Hardware | CPU, GPU, physical RAM, VRAM, storage type |
| Software | OS, driver, Godot build, renderer, resolution, graphics settings |
| Goal | Target frame rate and acceptable frame-time spikes |
| Scope | Player count, enemy count, level size, simultaneous effects |
| Headroom | Capacity reserved for gameplay, UI, audio, the OS, and future features |

At 60 FPS the entire frame has approximately **16.7 ms**. At 30 FPS it has
approximately **33.3 ms**. These are total frame budgets, not budgets available
exclusively to procedural content.

Start with provisional CPU, GPU, memory and loading budgets. Replace them with
measured limits on representative hardware. Do not present a guessed draw-call
count, node count or VRAM allowance as a universal Godot limit.

---

## 3. Measure the experience, not just average FPS

Every performance report must include the following scenarios:

1. **Cold launch and first level** — exposes initial loading, import or cache
   behaviour, and first-use shader stalls.
2. **Warm repeat** — separates recurring costs from cold-start costs.
3. **Typical traversal** — represents what most players see.
4. **Worst sightline** — looks across the largest visible portion of the level.
5. **Worst encounter** — runs the intended maximum of enemies, effects, audio
   and destructibles.
6. **Rapid traversal** — crosses generation or streaming boundaries as quickly
   as a player can.
7. **Repeated transitions** — loads and unloads several levels to expose leaks
   and retained resources.
8. **Long session** — checks whether memory or frame times drift upward.
9. **Multiple seeds** — includes ordinary seeds and deliberately stressful ones.

Use deterministic seeds and recorded camera/player paths. Record whether the
run was in an exported build or the editor; use exported builds on target
hardware for acceptance decisions.

Report frame times in milliseconds: **median, p95, p99, and worst observed
spike**, alongside the number of frames measured. FPS alone hides the stutters
that make traversal feel bad. Keep cold and warm results separate.

---

## 4. Required measurements

Godot exposes built-in performance monitors, including frame timing, memory,
rendering statistics and physics counts. Its debugger includes CPU and visual
profiling tools. Use those to identify a problem, then use platform profilers
when engine counters cannot explain it. Monitor names and availability must be
verified against the exact 4.7 build and renderer selected for the project.

| Area | Runtime measurements | Tool-owned measurements |
|---|---|---|
| Frame pacing | Frame-time distribution; spikes during traversal, combat, generation and cleanup | Time spent generating, instantiating, activating and retiring content |
| CPU | Main-thread, physics and rendering CPU time; costly script functions | Generation time by phase; work queued per frame; active AI and interaction counts |
| GPU | GPU frame and pass timing where available; resolution sensitivity | Visible geometry, materials, shadow casters, transparent surfaces, lights, effects |
| Draw calls | Draw calls in representative views; changes by camera position | Instanced objects, mesh surfaces, material variants, batch or MultiMesh groups |
| VRAM | Engine-reported video memory where supported; device or platform telemetry | Estimated texture, mesh, render-target and level-specific resource footprint |
| RAM | Process memory and trend across level transitions | Live nodes, resources, generated arrays, caches, retained level data |
| Physics | Physics frame time, active bodies, collision pairs where available | Collision shapes, rigid bodies, raycasts, destructibles, overlap checks |
| Navigation | Build/update time and traversal-time impact | Navigation regions, polygon complexity, agents, avoidance participants |
| Storage and loading | Load duration, main-thread stalls, bytes read where observable | Files loaded, bytes requested, cache misses, simultaneous requests |
| Shaders | First-use stalls and pipeline compilation indicators where available | New shader/material variants introduced by a tool |

Interpret counters carefully. Engine video-memory figures may not represent
complete GPU allocation; process RAM does not explain which tool retained a
resource; draw-call count does not measure shader cost or overdraw. When a
metric is unavailable, mark it unavailable and use a named external measurement
method. **Never report an unavailable metric as zero.**

---

## 5. The contract every tool must implement

A tool that adds runtime content must provide five things.

### A. Cost estimate before placement

Before committing content, estimate its incremental cost in the categories it
affects:

```
estimated_cost = {
  cpu_ms_per_frame,
  gpu_ms_per_frame,
  ram_bytes,
  vram_bytes,
  draw_calls_visible,
  physics_active_count,
  nav_build_ms,
  load_bytes,
  expected_main_thread_activation_ms
}
```

An estimate is a planning aid, not proof of performance. Measure actual output
and update estimates when they consistently miss.

### B. Ownership tags

Tag generated content with its tool, seed, level, chunk, feature and asset
variant. A runtime event should be traceable to the tool that caused it.

At minimum, logs must identify:

```
build_id, godot_version, renderer, hardware_profile, quality_profile,
level_id, seed, chunk_id, tool_id, phase, timestamp, measured_value
```

### C. Bounded output

Each tool defines hard limits appropriate to its job: maximum active instances,
simultaneous effects, collision shapes, texture variants, generation work per
activation, or other meaningful units. A limit must apply to the **visible or
active working set**, not merely the number of objects across the entire level.

### D. Graceful reduction

Each tool specifies what it can reduce when capacity is scarce. Examples:

- Remove optional clutter before removing cover or navigation cues.
- Reduce distant decorative instances before nearby interactable objects.
- Shorten effect lifetime before suppressing essential hit feedback.
- Defer noncritical activation across frames.
- Keep collision, cover, doors, objectives and traversal geometry functionally
  correct.

### E. Cleanup proof

When a chunk or level unloads, the tool releases its nodes, references,
signals, server resources, caches and pending jobs as appropriate. A repeated
load/unload test must show memory returning to a stable range. Track expected
caches separately from leaks.

---

## 6. Allocate budgets by phase and owner

A single "level budget" is too blunt. Track costs by runtime phase:

| Phase | Primary risk | Required limit |
|---|---|---|
| Generate | CPU spikes and temporary allocations | Maximum work per generation job and per frame |
| Load | Disk waits, decompression, resource creation | Maximum load latency and simultaneous requests |
| Activate | Node creation, collision registration, GPU uploads | Maximum main-thread activation time per frame |
| Play | CPU, GPU, physics, VRAM | Frame-time and active working-set limits |
| Transition | Old and new levels coexist temporarily | Peak RAM/VRAM allowance |
| Unload | Stalls and retained memory | Cleanup time and post-unload memory baseline |

Assign an owner to every portion of the budget. Reserve a portion for features
the generator does not control. A new tool must declare which existing
allocation it uses or which owner approved a budget change.

**Do not add individual peak costs together as if they all occur at once.**
Model realistic overlap — for example, a combat encounter while the next chunk
loads and the previous chunk unloads — and test that overlap explicitly.

---

## 7. Design rules for generated 3D levels

### Visibility is a generation input

The generator should know how far the player can see from likely positions.
Evaluate long corridors, elevated viewpoints, open plazas, glass walls and
doorways. Place occluders where they support the level design; do not assume a
large world will be cheap because most objects are distant.

Godot supports frustum and occlusion culling, but their benefit depends on the
scene's layout and what can actually be hidden. Measure the worst sightlines
with the intended renderer.

### Instance repeated detail deliberately

Use shared resources and consider MultiMesh for large groups of identical,
mostly noninteractive objects. Partition groups by a useful visibility unit,
such as a room or chunk: **individual instances inside a MultiMesh are not
independently frustum culled.** Compare fewer draw calls against the extra
geometry drawn when a whole group remains visible.

Keep interactive props separate where they need individual collision, state,
damage or selection. A visual instance is not automatically a cheap interactive
object.

### Count material and surface variants

A mesh is not necessarily one draw call. Track surfaces, material variants,
transparency, shadows and rendering passes. Asset substitution tools should
prefer reuse when the visual result allows it. A new prop variant must disclose
whether it introduces new textures, materials or shaders.

### Treat transparency, shadows and lights as scarce

Track overlapping transparent surfaces and screen coverage, not just object
count. Set explicit limits for shadow-casting lights and expensive effects
within an encounter or visible chunk. Measure these costs in the worst
encounter at the target resolution.

### Generate collision and navigation for gameplay needs

Use simple collision where it preserves the intended interaction. Keep
decorative geometry out of physics and navigation unless it changes play.
Distinguish static level collision, dynamic bodies, query-driven interactions
and AI avoidance; they have different costs.

### Bound resource residency

Document whether a tool shares an asset, loads it on demand, holds it for an
entire mission, or evicts it when its chunk unloads. Record peak residency
during transitions, when old and new content may coexist.

---

## 8. Loading and streaming rules

Synchronous resource loading can block the calling thread. Use Godot's
background loading facilities for appropriate resources, then measure the point
where loaded content is instantiated and activated; background loading alone
does not guarantee a smooth frame.

Every streaming system must:

- Define the distance or event that requests content.
- Define how many chunks may be requested and activated concurrently.
- Prioritize gameplay-critical content.
- Cap main-thread activation work per frame.
- Cancel or discard obsolete requests when the player changes direction.
- Log request, ready, activation and retirement times separately.
- Test movement faster than the expected player speed.
- Avoid evicting content that will immediately be needed again.

**Visible failure policy:** if content is late, preserve collision and readable
traversal. Optional decoration may appear later; floors, cover, exits,
objectives and enemies must follow explicit design rules rather than silently
popping into an invalid state.

---

## 9. Runtime budget controller

Measure continuously, but avoid reacting to a single noisy frame. Use a rolling
window and thresholds with hysteresis.

| State | Trigger | Response |
|---|---|---|
| Healthy | Measurements remain within the profile | Generate normally |
| Pressure | A rolling measurement nears a budget or spikes repeat | Stop optional additions; reduce upcoming decoration and effects |
| Over budget | Sustained violation or hard memory limit | Apply the tool's documented reduction order; throttle jobs |
| Unsafe | Cannot preserve essential gameplay within limits | Reject the seed or chunk, select a validated fallback, and log the failure |

Do not treat dynamic resolution or graphics settings as the first fix for
excess node creation, physics work or memory retention. The response must
target the resource under pressure. Do not change level geometry during play in
a way that alters collision or traps players.

**Record both requested content and delivered content.** Otherwise a generator
can appear performant simply because it quietly stopped producing the intended
game.

---

## 10. Seed validation and regression gates

Keep a permanent benchmark set containing:

- A small level.
- A typical level.
- The largest allowed level.
- A long-sightline level.
- A dense encounter.
- A level with heavy prop variation.
- A rapid streaming path.
- One or more previously problematic seeds.

For each tool change:

1. Run static checks on generated output: counts, resource estimates,
   unsupported combinations and hard caps.
2. Run the fixed seed set in an exported build.
3. Compare measured results with the baseline on the same hardware profile.
4. Investigate material regressions in p95/p99 frame time, memory peak, load
   latency or activation spikes.
5. Run a targeted stress seed when the change affects the relevant subsystem.
6. Store the results with the build and seed so the regression can be
   reproduced.

A change passes only when it meets both the hardware profile's absolute limits
and the project's agreed regression threshold. Define those thresholds from
baseline measurements; avoid arbitrary universal numbers.

---

## 11. Required report format

Each automated run should produce machine-readable results plus a short human
summary:

```json
{
  "build_id": "example",
  "godot_version": "4.7-exact-build",
  "renderer": "record-actual-renderer",
  "hardware_profile": "min-spec-desktop",
  "quality_profile": "low",
  "level_id": "location_01",
  "seed": 12345,
  "scenario": "dense_encounter",
  "duration_seconds": 120,
  "frame_ms": {
    "median": null,
    "p95": null,
    "p99": null,
    "worst": null
  },
  "memory": {
    "process_peak_bytes": null,
    "engine_video_memory_peak_bytes": null,
    "video_memory_method": "engine-monitor-or-external-tool"
  },
  "render": {
    "draw_calls_p95": null
  },
  "loading": {
    "worst_activation_ms": null
  },
  "tool_costs": {},
  "budget_violations": []
}
```

**A null value means not measured.** Specify whether each peak covers cold
launch, steady play, transition, or the entire run. Preserve raw samples or
trace files when possible.

---

## 12. Implementation order

1. **Establish target hardware and frame goals.** Without these, "optimized"
   has no testable meaning.
2. **Build the benchmark harness.** Fixed seeds, camera paths, combat scripts,
   exported builds and consistent reports.
3. **Instrument tool ownership.** Identify which generator and chunk produced
   each costly object or job.
4. **Measure the current baseline.** Capture typical and stressful levels
   before imposing detailed quotas.
5. **Set provisional budgets.** Include headroom and limits for generation,
   activation, play, transition and unload.
6. **Add static validation.** Reject obviously excessive output before running
   a level.
7. **Add runtime pressure responses.** Reduce optional work in a documented
   order.
8. **Gate changes on representative hardware.** Keep the benchmark seeds stable
   while adding new adversarial seeds as failures emerge.

---

## 13. Definition of done for a new tool or feature

A procedural tool is ready to join the level pipeline when it has:

- A named owner and documented runtime phases.
- A pre-placement cost estimate and bounded output.
- Tool, chunk and seed identifiers in telemetry.
- Measured cold and warm behaviour on relevant hardware.
- Results for typical and stressful benchmark seeds.
- A response to budget pressure that preserves gameplay.
- A repeated load/unload check.
- A recorded baseline and regression threshold.
- A fallback when it cannot produce a valid level within budget.

**Acceptance principle:** a generated level must remain playable at its worst
supported combination of visibility, combat, loading and content density — not
merely when viewed from a convenient camera position.

---

## Godot reference points

- Performance monitors — Godot Engine (stable) documentation
- Debugging tools and profilers — Godot Engine (stable) documentation
- Background loading — Godot Docs
- Optimizing 3D performance — Godot Engine (4.3) documentation
- Using MultiMeshes — Godot Docs
