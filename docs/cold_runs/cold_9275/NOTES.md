# Cold run 9275 -- Laser Tag 0.30.0, a guard held by another bot is blocked, not stuck

**What it tested:** Laser Tag 0.30.0 in a real drive of restaurant_row_001 (roadmap 242;
`docs/findings/route_snag/README.md`, "Laser Tag 0.30.0"). As a held guard's 3 s window closes, the grader
now asks what this frame's move met: every contact but the floor another bot's body, and it records
EnemyBlocked, which NPC Pathing does not charge; any contact of the level, and EnemyStuck as before. A
blocked guard is handled as a stuck one, so the fights should play exactly as they did. Everything else as in
9274.

**Result: 0 interventions, 0 tool files changed.**

- seed_9104 was picked as before, and the three candidates graded PASS 90 as in 9274.
- **Findings 117 -> 117**, no issue id moved.
- The bake is 9274's to the count: 567 models and 224 primitive meshes lightmapped, 3,392 users.
- The graded lot is 9274's: seed_9104's staged `level.tscn` is byte-identical.

## What the grader says

The candidates' Laser Tag reports, 9274 (0.29.0) against 9275 (0.30.0):

    candidate    grade      enemy stuck    enemy blocked
    seed_9003    PASS 90    0 -> 0         0
    seed_9104    PASS 90    3 -> 0         3
    seed_9205    PASS 90    0 -> 0         0

**The control:** on all three, every summary field except the stuck count, its per-enemy rate and the new
blocked count reads the same. Every event except EnemyStuck and EnemyBlocked reads the same too: 1,331, 2,181
and 1,554 events, matched by kind, run and time. seed_9104's three EnemyBlocked are 9274's three
EnemyStuck: the same runs, times, guards and positions -- LT_Enemy_02 at (-2.05, 0.02, 12.24) in runs 10 and
15, and LT_Enemy_04 at (-2.75, 0.02, 12.24) in run 10. Those are the guards queued behind guards that
`docs/findings/stoop_breadth/enemy_stop_trace.py` traced.

**Moved in the report:** one line on seed_9104. "No enemy stuck events recorded." now passes; 9274's report
did not carry it. That line is the stuck count, read. The three events were under the score's 0.25-a-run line
in 9274, so no grade could move.

## The time

    run    shell   art     export   walk   retire   the drive
    9274   94 s    161 s   172 s    12 s    3 s     7.7 min (459 s)
    9275   96 s    164 s   175 s    11 s    4 s     7.8 min (468 s)

## What is evidence of what

- The grader: each candidate's `jobs/restaurant_row_001.laser_tag_evaluate.candidate.<seed>/1/out/lasertag.report.json`
  in `workspaces/cold-9275-ws/.level_factory/`, against 9274's.
- The count: `cold_run.py --end`.
- The breadth that priced the change before it shipped: `docs/findings/route_snag/blocked_breadth.out.txt`.
