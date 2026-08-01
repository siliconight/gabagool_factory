# Session state — 1 Aug, z-fighting and the level look

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

## What the flicker actually was

Not geometry. The composed gate read **961 solids in one frame** and found no
coplanar pair anywhere near a wall meeting a floor. Turning the sun's shadow off
made the band vanish. It is shadow acne, cross-hatched by more than one
directional light.

The geometry work was still real and still needed — it just was not what was on
screen.

## Open — lighting (where this stopped)

**Sun Link does not take effect.** At runtime the scene has two directional
lights: Lot's `Sun` and one Lux creates. `lux_inject` sets
`sun_light = NodePath("../Sun")`, and `patch_lux_sunlink.py` made
`_build_modules` adopt it — but two suns still render, so `sun_light` is
evidently null at that point in the lifecycle.

**Next measurement, before any further patch:** run the scene, switch the Scene
dock to the **Remote** tab, expand `Lux`. If a `LuxSun` exists there, the
exported node reference is not resolved during `_build_modules()` and the
adoption must move to `apply_preset` (where `_resolve_sun_link` has definitely
run). If it does not exist, the second light is something else and the reading
above is wrong.

**Editor-only accumulation, separate defect.** With the scene open in the
editor, `Lux` accumulates DirectionalLight3D and CRT post stacks — four lights
and three stacks observed. The scene *file* stays clean (8,146 bytes, one
`Sun`), and runtime shows two, so this is editor scaffolding, not shipped state.
`patch_lux_rebuild.py` made `_build_modules` clear its previous children, which
did not stop it — the nodes appear during a *single* load, which is why the
name-clash dialog fires at load time.

Suspected root cause, unverified: `ensure_sun` does
`sun.owner = parent.get_tree().edited_scene_root`. Giving runtime scaffolding an
owner makes it a saveable member of the edited scene, which is why it shows in
the dock at all and why one Ctrl+S would bake it in permanently. Runtime modules
should probably be ownerless.

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

## Instruments built this session

All three live in `tools/` except `probe_fights.py`, which sits beside
`zfight_gate.py` in `deli_counter/`.

- `probe_fights.py` — every fight in one `.glb` with both boxes' real extents,
  an overlap-shape classification, and whether anything covers the outward side.
- `sweep_fights.py` — the built library, one row per distinct build, with the
  build date so a stale export cannot hide inside an average, and a `DIVERGED`
  mark when one building exists at two sizes.
- `site_fights.py` — a **composed** site: Lot's box nodes plus every building's
  `.glb` expanded node-by-node through its instance transform. This is the one
  that found the ground-plate ring.

### Known instrument limits, kept deliberately

- Box extents inside a `.glb` come from the glTF POSITION accessor min/max, so a
  slab with a stairwell hole booleaned through it still reports as solid there.
  That is 6 of `cr_deli`'s 23 and ~4 per building across the library — the flat
  tail of identical counts in the sweep. A real mesh test would remove it.
- `site_fights` reduces rotated boxes to their world AABB for non-horizontal
  face pairs. Horizontal pairs now use the true yaw-rectangle intersection, so
  the "158 m² path ↔ path" it first reported is gone; anything still marked `~`
  is a lead, not a fact.

## Toolchain defects found in passing, none fixed

- **`cater` freshness hashes the spec, not the emitter.** Three of four
  buildings in the first dressed level were pre-fix exports reported as
  "already fresh", because their specs had not changed. `check_freshness`
  should fold the emitter's identity into its hash.
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
- **`deli_counter/build/` is a graveyard.** 103 `.glb` going back to 19 July,
  looking exactly like the library. It cost one wrong measurement already —
  `deli_a01` reported at 410 straight after a successful rebuild, from a July
  file.
- **`lux/addons/` now carries `.pre_*` backups** written by this session's
  patches. `lux_dress` copies the addon wholesale, so they travel into every
  dressed project (94 → 96 files) and would reach somebody else's Godot project.
  Move them to `_bridge/`.

## Uncommitted at pause

- `lot/lot.py` — `GROUND_SINK` applied and verified in a generated scene.
- `lux/addons/lux/runtime/lux_root.gd` — both patches applied. `rebuild` did not
  fix what it aimed at; `sunlink` is correct in intent and ineffective in
  practice. Commit honestly or revert; do not commit them as a fix for the
  editor accumulation.
- `tools/sweep_fights.py`, `tools/site_fights.py`,
  `deli_counter/probe_fights.py` — new, untracked.
