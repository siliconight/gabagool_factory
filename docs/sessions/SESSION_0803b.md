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

## What the walk turned up

1. **Fixture lights emitted nothing** — FIXED. The whole artificial-light layer
   of a night level was missing; one directional at 0.9 energy, 4 deg above the
   horizon was the entire budget. Every visual judgement below was made under
   that.
2. **Wall packs sit low over doors and some float in the air.** NOT a rule
   violation: `dressing_in_nav --prefix WallPack_` reports 36 fixture meshes,
   0 in walkable space. A looks problem, so it drops down the queue rather than
   off it. `_WALL_PACK_RISE` is 0.25 m and the emissive lens sits at the
   fixture's bottom, so its bloom washes over the door head.
3. **Pilasters standing in walkable interior space** — FIXED, and the cause was
   not where the rule was looking. `paneling.wall_slots` selected exterior walls
   with "facing or an ext_ prefix", and DC sets `facing` on interior partitions
   too: 299 wall slots, all 299 with `facing`, 74 of them `int_`. The filter
   admitted the whole building. Excluding `int_` took orders from 1778 to 1331
   and room intrusions from 56 to 0. Gutters were affected as well, since
   `roofline_slots` filters from the same list.
4. **The tile grid** — proud 0.03 -> 0.012 (Zoo) and joint 0.03 -> 0.01
   (Patina). A 3x3 cm groove around every cell becomes a ~1x1 cm line. The grid
   is not gone; articulation has seams. Cell size was NOT the lever: halving it
   triples the count, and doubling it was offered and not taken.
5. **An interior partition crosses a window mid-span.** Untouched. DC layout vs
   facade openings, nothing checking the two against each other.
6. **Window shapes read as unconventional.** Untouched, undiagnosed.
7. **Floors and ceilings want Pixelcoat packs** (new). Zoo has `floor.py` and
   `ceiling.py` and `make_material` already resolves a pack per material kind,
   so the missing piece is the packs -- wood / carpet / tile for floors,
   something separate for ceilings -- plus the kinds being declared in the
   genome. The first additive item on the list rather than a defect.

## THE WALKABLE-SPACE RULE, finally measured

"No dressing in walkable space or firing lines" could not be enforced where it
was breaking, and the reason is structural. Patina reads ONE building's
manifests, so `keep_out_boxes` sees a door lane and `room_boxes` sees a room
interior and neither can see the gap between two buildings. A pilaster 5 cm
proud is legal on its own facade and becomes an obstruction the moment Lot
places a neighbour 1.2 m away. `room_boxes` reporting 0 means the rooms are
clean, not that the rule holds.

`tools/dressing_in_nav.py` puts the gate where the fact lives: after
`lot_assemble`, against the baked navmesh, which IS the answer to "where can a
body go". Result: **5868 covers, 0 in walkable space; 36 fixture meshes, 0.**

It corrected itself twice, and both corrections are in the file:

* It grew each cover's box by the agent radius. The navmesh bake already insets
  by that radius -- a nav sample is where the body ALREADY fits -- so this
  applied it twice: 990+ false positives, each reporting exactly 2 samples,
  which is the two nearest polygon vertices sitting on the boundary.
* It accepted a bake that parsed MESH_INSTANCES, which carves walkable surface
  AROUND the dressing. No cover can overlap nav under that bake, so the zero
  could not have come out any other way. The bake is now forced to
  STATIC_COLLIDERS -- covers carry no collision by contract, the DC greybox
  does -- and the report names what was parsed, so a circular zero is reported
  as circular rather than as a pass.

Two findings from the same run, unrelated to dressing:

* **Lot's walk scene ships an UNBAKED NavigationMesh** -- one region, zero
  polygons. Anything that navigates in a preview built this way has no surface.
  Worth checking whether `walktest` bakes its own.
* Parsing mesh instances gave 4145 polygons against 2120 from colliders alone.
  Roughly half the walkable surface in that bake was agents standing on visual
  geometry, dressing included. Any stage baking with default parsing inherits
  that.

## Also open

