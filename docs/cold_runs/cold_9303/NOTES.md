# Cold run 9303 -- a walk-up stands a steel fire escape on its front (Zoo 1.110.0, Deli Counter 0.220.0)

**What it tested:** Zoo 1.110.0's `fire_escape`, drawn a storey a slot, and Deli Counter 0.220.0 standing one on
the front of every mid-rise Empty of six storeys or fewer that is no corner block (roadmaps 156 and 241;
`docs/proposals/FIRE_ESCAPE.md`). urban_row_001, seed_9104 named against 9302's, the rest of the toolchain as
9302's (Level Factory 0.208.0, Lux 0.77.0, Lot 0.123.0, Laser Tag 0.32.0). Staged from cold run 9302.

**Result: 0 interventions (journal 0, unattributed files 0). Six walk-ups on the picked candidate stand a fire
escape, and nothing the graders read moved.**

- **What stood** (seed_9104's package): `gs_midrise_i` three times, `_a`, `_h` and `_b`, 28 fire escape instances
  in all, from 16 new GLBs, four a design.
- **The light bake** read 632 models and 3,175 lightmap users, against 9302's 616 and 3,147: the 16 GLBs and the
  28 instances.
- **The pick held: seed_9104 at PASS 100,** and 0 of 32 summary fields moved on each candidate against 9302
  (`docs/findings/fire_escape/fight_fields_9303.out.txt`).
- **Findings 109 -> 109.**
- **Seen** (`docs/findings/fire_escape/walkups_9303_sheet.png`): the stacks read under a street lamp; black on dark
  brick where none lights them.
- **Priced** against 9302's package at 53 headings, 9302 the control twice: +3.3 draws a heading on the mean, +26
  at the worst (the level's busiest heading, 2,550 -> 2,576), p95 -0.09 ms at the median against a floor of
  0.38 ms. Memory: textures +0.1 MiB (`docs/findings/fire_escape/price/`).
- **Found, two:**
  - Level Factory's per-side merge left every storey a module drawn on its own, four to six a walk-up: the
    proposal's "one more draw a front" was wrong (the findings README, "Refuted").
  - Patina moved each walk-up front's coping, base course and curbs onto the stack's greybox boxes, 1.34 m off
    the wall. The awning has done the same to the corner blocks since 9297, and the stoop to the rowhomes since
    9271 (the findings README, "Found"; roadmap 248).
- **Every differing file attributed** (`docs/findings/fire_escape/package_9302_9303.out.txt`):
  - 56 new files, the 16 GLBs with their imports and unwrap caches;
  - 46 changed: the four walk-ups' scenes, bases and dressing; the bake (`bake.exr` +1.75 MB);
    `occluders.json`'s count of nodes; the records any two exports differ in; and eight scenes Godot saves -- the
    four other mid-rises', the two corners', `bake.tscn` and Lux's applied scene -- 0 lines apart once its
    per-save ids are masked (`per_save_ids_9302_9303.out.txt`).

## The time

    run    shell   art     export   walk   retire   the drive
    9302   117 s   228 s   201 s    11 s    9 s     9.7 min (584 s)
    9303   113 s   223 s   203 s    12 s    4 s     9.5 min (570 s)
