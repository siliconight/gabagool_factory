# Cold run 9297 -- the corner shop's awning (Zoo 1.108.0, Deli Counter 0.219.0)

**What it tested:** urban_row_001 (9296's brief unchanged) on:
- Zoo 1.108.0 (b028d3d), which draws `shop_awning`: a canvas shed with a 10 in valance and closed ends, in four
  colours as the form;
- Deli Counter 0.219.0 (42fe102a), which hangs one over each corner block's storefront in its shop's colour.

**seed_9104 named** against 9296's. Level Factory 0.206.1, Lot 0.123.0, Laser Tag 0.32.0. Staged from cold run 9296.

**Result: 0 interventions (journal 0, unattributed files 0). Both standing corners hang their awning, and nothing
the graders read moved.**

- **The awnings reach the package.**
  - The art leg built `prop_shop_awning_delco_1997_04_w1140_d120_h85_fshed_navy.glb` for the laundromat
    (`gs_cornershop_c`).
  - The package's `lot/gs_cornershop_c/site.tscn` and `lot/gs_cornershop_d/site.tscn` each instance one
    `shop_awning` node.
- **The light bake took them in:** 711 model imports against 9296's 707 (the four corner blocks' awning
  modules), and 3,147 lightmap users against 3,145 (the two standing).
- **The pick held: seed_9104 at PASS 100,** every grade as 9296's.

      seed 9003: 0 major (not counted: LOT_DESTINATION_ABOVE_FLOOR, LT_MAP_TRIVIAL_ENCOUNTER), route completion 1.00, grade PASS_WITH_TUNING 89
      seed 9104: 0 major, route completion 1.00, grade PASS 100
      seed 9205: 0 major (not counted: LOT_DESTINATION_ABOVE_FLOOR), route completion 1.00, grade PASS 90

- **No fight moved** (`docs/findings/urban_street/fight_fields_9297.out.txt`). 0 of 32 summary fields moved on
  any candidate, and every spawn stood at 9296's transform. The awning has no collider, and Laser Tag's shots and
  sightlines read collision.
- **Findings 109 -> 109.**

## The time

    run    shell   art     export   walk   retire   the drive
    9296   111 s   212 s   210 s    12 s   19 s     9.75 min (585 s)
    9297   111 s   218 s   215 s    13 s   19 s     9.9 min (593 s)

The light bake read 70.4 s in the editor, against 75.7 s in 9296.

## Seen and priced against 9296

**Seen** (`docs/findings/urban_street/ab_9297/corner_sheet.png`, 9296 left, 9297 right, from `corner_stations.py`'s
stations; `awning_zoom.png`, the grocery's storefront at twice the size, 9296 above, 9297 below):
- **The awning is there:** a band of dark green canvas over the grocery's four lit windows, and navy over the
  laundromat's.
- **At night it barely reads.** The canvas is unlit -- the shop's glow is paint, which casts no light -- and the
  dark colours go nearly black. The comps' awning is lit from under it by the shop.
- **For the walker:** brighter canvas, or the shop casting light on it (a Lux light, the expensive version, not
  priced here). The street-end stations show no difference at 30-40 m.

**Priced** (`ab_9297/price/price.txt`, and `price_rerun/price.txt` on the same copies):
- **Draws: +0.7 a heading on the mean (-1 to +2), the same in both runs** -- the two awnings where they are in
  view.
- **Frame time and memory: not priced.**
  - StarCraft II (`SC2_x64`, 2.95 GB, 558 CPU seconds) was running on the machine when it was checked after the
    second run. The first run's controls were already that unsteady.
  - The two controls, one package measured twice, disagreed with themselves: p95 medians 3.25 against 3.73 ms,
    then 4.04 against 5.14 ms, and buffers 71.8 against 67.8 MiB, then 67.8 against 71.8.
  - Today's earlier prices had floors of 0.04 to 0.11 ms. A number whose control moves that much measures the
    machine, not the change.
  - To price again when the machine is quiet.
