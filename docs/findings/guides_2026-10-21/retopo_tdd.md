# The retopology and Godot 4.7 runtime TDD, checked against Zoo and Deli Counter

A read-only research pass on 2026-10-21. It checked
`docs/proposals/Blender_Retopology_Planner_Executor_TDD_v3.0_Godot47_Runtime_MultiMesh.md` (156,614 bytes, LF line
endings, 2,113 lines, read in full) against the repositories. It wrote nothing in the factory. Its instruments are in
this scratchpad, listed at the end.

Each claim carries a mark:

- **V**: read in code, or measured on an artefact, in this pass.
- **I**: inferred.
- **C**: cited from a factory document that this pass did not re-derive.

**The artefact, and what produced it.** Everything below was measured on one package:
`workspaces/cold-9370-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot`.

- It is cold run 9370: restaurant_row_001, seed 9003, 0 interventions, built 2026-10-21T12:18Z.
- The tools that built it were Deli Counter 0.248.0, Zoo 1.120.1, Level Factory 0.228.0, Lot 0.126.0 and Lux 0.79.0,
  per `_runs/cold/cold_9370/before.json`. The package's own manifest names other versions (surprise 2).
- It runs on `gl_compatibility` with the `blue_hour` lighting preset.
- No new frame times were taken. The latest price of this level is cold run 9369's
  (`docs/findings/denser_rooms_148/price_9369_b.json`): same level and seed, with Deli Counter one version older.

**Grounding.** This pass read CLAUDE.md, the whole TDD, `docs/PERFORMANCE_CONTRACT.md`, `docs/DRAW_CALL_BUDGET.md`,
the three reports in `docs/findings/guides_2026-10-19/`, and every code location cited below. Byte check on the
import script: the package's `zoo_worldskin.gd` is 109,030 bytes and the source copy
(`level_factory/assets/godot/zoo_worldskin.gd`) is 106,681. The difference is exactly the file's 2,349 CRLFs; after
normalising the line endings the two are identical.

## (a) Summary

**The retopology core has almost nothing to act on.** The TDD has two halves, and they land very differently here. Its
retopology core (§§1-24: inspect, plan, strategies S0-S8, two-way surface QA) finds little in what Zoo and Deli Counter
ship:

- Zoo builds from primitives, with no modifiers and no booleans. A 2 m wall module is 12 triangles, a doorway 76, and a
  window 112 plus a 12-triangle pane.
- Deli Counter has two boolean paths. One never reaches the screen: its greybox walls ship only as orphan mesh data. The
  other leaves slab tiles of 20-32 triangles.
- Every primitive that reaches Godot is already a triangle list.
- The factory has measured twice that frame time follows draw submissions, not geometry, on the only GPU it has.

The planner's one real customer would be Zoo's ingest path. Today ingest normalises an external mesh's scale, pivot,
transforms and collision without looking at its topology.

**The runtime half mostly restates what the factory already does and has priced.** The TDD's runtime half
(§§25-38) asks for things the factory already has:

- It merges building geometry per room cell and material. What it keeps out of the merge is almost exactly the TDD's §27
  list of hard gates: interactive objects, openings, anything animated or scripted, light fixtures, and anything driven
  by a shader.
- It uses MultiMesh only for the layers no lightmap covers: the ground dressing and the backdrop.
- Lot merges markings, drains and overhead wires per material, one mesh per 32 m cell.
- Every solid wall module gets a box occluder.
- Each model gets a lighting class at export.
- Changes are priced A/B, against a no-change control, at fixed stations taken from the package itself.

**What the factory does not do:**

- Cull back faces. Culling is off on every surface it ships.
- Decide which meshes cast shadows.
- Split the dressing MultiMesh by area.
- Use visibility ranges or far proxies (HLOD) inside the level.
- Ship LODs on the meshes that actually draw the buildings.
- Measure interiors, doorways, lighting states or gameplay load in its benchmark.

None of this moves interventions-per-level, which was 0 on cold run 9370. All of it is frame cost on hardware nobody
here has measured. The measurement that would say what any of it is worth, an exported build on a low-end GL
Compatibility machine, still does not exist.

**The three gaps that look highest-value for runtime cost on GL Compatibility:**

### 1. Nothing decides which meshes cast shadows (TDD §32.5)

**Evidence.**

