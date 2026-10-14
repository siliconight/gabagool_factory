# Cold run 9305 -- a prop is not the building (Patina 0.31.0)

**What it tested:** Patina 0.31.0 (2279f04), whose classifier leaves a shell's `prop` slots out of its bounds and
never reads their faces as exterior wall or roof, so the dressing Patina orders off the walls stays on the walls
(roadmap 248; `docs/findings/patina_props/`). urban_row_001, seed_9104 named against 9304's, the rest of the
toolchain as 9304's (Level Factory 0.209.0, Zoo 1.110.0, Deli Counter 0.220.0, Lux 0.77.0, Lot 0.123.0, Laser Tag
0.32.0). Staged from cold run 9304.

**Result: 0 interventions (journal 0, unattributed files 0). The walk-ups' and corner blocks' front dressing is
back on the wall, none of it off it, and nothing the graders read moved.**

- **The dressing orders** (each building's `patina_dressing` job, 9304 against 9305):
  - off the walls -- past y +-7.66 -- 3 on each walk-up, 12 on gs_cornershop_c and 18 on gs_cornershop_d in 9304;
    0 on every building in 9305;
  - gs_midrise_a: coping strips 37 -> 48, curbs 24 -> 30, base courses 12 -> 14, the other kinds unchanged;
  - gs_midrise_c, which stands no prop past its walls, 372 orders in both, kind for kind.
- **The light bake:** 632 models and 3,153 users, as 9304's; the dressing is merged per side, so the covers it
  added joined meshes that already stood.
- **The pick held: seed_9104 at PASS 100,** and 0 of 32 summary fields moved on each candidate against 9304
  (`docs/findings/patina_props/fight_fields_9305.out.txt`).
- **Findings 109 -> 109.**
- **Priced** against 9304's package at 53 headings, 9304 the control twice (`docs/findings/patina_props/price_9305/`):
  draws +2.0 a heading on the mean and +6 at the most, none fewer; p95 0.00 ms at the median inside a floor of
  0.06 ms; memory +0.2 MiB video, textures unchanged. The covers back on the fronts come into view.
- **Seen** (`docs/findings/patina_props/roofline_9304_9305.png`, the walk-up stations of
  `docs/findings/fire_escape/walkup_stations.py`): the coping strips back along the front parapets, bare in 9304.
  The corner blocks' storefronts differ by 2 pixels from the corner stations: what had floated at the awning's box is
  not seen from a 1.7 m eye across the street, so their orders are the evidence.

## The time

    run    shell   art     export   walk   retire   the drive
    9304   119 s   223 s   204 s    12 s    4 s     9.7 min (583 s)
    9305   110 s   214 s   202 s    12 s    4 s     9.4 min (561 s)
