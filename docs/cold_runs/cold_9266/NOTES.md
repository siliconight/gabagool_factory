# Cold run 9266 -- a bot standing to fight is not stuck, in a real drive

**What it tested:** Laser Tag 0.28.0 in a real drive of restaurant_row_001: a frame on which a crew
bot stands to fight restarts its stuck window, so a bot that fought all window is no longer counted
stuck -- 10 traversal points and a skipped route point each (roadmap 242,
`docs/findings/route_snag/`, "The stuck detector counts fights"). Lux 0.76.1 changes only a comment.
Everything else as in 9265.

**Result: 0 interventions, 0 tool files changed.** seed_9104 picked as in 9241 to 9265, the only
candidate without a major finding (seed_9003 and seed_9205 each carry Lot's
LOT_DESTINATION_ABOVE_FLOOR, as before) -- and now at route completion 1.00 where 9265 read 0.72.
Findings 119 -> 118: LT_MAP_PLAYER_STUCK 2 -> 1.

## What Laser Tag said, candidate by candidate

The jobs' own reports (`jobs/restaurant_row_001.laser_tag_evaluate.candidate.seed_N/out/`), 9265's
under 0.27.0 against this run's under 0.28.0, Godot Physics:

    candidate  9265 (0.27.0)                                 9266 (0.28.0)
    seed_9003  PASS_WITH_TUNING 80, route 0.96, stuck  3     PASS 90, route 1.00, stuck  0
    seed_9104  PASS_WITH_TUNING 78, route 0.72, stuck 72     PASS_WITH_TUNING 80, route 1.00, stuck 74
    seed_9205  PASS 90, route 1.00, stuck 0                  PASS 90, route 1.00, stuck 0

seed_9003's PLAYER_STUCK finding is gone: all three of its events were bots standing to fight
(`why_breadth.out.txt`). seed_9104 walks its whole route -- the false events had been skipping its
crew past route points -- and keeps its 74 events, all the one real pin at the deli register counter's
corner (`pin_trace.py census`), the pin Laser Tag's held keep-on-mesh draft (0.29.0) is for. Each row
is the one the 16-lot breadth measured for this lot (`engine_breadth_fight.out.txt`), in the
generator's own drive.

## As built

The export as in 9265 -- 497 models and 224 primitive meshes lightmapped, 3,338 users -- the bake
28.9 s and its editor 55.8 s (9265: 32.7 s and 60.9 s, which its notes had put on the baked sun's
shadows; retracted there).

## The time

    run    shell   art     export   walk   retire   the drive
    9265   88 s    200 s   181 s    12 s   18 s     8.7 min (524 s)
    9266   84 s    182 s   166 s    12 s   19 s     8.0 min (480 s)

The retire step removed one workspace (0.9 GB).

## What is evidence of what

- The grades: the three jobs' `lasertag.report.json` in this run's workspace and 9265's.
- The pick and the findings: `driver.log`; the count: `cold_run.py --end`.
- The breadth these rows repeat: `docs/findings/route_snag/engine_breadth_fight.out.txt`.
