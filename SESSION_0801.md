# Session state — 1 Aug, z-fighting, the level look, and the lights

Written as a handoff. Everything below is measured unless it says otherwise.

## What was fixed, and the numbers that say so

Four defects in the building emitter, each landed as its own commit in
`deli_counter`, measured on `cr_deli` by `zfight_gate.visible_fights`:

| step | visible fights | what changed |
|---|---|---|
| baseline | 363 | — |
| slab inset | 151 | wrong shape, reverted |
| wall cap | 45 | walls stop under the slab that caps them |
| parapet corners | 29 | N/S own the corners, E/W stop at their inner faces |
| stair plate | 23 | the landing *is* the top step |

Across the rebuilt library — 57 distinct builds, all stamped 2026-08-01,
no divergence:

```
visible   311 total    8/57 clean
exposed   206 total   10/57 clean
```

Against a baseline of **103 of 103 buildings affected, 410 in the worst**.

Then the composition, which no per-building check could see. Lot's ground plate
topped out at y = 0 and so does a building's ground-floor slab, with
`GROUND_HOLE_INSET = 0.45` deliberately leaving a ring of overlap around every
building — ~59 m² of coplanar up-facing surface per 38 × 28 building. Fixed by
`GROUND_SINK`, which drops the plate one tier below the floor datum and extends
roads, paths and courtyards downward by the same amount so no top face moves.
Verified in the generated scene: `Ground` spans `[-0.5000, -0.0020]`,
`path_0` `[-0.0020, +0.0120]`, tops unchanged.

Composed result: **zero `site ↔ building` pairs.**

## What the flicker actually was — closed

Not geometry. The composed gate read **961 solids in one frame** and found no
coplanar pair anywhere near a wall meeting a floor. Turning the sun's shadow off
made the band vanish. It is shadow acne, cross-hatched by more than one
directional light.

The geometry work was still real and still needed — it just was not what was on
screen.

The second light is now accounted for, and the two are **one degree apart**:
`Sun` at +45.0° elevation, `Lux/LuxSun` at +46.0°, both casting. That is the
geometry that cross-hatches rather than producing two legible shadows, and it is
why the band read as acne rather than as a second sun.

## Sun Link — closed, and the previous diagnosis was wrong

`lux_inject` wrote `sun_light = NodePath("../Sun")` into the walk scene and Godot
discarded it. **The property is never assigned at any point in the lifecycle**,
so the previous entry's proposed next step — move the adoption from
`_build_modules` to `apply_preset`, where `_resolve_sun_link` has definitely run
— would not have worked either. It is not a lifecycle problem.

Godot's text scene loader treats a property as a node reference only when the
`[node ...]` header names it in a `node_paths` field; the loader builds that set
solely from the header. Without it the loader does a plain
`set("sun_light", NodePath("../Sun"))` — a NodePath into a
`DirectionalLight3D`-typed property — which GDScript rejects and drops with no
error and no warning.

Measured on 4.7.stable, one field the only difference, on a project built from
`cater` → `lux_dress` → `lux_inject` with no hand edits:

```
                                 patched          control (old header)
DirectionalLight3D                     1                            2
  Sun                     energy 1.500                  energy 1.000
  Lux/LuxSun                         —                   energy 1.500
Lux.sun_light                       Sun                       <null>
Lux children              no LuxSun         LuxSun present
```

The energies are the part to keep. Patched, Lot's own `Sun` reads 1.500 —
Lux is *driving* it, which is what Sun Link was always supposed to mean.
Unpatched, `Sun` sits at its own 1.000 untouched while `LuxSun` adds a second
1.500 beside it.

Corroboration that was on disk the whole time: `_runs/lux_0801b`'s
editor-resaved scene has **no `sun_light` line at all**. The editor dropped it on
save because it was never set.

**Fixed in `tools/lux_inject.py`** — the `[node]` header now carries
`node_paths=PackedStringArray("sun_light")` whenever a `Sun` is found. One line
plus the reasoning above it.

`patch_lux_sunlink.py`'s edit to `lux_root.gd` is correct and load-bearing:
without `if sun_light != null: _lighting.sun = sun_light`, `ensure_sun()` still
manufactures a light regardless of what resolved. It was never ineffective —
it had nothing to act on.

## Every Lux scene in the tree has the same defect

Swept all 242 `.tscn` on disk (146 staged, one per distinct name+size+mtime):

```
LuxRoot scenes                33   (9 product + 24 addon copies)
declaring node_paths           0
not declaring node_paths      33
```

