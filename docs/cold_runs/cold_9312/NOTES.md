# Cold run 9312 -- deli_a01's basement closed, and the office's stairs filled to the ground (urban_row_001)

**What it tested:** Deli Counter 0.221.0 (33e6866f) and 0.222.0 (6c312336), as 9311 did (`docs/findings/
walk_2026-10-14/`), on urban_row_001.
- **0.222.0:** deli_a01's basement divider runs wall to wall, and the utility room gets its door -- finding 5, the
  walker's own frame.
- **0.221.0:** the office's second flight stands on the ground.

urban_row_001's brief as cold run 9308 ran it, seed_9104 named as 9308 named it. The rest of the toolchain is
9308's. Staged from 9308.

**REFUTED AND KEPT: this run's batch description** says "no switchback of this lot is cut over two storeys". The lot
stands `office.glb` beside deli_a01 (the shell line in `driver.log`), and the office's stair is one 0.221.0 fills;
the bake's one new model is its back. The description was written from the 14 changed shells' names without
reading the lot, and it is kept as staged, as the run's own input.

**Result: 0 interventions (journal 0, unattributed files 0). The grades held, and the walked candidate's fight moved
with the two changes together.**

- **The grades:** every candidate as in 9308, with the same enemy and crew spawns (`fight_fields_9308_9312.out.txt`).
  - seed_9104, the one walked: PASS 100, and 10 of 32 summary fields moved. Survival 52.40 -> 55.61 s on the mean,
    player deaths 13 -> 12, enemy blocked events 0 -> 1, shots fired 1,042 -> 1,048.
  - This run cannot say which change moved them: the lot carries both. 9311 carried both too, and its walked
    candidate's fields moved by hairs.
  - seed_9003: 2 fields, by a hair. seed_9205: none.
- **Findings 109 -> 109.**
- **The light bake:** 348 models -> 349, users 3,153 -> 3,160. The one new model is the office's back,
  `lot/office/art/zoo/prop_delco_1997_01_w160_d80_h330.glb`, as in 9311.
- **Merged modules:** 284 removed (6.9 MB), 4 named and kept, as in 9308.
- **Seen:** `docs/findings/walk_2026-10-14/basement_9308_sheet.png` against `basement_9312_sheet.png`, at the walker's
  spot, the old vault-utility gap and the new door, in the level's own light and in the inspection light.

## The time

    run    shell   art     export   walk   retire   the drive
    9308   130 s   286 s   211 s     8 s    4 s    11.0 min (660 s)
    9312   131 s   249 s   201 s    10 s    5 s    10.2 min (611 s)

Neither is a speed measurement. 9308's legs ran beside the fix frames of 2026-10-14, as its notes say. 9312's shell
and art legs ran beside 9311's stairwell frames (`core_frames.sh 9311`, Godot windows from about 22:41 to 22:50).
