# Cold run 9304 -- a walk-up's fire escape merges with its front (Level Factory 0.209.0)

**What it tested:** Level Factory 0.209.0 (3ffe5c6), whose `merge_empties.gd` gives a `fire_escape_*` slot the
front's side, so a walk-up's storeys and drop merge into one mesh with the rest of that side's painted steel, where
each drew on its own in cold run 9303 (roadmaps 156 and 241; `docs/findings/fire_escape/`, "Refuted").
urban_row_001, seed_9104 named against 9303's, the rest of the toolchain as 9303's (Zoo 1.110.0, Deli Counter
0.220.0, Lux 0.77.0, Lot 0.123.0, Laser Tag 0.32.0). Staged from cold run 9303.

**Result: 0 interventions (journal 0, unattributed files 0). Every walk-up's stack is one mesh on its front, and
nothing the graders read moved.**

- **The package:** gs_midrise_a, _b, _h and _i stand no `fire_escape_*` instance, and each front carries five merged
  meshes where 9303's carried four beside the stack's four to six. gs_midrise_c, standing none, still carries four.
- **The light bake:** lightmap users 3,175 -> 3,153, the 28 storey instances become 6 merged meshes; models 632 as
  9303's, the fire escape GLBs still imported with a lightmap unwrap though no scene instances them.
- **The pick held: seed_9104 at PASS 100,** and 0 of 32 summary fields moved on each candidate against 9303
  (`docs/findings/fire_escape/fight_fields_9304.out.txt`).
- **Findings 109 -> 109.**
- **Priced** against 9303's package at 53 headings, 9303 the control twice (`docs/findings/fire_escape/price_9304/`):
  - draws -3.7 a heading on the mean and -24 at the most, and no heading gained;
  - p95 -0.00 ms at the median, inside a floor of 0.11 ms;
  - memory flat: textures 79.7 MiB in both, video +0.1.
- **Against 9302, which had no fire escape** (`draws_9302_9304.out.txt`): at most +2 draws at any heading, -0.4 on
  the mean, where unmerged it cost up to +26.
  - Exact counts read across the two prices: 9303, measured in each, reads the same draws at all 53 headings.
  - The headings below zero (as low as -4) sit with the front dressing Patina moved onto the stack (roadmap 248).
- **Every differing file attributed** (`package_9303_9304.out.txt`, `per_save_ids_9303_9304.out.txt`):
  - the walk-ups' scenes and merged meshes, renumbered by the new front group, the steel 0.27 to 0.45 MB a walk-up;
  - the export's merge report: each walk-up 5, 6, 5 and 4 meshes more in, 13 -> 14 groups;
  - the bake (`bake.exr` -24.6 KB); the records any two exports differ in;
  - eight scenes Godot saves, 0 lines apart once its per-save ids are masked.
  - The package is 1.4 MB larger, the merged steel carrying its own lightmap UVs.
- **Found:** 289 of the package's 612 GLBs, 9.2 MB with their import files, are named by no scene, and 315 of the
  bake's 632 model imports are files no scene names. They are mostly the modules Level Factory merged the Empties
  from (`unreferenced_glbs_9304.out.txt`; roadmap 249).

## The time

    run    shell   art     export   walk   retire   the drive
    9303   113 s   223 s   203 s    12 s    4 s     9.5 min (570 s)
    9304   119 s   223 s   204 s    12 s    4 s     9.7 min (583 s)