- Only Lot's 7 overhead-wire meshes, 10 drain meshes and the backdrop ground opt out of shadows. Across all 22 package
  scenes there are 35 `cast_shadow = 0` lines: the same 17 in `site.tscn` and in its Lux copy, plus 1 in the backdrop
  (V).
- Everything else casts: 1,055 merged building meshes, 29 MultiMeshes (including the four site-wide dressing batches),
  and every node instanced from a GLB (V).
- 12 lights ship with `shadow_enabled` (V).
- The factory has priced the street lights' shadow maps at 300.1 draws per heading with 12 shadowed lights and 59.2
  with 4 (roadmap 243, cold run 9262) (C).
- On 9369's price, the render thread's CPU time exceeds GPU time at 14 of 14 stations (V). Submissions are the
  bottleneck on that machine.

**First step.**

1. Run `level_factory/tools/draw_attrib.gd` on cold-9370's package. Split each heading's draws into the colour pass and
   the local-light shadow pass, and group the shadow-pass casters by size (or by Zoo category).
2. Run one A/B. The arm sets `cast_shadow` off on the class that has the most shadow submissions and the least shadow
   role: the dressing MultiMeshes and small Zoo clutter. Compare it against the package as shipped, measured twice, in
   one session.
3. Report draws per heading. They should fall only at headings where a shadowed light sees those casters, and the
   control must not move. Also report p95, and capture frames at the lit stations.

Which classes may stop casting is a look call for the walker. The TDD itself says never to drop shadows that matter
for cover or mood.

### 2. Back-face culling is off on every opaque surface (TDD §32.2, fixture G06)

**Evidence.**

- 410 of 410 materials in the 134 package GLBs are `doubleSided: true`, including all 376 opaque ones (V).
- Decoding the 1,066 shipped binary meshes: 1,067 of 1,067 embedded materials carry `cull_mode = 2` (CULL_DISABLED),
  and 1,065 of those are opaque (V).
- No tool turns culling on anywhere: not Zoo, not Deli Counter, not Level Factory's import script or merges (V).
- The risk of turning it on, measured: of the 1,104 opaque visual primitives in GLBs that a scene uses, 1,039 are
  closed shells. All of those are wound outward, and none has a flipped edge. 65 are open shells, almost all flat art
  faces (V).
- It has never been priced (V; no price found).

**First step.**

1. Copy the package. In the copy, a load-time pass sets CULL_BACK on every opaque material that is not a card or an
   art face. It has to run at load, because the merged meshes already carry CULL_DISABLED inside their binary files.
2. The control is the same pass doing nothing, run twice.
3. Measure GPU time and p95 at all stations, plus frames diffed for faces that vanish. Draws must not move; that proves
   the instrument works.
4. Repeat on a low-end GL Compatibility machine. On the RTX 2060 the CPU is the bottleneck, so a GPU-side saving may not
   show there.
5. If it holds, the lasting fix belongs in Zoo (`use_backface_culling` true for opaque packs) and in Deli Counter's
   greybox material, not in an import patch.

### 3. The surface dressing is four MultiMeshes, each covering the whole site (TDD §29)

**Evidence.**

- The four batches hold 1,018, 1,035, 1,062 and 1,012 instances. Each batch's instance origins are spread over
  207.7 x 103.8 m (V).
- None sets `custom_aabb` or a visibility range, and all cast shadows (V).
- The code groups placements by asset alone (`dressing_scene.orders_by_asset`, dressing_scene.py:161-171) (V).
- This breaks CLAUDE.md's own rule ("never one for the level"). The break has been on record since cold run 9088
  (gap 1 in DRAW_CALL_BUDGET.md) and was left as an open question in roadmap 266 (V).
- Its only price so far: on the RTX 2060, removing 29.8 % of the dressing's primitives moved the median frame by
  +0.018 ms, against a control's +0.021 ms (C, geometry.md row 15).

**First step.**

1. In a clone, Level Factory's `dressing_scene.py` emits one MultiMesh per asset per 32 m cell (Lot's `PAINT_CELL_M`,
   the factory's existing street chunk). Each carries a `custom_aabb` covering its transformed meshes.
2. A/B against the package as shipped, measured twice.
3. Report draws per heading (4 becomes 4 times the number of cells in view), primitives per heading (which should drop
   where a view sees only part of the site), GPU time, and the lights-per-object census. A MultiMesh counts as one
   object against the 8-light cap.
4. Run it together with gap 1's shadow arm, and repeat on the low-end machine.

