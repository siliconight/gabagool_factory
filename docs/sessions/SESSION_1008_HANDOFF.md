# Session handoff — 2026-10-08

Written at the close, from the artifacts. Every figure was read or measured on
this date. Read `CLAUDE.md` and the memory index first, then this, then
`PIPELINE_ROADMAP.md` items 208, 212 and 213.

## State at close

| repo | version | unpushed commits |
|---|---|---|
| lot | 0.99.1 | 5 |
| level_factory | 0.158.0 | 4 |
| lasertag | 0.25.0 | 1 |
| zoo | 1.85.0 | 4 |
| deli_counter | 0.203.0 | 0 |
| lux | 0.68.2 | 0 |
| dispatch, patina, pixelcoat, pipeline | 0.5.2, 0.29.1, 0.61.0, 0.6.0 | 0 |
| factory root | -- | 11, this one included |

- **Clean.** Every tool repo has a clean tree.
- **Nothing running.** No cold run is in flight, and no Godot or Blender
  process is left.
- **Not pushed.** Commits are local; push only when the walker asks.
- **Disk:** 29 GB free (94% used). `tools/factory_retire.py` lists 10.1 GB
  retirable: 13 cold-run workspaces beyond the newest 12, unreferenced.
  Nothing was retired; `--apply` is the walker's call or the disk's.

## Waiting on the walker -- ask before building