* `upstream_artifact_hashes` — the general form of the cache bug. The scheduler
  reads it from `job_spec["upstream_hashes"]`; nothing populates that key, so
  EVERY DAG edge is blind. `27a5db9` patched one edge. Roadmap 39.
* `walk_themed --godot` should not be optional. Without it the GLBs never import,
  `building.tscn` fails to load entirely, and every measurement taken against
  that project is meaningless — several today were.
* `gather_facts` never runs on the dressing path, which is why nothing caught the
  flat wear. `build_dressing` writes its own index and never calls it.
* `lux_apply` cache-hit after the dressing rebuild, so the shipped
  `lux.applied.tscn` is one art pass behind. Same blindness `27a5db9` fixed for
  `lot`: it takes the composed scene by path, and lot rewrote byte-identical
  .tscn text. Second edge of the same hole.
* `LuxFixtureSpawner.spawn()` returns a count of rigs it ATTEMPTED to add, not
  rigs in the scene. That belongs upstream in Lux; every consumer inherits the
  number, and it cost six rounds here because it looked authoritative.
* `openings.room_boxes` is measured and UNWIRED. Nothing calls it, and on this
  building nothing needs to. It stays that way until something does.

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

## Floors and ceilings: wired end to end, then withdrawn

The vocabulary and the art were ready and nothing asked. Zoo has
`recipes/floor.py` and `recipes/ceiling.py`; its genome declares
concrete/tile/carpet/wood/dirt for floors and
concrete/plaster/ceiling_tile/drywall/metal for ceilings; Pixelcoat builds
`wood_`, `carpet_`, `tile_`, `plaster_`, `ceiling_tile_`, `drywall_` packs.
Deli Counter emitted `roof 1, wall 299, doorway 10, breach 3, window 6` -- no
floor, no ceiling, ever. `_slabs` gave each slab a MESH role and only the roof
became a SWAP SLOT.

`deli_counter/floors.py` (new, pure, 12 tests, mirroring `roofs.py`) emits
per-room floor and ceiling skins: two per room, because one slab is two
surfaces and slotting it once forces a wood floor to imply a wood ceiling.
Material follows room role -- a gaming floor is carpeted, a concourse tiled,
back-of-house concrete -- with a room's own material overriding and unknown
roles falling back to the spec default.

It worked end to end: slots `floor 7, ceiling 7`, kit modules `floor 6,
ceiling 6` claiming those slot types, red carpet and an acoustic ceiling grid
in the walk. Then two defects, BOTH DOWNSTREAM of the slot data, which was
exactly right (`floor_gaming_floor` 44.0x24.0 at z 0.01, `floor_vault`
44.0x32.0 at -3.99):