**Next, gated by a look call:** visibility ranges on small far props (TDD §31). This cuts draws, which is the measured
bottleneck, but pop-in is the walker's call: LOD was ruled out of scope on 2026-09-26.

## (b) Item by item

| TDD section | What the factory does today (evidence) | V/I | Gap | Measurable first step |
|---|---|---|---|---|
| **1. §32.2, fixtures G06/G07: back-face culling and `doubleSided`** | **All 134 GLBs are `doubleSided: true`.** That is 410 of 410 materials: 376 OPAQUE, 28 BLEND, 6 MASK. By maker: Zoo's 117 GLBs 296/296; Deli Counter's 15 base GLBs (written by pygltflib, `gb_*` materials) 96/96; the 2 `assets/` GLBs that no scene references 18/18. **Every shipped binary mesh has culling off.** All 1,067 StandardMaterial3D in the 1,066 binary meshes (1,055 merged by Level Factory, 7 backdrop, 4 dressing) carry `cull_mode = 2`; 1,065 of them are opaque. **Where it comes from.** Zoo sets `use_backface_culling = False` only on cut-out and blended cards (zoo_keeper/bpylayer/materials.py:831, :849) and never sets True. Deli Counter's `_greybox_material` never sets it (deli_counter.py:361-388). The base rewrite passes materials through untouched (portable_building.py:251-320). The import script `zoo_worldskin.gd` never touches `cull_mode`, and all 134 sidecars read `materials/extract=0`, `_subresources={}`. No Level Factory Godot script sets it. The merge copies the imported material (`src.duplicate(true)`, merge_buildings.gd:361). Lot is double-sided on purpose for road markings and sign cabinets (lot.py:1547, :2325, :2373). **Risk if culling were on.** Of 1,104 opaque visual primitives in GLBs a scene uses: 1,039 are closed, all wound outward (positive signed volume), and 0 have a flipped manifold edge. 65 are open: pole flyers, payphone, ATM and video-poker art faces, 3 sign-box faces, 2 roof props. Zoo's own `tools/coplanar_probe.py:24` records the double-siding as known. | V. I: that Godot's glTF import is the step that turns `doubleSided` into CULL_DISABLED (nothing else sets it, and the merged copies carry it). | Never priced. No import warning (the TDD's G06). | Gap 2 above: a load-time CULL_BACK pass in a package copy, against the same pass doing nothing (twice). Report GPU ms, p95 and frames; draws must not move. Repeat on a low-end Compatibility machine. |
| **2. §27: runtime intent per asset** | **No single classifier exists, but every decision the TDD names is made somewhere**, keyed by name or metadata. **Zoo:** merges a module's parts per material and never across modules; merges a layer per placement (merge.py:1-80); merges covers per side per material (build.py:451-548). **Level Factory:** merges the Empties one mesh per side per material (merge_empties.gd:1-29). It merges enterable buildings per 6 m room cell, storey wall side, partition run, parapet side and roof, times material (merge_buildings.gd:2-49). It keeps whole exactly the TDD's §27 hard gates: `interactive_id`, `_open` openings, AnimationPlayer or script, light fixtures, ShaderMaterial, and nodes with a group or metadata (:168-231). That merge was priced at -11 % draws, worst heading 10.05 -> 9.14 ms p95 (header :44-49, C). **Lot:** street props are individual instances of shared GLBs (169 placements of 45 GLBs). Markings, drains and wires merge per material per 32 m cell (lot.py:911; site_drains.py:86; site_poles.py:411). **MultiMesh:** only the dressing (dressing_scene.py:161-171) and the backdrop (backdrop_layer.py:21-24). Lighting class per model: row 8. | V (C where marked) | No per-asset record of which way each placement went; the reports only count (`merge_buildings.json` `slots_merged`, `kept_carrying`). This is process, not frame cost. | None for runtime cost. |
| **3. §28: archetype reuse and per-instance colour** | **Repeated placements share one imported mesh.** One parking-meter GLB is placed 46 times. The 12 Empty rowhome archetypes have 26 placements, which share their archetype's merged meshes (374 nodes on 172 `.res`). GLB-level duplication is 4 extra copies in 134 files (1.1 MB), and 1.03 MB of that is `assets/lot.glb`, identical to `assets/shell.glb`. **On GL Compatibility a shared mesh is not a shared draw.** Draws equal frustum-visible surfaces exactly, ratio 1.00 (DRAW_CALL_BUDGET.md:301-302, cold run 9088, C). So the 46 meters are up to 92 colour-pass submissions (I). **glTF instancing is closed:** Godot 4.7 drops `EXT_mesh_gpu_instancing` silently, and Zoo 1.1.1 forbids it (roadmap 167, measured 2026-09-21, C). **Colour variation lives in vertex colour.** 0 of 29 MultiMeshes set `use_colors`. Colour rides COLOR_0, and the import turns on `vertex_color_use_as_albedo` per material when any vertex is darker than 0.99 (zoo_worldskin.gd:1106-1150): on in 811 of 1,067 decoded materials. **Material census on this package:** 410 entries, 101 names, 8 tint families holding 44 materials. Cold run 9080 had 908 / 242 / 11 / 183 (C). **Roadmap 280** (the cargo container, 9 materials) is still OPEN. Its unread half, read for this package: the backdrop path keeps the vertex-colour flag. The water tower's painted metal in a backdrop MultiMesh draws vertex colour; the six rowhome `_Face` materials do not. This package has no container. | V (C where marked) | Archetype identity is by stem name, not content hash. Low value: 4 duplicates. 280 remains. | 280's own close as written. Nothing new. |
| **4. §29: MultiMesh partitioning** | 29 MultiMeshInstance3D. None sets `custom_aabb` or `visibility_range_*`, and none sets `cast_shadow`, so all cast. **Dressing:** 4 batches of 1,018 / 1,035 / 1,062 / 1,012 instances. Each batch's origins spread 207.7 x 103.8 m, the whole site. It is grouped by asset only (`orders_by_asset`, dressing_scene.py:161-171). **Backdrop:** 25 batches, one per module per side, 274 instances; side strips up to 232.9 m long. **One MultiMesh spans the level: yes**, the dressing. That breaks CLAUDE.md's rule. It is on record as DRAW_CALL_BUDGET.md gap 1 (9088) and as "a question" in roadmap 266 and `docs/findings/multimesh_audit/` (9339). **Price on the 2060:** -29.8 % dressing primitives moved the median frame +0.018 ms against a control's +0.021 (C). | V (C for the price) | No spatial split, no bounds. The batches are in every shadow pass whose frustum touches the site (I). | Gap 3 above: per 32 m cell, with a `custom_aabb`, A/B against shipped twice. Report draws, primitives, GPU ms and the light census; repeat on the low-end machine. |
| **5. §30.2: surfaces and a render-vertex proxy** | **Zoo budgets triangles only.** All 139 genomes budget `tris_lod0`, and one also `tris_per_bay`. There is no surface, material, draw or vertex budget. `core/validate.py:85-89` is a warn-only triangle check; `:98-100` only asks that materials exist. A module's `meta.json` keeps the validation report and drops the merge's stats (bpylayer/build.py:103); layers keep them (:537-548). **Every drawable is effectively one surface:** all but 5 of 4,895 GLB meshes, and 1,065 of 1,066 `.res`. **The vertex proxy needs no Blender.** glTF already stores split vertices. Render vertices / unique positions per group: 1.92 (roof props) to 3.00 (DC bases; a box splits per face). Cover 2.28, kit modules 2.83, dressing GLBs 2.23, fixtures 2.24. **Level Factory already counts the runtime pool:** `material_census` (wired, adapters/presentation/__init__.py:498), `draw_attrib.gd` per GLB at stations, and `instancing_census.gd`. | V for the GLB arrays. I for Godot's imported arrays, not read (`ensure_tangents=true` may change them). | No per-module surface or vertex budget. Low value, because draws are measured where they are spent. | None recommended. |
| **6. §31: LOD and HLOD** | **The import asks for LODs everywhere.** `generate_lods=true` on 134 of 134 GLB sidecars and 36 of 36 OBJ sidecars; `create_shadow_meshes=true` on all 134. **The meshes that draw the buildings have none.** The 1,066 shipped binary meshes carry no LODs (0 surfaces with a `lods` key) and no shadow mesh: the merge (`SurfaceTool.commit`) and the extraction drop both. **Mesh nodes the entry reaches (static count):** 3,027 in total, which matches the harness's 3,027 on 9369, one tool apart. 1,615 are GLB-instanced and can carry import LODs; 36 OBJ; 1,257 merged `.res` (none); 119 inline. There are also 29 MultiMeshes (none). **No distance cuts:** Zoo's LOD path is off (build.py:24). No `visibility_range_*` or `lod_bias` in any of the 22 scenes. The backdrop is an authored far layer beyond the edge (48-triangle rowhome cards). **Walker's call:** LOD is out of scope (docs/proposals/SILHOUETTE_READING.md:236-246). DRAW_CALL_BUDGET.md:170-183 argues for reopening it narrowly as visibility-range HLOD, because the lever is draws. | V. I: import LOD never priced (none found). | No submission cut by distance. | Use `draw_attrib.gd` to split draws at `longest_sightline` and `highest_vantage` by distance band. If small far props are a large share, A/B `visibility_range_end` on them. Pop-in is the walker's call. |
| **7. §32.4: occlusion** | `use_occlusion_culling=true`. `occluders.tscn` holds 1,509 OccluderInstance3D over 53 shared BoxOccluder3D shapes, and the entry `mission.tscn` instances it. The occluders are built from measured module extents (`assets/godot/bake_occluders.gd`, `packages/exporting/occluders.py`), not by Godot's occluder bake. So the TDD's caveat that the bake reads only MeshInstance3D does not bite. Modules are classified solid 1,524 / porous 262 / glass 118 / holed 15 / filler 867 / other 729 (`occluders.json`). Interior draws fell 74-79 % when this shipped (roadmap 166, C). | V (C for 74-79 %) | None found. | None. |
| **8. §32.5 shadows, §32.3 lighting** | **Shadows:** no tool sets `cast_shadow` on what it generates, except Lot's wires and drains and the backdrop ground (35 lines in 22 scenes). 12 lights cast live shadows (Lux High tier; the tier is the walker's call, roadmap 243). The sun is baked and casts no live shadow while a lightmap shows (lux/addons/lux/runtime/lux_lighting.gd:343-376). Blended glass leaves the shadow pass at import (zoo_worldskin.gd:1066-1103). The street lights' shadow maps cost 300.1 draws per heading at 12 casters and 59.2 at 4 (C). **Lighting:** 124 GLBs import as Static Lightmaps, with Godot unwrapping UV2 at 0.2 m texels. Merged meshes unwrap their own UV2 at 0.2 (merge_buildings.gd:362) and are GI static (:373). 9 models whose second UV set carries shader data import Static but not lightmapped: 3 tree species, 2 ATMs, 4 video poker machines (packages/exporting/export.py:844-847). The police cruiser imports Dynamic (light_bake.py:96-104). **MultiMesh and the bake:** MultiMesh is kept out of baked roles on the strength of a reading of `light_bake.py` (`docs/findings/street_draws/README.md:93`). `docs/findings/multimesh_audit/README.md` calls the same question "unknown here, not assumed: a bake test settles it". | V (C for 300.1/59.2) | No mesh shadow class (the TDD's REQUIRED / OPTIONAL / NONE). No bake test for MultiMesh. | Gap 1 above. Separately, one bake test: a MultiMeshInstance3D beside a MeshInstance3D of the same mesh, baked, with the lightmap's users read back. |
| **9. §32.2, G15, S2 / T01 / T19: triangulation, n-gons, booleans** | **Everything arrives as triangles.** 4,895 of 4,895 GLB primitives are triangle lists, and all 11,862 faces in Lot's 36 OBJs are triangles. **Zoo:** no booleans and no modifiers (zoo_keeper/bpylayer/geometry.py:281-289). It bisects only for hemispheres (:181) and chipped rubble (:550). **Deli Counter:** EXACT boolean DIFFERENCE in two places: greybox walls with openings (`_box_with_holes`, deli_counter.py:469-498) and slab tiles under stair and ladder holes (`_slab_holes_cut`, :2465-2519). **In the shipped package:** the greybox walls never draw. In the 4 bases measured, every visual `ext_*` / `int_*` mesh is an orphan: `strip_greybox_base` nulls the node's mesh (portable_building.py:312-313) and only the colliders keep a node. Cut slab tiles are 20-32 triangles against 12 for an uncut tile (office 6 tiles, deli_a03 11). The walls that draw are Zoo kit modules: plain 12, doorway 76, window 112 plus a 12-triangle pane, the same at every width from 1.2 to 5.0 m. | V | None worth work: T01/T19's dense wall with a window cut-out has no instance in drawn output. | None. |
| **10. §35: the perf harness** | `level_factory/tools/perf_stations.gd` takes up to 12 stations, round-robin over 8 anchor types from `gameplay_anchors.json` (cover anchors excluded), plus `highest_vantage` and `longest_sightline`. At each: 4 headings, eye at 1.6 m, FOV 75, 1280x720, vsync off, 30 warm-up frames and 60 measured, 2 passes keeping the lower p95. It records draws, primitives and objects; median, p95 and worst frame; GPU and render-thread CPU time from a separate timers-on pass; texture, buffer and video memory; and the lights-per-object census (:71-104, :321-371, :519-748). The report has no engine build, GPU, driver or resolution (:504-518) and no p99. **Against the TDD's list:** street long view is roughly `longest_sightline` (the longest ray, not chosen as a street). Rooftop overlook is roughly `highest_vantage`. Interior cluttered room, sidewalk prop cluster and doorway transition: no station type picks them. Night light-heavy: one lighting state per package (`blue_hour` here), and no lighting arm. Four-player stress: none. **Latest price of this level (9369):** 14 stations, worst 9.46 ms p95 at 1,838 draws; the render thread's CPU time exceeds GPU time at 14 of 14. | V | Interior and doorway stations; a lighting-state arm; hardware identity in the report. | Derive room-centre stations from each building's `rooms.json` and doorway stations from `interactives.json`. Write engine version, GPU, driver and resolution into the report. This hardens the instrument and is second-order. |
| **11. Contradictions with the factory's measurements** | **(1) Emphasis.** Most of the TDD (§§1-24 and §30.1's Class E) is triangle and topology reduction. Measured here: 1,730 draws read 9.49 ms and 6,376 draws read 25.59 ms, at a flat ~1.4M primitives (CLAUDE.md). Across 9088's walk, primitives moved +15 % while frame time grew 4.3x (DRAW_CALL_BUDGET.md:42-56). Removing 29.8 % of primitives moved nothing measurable (C). The TDD says in words that fewer triangles are no proof of speed, but most of the document is still triangle work. **(2) Renderer.** Its examples, and its baseline arm C, use Forward+ automatic instancing. The factory ships GL Compatibility, where it measured draws equal to visible surfaces (C); the TDD's own G20 forbids inferring from Forward+. **(3) MultiMesh for repeated props.** The TDD offers MultiMesh for repeated rigid props; the factory merges instead because packages bake. The TDD's §32.3 agrees, so this is not a contradiction of fact. **(4) Light cap.** The TDD names the per-object light cap only for MultiMesh. The factory measured it binding merged meshes too and chose 6 m cells because of it (merge_buildings.gd:44-61). **(5) glTF GPU instancing (§33.3).** Settled negative (roadmap 167). **(6) Triangulate before export (§32.2).** Moot; everything arrives as triangles. | V (C where marked) | Not a gap: it records where the factory's measurements outrank the document. | None. |
| (extra) **§4A, §9A, §11: who the retopology core is for** | Zoo's ingest path (core/ingest.py:1-10; bpylayer/ingest.py:1-8) adopts external meshes (glb, gltf, fbx, obj, dae, stl, ply, blend). It normalises scale, pivot, transforms and collision, and does no topology analysis. The heaviest shipped modules are procedural recipes, not ingests: callery pear 3,552 triangles placed 12 times, step van 13,792, cars 2,740-3,282. | V | The planner has one customer, ingest, and ingest is not a production path in this level. | Only if the walker wants it: the TDD's Sprint A audit as a read-only report over existing ingests. Low value. |
| (extra) **§30.3: physics separate from render** | Colliders are separate `-colonly` / `-convcolonly` meshes. The merge copies StaticBody3D whole (merge_buildings.gd:293-305). The base rewrite never touches colliders (portable_building.py:310-311). | V | None. | None. |
| (extra) **§28.2: pivots and transforms** | Zoo exports with `export_apply=True` and `export_yup=True` (export.py:131-133), measures the pivot it claims (:190-197) and reports unapplied transforms (:228-230). Deli Counter runs `_apply_scales()` before export (deli_counter.py:3660). | V | None. | None. |

