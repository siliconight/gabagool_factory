# Cold run 9308 -- the walk's findings 1-4, fresh for the walker's demo (urban_row_001)

**What it tested:** the four contained findings from the walker's walk of cold runs 9305-9307, fixed in the tools and
run fresh for the walker's 21:00 demo (`docs/findings/walk_2026-10-14/`):
- Zoo 1.111.0 (9176f8d): a lit shop's room glows under its goods, and every desk's stock faces its sitter.
- Zoo 1.112.0 (8d1e2a4): a door under its building's band says the trade.
- Level Factory 0.211.0 (5c67868): a ground under the backdrop.

It is also the first cold run of Level Factory 0.210.0, which drops the modules the per-side merge made redundant
(roadmap 249). urban_row_001, seed_9104 named as in 9305. The rest of the toolchain is 9305's: Deli Counter 0.220.0,
Lux 0.77.0, Lot 0.123.0, Laser Tag 0.32.0, Patina 0.31.0. Staged from 9305.

**Result: 0 interventions (journal 0, unattributed files 0). Nothing the graders read moved, and the package
dropped the 284 modules no file names.**

- **The grades:** 0 of 32 summary fields moved on any candidate against 9305, and every enemy and crew spawn stands
  where it stood (`fight_fields_9305_9308.out.txt`). seed_9104 PASS 100, seed_9003 PASS_WITH_TUNING 89, seed_9205
  PASS 90.
- **Findings 109 -> 109.**
- **Merged modules (Level Factory 0.210.0):** `[export] merged Empties' modules no file names: 284 removed (6.9 MB),
  4 named and kept`.
  - The light bake's models went 632 -> 348; its users stayed 3,153, as in 9305.
  - The editor's bake took 71.5 s against 75.3 s, one run each. Other Godot jobs ran beside this run (below), so
    that is not a speed measurement.
- **Every file that left or joined the package** (`docs/findings/merged_modules/package_files_9305_9308.out.txt`):
  3,343 files -> 2,487, 205.6 MB -> 198.5 MB.
  - The modules' 852 files (284 GLBs with their sidecars).
  - The deli's and the pharmacy's door boxes: the band's pack textures out, painted faces in (DELI; PHARMACY).
  - The corner shops' pane emission texture: one out and one in each, Zoo 1.111.0's room glow.
- **The primitive count 224 -> 225 is the backdrop's ground getting a UV2, not a bake.**
  - The bake report's `primitives` reads `site_backdrop.tscn: 1` beside `site.tscn: 112` and
    `presentation/lux.applied.tscn: 112`. `add_primitive_uv2` writes `add_uv2 = true` on every inline primitive in
    every scene, and the log line sums those counts as "lightmapped".
  - The plane is not a lightmap user. `bake.lmbake` names the plate's `Ground_*` pieces and no backdrop node, and
    `mission.tscn` loads `site_backdrop.tscn` at run time, outside `bake.tscn`.
  - The same sum counts each of the level's 112 primitives twice, once per scene. Both wordings are filed in the
    roadmap; neither changes a level.
- **Seen:** fixes 2 and 4 confirmed and 1 improved in frames at the walker's own spots; 3 not decided by frames
  (`docs/findings/walk_2026-10-14/README.md`, `fixes_9305_9308.png`, `fixes_1_3_9305_9308.png`).
- **Loaded headless** at 18:45 (`--headless --quit-after 600` on `_runs/walk_export_urban_row_001`): exit 0,
  no engine error, and the one warning this afternoon's copy also prints (`[cycle] no sky provider in this scene`).
- **Not priced.** "One draw", in Level Factory 0.211.0's entry, is read off the scene. The ground is a shaded mesh
  spanning the whole level, so any light that reaches it may cost more, and that is unmeasured. The plan is to
  price it after the demo: this package against itself with the `BackdropGround` node removed, which isolates
  the plane.

## The time

    run    shell   art     export   walk   retire   the drive
    9305   110 s   214 s   202 s    12 s    4 s     9.4 min (561 s)
    9308   130 s   286 s   211 s     8 s    4 s    11.0 min (660 s)

The frames for the fixes were shot in Godot while this run's export leg ran (`_scratch/fix_before_9305`, written
18:15). Its art leg is the slowest of the six runs since 9305. Neither leg is evidence about the tools' speed.
