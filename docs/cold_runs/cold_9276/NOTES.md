# Cold run 9276 -- Laser Tag 0.31.0, the guards walk as the crew does

**What it tested:** Laser Tag 0.31.0 in a real drive of restaurant_row_001 (roadmap 242;
`docs/findings/route_snag/README.md`, "Laser Tag 0.31.0"). The crew bot's keep-to-the-mesh and step-up
move into `LT_Steering`, and the guards now call them: each step kept on the mesh the guard plans on, and a
step-up after the slide to the scenario's `player_max_step_up_m` (0.5). Unlike 0.30.0, this one moves the
guards, so it moves the fights. Everything else as in 9275.

**Result: 0 interventions, 0 tool files changed.**

- seed_9104 was picked as before.
- **Findings 117 -> 117**, no issue id moved.
- The bake is 9275's to the count: 567 models and 224 primitive meshes lightmapped, 3,392 users.
- The graded lot is 9275's: seed_9104's staged `level.tscn` is byte-identical.

## What the grader says

The candidates' Laser Tag reports, 9275 (0.30.0) against 9276 (0.31.0):

    candidate    grade      route    enemy stuck   enemy blocked   crew deaths   mean crew survival
    seed_9003    PASS 90    1.00     0 -> 0        0 -> 0           7 -> 6       50.30 -> 52.90 s
    seed_9104    PASS 90    1.00     0 -> 0        3 -> 6          30 -> 28      16.49 -> 23.16 s
    seed_9205    PASS 90    1.00     0 -> 0        0 -> 0           2 -> 3       64.42 -> 61.93 s

The grades, routes and stuck counts hold. The fights moved on all three: shots, hits, engagement distance
and survival. As the 16-lot breadth measured, a guard that keeps to the mesh takes corners differently and
meets the crew elsewhere. In the reports, the only findings that changed are the share of shots the world
blocked, 27 -> 28 %, 53 -> 55 % and 32 -> 33 %. seed_9104's guards are held by one another 6 times where
9275's were 3. That count is reported and not scored.

The control for this change is the breadth's, not this run's: 0.31.0 with the guards' steering switched
off read 0.30.0 exactly on all 16 lots (`docs/findings/route_snag/guard_steer_breadth.out.txt`). This run
shows the release in the pipeline: staged, imported (its new `LT_Steering` class registered by the
staging's import pass), graded and picked as before.

## The time

    run    shell   art     export   walk   retire   the drive
    9275   96 s    164 s   175 s    11 s    4 s     7.8 min (468 s)
    9276   97 s    162 s   174 s    11 s    4 s     7.8 min (465 s)

## What is evidence of what

- The grader: each candidate's `jobs/restaurant_row_001.laser_tag_evaluate.candidate.<seed>/1/out/lasertag.report.json`
  in `workspaces/cold-9276-ws/.level_factory/`, against 9275's.
- The count: `cold_run.py --end`.
