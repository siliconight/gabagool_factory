# Cold run 9285 -- Deli Counter 0.214.0, every walkable door at the contract's 1.25 m, on restaurant_row_001

**What it tested:** Deli Counter 0.214.0 (2879716a) in a real drive of restaurant_row_001 (roadmap 197;
`docs/findings/door_widths/`). Every walkable door Deli Counter writes is now at least the agent contract's
`min_door_width_m`: 152 authored library doors in 29 specs were widened, a width-less door now resolves to
1.25, and the presets write theirs at `presets.DOOR_W`. The library was refurnished where the doors moved
pieces, and every shell was rebuilt. Also new since 9277: Lot 0.120.2 (9be94e0), the cover fallback at the
contract's cell, which its own A/B showed moves no built site. Staged from cold run 9277; the driver picked
the seed.

**Result: 0 interventions (journal 0, unattributed files 0). The doors reached the level; nothing the grader
measures moved.**

- **The doors reached the level.** The generated corner deli (`deli_generate`) was built with seven doors
  at 1.25 m and two at 1.4 in all three candidates. In 9277 it had six at 1.1, one at 1.2 and two at 1.4,
  and the job's `shell.gameplay.json` records both. In seed_9104's assembled lot, `buildings/deli_a01.glb`
  and `buildings/office.glb` changed (both migrated specs), as did `site.tscn` and the site's drawn,
  gameplay and slots manifests. The other 40 files are byte-identical.
- **This level does not stand the generated deli.** Its lots are library buildings: deli_a01, office,
  pharmacy_a01 and the rowhome Empties. So the generated deli's rear door, roadmap 197's own, is tested by
  cold run 9286 (deli_001), not here.
- **The staged lots:** seed_9003's `level.tscn` and `site.tscn` are byte-identical to 9277's. Its lot
  holds no building whose doors changed. seed_9104's and seed_9205's `site.tscn` differ, and every
  candidate's `level.tscn` is the same.
- **The grader:** all 32 summary fields of every candidate's Laser Tag report are identical to 9277's. All
  three PASS 90, and seed_9104 was picked as before, with no guard stuck, 6 blocked and no crew stuck. Its
  routes and fights do not reach a door whose width changed; that much is measured, and which doors they
  pass is not.
- **Findings 117 -> 117**, the same codes, candidates and messages.
- **The bake:** 566 models and 224 primitive meshes lightmapped, against 9277's 567 and 224, and 3,392
  users as before. The one model is not attributed.

## The time

    run    shell   art     export   walk   retire   the drive
    9277   91 s    161 s   187 s    12 s    4 s     7.9 min (473 s)
    9285   96 s    161 s   176 s    11 s    4 s     7.5 min (451 s)

## What is evidence of what

- The doors: each candidate's `jobs/restaurant_row_001.deli_generate.candidate.<seed>/out/shell.gameplay.json`
  in `workspaces/cold-9285-ws/.level_factory/`, against `workspaces/cold-9277-ws/`.
- The lots: `jobs/restaurant_row_001.lot_assemble.candidate.seed_9104/out/`, file by file, and each
  candidate's `staging/restaurant_row_001.laser_tag_evaluate.candidate.<seed>/`.
- The grader: the same jobs' `out/lasertag.report.json`.
- The count: `cold_run.py --end`.
