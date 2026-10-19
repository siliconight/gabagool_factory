# The baked-lighting guide against the factory

A read-only research pass, 2026-10-19, over `docs/reference/Baked_Lighting_Level_Generation_Blender_Godot_4_7.md` --
which the walker asked to be "chased/addressed" -- and the repository. **V** = it read the cited place; **I** = it
inferred. pkg means `_scratch/review/walk_9334/`, the walk copy of cold run 9334 (county_hospital_001), whose bake code
is current. Its only writes were throwaway files in a scratchpad (a `.lmbake` string-table reader and two dumps). Its
report, as given.

## 1. Verdict

The factory already does the guide's core: it bakes the assembled level in the editor at export, on GL Compatibility,
one bake per time slot; Godot's import makes the UV2; steady lights bake static, the sun and sky are in the bake, and
cycling stage lamps stay live; reflection probes are fitted to rooms; the result is deterministic and hashed.

Two of the guide's rules contradict measurements made here (keep the sun's direct light live; hiding a light does not
exclude it from the bake). What is new is everything that moves or changes:
- Actors get 126 automatic probes over a 120 x 90 m level, and no frame has ever shown a body lit by them.
- Every gameplay lighting state drops the whole lightmap.
- The bake sees every doorway open.
- Glass panes are in the bake, and nobody has measured whether light passes through them.
- Models whose second UV set is shader data are misclassified.

None of this moves traversal interventions, which sweeps already run at 0. It moves the "good" gate (roadmap 18): today
only a person playing would catch, say, a body lit by the baked sun indoors (I).

## 2. Guide against the factory

