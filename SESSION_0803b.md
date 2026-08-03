# Session 0803b — the wear defect, and a walk that found six more

Picking up from `SESSION_0803.md`, which left the wear diagnosis WRONG and said so.

## What was actually broken, and how it was found

`tools/vertex_variation.py` said every cover on a shipped dressing GLB was pure
white — no variation between copies, none inside one — while `rockay` declares
`wear: 0.29`. Last night's fix (making the `Wear` layer the active colour
attribute) did not move the number. That was the second wrong diagnosis of the
same defect.

`zoo/tools/wear_probe.py` was written to stop guessing: it builds ONE real cover
through the real recipe and reports what is true at each boundary wear has to
cross — style→plan, computed→mesh, mesh→active layer, exporter→file. It found
the mesh holding correct wear (0.7011–0.9823) and the file holding 1.0000.

The difference was the material. `materials.make_material` has two branches: the
flat one wires a `ShaderNodeVertexColor` on the wear layer into Base Color, and
`_textured` deliberately omitted it — the docstring said "to keep the exporter's
texture detection unambiguous." Measured on Blender 5.1, same mesh, same
`export_vertex_color="ACTIVE"`:

    flat material     (reads vertex colour)  -> COLOR_0  0.7011 .. 0.9823
    textured material (reads none)           -> COLOR_0  1.0000 .. 1.0000

So every skinned building — which is every building — shipped with no wear.
The omission that was supposed to protect the texture is what erased the wear.

Wiring the multiply on both paths costs nothing the theory was protecting: the
probe reports `images 2, baseColorTexture 1` on the fixed export. Rebuilt
dressing, 1884 covers, all seven families:

    mean 0.845    BETWEEN sd 0.016–0.019    WITHIN sd 0.084
    (was mean 1.0000, both sds 0.00000)

## Committed

* `zoo 26728c7` — the wear fix + `tools/wear_probe.py`
* `zoo f7ee3e2` — `dress_plan` carries `ambient` (rockay 0.05, dropped by nobody
  copying it). Works, but near-invisible: `vertex_variation` averages RGB and the
  tint is chromatic, and `wear_colors` clamps `min(1.0, g*tint)` so the
  above-white half of the tint is discarded. Both known, both unfixed.
* `zoo e2c6160` — the tangent orientation fix, uncommitted since 2026-08-02.
  Every measurement taken that day depended on it and it was not in git.
* `level_factory 27a5db9` — `lot` fingerprints the art a composed `.tscn`
  references by path. `themed_site_assemble` and `lux_apply` were cache-hitting
  after a dressing rebuild because the scene's own bytes never move.

## Uncommitted, working, measured

* `level_factory/assets/godot/run_lux_apply.gd` — calls `LuxFixtureSpawner` and
  re-owns the result (the spawner sets `owner` only in the editor, and
  `PackedScene.pack()` drops unowned nodes silently). `lux.quality.json` now
  carries `fixture_lights` / `fixture_msg` and raises `LUX_NO_FIXTURE_LIGHTS` on
  zero. Reports `Spawned 152 fixture light(s) from 152 marker(s)`.
* `tools/walk_themed.py` — four changes: carries the mission's Lux preset into
  the preview (it had none, so every walkthrough ever was lit by Lux's default
  while the level ships Blue Hour); spawns fixture lights; `--no-fixture-lights`
  for A/B; and a runtime report of what the spawn produced.

## THE FIXTURE-LIGHT DEFECT — found, and it was a silent add_child failure

    [walk_fixtures] Spawned 152 fixture light(s) from 152 marker(s)
    [walk_fixtures] immediately: omni=0 containers=0

`containers=0` in the same breath as 152 successes, and `immediately` rather
than a frame later, so nothing was freeing it -- `add_child` never took. The
spawn ran from a node's `_ready`, which is while the parent is still setting up
its children, and Godot refuses `add_child()` on a parent in that state.
`LuxFixtureSpawner.spawn()` does not check the result, so it parented 152 rigs
into a detached container and returned a count of what it had ATTEMPTED.

