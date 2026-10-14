# Cold run 9295 -- the corner shop: the urban wall opens and closes on a lit shop (Zoo 1.107.0, Deli Counter 0.218.0, Level Factory 0.206.0)

**What it tested:** urban_row_001 (9294's brief unchanged) on the corner shop's first three steps (the factory
root's `docs/proposals/CORNER_SHOP.md`):
- Zoo 1.107.0 (fbbe818) paints a shop's window from its own atlas;
- Deli Counter 0.218.0 (173c91b5) builds four corner blocks, `gs_cornershop_a` to `_d`, mid-rises whose
  ground-floor front is a deli, a bar, a laundromat or a grocery;
- Level Factory 0.206.0 (e8bd89b) opens and closes each run of the urban wall on one.

**seed_9104 named** against 9294's. Lot 0.123.0, Laser Tag 0.32.0. Staged from cold run 9294.

**Result: 0 interventions (journal 0, unattributed files 0). Every candidate's wall opens and closes on a corner
shop; the pick held; the fights barely moved.**

- **The corners** (`docs/findings/urban_street/corner_stations.py`, reading each candidate's site spec). On
  urban_row_001 no road crosses the far side, so the wall is one run and its corners stand at the plate's ends:

      seed     west corner                      east corner                      east end left open
      9003     gs_cornershop_d, the grocery     gs_cornershop_b, the bar         12.70 m  (9294: 3.70)
      9104     gs_cornershop_c, the laundromat  gs_cornershop_d, the grocery      1.20 m  (9294: 1.20)
      9205     gs_cornershop_b, the bar         gs_cornershop_d, the grocery      4.70 m  (9294: 3.20)

- **seed_9003's wall stops 12.70 m short of the plate's working end,** after its closing corner, where 9294's
  stopped 3.70 m short. So that corner does not stand at the corner.
  - **Traced** (`patches/lf_corner_fill/replay_9003.py`, `replay_9003.out.txt`). Its replay stands the run's wall
    block for block. The fill stopped at x 55.50 with 18.70 m to fill before the closing corner's room, and
    the one block left on the bag was `gs_midrise_f`, at 19.8 m. 0.206.0's `_cornered` stops when nothing LEFT
    ON THE BAG fits, the condition `infill` answered in 0.203.0 with a fresh deal.
  - **Fixed in Level Factory 0.206.1 (c189baf),** measured before it was written (`measure_remainder.py`, 600
    walls at the thirteen built widths). The shortfall's median went 4.70 -> 0.60 m and its worst 14.20 ->
    4.10. Walls more than the narrowest design's 6.6 m short went 171 -> 0.
  - **Replayed on this run's candidates** (`replay_candidates.py`): seed_9003 12.70 -> 1.90 m, seed_9205
    4.70 -> 2.60. seed_9104, the pick, stands as it stood, so this package is the one 0.206.1 makes. Cold run
    9296 proves it.
- **The chain held from the slot to the module.** Zoo built
  `window_delco_1997_01_w240_mbrick_brown_pshop_laundry_oab7522.glb` for the laundromat; its materials are
  `M_Shop_pane_Face` and the brick, its images `shop_pane_albedo` and `shop_pane_emission`.
- **The pick held: seed_9104 at PASS 100,** every grade as 9294's.

      seed 9003: 0 major (not counted: LOT_DESTINATION_ABOVE_FLOOR, LT_MAP_TRIVIAL_ENCOUNTER), route completion 1.00, grade PASS_WITH_TUNING 89
      seed 9104: 0 major, route completion 1.00, grade PASS 100
      seed 9205: 0 major (not counted: LOT_DESTINATION_ABOVE_FLOOR), route completion 1.00, grade PASS 90

- **The fights barely moved** (`docs/findings/urban_street/fight_fields_9295.out.txt`). Every spawn stood at
  9294's transform, under the same evaluation seed.
  - seed_9205 read 9294 exactly.
  - seed_9003 moved one field, survival_max +0.07 s.
  - seed_9104 moved 11 of 32 by a little: shots blocked 501 -> 513, mean engagement distance 14.91 -> 15.38 m,
    crew deaths unchanged.
  - The wall across the street was re-dealt between its corners, and the fights are on the near side.
- **Findings 109 -> 109.**
- **The package carries all four corner blocks; seed_9104 stands two** (c and d). It also carries
  `gs_midrise_g`, which seed_9104 stands nowhere: the package has always carried every Empty the brief was themed
  with.
  - 194 -> 210 MB.
  - The light bake's model imports went 581 -> 707. Lightmap users went only 3,143 -> 3,145.
  - Two scenes nothing instances draw nothing. Their cost is disk and import time, recorded and not fixed here.

## The time

    run    shell   art     export   walk   retire   the drive
    9294   114 s   192 s   220 s    12 s   19 s     9.6 min (576 s)
    9295   112 s   219 s   215 s    13 s   20 s    10.0 min (597 s)

- **The art leg is 27 s longer:** the four corner blocks' art jobs.
- **The light bake read 72.9 s in the editor,** against 91.9 s in 9294.

## Seen and priced against 9294

**Seen** (`docs/findings/urban_street/ab_9295/`, 9294 left, 9295 right):
- **`corner_sheet.png`** is shot from the near sidewalk's centre line straight across at each corner
  (`corner_stations.py`'s stations, from seed_9104's spec), where 9294 stood a mid-rise.
  - **The laundromat** (`gs_cornershop_c`, the west end) shows three lit storefronts with the white shop door
    between them. The washers' round dark doors read in the glass.
  - **The grocery** (`gs_cornershop_d`, the east end) shows four, aisles of goods behind the glass, and a dark
    iron door.
  - Both are the brightest thing in their frames. Both cool rooms glow nearly white at the material's
    `EMISSION` 2.2.
- **`ab_sheet.png`** is the standard sheet: two street-end stations, the spawn, the objective and four elevations.

**Priced** (`ab_9295/price/price.txt`; 53 headings at 14 stations, control-subject-control):
- draws -4.0 a heading on the mean (-21 to +7), against the controls' 0.0;
- p95 +0.06 ms at the median, against a 0.11 ms floor;
- memory: textures 78.9 -> 79.6, buffers 68.4 -> 71.8, video 147.2 -> 151.4 MiB.

The corner shops cost no draw and no light: their glow is the shop atlas's emission paint. The comps' own table
(`docs/reference/URBAN_MIDRISE_COMPS.md`) names Lux for "the shop's light". A spill onto the pavement would be a
light, the expensive version, not priced here.
