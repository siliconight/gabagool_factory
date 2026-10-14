# Cold run 9289 -- the urban street on both sides: narrow mid-rises stand between the mission's buildings

**What it tested:** urban_row_001 (9288's brief unchanged) on Deli Counter 0.217.0 (b3c2354b). That release
adds three narrow mid-rises -- 12.30, 10.30 and 6.60 m wide as built -- for the 6.7 to 12.7 m rooms that
cold run 9288 left between the mission's buildings, where the six's narrowest is 15.3. On Level Factory
0.201.0 and Lot 0.121.0. Staged from cold run 9288.

**Result: 0 interventions (journal 0, unattributed files 0). The near side stands Empties, and the picked
candidate grades PASS 100.**

- **The near side:** seed_9003 a 12.3 m block between b0 and b1 and the 6.6 m at the east end; seed_9104
  and seed_9205 the 6.6 m at the west end. Across the street, 9 or 10 a candidate, all nine shells used,
  themed.
- **Not filled:** seed_9104's 6.70 m room between b1 and b2. Only the 6.6 m block fits it, and the bag had
  already dealt it once; the deal shows each design once before a new bag, so the room stayed open. A
  refinement for `infill`: deal a fresh bag when nothing left in the current one fits but a design would.
- **The grader:** seed_9104 picked at PASS 100 (9287 and 9288: PASS 90), enemy stuck 1, blocked 4, crew
  0; seed_9003 PASS 100. Findings 118 -> 108.
- **seed_9205 was never graded.** `LOT_ENEMY_SPAWN_UNPLACEABLE`: 6 of 6 enemy spawns found no open ground
  within 80 m of the route that is at least 8 m from the crew spawn and either beyond 45 m or behind a
  building from it. Laser Tag refused a map with no enemies (`LT_NOT_EVALUATED`, a blocker), and the
  picker passed over it. Split by elimination on the candidate's own site spec through Lot
  (`_scratch/2026-10-13_spawn_split/`):
  - as 9289: unplaceable;
  - without the one near-side Empty: placed, as in 9288;
  - without the nine across the street: placed.

  So it is the two together. 9288's enemies on this seed stood 25 m east of that near-side block, so how it
  starves the search is not traced. Enemy placement is the gameplay layer's and provisional.
- **The other new major** is `LOT_DESTINATION_ABOVE_FLOOR` on seed_9003 and seed_9205, roadmap 52's class.

## Seen and priced against 9285, the strip (`docs/findings/urban_street/ab_9289/`)

Same seed and same mission buildings; the far side a mid-rise wall and the near side two narrow blocks
where the strip had rowhomes across and plate between.

- `ab_sheet.png` holds the frames.
- **The harness refused its per-heading comparison** (`price_glow.py`: STATIONS DIFFER). The station
  `longest_sightline` is derived from the level's geometry, and the urban street moved it from (-51, 13.5)
  to (44.8, 15.5).
- **Over the 52 headings that stood in the same place** (`price_matched.py`, `price/price_matched.txt`):
  - draws -38.5 a heading on the mean (median -15.5; -290 to +202);
  - p95 -0.26 ms at the median, against a 0.12 ms spread between the two controls;
  - textures 76.0 -> 78.9 MiB, **buffers 47.9 -> 83.0 MiB, video 123.9 -> 161.9 MiB**.

  The same tool reads 9287's price as before: -71.6 draws, -0.15 ms.

## The time

    run    shell   art     export   walk   retire   the drive
    9288   100 s   159 s   177 s    10 s    3 s     7.5 min (451 s)
    9289   88 s    176 s   192 s    9 s     3 s     7.8 min (470 s)

The bake: 578 models and 224 primitive meshes lightmapped, 3,112 users.
