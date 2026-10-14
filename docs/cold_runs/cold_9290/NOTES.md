# Cold run 9290 -- the urban street with enemies behind its near side: Lot 0.122.0, picked by Level Factory 0.202.0

**What it tested:** urban_row_001 (9289's brief unchanged) on Lot 0.122.0 (030901f). In that release a row the
fences leave open shuts nothing, so enemies may stand behind the near side's blocks. Picked by Level Factory
0.202.0 (2f5b217), where a pick no longer counts Laser Tag's fight verdicts, nor Lot's upstairs-objective doubt
where the walk test walked to the objective. Deli Counter 0.217.0. Staged from cold run 9289.

**Result: 0 interventions (journal 0, unattributed files 0). Every candidate was graded, and all three grade PASS 90.**

- **The starved candidate stands its enemies.**
  - seed_9205 in 9289: six of six unplaceable (`LOT_ENEMY_SPAWN_UNPLACEABLE`), and Laser Tag refused the map.
  - Here: six enemies, graded PASS 90, route completion 1.00, crew deaths 1 in 25 runs.
- **The fences are as they were** on all three candidates: two end runs on the far row, and the near row left
  open (`LOT_FENCE_SKIPPED: row 1 left open`).
- **The pick** (Level Factory 0.202.0's lines in `driver.log`):

      seed 9003: 0 major (not counted: LOT_DESTINATION_ABOVE_FLOOR), route completion 1.00, grade PASS 90
      seed 9104: 0 major, route completion 1.00, grade PASS 90
      seed 9205: 0 major (not counted: LOT_DESTINATION_ABOVE_FLOOR), route completion 1.00, grade PASS 90

  Three-way tie, so the lowest seed: seed_9003. 9289 picked seed_9104, which no longer wins its ties
  (roadmap 245).
- **The fights moved with the enemies.**
  - Every candidate's `combat_pacing` fell from 15 to 5 on `INSTANT_CONTACT`. The enemy's first shot averaged
    1.96, 1.93 and 2.65 s: under Laser Tag's 3 s minimum, still above Lot's 1 s reaction contract.
  - So seed_9003 and seed_9104 fell from PASS 100 to PASS 90. Crew deaths over 25 runs: 9003 5, 9104 31,
    9205 1.
  - Enemy placement is provisional, and the encounter categories describe the fight rather than the level
    (`lasertag_report.ENCOUNTER_CATEGORIES`). Recorded, not tuned.
- **Findings: 108 -> 109.** The spawn findings carry the change:
  - `LOT_ENEMY_SPAWN_UNPLACEABLE` 1 -> 0, `LT_MAP_MISSING_ENEMY_SPAWNS` 1 -> 0, `LT_NOT_EVALUATED` 1 -> 0;
  - `LOT_ENEMY_SPAWN_CLOSE` 1 -> 4, `LOT_ENEMY_SPAWN_STANDOFF` 2 -> 4, `LT_MAP_INSTANT_CONTACT` 0 -> 3,
    `LT_OPENING_STANDOFF` 1 -> 3: enemies nearer the crew's route, where the band had kept them out;
  - `LT_OPEN_SIGHTLINE` 6 -> 0.
  - `LOT_DESTINATION_ABOVE_FLOOR` 2 -> 3: the picked seed_9003's objective is a storey up, and the art leg's
    assemble files it again.

## The time

    run    shell   art     export   walk   retire   the drive
    9289   88 s    176 s   192 s    9 s     3 s     7.8 min (470 s)
    9290   104 s   177 s   201 s    10 s    4 s     8.6 min (514 s)