The string `node_paths` does not appear anywhere in the tree. The four
8,146-byte `coldrun_pawn_job_walk.tscn` files in `_runs/lux_0801`, `lux_0801c`,
`lux_0801d` and `lux_dressed` are the exact failure mode — `sun_light` present,
a real `Sun` sibling present, no `node_paths`. **Re-injection will not fix them:**
`lux_inject` returns early on `if SCRIPT_RES in src`, so they need restoring from
their `.pre_lux` backups first, or the header edited by hand.

### The fix does not reach the Level Factory path, and the reason matters

There are **two** ways a LuxRoot gets into a scene, and only one of them was
broken in this way:

1. `cater` → `lux_dress.ps1` → `tools/lux_inject.py` — writes the node as
   **text**. This is the path that was broken, and is the one now fixed.
2. Level Factory's `lux_apply` job → `level_factory/assets/godot/run_lux_apply.gd`
   — builds the node **in-engine** and saves with `PackedScene.pack()` +
   `ResourceSaver.save()`. The engine's own saver emits `node_paths`
   automatically for a Node-typed export, so this path could never have had the
   defect.

So the earlier framing — "every generated project has been double-lit" — is
**wrong for path 2 and right for path 1.** Path 2 has no sun to link to: the
composed presentation scene is written by `deli_counter/themed_tscn.py`, whose
entire node vocabulary is a root `Node3D`, a `GreyboxBase` instance and one
instance per slot. No `DirectionalLight3D`, no `WorldEnvironment`, no `Sun`.
`run_lux_apply.gd` never mentions `sun_light`, and there is nothing for it to
mention.

That leaves a different and arguably larger question, which is **open**: the two
paths ship different lighting. Path 1 ships Lot's `Sun`, now driven by Lux. Path
2 ships a `lux.applied.tscn` containing a bare scripted `LuxRoot` with
`active_preset` and none of Lux's runtime children — because at runtime
`Engine.is_editor_hint()` is false, Lux sets no owner, and `PackedScene.pack()`
drops unowned nodes. Its lighting is re-manufactured by `apply_on_ready` in
whatever project loads it. Nobody has compared what the two produce.

Note the symmetry with the editor-accumulation defect below: the owner
assignment that makes editor scaffolding wrongly saveable is the same mechanism
that makes runtime scaffolding correctly disposable. Removing owners is right
for the editor case and must not be applied blindly to the packed-scene case.

Small, found while reading it: `run_lux_apply.gd` discards
`ResourceSaver.save()`'s return value — only `pack()`'s result feeds
`applied_ok` — so a failed write still reports success.

## Editor accumulation — mechanism confirmed, multiplication not reproduced

The `ensure_sun` owner suspicion was right, and it is not only `ensure_sun`.
Driving Godot's headless editor against a real project and reading the edited
scene tree:

```
Lux child                class                owner
  LuxEnvironment         Node                 <null>
  LuxWorldEnvironment    WorldEnvironment     coldrun_pawn_job_walk
  LuxLighting            Node                 <null>
  LuxSun                 DirectionalLight3D   coldrun_pawn_job_walk
  LuxPostFX              Node                 <null>
  @CanvasLayer@20061     CanvasLayer          coldrun_pawn_job_walk
```

Exactly the three nodes with an owner are the three that appear in
`_runs/lux_0801b`'s saved scene, and the three ownerless module Nodes do not.
**Owner is what decides saveability**, and the addon assigns it in nine places:

```
runtime/lux_environment.gd:42        world_env.owner
runtime/lux_lighting.gd:30           sun.owner
runtime/lux_post_fx.gd:57,58,59      layer, back_buffer, rect
runtime/lux_post_fx.gd:84,85         crt_back_buffer, crt_rect
runtime/lux_fixture_spawner.gd:51,77 container, rig
runtime/lux_light_loader.gd:43,57,188
```

Two things this does NOT establish. It does not reproduce the four lights and
three stacks observed last session — a single clean headless editor load
produces **one** of each, so the multiplication needs whatever else that session
did (script reloads are the obvious candidate) and has not been isolated.
And fixing Sun Link removes one of the three owned nodes but not the other two,
so a Ctrl+S on a dressed scene still bakes in a `LuxWorldEnvironment` and a
post-FX `CanvasLayer`.

Separately, and new: **in the editor, Lux creates a second WorldEnvironment**
even though the scene already has Lot's. At runtime it correctly adopts the
existing one — the census reads exactly one. So `ensure_world_environment`'s
reuse path fails specifically under `Engine.is_editor_hint()`.

