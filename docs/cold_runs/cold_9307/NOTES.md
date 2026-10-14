# Cold run 9307 -- a prop is not the building, on a gas station and its rowhomes (Patina 0.31.0)

**What it tested:** Patina 0.31.0 (2279f04) on gas_block_001, whose gas station's forecourt -- its pad, canopy,
columns and pumps, all `prop` slots -- had stood as the building's face, and whose rowhome Empties had stood their
fronts on the stoop since cold run 9271 (roadmap 248; `docs/findings/patina_props/`). gas_block_001's brief as cold
run 9281 ran it (the breadth sweep of 2026-10-13), the pick automatic; the toolchain as 9305's. Staged from 9281,
whose workspace survives.

**Result: 0 interventions (journal 0, unattributed files 0). The gas station and every rowhome stand their dressing
on their own walls, and the three candidates grade exactly as 9281's.**

- **gas_station_a02** (each run's `patina_dressing` job, 9281 against 9307): its anchors from y -32.00..14.00 and
  x -23.00..23.00 -- out across the forecourt's pad and canopy -- to the building's +-11.15 and +-16.15, the
  replay's 0.31.0 figures for that shell (`docs/findings/patina_props/replay.out.txt`).
  - **In 9281 every coping strip, base course and curb it ordered stood off the building**: all 180 (64, 52, 64)
    past +-11.2 or +-16.2, on the canopy's and the pad's edges. The building itself carried none.
  - In 9307, none off it: coping 64, base courses 26, curbs 47 on the building, and 2 conduit runs, its walls now
    carrying exterior-light anchors (0 -> 2). Gutters (64) and downspouts (10), ordered off the slots, unchanged.
- **The twelve rowhome Empties:** front anchors from -7.61, the stoop's bottom tread, back to the walls at -6.15;
  gs_empty_rowhome_a ground edge 16 -> 18, roofline 25 -> 28, wall base 9 -> 10.
- **landmark_hall_a02 and rail_station_a01,** standing no prop past their walls, order as in 9281, kind for kind.
- **The pick: seed_9080, as 9281's.** seed_9080 PASS 100, seed_9181 PASS_WITH_TUNING 89 at route 0.96, seed_9282
  PASS 100, in both. Not compared field by field: a day of tool changes lies between them besides Patina.
- **Findings 105 -> 105.**
- **The light bake:** 547 models and 3,191 users.
- **Seen, not decided:** from the far side of the road and from 22 m up (`gas_street`, `gas_high`, shot on both
  packages), the frames differ only in the road's foreground, the lightmap's repack. The forecourt's change does
  not show from there at midnight; the orders are its evidence, and a walk is where it can be judged.
- **Not priced:** 9281's package is a day of other changes away; 9305's price is the dressing's.

## The time

    run    shell   art     export   walk   retire   the drive
    9307   116 s   160 s   176 s    12 s    4 s     8.1 min (483 s)
