# Cold run 9306 -- a prop is not the building, on a strip: the rowhomes' fronts (Patina 0.31.0)

**What it tested:** Patina 0.31.0 (2279f04) on a strip brief, whose rowhome Empties had stood their front dressing
on the stoop's greybox boxes since Deli Counter 0.211.0 (cold run 9271; roadmap 248, `docs/findings/patina_props/`).
restaurant_row_001's brief as 9293 ran it, the pick automatic; the toolchain as 9305's (Level Factory 0.209.0, Zoo
1.110.0, Deli Counter 0.220.0, Lux 0.77.0, Lot 0.123.0, Laser Tag 0.32.0, Patina 0.31.0). Staged from cold run 9293,
the last restaurant_row_001 run, whose workspace is retired.

**Result: 0 interventions (journal 0, unattributed files 0). All twelve rowhome Empties stand their dressing on
their walls, and the three candidates grade as 9293's did.**

- **The rowhomes' anchors** (each `patina_dressing` job): every one within y +-6.15, the walls, where from 9271 to
  9302 each front had one of each kind at -7.61, the stoop's bottom tread. gs_empty_rowhome_a: ground edge 18,
  roofline 28, wall base 10 -- the replay's 0.31.0 counts for that shell exactly
  (`docs/findings/patina_props/replay.out.txt`).
- **The enterable buildings** (deli_a03, office, pharmacy_a01) are among the replay's 118 unchanged shells.
- **The pick: seed_9003, as 9293's.** All three candidates PASS 90 at route completion 1.00, as in 9293.
  - Not compared field by field: 9293's workspace is retired, and the tools have moved since it besides Patina
    (Lot 0.123.0's trees among them).
  - seed_9003 now carries two uncounted LOT_DESTINATION_ABOVE_FLOOR findings where 9293's notes show one. Not
    attributed here; Patina orders no destination.
- **Findings 112,** as 9293's. The driver's delta reads "0 -> 112" because the workspace it compares against is
  retired.
- **The light bake:** 564 models and 3,490 users.
- **Not priced:** no package from this toolchain without Patina 0.31.0 exists to price against. 9305's price is
  the dressing's: +2.0 draws a heading on the mean.

## The time

    run    shell   art     export   walk   retire   the drive
    9293   95 s    161 s   174 s    11 s    4 s     7.7 min (462 s)
    9306   97 s    172 s   178 s    12 s    4 s     8.0 min (478 s)