## A project cater has SERVED does not run

New, and it applies to every generated project. Running the walk scene on a
project Godot has never opened:

```
59 parse errors
  res://addons/lux/runtime/lux_root.gd     failed to load
  res://addons/lux/resources/lux_preset.gd failed to load
Node './garage' was modified from inside an instance, but it has vanished.
Node './deli'   ... './pawn' ... './gas'   (all four buildings)
```

It does not self-heal: a second run is identical. Only `--import` fixes it,
after which it is 0 errors. `class_name` resolution and `.glb` import both need
the editor's scan, and running the game never performs it.

Harmless for a human, who opens the project. A silent trap for anything
automated, and `cater` currently prints `SERVED -> open ..., F6` with no mention
of it. `tools/godot_probe.py` runs the import pass for this reason.

## `cater` freshness, reproduced live

The carried defect — freshness hashes the spec, not the emitter — was watched
happening rather than argued. The four `cr_*.glb.spec.sha256` stamps are dated
02:25; the `.glb` files they stamp were rebuilt at 19:10 and 19:33 by something
that is not cater. Because the stamps still match the current specs, cater
printed `0 built, 4 already fresh` — it would not have rebuilt them on a day the
emitter changed four times.

## Instruments built this session

`tools/` gained three, sharing one runner:

- `godot_probe.py` — finds Godot in the same order as `walktest.py` and
  `library_walk.py`, **mirrors the project to scratch** before instrumenting it,
  runs it, and reads a fenced JSON block off stdout. Mirroring because an
  autoload means writing `[autoload]` into `project.godot`, and doing that to the
  project under test makes the instrument a modification of the thing it
  measures — one that survives a crashed probe. stdout rather than a report file
  because `user://` depends on project name and platform, so "the file is not
  there" and "the probe never ran" are indistinguishable from outside. No mode
  reports a skip as a pass.
- `light_census.py` / `.gd` — the lights and environments a scene actually RUNS
  with: per-light energy, elevation, shadow and visibility; every
  WorldEnvironment's grade fields; each LuxRoot's resolved `sun_light` and what
  it parented onto itself; sibling name collisions. Reports and exits 0 whenever
  it measured. `--max-directional N` makes it a gate, so the number is somebody's
  decision rather than the tool's assumption.
- `look_shots.py` / `.gd` — renders and reports exposure. Cameras are derived,
  not chosen: eye-level shots stand on the scene's own exported `spawn_pos` /
  `objective_pos` / `extraction_pos` at the height of the Player's own
  `Camera3D`, facing the next leg; the overview is framed from the site AABB
  against the FOV. Hides non-Lux `CanvasLayer`s — the HUD is white text and
  clips — keeping Lux's post stack, distinguished by ancestry rather than name.

Both `.gd` pass `tools/gdcheck.py`.

### Known instrument limits, kept deliberately

- `look_shots` needs a display; `--headless` disables rendering outright. On a
  Linux box with no DISPLAY it runs under `xvfb-run`, which means llvmpipe.
  Usable for an A/B against itself, **not** for a number quoted beside a
  Forward+ one. The report carries the project's `rendering_method` AND the API
  the process actually bound, because `--rendering-driver` moves the second
  without touching the first — reporting only the setting is how an OpenGL run
  gets filed as a Forward+ measurement.
- The exposure figures are Rec.709 on the 8-bit sRGB the swap chain received,
  after tonemapping and after Lux's post stack. Not scene-referred light.
- Box extents inside a `.glb` still come from the glTF POSITION accessor min/max
  (`probe_fights`, `sweep_fights`, `site_fights` — unchanged from last session).

### Retracted, kept above the result that replaced it

A first pass reported Lot's own WorldEnvironment "blowing 28.6% of the overview
and 59.9% of the objective shot to pure white". Those came from a hand-run at
1280×720 through hand-placed cameras counting ≥254 as clipped. Re-measured
through `look_shots`' derived cameras at 1600×900, the same project clips
**0.00%** at 255. The effect is real and an order of magnitude smaller than
advertised:

```
coldrun_pawn_job, opengl3/llvmpipe, HUD hidden
                mean    p95   near-clip
  no Lux       108.6    254      18.62%
  Lux, 2 suns  151.7    248       3.17%
  Lux, 1 sun   147.0    222       1.13%
```

Two framings of one scene are two instruments. The number that ships is the one
the tool produces.

## Open — geometry, characterised but not fixed