## (c) Surprises

1. **The whole level draws double-sided, and it is known but uncosted.** Zoo's coplanar probe records "Zoo's materials
   export `doubleSided: true`" as a fact (tools/coplanar_probe.py:24). Nothing anywhere asks what it costs.
2. **The package's manifest names tools that did not build it.** `LF_MANIFEST.json`'s `tools` block (`"tools_source":
   "factory.manifest.json"`) reads Deli Counter 0.241.0, Zoo 1.117.0 and Level Factory 0.227.0, which are the release
   pins. Cold run 9370's `before.json` records 0.248.0, 1.120.1 and 0.228.0 (V). So a recipient cannot read from the
   package which tool versions made it.
3. **The merge drops what the import asks for.** Every GLB sidecar asks for LODs and shadow meshes. Every merged and
   extracted mesh has neither, and those meshes make up 1,257 of 3,027 mesh nodes (V). Whether GL Compatibility uses
   shadow meshes at all was not checked.
4. **Two findings answer "is a MultiMesh lightmapped" differently.** `street_draws/README.md:93` says no, from reading
   the bake code. `multimesh_audit/README.md` says unknown until a bake test. No bake test was found. This is the gate
   that decides merge versus MultiMesh for repeated baked props.
5. **Bytes shipped that nothing draws.** Every slot visual that a themed module replaces stays in `site_base.glb` as
   an orphan mesh. The office base alone carries 35 orphan slabs and 27 orphan exterior-wall meshes, among others. Also,
   `assets/lot.glb` and `assets/shell.glb` (the same 1.03 MB file twice) are referenced by no scene; they are listed in
   `portable_resource_manifest.json`. Neither costs frame time.
