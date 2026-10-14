# Cold run 9292 -- heights by cause: the urban wall rises with distance from the action (Level Factory 0.204.0)

**What it tested:** urban_row_001 (9291's brief unchanged) on Level Factory 0.204.0 (065ab60). On an urban wall,
each block is the one on the bag whose height is nearest the height a block standing there is drawn toward:
lowest across from the action's centre, rising with distance from it. **seed_9104 named**, not `auto`, so the A/B
against 9291 stands on one candidate (roadmap 245: a pick follows the grade, and grades move with any change
near a fight). Lot 0.122.0, Deli Counter 0.217.0. Staged from cold run 9291.

**Result: 0 interventions (journal 0, unattributed files 0). Every candidate's wall rises with distance from the
action; nothing else moved.**

- **The walls** (`docs/findings/urban_street/wall_heights.py`, `wall_heights.out.txt`): the rank correlation of a
  block's distance from the action's centre with its top, against 9291's walls (dealt alone, as in 9287 to 9291):

      seed     action's centre    9291     9292
      9003     x -28.5            +0.40    +0.93
      9104     x  -2.5            -0.05    +0.92
      9205     x -27.0            +0.03    +0.91

  seed_9104, west to east, in metres: 9291 stood 16.5, 22.7, 16.5, 32.5, 26.2, 19.6, 13.2, 38.7, 19.8, 26.2.
  9292 stands 32.5, 26.2, 22.7, 16.5, 13.2 (at x -6, beside the action's centre), 16.5, 19.6, 19.8, 38.7, 26.2.
  The last block is 26.2 m, not taller: the 18.0 m left before the plate's end holds neither of the two tallest
  (19.8 and 24.3 m wide), and d, 16.8 m wide, is the tallest that fits.
- **The near side** stood as 9291's: `infill` is unchanged and the seed the same.
- **The fights barely moved.** Every candidate's grade is as 9291's. seed_9104's first enemy shot came at
  6.57 s, not 6.62, and its crew deaths stayed 8. The fights are on the near side; the wall stands across the
  street.
- **Findings 111 -> 111**, no code moving.

## The time

    run    shell   art     export   walk   retire   the drive
    9291   107 s   175 s   195 s    11 s    3 s     8.4 min (506 s)
    9292   108 s   180 s   197 s    11 s    3 s     8.6 min (514 s)

## Seen and priced against 9291

**Seen** (`docs/findings/urban_street/ab_9292/skyline_sheet.png`, 9291 left, 9292 right).
- **Why not the standard sheet.** `ab_record.sh`'s elevations frame one mission building and crop the wall's top,
  so they cannot show a skyline. That sheet was not kept.
- **Three given stations were shot on both packages instead:**
  - `skyline_N`, from behind the near side 25 m up, looking south (east on the left);
  - `street_up_W` and `street_up_E`, from the action's centre on the street, tilted up toward each end.
- **What they show.** 9291's skyline jumps where the deal fell: its 32.5 m block is the nearest far-side block
  looking west from the action. 9292's wall is low across from the action's centre (13.2 m at x -6) and rises
  toward both ends: 32.5 m at the west end, 38.7 m at x 54 on the east.

**Priced** (`ab_9292/price/price.txt`; 53 headings, the same stations in both runs, control-subject-control):
- draws -7.6 a heading on the mean (-33 to +14), against the controls' ±0.4;
- p95 +0.04 ms at the median, against a 0.04 ms floor;
- memory identical: textures 78.9, buffers 74.5, video 153.4 MiB. It is the same ten blocks, reordered.