**`volumes` props share base planes.** 47 of the 52 exposed pairs in the
composed site. Every one is `Y min @ 0.0`: `forecourt_pad ↔ pump_island_1`
(9.6 m²), `pump_island_1 ↔ pump_1`, `VAULTLEDGE_0 ↔ register_counter` (1.2 m²
at y = 1.1, nothing in front of it). A `volumes` entry carries an absolute z and
nothing checks that it rests *on* the surface beneath it rather than inside it.
`deli:server_rack_cluster` is authored at z = 4.1 with size_z = 2.2, so its base
sits at 3.0 while storey 1's floor is at 3.3 — sunk one `floor_thick` into its
own ceiling. `presets.py` generates these, so it will not be the only one.

**Same-class surfaces share a tier.** Lot's ladder separates road (0.010) from
path (0.012) from courtyard (0.014), and that works. It never separated two
paths from each other, so wherever two cross, their top faces are the same plane
by construction — measured at 8.61 m² and 6.71 m² on `coldrun_pawn_job`.
**Decision taken:** colour the overlap graph — compute which paths actually
overlap and greedily assign micro-rungs so no two overlapping surfaces share a
height. Derived rather than guessed, bounded by the largest clique. Not yet
written.

**`VAULTLEDGE_0` and `_1` lose their colliders' names.** `cr_deli.glb` carries
both `VAULTLEDGE_0` (mesh) and `VAULTLEDGE_0-convcolonly`; Godot's importer
strips the suffix to name the body `VAULTLEDGE_0`, which the mesh already owns,
so the body is auto-renamed `@StaticBody3D@20060`. 372 `-convcolonly` nodes in
that glb and only these two collide, because only these have a visual sibling
with exactly the stripped stem. Physics is unaffected; the body is unfindable by
name, and `VAULTLEDGE_0` is already on the exposed-pair list above.

## Toolchain defects found in passing, none fixed

- **`cater` freshness hashes the spec, not the emitter.** See above — now
  reproduced rather than inferred. `check_freshness` should fold the emitter's
  identity into its hash.
- **`sightlines._occluders` calls `floorplan._opening_gaps` and
  `_wall_segments_with_gaps`, neither of which exists any more.** It raises on
  any storey with an exterior wall or a partition. `pvp_heist._spawn_los`
  catches it with a bare `except Exception: continue`, so **`PVP-SPAWN-LOS` has
  been silently unrunnable** and the fixture written to fail has been passing.
  Reproduced directly; two of the four standing pytest failures are this.
- **The nav traversal gate has been skipped on every run.** `DC_GODOT` is not
  set to a real binary, so `check.py` prints "skipping the traversal gate" and
  still says "All checks passed".
- **Two `test_nav_gate` failures are a POSIX-only fixture.** `_fake_godot`
  writes an extension-less file with a shebang and `chmod +x`; Windows cannot
  execute it. They cannot pass on this machine and never have. That is the other
  two of the four.
- **`deli_counter/build/` is a graveyard.** 1,165 entries, going back to
  19 July, looking exactly like the library. It cost one wrong measurement
  already — `deli_a01` reported at 410 straight after a successful rebuild,
  from a July file.
- **`lux/lookdev/lookdev.tscn.bak` travels.** The `.pre_*` backups are out of
  `lux/addons/` and into `_bridge/` — 0 remain across 152 addon files — but this
  one is still copied wholesale into every dressed project by `lux_dress`.

## Uncommitted at pause

Nothing below is in git. See the commit plan issued with this handoff.

- `lot/lot.py` — `GROUND_SINK` applied and verified in a generated scene.
- `lux/addons/lux/runtime/lux_root.gd` — both patches applied. `sunlink` is
  correct and now demonstrably load-bearing; commit it as the fix it is.
  `rebuild` did not fix what it aimed at — the clearing loop is defensible
  hygiene but it is **not** the fix for the editor accumulation, and its
  docstring currently implies otherwise. Commit it with that claim removed, or
  revert it.
- `tools/lux_inject.py` — the `node_paths` fix.
- `tools/godot_probe.py`, `tools/light_census.py`, `tools/light_census.gd`,
  `tools/look_shots.py`, `tools/look_shots.gd` — new, untracked.
- `tools/sweep_fights.py`, `tools/site_fights.py`,
  `deli_counter/probe_fights.py` — new, untracked, carried from last session.

None of the new instruments is wired into `check_all.py` or any DAG job. They
are hand-run tools until somebody decides what number they should gate on.
