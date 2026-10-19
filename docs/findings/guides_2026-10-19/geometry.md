# The geometry-audit guide against the factory

A read-only research pass, 2026-10-19, over `docs/reference/Low_Poly_Geometry_Audit_Blender_Godot_4_7.md` and the
repository; it wrote nothing. **V** = it read the cited place; **I** = it inferred. Its report, as given.

## 1. Verdict

The factory already does most of what this guide asks, and it has measured what the guide only proposes. The guide's
one live point is a mislabel, and it is cheap to fix. Godot's primitives monitor is printed as "tris" on the perf
panel (F4, not F3: debug_overlay.gd:33, :511-515) [V]. CLAUDE.md:90 makes the same slip: "1.4M triangles were on
screen", but that 1.4M is the monitor (debug_overlay.gd:93) [V].

The monitor moves with render passes. On one package copy where only the Lux tier changed, over 53 headings the
monitor read a median 3.9x more at High than at Compatibility (from docs/findings/lux_tiers/perf_high.json and
perf_compat.json) [V]. That the extra comes from shadow passes is [I].

The guide assumes fewer triangles might buy frame time. The measurements contradict that on the only GPU ever measured,
an RTX 2060 (row 15). None of this moves interventions-per-level, which is already 0 on cold 9337
(docs/cold_runs/cold_9337/NOTES.md:7) [V]. This is frame-cost work. The measurement that decides it, a run on a
low-end GL Compatibility machine, has never been taken (PIPELINE_ROADMAP.md:7877-7878) [V].

## 2. Guide vs factory

| # | Guide asks | Factory today | Verdict |
|---|---|---|---|
| 1 | Never call the monitor "triangles" (§2, §9.3) | The harness says "primitives" (perf_stations.gd:347-348, perf_stations_run.py:150). The F4 panel says "tris" (debug_overlay.gd:511), and so do CLAUDE.md:90, DRAW_CALL_BUDGET.md:38 and :51, and tint_merge_run.py:150 [V] | PARTLY |
| 2 | G1: evaluated vs base triangles (§5.4, §9.1) | Zoo counts triangles every build, as a warning only (zoo_keeper/bpylayer/export.py:201-209; core/validate.py:85-89) [V]. No modifier stack, only lods.py:11's Decimate, which is off (build.py:24) [V], so base equals evaluated [I]. The count survives only as message text in meta.json [V] | PARTLY |
| 3 | G2: imported LOD0 triangles | No instrument [V]. A GLB census covers one size per species at Zoo 1.87.0: 121 species, median 320, p90 2,892 (docs/findings/weighted_normals/census.json); Zoo is now 1.113.1 [V] | NEW, low value |
| 4 | G3: triangles x placements (§9.2) | Not built. draw_census.py counts mesh nodes (:5-12); draw_attrib.gd counts surfaces (:21-24) [V] | NEW |
| 5 | R1 with draws, CPU/GPU ms and p95 | perf_stations.gd covers it (:24-85), and GPU shows "n/a" rather than 0 (debug_overlay.gd:504-509) [V]. No cold run calls it (tools/cold_drive/, cold_run.py) [V] | DONE, ungated |
| 6 | 6-12 sides on poles and pipes (test E) | Utility pole 10 (utility_pole_forms.py:68), fence post 8 (chain_link_fence_forms.py:40), streetlight 8 (streetlight.py:48), shared cylinder default 8 (prims.py:54, 467) [V] | DONE |
| 7 | Share materials, merge locally (test H) | CLAUDE.md:97-110; one surface per drawable (DRAW_CALL_BUDGET.md:328); roadmap 180, 182, 231, 233 CLOSED [V] | DONE |
| 8 | Partition MultiMeshes, set custom_aabb (test G) | Backdrop: 25 MultiMeshes [V]. Dressing: 4 MultiMeshes spanning the level, 5,748 instances, no custom_aabb, shadows left on (cold 9337 gas_block_001_dressing.tscn:8-43; dressing_scene.py:161-164) [V]. Logged in DRAW_CALL_BUDGET.md:118-164 but never a roadmap item [V] | PARTLY |
| 9 | Occlusion culling (test D) | 1,638 box occluders wired in (cold 9337 occluders.json; project.godot:11); interior draws fell 74-79% (roadmap 166) [V] | DONE |
| 10 | Shadow-pass triage (test C) | The sun's live shadows were 1,854 of 2,642 draws a heading; the sun is now baked, worth 3.03 ms p95 (roadmap 243 NARROWED) [V]. The tier is still High, with 12 shadowed lights [V]. Shadow casting is off only for drains, wires, the backdrop ground and lamp cones (lot/site_drains.py:477, lot/site_poles.py:580, backdrop_layer.py:147, lux_streetlight_rig.gd:317), and nowhere in Zoo [V] | PARTLY |
| 11 | Check import LOD; HLOD (test F) | `generate_lods=true` on 302/302 GLB and 46/46 OBJ sidecars in cold 9337's package, Godot's default, never priced [V]. DRAW_CALL_BUDGET.md:166-168 says LOD is unused [V]. Merged Empties carry no LODs (merge_empties.gd:163-189) [V]. No `visibility_range` or `lod_bias` in any tool repo [V] | NEW |
| 12 | Duplicate geometry (§4) | check_coplanar.py:1-25, site_fights.py; roadmap 177 [V] | PARTLY |
| 13 | Budgets by class, asset record (§12-13) | One `tris_lod0` per genome; class, viewing distance and placements are missing (MODERN_LOW_POLY_IN_ZOO.md:37-75; roadmap 214) [V] | PARTLY |
| 14 | Four-player encounter measured separately | The harness runs nothing else (DRAW_CALL_BUDGET.md:76-79) [V] | NEW |
| 15 | Fewer triangles may buy frame time | 9142 vs 9144 (dressing reduced): primitives -29.8% at the median heading and at least 423,160 lower at all 53; draws unchanged; median frame +0.018 ms against a control +0.021; GPU -0.10 ms (docs/findings/dressing_price/; cold_9144/NOTES.md:23-34) [V]. 9308 with the ground removed (walk_2026-10-14/README.md:276-283): at 426 vs 450 draws, primitives 0.65M vs 2.97M, frame 2.98 vs 2.68 ms, GPU 0.85 vs 1.41 ms (ground_shaded/perf_control_1.json) [V] | CONFLICTS-WITH-MEASUREMENT (RTX 2060 only) |

