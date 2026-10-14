# Cold run 9291 -- the urban street's near side fills its rooms: Level Factory 0.203.0

**What it tested:** urban_row_001 (9290's brief unchanged) on Level Factory 0.203.0 (c132c30). Where nothing left
in the near side's bag fits a room and some design does, the near side deals afresh. On Lot 0.122.0 and Deli
Counter 0.217.0. Staged from cold run 9290.

**Result: 0 interventions (journal 0, unattributed files 0). Every near-side room holds a block, and the pick
went to the higher grade.**

- **The near side** (`docs/findings/urban_street/near_blocks.py`, `near_room.py`):

      seed_9003   2 blocks, as in 9289 and 9290: the 12.67 m room the 12.30 m block, the 11.35 m room a 6.6 m one
      seed_9104   1 -> 2: the 7.33 m room, and now the 6.70 m room between b1 and b2, a 6.6 m block in each
      seed_9205   1 -> 2: the same two rooms, the same two blocks

  Every room is left with less than the narrowest design's 6.6 m. seed_9003's 11.35 m room keeps 4.75 m open,
  where the 10.30 m block would have left 0.05 m: the deal's order chose it, which is the deal working.
- **The pick** (Level Factory 0.202.0's rule): all three candidates had 0 counted majors and route completion
  1.00, so the higher grade decided it. That was seed_9104 at PASS 100 over PASS 90 and PASS 90.

      seed 9003: 0 major (not counted: LOT_DESTINATION_ABOVE_FLOOR), route completion 1.00, grade PASS 90
      seed 9104: 0 major, route completion 1.00, grade PASS 100
      seed 9205: 0 major (not counted: LOT_DESTINATION_ABOVE_FLOOR), route completion 1.00, grade PASS 90

- **One block, one enemy, a different fight.** seed_9104's new block covers the spot where 9290's Enemy_1
  stood, (20.7, -4.7), so Enemy_1 stands at (17.1, -1.0). The other five did not move. Against 9290:
  - the first enemy shot came at 6.62 s, not 1.93;
  - crew deaths over 25 runs fell from 31 to 8;
  - `combat_pacing` rose from 5 to 15, and the grade from PASS 90 to PASS 100.

  seed_9003's and seed_9205's Laser Tag summaries read as 9290's. seed_9205's new block stands at x 21 to 28, east
  of its route and of its enemies (x -10 to -32). That a 5 m move of one enemy moves a fight this far is roadmap
  242's lesson again: the encounter re-plays on any change near it.
- **Findings 109 -> 111:**
  - `LT_MAP_INSTANT_CONTACT` 3 -> 2: seed_9104's is gone;
  - `LOT_SIGHTLINE_UNBREAKABLE` 1 -> 2, `LOT_PATH_END_OFF_DOOR` 11 -> 14, `S_STREET_CROSS` 4 -> 6, and
    `LOT_COVER_PLACED` and `LOT_ROUTE_COVER_PLACED` 1 -> 0 each, with the picked candidate changed;
  - `LOT_DESTINATION_ABOVE_FLOOR` 3 -> 2: the picked seed_9104's objective is on the ground, so the art leg
    files none.

## The time

    run    shell   art     export   walk   retire   the drive
    9290   104 s   177 s   201 s    10 s    4 s     8.6 min (514 s)
    9291   107 s   175 s   195 s    11 s    3 s     8.4 min (506 s)