| § | Guide | Factory today | Verdict |
|---|---|---|---|
| 3, 12 | Bake in production; fixed time per variant; one domain with its blockers | Levels frozen at build, one bake per slot (V `docs/LEVEL_STANDARD.md:747-749`; roadmap 31 ANALYSIS). One LightmapGI beside the site (V pkg `bake.tscn:6-14`). The backdrop and dressing load outside it, so they take and cast no baked sun (V roadmap 243; `docs/findings/lux_tiers/README.md:110-116`) | DONE / PARTLY |
| 5.2, 7.1 | Pane separate from frame; no runtime shadow; collision separate | `Window_Glass` its own node with a BLEND material (V, window GLB JSON); blended glass leaves the shadow pass, measured (V `level_factory/assets/godot/zoo_worldskin.gd:1023-1060`); colliders `-colonly` | DONE |
| 7.1, 7.3 | Pane excluded from the bake | Panes are lightmap users: `Window_Glass`, `Car_glass_delco_1997`, `BusShelter_glass_delco_1997` in pkg `bake.lmbake`'s string table (V). Whether 4.7's lightmapper passes light through them was never measured (V). Baking the sky moved every room 1.2 or less (V `docs/findings/lighting_spec_vs_lux/README.md:177`), which fits panes blocking light without proving it (I) | NEW |
| 6 | One UV2 owner; Godot import; validate | Godot unwraps at import, deterministically (V `level_factory/packages/exporting/light_bake.py:13-23`); 140 `.unwrap_cache` files ship; all 128 sidecars at texel 0.2 (V). **But** models whose TEXCOORD_1 is shader data import at `light_baking=1` (V `export.py:837`; pkg `cover/prop_red_maple_...glb.import:29`): the lightmap's users include `StreetTree_Crown` and `ATM_Shutter` and not `StreetTree_wood` (V, string table), so sway and shutter data serve as lightmap UVs and trunks get neither lightmap nor probes (I, by `level_factory/CHANGELOG.md:3164-3165`'s rule). This contradicts roadmap 217's "trees are kept dynamic and cast none into a bake" | PARTLY + defect |
| 8.1 | Bake role per light | Steady rigs and room fills BAKE_STATIC (V `light_bake.py:299-331`; plugin `:70-77`). Failing rigs keep the engine default, "only indirect is baked" by Lux's own description (V `lux/addons/lux/resources/lux_light_rig.gd:99,103`), so their bounce is frozen (I). Stage lamps zero their indirect energy (V `lux_stage_light_rig.gd:106-112`), the only rig that does | PARTLY |
| 8.1, 8.3 | Keep the sun's direct light live for actor shadows | The sun is baked and unshadowed at run time (V `lux/addons/lux/runtime/lux_lighting.gd:363-376`): -1,854 draws and -3.56 ms a heading (V `lux_tiers/README.md:65`); the walker's call, the trade-off recorded ("what moves takes and casts no sun shadow", roadmap 243) | CONFLICTS-WITH-MEASUREMENT |
| 8.2 | Hiding a light does not exclude it from the bake | Dusk-to-dawn hides the rig, and cold run 9214 measured a hidden lamp is not baked (V `lux_streetlight_rig.gd:129-133`; roadmap 217) | CONFLICTS-WITH-MEASUREMENT |
| 8.2 | Bake no permanent consequence of a temporary state | Power cut and runtime preset change both drop the whole lightmap, and the sun goes live with its shadows (V `lux_lighting.gd:266-274, 334-340, 371`; `lux_root.gd:493-496`); the cut was priced only before the sun bake (V `docs/findings/light_bake/NOTES.md:150`). Alarm and mission-phase hooks unwired (V `LEVEL_STANDARD.md:552`). Doors ship as openings (V roadmap 174), so the bake sees every doorway open (I), while all 19 doors in pkg `interactives.json` default to `closed` (V). Breach walls bake intact (V pkg `lot/shell/site.tscn:277-281`) | PARTLY |
| 9 | Probes for actors, 1-2 m apart at thresholds; walk a grey proxy | Automatic probes only: 126 points, 1,134 SH coefficients, over 120.3 x 15.0 x 90.2 m (V, decoded from `bake.lmbake`), about 11 m apart (I). The cruiser is set Dynamic (V `light_bake.py:98-104`), but the evidence is a table, not a frame. Laser Tag's pills set no `gi_mode` (V `LT_EnemyPill.tscn:33-35`); pkg `HANDOFF.md` gives the gameplay layer no GI rule (V) | NEW |
| 10 | Room-fitted reflection probes, Once | Room boxes, `interior`, `UPDATE_ONCE` (V `lux_light_loader.gd:753-758`); atlas 16 x 64 px (V; roadmap 238) | DONE |
| 11 | Quality and density separate dials; tiers | Low quality, 2 bounces, 4096 cap, no directional (V `light_bake.py:83-85, 122-137`). Quality measured as not the lever (V roadmap 224; `docs/findings/bake_quality/README.md:36-40`). The texel test is written and unrun (V `docs/findings/bake_texel/README.md:13`) | PARTLY |
| 11.2, 16.1 | Report slices, format, memory, probes | The report keeps width and height only (V plugin `:256-264`); the real lightmap is 3 layers of 2048 x 1024 (V pkg `bake.exr.import`), 6,291,540 B in BPTC (V). Prices carry engine memory since LF 0.199.0 | PARTLY |
| 15 | Fingerprint; invalidation; the matched package on every client | Every export re-bakes; byte-identical with the clock stopped (V `light_bake_plugin.gd:19-33`); every output hashed. Lux's bind checks the data exists, not that its users still resolve (V `lux_lighting.gd:279-289`) | MOSTLY DONE |
| 16 | Bake through the editor; never fake a status | The editor's own button in a Forward+ copy, bounded and retried (V `light_bake.py:28-35, 590-616`). A failed bake ships unbaked with a log WARNING and no finding (V `light_bake.py:653-660`; `export.py:2394-2403`) | PARTLY |
| 13 | Plan light by building use; check readability at play positions | Light anchors follow building use; dens of sin stay dark; `light_check.py` holds floors at rooms, street, spawn, objective and extraction (V roadmaps 198 CLOSED, 217 NARROWED) | PARTLY |
| 17 | Validation room | None. The Lighting Spec's test scene (V `docs/reference/Godot_4_7_Natural_and_Artificial_Lighting_Spec.md:488`) "not run as a set" (V); five of its tests were done on real levels | PARTLY |

## 3. Ranked actions

