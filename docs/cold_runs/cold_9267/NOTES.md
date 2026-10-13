# Cold run 9267 -- the crew keeps to the mesh, and an arrival is not stuck, in a real drive

**What it tested:** Laser Tag 0.28.1 and 0.29.0 in a real drive of restaurant_row_001 (roadmap 242,
`docs/findings/route_snag/`): a crew bot that reaches a route point or cover restarts its stuck window,
so a round trip inside one window is no longer counted stuck (0.28.1); and the bot keeps to the navmesh
it plans on rather than cutting corners into the bake's clearance, where it was pinned at the deli
register counter (0.29.0). Everything else as in 9266.

**Result: 0 interventions, 0 tool files changed.** seed_9104 picked as in 9241 to 9266, the only
candidate without a major finding (seed_9003 and seed_9205 each carry Lot's LOT_DESTINATION_ABOVE_FLOOR).
Findings 118 -> 117: LT_MAP_PLAYER_STUCK 1 -> 0, the last of them.

## What Laser Tag said, candidate by candidate

The jobs' own reports, Godot Physics, across the three runs that carried the day's Laser Tag releases:

    candidate  9265 (0.27.0)                    9266 (0.28.0)                    9267 (0.29.0)
    seed_9003  PWT 80, route 0.96, stuck  3     PASS 90, route 1.00, stuck  0    PASS 90, route 1.00, stuck 0
    seed_9104  PWT 78, route 0.72, stuck 72     PWT 80, route 1.00, stuck 74     PASS 90, route 1.00, stuck 0
    seed_9205  PASS 90, route 1.00, stuck 0     PASS 90, route 1.00, stuck  0    PASS 90, route 1.00, stuck 0
    (PWT: PASS_WITH_TUNING)

seed_9104's 74 events in 9266 were the one real pin at the deli counter; 0.29.0 keeps the crew off the
counter's corner and none remain. Each row is the one the 16-lot breadth measured for this lot
(`engine_breadth_029.out.txt`), in the generator's own drive. The lot cold run 9263 built -- one of
the three whose route swung with the street furniture, 0.72 under 0.27.0 -- reads PASS 90, route 1.00,
no stuck event under 0.29.0 (`pin_9263_029.out.txt`); 9261's and 9262's lots were retired.

## As built

The export as in 9265 and 9266 -- 497 models and 224 primitive meshes lightmapped, 3,338 users -- the
bake 30.1 s and its editor 60.3 s.

## The time

    run    shell   art     export   walk   retire   the drive
    9266   84 s    182 s   166 s    12 s   19 s     8.0 min (480 s)
    9267   93 s    158 s   167 s    10 s    4 s     7.5 min (449 s)

The retire step removed nothing.

## What is evidence of what

- The grades: the three jobs' `lasertag.report.json` in this run's workspace, 9266's and 9265's.
- The pick and the findings: `driver.log`; the count: `cold_run.py --end`.
- The breadth these rows repeat: `docs/findings/route_snag/engine_breadth_029.out.txt`.