6. **A reading trap in the roadmap.** In `PIPELINE_ROADMAP.md` a `*STATUS*` line comes before its item's body (item 1:
   status at line 972, body at 974). The status line under item 280's body therefore belongs to item 281. This pass
   misread it as a misplaced status before checking.
7. **Untracked under `docs/`.** The TDD itself is untracked. So is `docs/proposals/Lived_In_Levels_Clear_Navigation_4P_PVE_1999_PA.md`,
   which appeared during this pass. FILING.md's rule says nothing should be untracked under `docs/` at the end of a
   block of work. `patches/dc_storey_shelter/` and `patches/patch_dc_storey_shelter.py` also appeared untracked during
   this pass. All of these are someone else's concurrent work, not this pass's: the tool repos' `git status` is clean.
8. **Two of this pass's own readings were refuted; both kept.**
   - A string scan of the `.res` files found `cull_mode` in all 1,066 of them. It proved nothing: the binary string
     table lists every storable property name, defaults included. It was replaced by a real decoder.
   - The first winding count reported 9, 37 and 29 primitives with "inconsistent" winding in three groups. Those were
     touching parts joined by the position weld (13,416 edges used three or more times in the dressing GLBs alone).
     Counted on manifold edges only, the number is 0.

## Questions only the walker can answer