One `await get_tree().process_frame` before the spawn:

    immediately: omni=140 containers=1
    container LuxFixtureLights rigs=152
    first rig Spawned_fluorescent(Node3D) kids = Fluoro_0(OmniLight3D)

A/B of two walk builds, mean luminance, same four derived cameras:

    shot         off      on
    spawn        69.9 -> 100.0   (+43%)
    extraction   77.8 ->  92.1   (+18%)
    overview     72.9 ->  73.0
    objective    36.3 ->  36.3

`lux.applied.tscn` carries 140 `OmniLight3D`, so the shipped scene has them as
well -- `run_lux_apply` awaits two frames before spawning and clears the guard.

TWO THINGS THIS LEAVES. `objective` did not move at all, and it is the darkest
shot of the four at 36.3 -- either no fixture reaches it or something there is
unlit for another reason, and it is the next thing to look at. And
`LuxFixtureSpawner` still reports attempts as successes; that belongs upstream
in Lux, because every consumer of that count inherits the lie. It cost six
rounds here precisely because the number looked authoritative.

## What the walk turned up (in the order found, not fixed)

1. **Fixture lights emitted nothing** — FIXED, above. The whole artificial-light
   layer of a night level was missing; one directional at 0.9 energy, 4° above
   the horizon was the entire budget. This is why it "looked really dark". Note
   that every visual judgement below was made under that, so re-look before
   acting on them.
2. **Wall packs sit low over doors and some float in the air.** The mount
   arithmetic is fine (the fluorescents prove it) so it is wall-pack-specific:
   `rot_y`, the arm's reach to a wall plane that may not be there, or
   `_WALL_PACK_RISE` (0.25 m, and the emissive lens sits at the fixture's bottom
   so its bloom washes over the door head). Wants the fixture equivalent of
   `openings.py`: a gate reporting clearance above the head and distance from the
   arm to the wall.
3. **Pilasters standing free in walkable interior space.** This is the interior
   keep-out rule that WAS measured and rejected — it flagged 1034 of 2098 orders
   because `gameplay.json` room bounds include the wall plane. The rule was
   thrown out because the test was wrong. Inset the room box by wall depth
   (`lane_reach` already does this arithmetic) and re-run.
4. **The tile grid is still visible.** Not texture — geometry. Each `panel_field`
   is 0.03 m proud with a 0.03 m gap, so every panel has four 3 cm edge faces,
   and under a sky-dominant ambient the up-facing ones draw a bright grid across
   1315 panels. `paneling.py` names the levers itself: proud depth and coverage.
5. **An interior partition crosses a window mid-span.** DC layout vs facade
   openings, nothing checking the two against each other. Also a firing-line
   problem, not only an ugly one.
6. **Window shapes read as unconventional.** Undiagnosed. Hypothesis only:
   adjacent window slots with different opening rects butting into one irregular
   outline.

## Also open

* `upstream_artifact_hashes` — the general form of the cache bug. The scheduler
  reads it from `job_spec["upstream_hashes"]`; nothing populates that key, so
  EVERY DAG edge is blind. `27a5db9` patched one edge. Roadmap 39.
* `walk_themed --godot` should not be optional. Without it the GLBs never import,
  `building.tscn` fails to load entirely, and every measurement taken against
  that project is meaningless — several today were.
* `gather_facts` never runs on the dressing path, which is why nothing caught the
  flat wear. `build_dressing` writes its own index and never calls it.

## Mistakes worth not repeating

* Overwrote `adapters/lot/__init__.py` (commit `302f254`, 44 lines) with a stale
  6419-byte staged copy, using `force: true` without checking the byte count
  against the device first. Recovered from git. The check exists because the
  bridge served a stale read THREE times today; skipping it once cost the work.
* Predicted ambient would raise `WITHIN sd`. It fell. The instrument averages
  RGB and the change is chromatic — I wrote the instrument and still predicted
  against it.
* Sent a static `grep` for light nodes when Lux builds its lighting at runtime.
  Zero was guaranteed either way.
