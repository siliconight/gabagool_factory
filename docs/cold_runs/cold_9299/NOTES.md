# Cold run 9299 -- a bevelled mesh is one mesh every build (Zoo 1.109.0)

**What it tested:** urban_row_001 (9298's brief unchanged) on Zoo 1.109.0 (c2edb80), whose `bevel_edges` restarts
every face it leaves at its lowest vertex, and whose `start_at_lowest` carries corner data with the corners
(`patches/patch_zoo_bevel_restart.py`, roadmap 247).

**seed_9104 named** against 9298's. Level Factory 0.207.0, Lot 0.123.0, Deli Counter 0.219.0, Laser Tag 0.32.0.
Staged from cold run 9298.

**Result: 0 interventions (journal 0, unattributed files 0). Every Zoo model's bytes moved once, as the replays
said they would, and nothing the graders read moved.**

- **The pick held: seed_9104 at PASS 100,** every grade as 9298's.

      seed 9003: 0 major (not counted: LOT_DESTINATION_ABOVE_FLOOR, LT_MAP_TRIVIAL_ENCOUNTER), route completion 1.00, grade PASS_WITH_TUNING 89
      seed 9104: 0 major, route completion 1.00, grade PASS 100
      seed 9205: 0 major (not counted: LOT_DESTINATION_ABOVE_FLOOR), route completion 1.00, grade PASS 90

- **No fight moved** (`docs/findings/roofprops_bytes/fight_fields_9299.out.txt`): 0 of 32 summary fields on any
  candidate, every spawn at 9298's transform. The graders read collision and the navmesh, not the render meshes.
- **Findings 109 -> 109.**
- **The package, against 9298's** (`docs/findings/roofprops_bytes/package_9298_9299.out.txt`, by
  `patches/lf_standing_lot/package_trim.py`):
  - the same 3,283 files, the same thirteen `lot/` packages, the same 616 baked imports and 3,147 lightmap users,
    the closure clean;
  - 1,078 files differ: 364 of the package's 596 GLBs (352 in the buildings, 12 under `cover/`), their 364 import
    sidecars and
    285 lightmap unwrap caches, the 40 merged Empty meshes built from them, the lightmap itself, Godot's per-save
    ids in 11 scenes, and the metadata that hashes them;
  - the package grew 1.4 MB, all of it the unwrap caches (+1.35 MB) and the lightmap (+67 KB): the GLBs keep their
    sizes, their triangles reordered, and the engine's unwrap packs other charts from them. Once.

## The time

    run    shell   art     export   walk   retire   the drive
    9298   113 s   216 s   203 s    12 s   19 s     9.7 min (584 s)
    9299   109 s   211 s   200 s    11 s   21 s     9.5 min (571 s)

The light bake read 75.4 s in the editor, as 9298's, and baked in 37.7 s against 38.7. One run each: the restart's
cost to the art leg cannot be read from them.
