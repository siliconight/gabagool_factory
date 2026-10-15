# Cold run 9311 -- the office's stairs filled to the ground, and deli_a03's basement closed (restaurant_row_001)

**What it tested:** Deli Counter 0.221.0 (33e6866f) and 0.222.0 (6c312336), the walker's two calls after the walk
of cold runs 9305-9307 (`docs/findings/walk_2026-10-14/`):
- **0.221.0, findings 7-9:** "fill the stairs to the ground". A cut switchback's second flight stands on the stair's
  lowest floor, and the walkway's mouth gets a back.
- **0.222.0, finding 5:** "close the basement", and the utility room's door. The delis' basement divider runs wall
  to wall, and the utility room gets a door from the corridor.

restaurant_row_001's brief as cold run 9310 ran it, seed_9003 named as 9310 named it; its lot stands the office and
deli_a03. The rest of the toolchain is 9310's. Staged from 9310.

**Result: 0 interventions (journal 0, unattributed files 0). The grades held and the fights barely moved.**

- **The grades:** every candidate PASS 90, as in 9310, with the same enemy and crew spawns
  (`fight_fields_9310_9311.out.txt`).
  - seed_9003, the one walked: 5 of 32 summary fields moved, each by a hair -- survival 52.90 -> 52.93 s on the
    mean, 756 -> 758 shots fired, 61 -> 63 missed.
  - seed_9104: none moved. seed_9205: 3, by a hair.
- **Findings 112 -> 112.**
- **The light bake:** 346 models -> 347, users 3,490 -> 3,496.
  - The one new model is `lot/office/art/zoo/prop_delco_1997_01_w160_d80_h330.glb`, 1.60 x 0.80 x 3.30 m: the
    office's new back in the second run, 1.605 x 0.795 x 3.3 m in the guard pass.
  - deli_a03's new door reuses a door module the package already carried.
- **Merged modules:** 218 removed (3.4 MB), 2 named and kept, as in 9310.
- **Seen:** `docs/findings/walk_2026-10-14/core_9311_sheet.png`, at the walker's three spots in the level's own light
  and in the inspection light, against `core_9310_sheet.png`.

## The time

    run    shell   art     export   walk   retire   the drive
    9310   103 s   181 s   179 s     8 s   21 s     8.5 min (507 s)
    9311    98 s   167 s   177 s    10 s    4 s     7.9 min (475 s)