1. **Show what an actor receives (§9).** Measured in root `tools/`; fixes in LF (probes), Lux (sun) and `HANDOFF.md`
   (the gameplay layer's `gi_mode`). First: look_shots stands a 1.8 m grey capsule at every `light_check` station and
   reports its luma beside the floor's, with the lights paired to it (the 8-light cap). Arms: GI_MODE_DYNAMIC against
   STATIC (STATIC is the no-probe control); sun on and off; a repeat for noise. Then the automatic probes against
   `LightmapProbe`s laid at every door, window, stair and objective from `interactives.json` and
   `gameplay_anchors.json`, the way room fills are laid. About a day. Risk: if the unshadowed baked sun lights bodies
   indoors, there is no free fix; probe lookups scale with moving bodies, so price it with 4 crew plus enemies.
2. **Price the lighting states gameplay changes, then bake them (§8)** (Lux and LF). The fixed-station harness
   alternating powered, cut, powered, cut, with a no-change control, on a day level and a night level. If the cut puts
   back roughly the 3 ms the sun bake removed, bake a second, fixtures-off LightmapGIData and swap it through Lux's
   `light_data` switch (`lux_lighting.gd:334-340`): one more editor bake (15-90 s), about 6 MiB on 9334 (I). Same
   change: keep failing rigs' and future `reacts_to_alarm` rigs' bounce out of the bake, as the stage rig does.
3. **Measure glass in the bake (§7.3 step 1)** (LF). `tools/lux_rebake.py` arms on a clear-afternoon walk copy: panes
   as shipped, panes GI_MODE_DISABLED, panes with `cast_shadow` off; control a no-change re-bake, which reproduces frames
   to 0.0 (roadmap 217). Measure the floor inside sunlit windows, paired lights and draws. Hours. Risk: brighter day
   rooms may trip `light_check`'s "room brighter than the street".
4. **Settle the shader-UV2 classification (§6)** (LF `export.py:837`, `mark_imports`; Zoo owns the shader data). A/B
   those models at `light_baking=3` against as shipped, plus a no-change control: the user count (1,434 today), frames
   at a tree and an ATM, the shade under the crowns. Hours plus a test. A crown that should both sway and bake needs its
   sway data on another channel (I).
5. **Make the bake report and the lightmap binding checkable (§15-16)** (LF and Lux): `light_bake.json` gains layers,
   format, bytes, probe count and bounds, rigs by bake mode; a finding when `ok` is false; Lux counts the users that
   still resolve. Control: 126 / 1,134 read back on 9334; a renamed node in a scratch copy must drop the count.
   Second-order.
6. **Build the validation room through the pipeline (§17)**: a one-building calibration brief through Deli Counter,
   Lot, Zoo, Lux and LF, so the room is the tools' own output; only what a real level confounds -- the pane, the frame
   shadow, the colour panel, the actor route, a door open and shut, the four-light calibration. 1-2 days; second-order;
   the regression fixture for 1-4 and for engine upgrades.

## 4. Wrong or low-value here

- Sun as an indirect-only bake: measured and decided otherwise (roadmap 243). The middle paths -- a short-range live
  sun shadow, or BAKE_DYNAMIC plus shadowmask -- are unpriced; shadowmask is used nowhere in the repo.
- "Hiding a light does not exclude it": refuted on 4.7 here (cold run 9214).
- High quality for release: quality is not the lever (roadmap 224); three bounces against two is an experiment.
- The 171 MiB memory arithmetic: this lightmap is 6 MiB; the memory problem was the reflection atlas (roadmap 238).
- SDFGI and VoxelGI: Forward+ only (roadmap 31).
- Blender-authored UV2, texel-gap padding, glTF-extras roles: a second UV2 owner is exactly action 4's defect.
- The §14 JSON role contract: roadmap 254 is parked by the walker; its two useful rules fit into `mark_imports`.
- Runtime modules, per-domain invalidation, approval states: every export re-bakes everything in 15-90 s.
- The <10% linear-luminance tolerance: the capture reads luma after the grade; keep the control-based A/B.

## 5. Questions only the walker can answer

1. Will gameplay use the power cut and the phase presets? Each its own bake, or the measured real-time fallback?
2. Doors: keep baking every doorway open, so a closed networked door shows baked light past it, or bake exterior doors
   closed?
3. If bodies indoors read as sunlit: a short-range live sun shadow, an actor light layer swapped indoors by gameplay, or
   accept it?
4. If panes block the baked sun: should sunlight fall through windows onto floors? A change to the daytime look.
5. Trees: baked crown shadows (Zoo moves sway out of UV2), or fully dynamic?
6. Which hardware defines "low-end"? The lightmap ships BPTC only, and a GPU without BPTC would decompress it (I).
