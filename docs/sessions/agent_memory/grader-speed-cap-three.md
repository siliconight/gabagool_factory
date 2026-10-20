---
name: grader-speed-cap-three
description: "cold-run speed (roadmap 239), the walker's theory-of-constraints loop: drive 30.4 -> 6.9 min by 9259 (LF 0.186-0.193); one workspace bakes the same bytes since LF 0.192.0, two cold runs one lightmap since Zoo 1.103.0 (9260/9261)"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-12T13:52:48.389Z
---

Walker asked 2026-10-11 how to make cold runs faster "without losing any
certainty"; later named it the Theory of Constraints ("The Goal"): find the
bottleneck, cut it, re-measure, repeat. Record: docs/findings/grader_speed/.

- **Drive:** 9245 30.4 min -> 9248 14.3 (fixed clock) -> 9249 12.1 -> 9251
  10.8 (Blender 3) -> 9252 10.3 (LF 0.186.0 compose side by side) -> 9253
  9.7 (0.187.0 bake marks) -> 9254 8.4 (0.188.0 kept cache) -> 9255 7.8
  (0.189.0 models imported once) -> 9256 7.5 (0.190.0 compressed
  everywhere, the walker's call) -> 9257 7.2 (0.191.0: the export writes
  .godot/scene_groups_cache.cfg; without it the bake's editor loaded every
  model ~20 s to read scene groups) -> 9258 7.0 (0.192.0: bake editor
  Engine.time_scale 0, open floor 240 -> 1 frame, localizer substring
  pre-check) -> 9259 6.9 (0.193.0: viewports stop AT the press -- from the
  start bakes 17.5 % darker, refuted; work copy on 8 threads, removed
  behind). 0 interventions throughout. 9260/9261 (Zoo 1.103.0) ran 434 and
  449 s: every leg slower, Pixelcoat too -- the machine (AVGUI busy,
  unmeasured); Zoo's own 16 kit builds A/B'd 55.7/56.4 old vs 55.4/58.7 new.
- **On a stranger's path (install test 8, factory 1.39.0, 2026-10-12):**
  make 34.1 -> 7.9 min, walk 10.9 -> 5.6 against install test 7. Its
  unpicked seed_9205 went PASS_WITH_TUNING 82 -> WARN 70 (crew survival
  75.7 -> 7.0 s) on a byte-identical scene: body_or_clock_ab.sh, a 2x2 of
  Laser Tag body (0.25/0.26) x clock (waiting/fixed) with both controls
  reproducing their jobs, put it ALL on 0.26.0's enemy body (0.40 pill ->
  the contract's 0.35); the clock moved no field on either body.
- **9258's split:** shell 74 s, art 154, export 175 (export_timeline_probe:
  sidecar imports 56.6 s, bake editor ~64 = start 5 + floor/ask ~8 + first
  frame of the level ~10 + press 2 + bake 35.5 + exit 3.5; other imports 16,
  scripts 12.6, Python 22 incl. work copy copy 4.9 + delete ~2.6), walk 10,
  retire 3.
- **Art leg chain (9256, leg_spans.py):** lead 9.6 s, pixelcoat 16.5, Blender
  waits 21.6 + 12.4, compose 30.7, themed_site_assemble 8.2, Lux staging wait
  26.5 (a full --import of 480 models + 428 textures; load-bearing, Lux loads
  the scene), lux_apply 3.7.
- **Instruments:** cold_drive.sh step stamps; leg_spans.py; re-export probes
  holding the run's package aside (sidecar_once_probe.py; bake_phases_probe.py
  with BAKE_T per plugin step, --scan, --verbose, --no-groups-cache control,
  --arm keeps log + bake.exr); lightmap_compare.py (+ exr_dump.gd; --layout
  with lightmap_layout.gd); import_digest.gd; walk_copy_census.gd;
  zoo_repro_probe.py (--jobs <ws> replays every Zoo job of a cold run N
  times, array by array); blend_mesh_dump.py; uvsphere_order_probe.py.
  Alternate change/control arms; never run du or other disk walks during a
  timed arm.
- **Bars:** two exports of one level bake the same bytes (LF 0.192.0+) and
  differ in 18 files (light_bake.json, 4 manifests, bake.tscn, 12 Empties'
  site.tscn -- why not asked). Two COLD RUNS (9260/9261, Zoo 1.103.0): same
  atlas layout, all but 15 of 16,777,216 texels bit-identical (< 0.00005).
  Residue: rowhome_k dressing's merged CoverS_metal_painted triangle order;
  lux.applied.tscn resource ids. The atlas is 16 slices where it was 15.
- **Zoo 1.103.0 (the "dome naming" was face ORDER):** Blender's
  create_uvsphere and bisect_plane lay faces in a per-process order;
  holes_fill and the bisect start a face at any corner; add_hemisphere gave
  its bisect a set. Fix: geometry.in_one_order, start_at_lowest (refuses
  with loop layers), bm_to_object sorts faces (BMElemSeq.sort needs a
  numeric key -> rank list). Not hash seeds, not threads (kept refuted).
  9259's 38 Zoo jobs replayed: 7 differed on 1.102.0, 0 on 1.103.0.
  LF 0.193.1 re-grounded contracts.GROUNDED to it.
- **Godot facts:** a model imported before its shared textures embeds copies;
  a base can't load() an unimported sibling; re-importing after textures
  resets pins; [importer_defaults] reach only files with NO sidecar; a
  sidecar's missing key takes its pre-key value; an editor on a project with
  no scene_groups_cache.cfg loads every scene first (headless never writes
  it); loading a .lmbake needs its lightmap's import; SubViewport's knob is
  render_target_update_mode, not update_mode.
- **Next candidates:** rowhome_k merged-cover order, Lux applied ids, the
  opened scene's first frame (~10 s, NOT the viewport -- tool
  scripts/gizmos?), one project for the two extractions (~3.5 s), sidecar
  model imports (32 s; serial in Godot), Lux staging 26.5 s, Blender waits,
  the LF suite (~6.4 min, now as long as a cold run).
- **Walker's calls queued:** grader step (4x vs 1/60 s); the level a
  failing lens bakes at (dark/full/mean; frozen at t=0 now). See
  [[open-work-2026-10-09]].