## 3. Ranked actions

None of these reduces interventions; ranked by frame-time leverage on GL Compatibility, cheap and certain first. Costs
are estimates [I]; none should be done while a cold run is in flight.

1. **Relabel the monitor** (level_factory, plus root docs). "tris" -> "prims (all passes)" at debug_overlay.gd:511 and
   in tint_merge_run.py:150's text; CLAUDE.md:90 and DRAW_CALL_BUDGET.md:38/51. Control: a test on the panel's format
   string that fails on today's file. Under an hour, no risk. Otherwise someone will check the reference guide's
   "visible triangles <= 1.0M" (Godot_4_7_Multiplayer_Procedural_Level_Performance_Bible.md:46) against a monitor that
   read 5,503,580 at 9308's worst heading [V].
2. **Attribute R1 by pass and origin, with an LOD arm** (level_factory). Extend draw_attrib.gd to sum index count / 3
   over the surfaces in view (single-pass visible triangles), and a second arm with `mesh_lod_threshold=0`. Controls:
   the modelled draws must match the engine's counter (DRAW_CALL_BUDGET.md:280-298); hiding one GLB of known count must
   move the sum by exactly that count; two unchanged runs bracket the LOD arm. Half a day.
3. **Dressing: shadows off, then partition it** (level_factory, dressing_scene.py). One change per arm: `cast_shadow`
   off; then cells, each with a `custom_aabb` and a `visibility_range_end`. Expect about 0 ms on the 2060 [I]; the
   payoff would be on weak GPUs.
4. **Shadow casting by size class** (a Zoo genome flag, applied by LF's zoo_worldskin.gd). Street lights' shadow maps
   were 300.1 draws a heading with 12 shadowed lights and 59.2 with 4 (roadmap 243) [V].
5. **One low-end GL Compatibility run** on the walker's hardware: as shipped twice (the control), dressing removed,
   the Compatibility tier. The only measurement that can make the guide's concern real or retire it.
6. **Visibility-range HLOD for far buildings** (level_factory, deli_counter), only after action 2. Large cost; pop-in
   risk; conflicts with the light bake.

## 4. Wrong or low-value here

- The modifier audit, script 9.1 and the 1.25 gate: Zoo builds "with no operators and no modifier stack"
  (geometry.py:284-289) [V]; Deli Counter's booleans cut 8 of 344 slabs (zoo_worldskin.gd:150-156) [V].
- Test E: poles are already 8-10 sided [V].
- Decimate, or thinning nearby geometry: the walker did not want poly counts cut "'just cause'"
  (DRAW_CALL_BUDGET.md:169-171) [V]; an LOD that keeps its draw count "buys little" (MODERN_LOW_POLY_IN_ZOO.md:81-84) [V].
- Moving poles, bins and fences into MultiMeshes: "A MultiMesh is NOT lightmapped" (street_draws/README.md:93), and
  packages bake by default [V].
- The guide's §10 curb savings: Lot's ground is box tiles, whose cost was the number of draws, which roadmap 231
  closed [V].
- Any budget read off R1: on identical meshes it moved 1.5-5.4x with the tier alone [V].

## 5. Questions only the walker can answer

1. Was the high count the F4 panel's "tris" line? On which level, facing where?
2. What is the minimum-spec GPU, and can we measure on one?
3. Which Lux tier should packages ship with (roadmap 243)?
4. Can dressing and small props stop casting live shadows?
5. LOD was left out on 2026-09-26 (SILHOUETTE_READING.md:238-239). Is pop-out at distance acceptable now?