1. Which mesh classes may stop casting live shadows? Candidates: the dressing clutter, and props under some size.
2. Is pop-out at distance acceptable now for small props (visibility ranges), given that LOD was left out on
   2026-09-26?
3. Which machine is the low-end GL Compatibility target? Gaps 2 and 3 are GPU-side, and the RTX 2060 cannot show them.
4. Should the planner be built at all, given that its only customer here is Zoo's ingest path?

## Instruments (scratchpad, read-only, `python -B`)

| script | what it measures |
|---|---|
| `glb_census.py` | Per folder group: materials by `doubleSided` and `alphaMode`, meshes, primitives, attribute sets, how many nodes reference each mesh. Output in `glb_census_9370.json`. |
| `rsrc_read.py` | A minimal decoder for Godot 4 binary resources (RSRC). Reads embedded material `cull_mode`, transparency and vertex-colour flags, and per-mesh surface counts, `lods`, shadow mesh and lightmap hint. An unrecognised variant tag stops it with an error. |
| `res_strings.py` | The refuted string scan (surprise 8), kept. |
| `res_by_group.py` | Vertex-colour flag and COLOR / UV2 surface-format bits, per group. |
| `glb_vert_split.py` | Render vertices against unique positions and triangles, per group. |
| `mm_extents.py` | Per MultiMesh: instance count and the spread of instance origins, plus node shadow, range and bounds settings. |
| `placed_tris.py` | Triangles and surfaces of the GLBs times their placements in `site.tscn`. |
| `site_base_census.py` | What each Deli Counter base GLB carries, drawn against orphan, and slab triangle counts. |
| `kit_wall_census.py` | Triangles per wall, window and doorway module. |
| `drawables.py` | Static count of the mesh nodes the entry scene reaches, by source. |
| `open_shells.py`, `open_shells_winding.py` | Open against closed opaque shells, orientation, and flipped manifold edges. |