* **Skins cap the holes.** DC's slabs are trimesh precisely because
  stairwells, ramps and hatches boolean-cut them; `_slabs` says a convex hull
  "fills any hole straight back in, capping the opening with invisible
  collision (you see the gap but can't pass)". A rectangular ceiling skin does
  the same thing: ceiling visible above the stairs, stairs and ladder
  impassable.
* **Zoo keys kit modules by WIDTH only.** `floor_rockay_01_w4400` was emitted
  twice -- once for a 44x24 room, once for a 44x16 one. Right for a wall,
  where width varies and height is the storey; wrong for a slab where both
  axes vary. One name wins, both rooms resolve to it, and the shorter room
  gets a slab 8 m too deep. That is the overhang. `dims` is null in the kit
  index, so nothing downstream could have seen it.

The two-line call was reverted; `floors.py` and its tests stay. Three things
before it goes back:

1. Split each room's skin around the hole rects DC already computes.
2. Key slab-like modules on both axes, and record `dims` in the kit index.
3. Verify Zoo's kit path honours `collision: "none"` -- the skins declare it,
   which is not the same as Zoo respecting it, and that was never checked.

## Still open from the last walk

* **Wall seams still read as tiles.** proud 0.03 -> 0.012 and joint 0.03 ->
  0.01 did not settle it. The geometry lever is spent; what is left is
  COVERAGE -- panel fewer walls, or retire `panel_field` and let pilasters,
  base course and gutters carry the articulation.
* **The albedo repeats at about a metre.** Visible mottling across every
  panel. Texture authoring, Pixelcoat, not geometry -- a different repo from
  the seams it is easily confused with.
* **Wall packs still read as floating in doorways.** NOT a rule violation:
  `dressing_in_nav --prefix WallPack_` measures 36 meshes, 0 in walkable
  space. `_WALL_PACK_RISE` is 0.25 m with the emissive lens at the fixture's
  bottom, and the arm reaches 0.15 m back to a wall plane that may not be
  there in a doorway reveal.
* **DC's own suite has 10 pre-existing failures** -- `test_audit_specs`
  FileNotFoundError, `test_nav_gate` OSError, `test_pvp_heist`. Confirmed
  unrelated to today's work by stashing and re-running: 10 failed / 380 passed
  either way.

## Floors and ceilings: DONE

Second attempt landed. Walked and confirmed: carpet on the gaming floor, an
acoustic grid over the public rooms, stairwells open from both sides, no
overhangs.

Six pieces across three repos:

* `zoo/core/arch.py` -- `plate_parts`/`plate_voids`, a horizontal counterpart
  to `slab_parts`. Not a reuse: `slab_parts` cuts x/z (a doorway in a standing
  wall), a floor cuts x/y. Guillotine grid, merged along x, voids inset 2 cm so
  the outer bbox still equals the authored dims.
* `zoo/recipes/_arch.py` -- plate path for floor/ceiling, and NO collision
  boxes for them. That was what blocked the stairs: the slot declared
  `collision: "none"` and nothing respected it.
* `zoo/core/kit.py` + `deli_counter/themed_tscn.py` -- the naming law gains
  `_d<cm>` and `_v<hash>` for plates. Width alone had stopped identifying a
  module TWICE: 44x24 and 44x16 both planned as `_w4400`, then two 22x16 rooms
  with different stairwells both planned as `_w2200_d1600`. Wall names
  untouched. Dims are in the key only when the fit is EXACT -- a wallEnd is one
  unit box scaled per slot, and keying it on slot dims split one module into
  two identical ones (`test_plan_collapses_to_distinct_modules` caught that and
  was right).
* `deli_counter/floors.py` -- per-room floor and ceiling skins, material by
  room role, holes read from `spec.slab_holes` and re-centred, duplicates
  dropped.
* `deli_counter/deli_counter.py` -- the call sits beside `_slab_holes_cut`,
  NOT in `_slabs`. The holes are appended during the build by `_stairs`,
  `_ladders`, `_ramps` and `_vertical_links`, all after `_slabs`; reading the
  list there saw only the one hatch the spec was authored with, and every
  stairwell stayed capped -- walkable but not see-through.

Zoo 233 passing, DC unchanged at its 10 pre-existing failures. Final kit: 14
plates, 14 distinct.

## UNRESOLVED -- the backing check in tools/dressing_in_nav.py

`--backing` reports 1807 of 5868 covers with no collider within 0.75 m, in a
scene carrying 2767 CollisionShape3D (1092 Wall, 116 WallEnd, plus greybox
ext_col/int_col). I do not believe it, and it has been wrong three times:

1. It grew the cover box by the agent radius -- double-counting what the
   navmesh bake already insets. 990+ false positives, each with exactly 2
   samples: the two nearest polygon vertices on the boundary.
2. It accepted a bake parsing MESH_INSTANCES, which carves walkable surface
   AROUND the dressing and makes a zero circular. Forced to STATIC_COLLIDERS.
3. It fired along WORLD axes, which on a yawed building runs parallel to the
   wall. Changed to the cover's own basis -- and the count moved by ONE, so
   that theory was wrong too.

Known false positive in the remainder: 248 of 256 flagged are `edge_strip` in
one evenly-spaced row at y=9.0, x -76..-107. That is a roofline, and an edge
strip caps a roof edge half-overhanging by design, so a ray from its centre may
legitimately find nothing.

NEXT STEP IS NOT ANOTHER PROBE. Open `_runs/walk_floors` and look at
`Cover_edge_strip_001` at [-103.206, 9.0, 22.0]. If there is a roof edge right
there, the check is lying and should be deleted rather than left in the tree.
The probe is UNCOMMITTED for that reason.