**1. Roadmap 213: the club's stage lights, live or baked, and how bright.**
- **The evidence:** `docs/findings/club_stage_live_price/` -- three frames
  of the main stage (as shipped, live at Lux's energy, live at ten times)
  and the price.
- **The price of live:** no draw calls; 0.11 to 0.17 ms at a view facing a
  stage, on frames of about 3 ms; nothing measurable level-wide.
- **The look:** at Lux's energy the stage does not read lit, baked or live.
- **Asked 2026-10-08.** The recommendation given: live, and show 2x and 4x
  frames before picking a brightness.

If the answer is live:
- **Where the change goes.** Level Factory's bake
  (`packages/exporting/light_bake.py`, `mark_steady_rigs`) bakes every rig
  RESOURCE with no `failing_kind`.
- **The trap.** The colour cycle lives on the rig NODE, not the resource:
  `cycle_period_s` and `colors` are `LuxStageLightRig` exports. The resource
  carries only `bake_mode` and the lamp numbers. So "keep a rig with
  `cycle_period_s > 0` live" (213's NEXT, as written) needs either:
  - the bake mapping each resource to the nodes that use it; or
  - Lux flagging the resource when it builds a cycling stage rig, so the
    bake reads the resource alone. Cleaner, but a Lux change too.
- **Then:** a test that fails while a cycling rig bakes, and a cold run on
  club_block_014.

For brightness:
- **The frames:** `make_live_copy.py --energy-scale K` on the walk export
  (`_runs/walk_export_club_block_014`). Then `tools/look_shots.py` at the
  three given stations, which are in the finding's `shots_*.json`
  manifests.
- **The fix belongs in Lux:** the stage solve in `lux_light_loader.gd`'s
  `stage_light` branch.

**2. Roadmap 212: the responders' cruiser.**
- **Asked 2026-10-08:** comps of a 1990s police cruiser, and an invented
  department's name.
- **Then:** a Zoo species from `simple_car`'s police style, priced the way
  the van was.

## Ready to start -- no input needed

**3. The perf light census, made bake-aware.** The walker asked for it in
this session on 2026-10-08; it was not started.

Two instruments count lights by reach and never read `light_bake_mode`:
- **The perf harness:** `level_factory/tools/perf_stations.gd`,
  `_light_census` (about line 380). The cap is read from
  `rendering/limits/opengl/max_lights_per_object`, so 8: Level Factory
  writes no per-object cap, on purpose (roadmap 54,
  `packages/core/godot_project.py`).
- **Roadmap 54's closing instrument:** the root `tools/mesh_light_census.py`.

Since the light bake (LF 0.131.0) most rigs are BAKE_STATIC. Cold run
9204's census reads "33 of 3,954 meshes over 8, worst 31" whether the stage
lamps are baked or live (`docs/findings/club_stage_live_price/`).

The steps:
1. **Establish the renderer's rule first.** Does GL Compatibility skip a
   BAKE_STATIC light for an instance that has a lightmap? It is recalled,
   NOT verified, that Godot's `drivers/gles3/rasterizer_scene_gles3.cpp`
   skips one where it fills an instance's omni and spot lists. Two ways to
   settle it:
   - **Read the 4.7 source** at that point.
   - **Measure it.** Make a copy of 9204's walk export with the stage rigs
     kept STATIC (`bake_mode` 1) at ten times energy. Shoot it against the
     shipped one at `main_stage_close`.
     - The control reads 0.00% of pixels and a largest move of 25.
     - If the copy reads the same, static lamps are skipped on lightmapped
       meshes.
     - If it shows the pool -- live at ten times reads 1.06% -- they are
       not.
     - `make_live_copy.py` needs a flag that keeps `bake_mode` 1 for this.
2. **Which meshes have a lightmap:** every `LightmapGI`'s `light_data` users
   (`LightmapGIData.get_user_count()`, `get_user_path(i)`, with paths
   relative to the LightmapGI node). That is exact; `gi_mode` is not.
3. **The new count:** per mesh, the lights whose reach covers it, less the
   BAKE_STATIC ones when the mesh is a lightmap user.
4. **Keep the reach count beside it for one release,** each labelled.
   `patches/zoo_cover_merge/price_robust.py` reads the top-level census
   fields, so keep their meaning and add the new count as its own block.
5. **A test that fails without it.** A headless scene, no bake needed: a
   `LightmapGIData` listing mesh A as a user and not mesh B, and one STATIC
   and one DYNAMIC light reaching both.
   - The new count reads A 1, B 2.
   - The reach count reads 2 and 2.
6. **Proof on the real package.** Run it on 9204's shipped package, on a
   second copy of it, and on `make_live_copy.py`'s live copy.
   - The two shipped copies must read the same.
   - The live copy's stage meshes must gain the four lamps in the new
     count, while the reach count does not move.
7. **Record it:**
   - a Level Factory release (`docs/SHIPPING_A_CHANGE.md`);
   - `tools/mesh_light_census.py` given the same rule;
   - roadmap 213's "Not measured: the 8-lights-a-mesh cap" bullet;
   - the memory `perf-census-is-bake-blind`.

**4. Roadmap 208: the walk test with the crew's body (measure first).**
`docs/findings/walktest_crew_body/` -- `rewalk.py` re-walks every distinct
staged walk test in the kept workspaces (18) from copies, never through
`walktest.py`'s `main()`, whose `sync_addon` would overwrite the patched
director.
- **The result:** with the crew's 0.35 m radius and 45 degree floor, and the
  director's step-up kept, the walk test passes 18 of 18, as recorded.
  Neither leniency is hiding a failure on these candidates.
- **Next:** `python docs/findings/walktest_crew_body/rewalk.py --variant
  crew_full`, about 50 minutes. It puts Laser Tag 0.24.0's step-up in the
  copy. Its GDScript passed `gdcheck` but has never been loaded by Godot, so
  the first walk is its load test.
- **Then 208's NEXT:** the walker reads the contract's body; its step-up
  lands only on a floor; it walks the mission's order.
- **A design input for that fix.** A 0.35 m walker at 4 m/s on the
  contract's 0.40 bake (cell 0.10) has a 0.05 m corner margin, under the
  0.067 m it moves in one physics frame. The director's waypoint rule cannot
  be met for it as derived: 0.03 froze every walker, while the default 0.072
  worked on all 18.

**5. Roadmap 212: the van closes a responder lane.**
`docs/findings/responder_entry_no_stop/` replays Lot's planner on cold run
9204's inputs.
- **The cause.** The getaway van's mirrors stand 0.45 m into the inbound
  lane, and the planner's rigid 3.0 m lane cannot pass them.
- **How often:** 1 of 6 distinct candidates since Lot 0.99.0.
- **The fix is bigger than it reads.** 9204's lane would have to swerve
  twice: round the van, then round the other cruiser's open doors.
- **It reaches past Lot.** The arrival record's `lane_box`, `keep_out()`,
  `blocked()`, and Level Factory's `write_responder_arrivals`
  (`responder_arrivals.json`) all read the lane.

## Smaller threads

- **Roadmap 209 and 210:** the walker's filed-for-later items, a music
  store's window displays and 1990s payphones.
- **Memory:** `responders-arrive-on-the-way-back` and
  `perf-census-is-bake-blind` carry the current state.
