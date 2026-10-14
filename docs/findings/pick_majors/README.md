# What a pick counts: the majors that decide a candidate (Level Factory 0.202.0)

**The question.** On 2026-10-13 the walker shared a QA proof-of-concept on navigation and combat and asked
whether it helps make Laser Tag good enough to use in the factory. The first step that came out of it was a
choice: which finding types should stop counting as majors when a candidate is picked. The walker left that
call to the factory "for the moment", and this folder is the measurement it was made on.

**The instrument.** `major_census.py` reads what the cold driver's picker reads, over every
`workspaces/cold-*-ws` on this disk:
- each workspace mission's validation issues;
- each candidate's newest walk test;
- each candidate's newest Laser Tag report.

That covers 62 workspace missions and 186 candidates (`major_census.out.txt`). Its copy of the picker's rule
picks what the real picker (`tools/cold_drive/pick_candidate.py` as of c868b5b) picked on all 62.

## What it found

**1. The majors on the candidates** (section 1 of the output):

    LOT_DESTINATION_ABOVE_FLOOR     96 candidates in 53 missions   Lot
    LT_MAP_NO_REACTION_TIME         19 candidates in 15 missions   Laser Tag
    WALKTEST_ANCHOR_ISOLATED         8 candidates in  3 missions   walk test
    LT_MAP_TRIVIAL_ENCOUNTER         2                             Laser Tag
    LT_ROUTE_NEVER_COMPLETED         2                             Laser Tag
    LT_MAP_TRAVERSAL                 2                             Laser Tag
    six more codes, one candidate each

**2. One code chose the picks, and it is not Laser Tag's** (section 2).
- **LOT_DESTINATION_ABOVE_FLOOR:** not counting it alone moves 28 of the 62 picks.
- **LT_MAP_NO_REACTION_TIME:** moves one, cold run 9283.
- **Every other code:** moves none.

**3. LOT_DESTINATION_ABOVE_FLOOR is a doubt the walk test answers.**
- **What Lot means by it.** Lot raises it for a mission point standing more than `FURNITURE_MAX` above the
  ground plane, because it cannot tell offline whether that height is a storey a stair reaches
  (`site_spawns.seat_destinations`).
- **What its message claims.** Laser Tag "cannot path to it either way and reports TRAVERSAL with 0%
  completion".
- **What it is on this disk.** All 96 are the objective, at 3.3, 3.6, 3.8 or 4.0 m: a storey.
- **What the walk test reads.** Its crew walkers go to every heist anchor, the objective at its room's floor
  among them (Lot's `_navqa_anchors`).

Of the 96:
- **95:** the walk test walked every leg. Every crew walker read exactly "ok", every target was reached, and
  no leg was credited as a ladder (`nav_qa_director._set_leg` credits one without walking it, and its own
  `ok` passes that).
  - **93** of those: Laser Tag's crew completed the route in at least one run.
  - **The other two:**
    - cold run 9180's warehouse_yard_001 seed_9004, which Laser Tag graded BROKEN 7 at 0% (not
      attributed);
    - cold run 9289's seed_9205, never evaluated (its enemy spawns were unplaceable).
- **1:** the walk test was not ok: cold run 9185's seed_9003. That is the doubt being right.
  - **The objective was stranded.** b0's apartment_hideout objective, 3.3 m up, stood on a navmesh island
    the main network does not reach. The walk test's proof to it stopped 60.99 m short ("disjoint
    islands").
  - **Its walkers had credited that leg as a ladder.** That is exactly why "walked every leg" is stricter
    than `ok`.
  - **The new rule counts the doubt there, and the candidate is out anyway.**
  - **Laser Tag's crew "completed" that route in every run** (see Found, below).

On the 95 the walk test walked, the consequence the message names held on none, unless it held on the 9180
case. Laser Tag's completion is the weaker instrument of the two, which is why the rule reads the walk test.

**Counted, it chose 28 picks.** Against the candidate picked without it, the old pick was lower on route
completion or score on 12, equal on 16, and higher on none (section 5).
- Cold runs 9263 to 9265 took restaurant_row_001's seed_9104, at 0.72 completion and PASS_WITH_TUNING 78,
  over seed_9205 at 1.00 and PASS 90.
- 9222 to 9237 took PASS_WITH_TUNING 75 to 80 over PASS 90.

It is not a preference anybody chose. It is the old rule preferring a ground-floor objective by accident.

**4. Laser Tag's verdicts on the fight bracket each other, and decide nothing.** Cold run 9283's three
candidates carried one major each:
- NO_REACTION_TIME on seed_9061 (crew survival 6.44 s) and seed_9162 (7.80 s);
- TRIVIAL_ENCOUNTER on seed_9263 (the crew lost nobody).

Those are opposite verdicts on one fight. Not counting NO_REACTION_TIME alone moves the pick to the 77,
because the trivial encounter still counts. Not counting the five fight verdicts together moves none of the
62 picks, whether or not LOT_DESTINATION_ABOVE_FLOOR is answered.

**5. TRAVERSAL is the one ambiguous code** (section 4). On its two candidates (9180's warehouse_yard_001
seed_9105 and 9282's bank_block_001 seed_9256), no run ended on the clock, and 20 and 21 of 25 ended in a
wipe: the crew died before walking half the route. Both times that is a fight outcome. But a crew the
geometry holds reads the same way, so it stays counted.

## The call, shipped in Level Factory 0.202.0

`level_factory/packages/pipeline/pick.py` keeps its out rule:
- the walk test not ok;
- LT_ROUTE_NEVER_COMPLETED;
- ENEMY_PATHING_BROKEN.

Among the rest it takes the fewest major findings, then the highest route completion, then the higher Laser
Tag score (the walker's "ties should go to the higher grade"), then the lowest seed. Two kinds of major are
shown on each candidate's line as "not counted":

- **`ADVISORY`**, Laser Tag's five verdicts on the fight its bots played: TRIVIAL_ENCOUNTER,
  NO_REACTION_TIME, LT_NO_SURVIVABLE_OPENING, NO_ENGAGEMENT and NO_CONTACT. They still reach the pick
  through the score.
- **`ANSWERED_BY_WALK`**: LOT_DESTINATION_ABOVE_FLOOR, where the walk test walked every leg
  (`walked_every_leg`).

**Why this line.** It is the one `lasertag_report` already draws for blocking: "What blocks here should be what
our tools ARE authoritative on -- navmesh, collision, reachability -- not what a firefight did afterwards."
And the fight moves when the level does not. Laser Tag 0.31.0 changed only how its guards walk; its control
read 0.30.0 exactly on all 16 lots (`docs/findings/route_snag/guard_steer_breadth.out.txt`). Yet on
gas_block_001 seed_9181, with the level unchanged:
- crew survival went from 9.51 to 18.88 s;
- route completion went from 0.88 to 0.80;
- wipes went from 3 to 4.

**One spelling.** `tools/cold_drive/pick_candidate.py` now reads the tool's module and spells none of the rule
(`patches/patch_pick_candidate_reads_lf.py`). For a day it had been a second copy: the grade tie-break went
into it and not into `level-factory pick`.

## Proven

- **The shipped code agrees with the census.** `pick_replay.out.txt` runs `breadth_sweep_2026-10-13/pick_replay.py`
  as the driver runs a picker, the old copy against the new one: 62 workspace missions, 28 picks differ. They
  are the same 28 the census predicted, each to the same seed.
- **The test can fail.** `level_factory/tests/unit/test_pick_counts.py` has 6 checks, and 5 fail on 0.201.0.

## What it changes

On these workspaces the new rule picks a different seed in 28 of 62 missions, in three missions only:
- restaurant_row_001: 23 of its 42 runs, every run since 9263 among them;
- urban_row_001: all 3;
- club_block_014: 2 of 4.

Any A/B against a run before 0.202.0 must name its seed: `cold_drive.sh N PREV mission 9104`, not `auto`.
`urban_street/ab_record.sh` compares two runs' packages and was sound because both had picked seed_9104.

## Found, not fixed: Laser Tag counts the end of a short path as arriving

**The measurement.** Cold run 9185's restaurant_row_001 seed_9003 read route completion 1.00 in Laser Tag,
every run. On the same candidate, the walk test's path to the objective stopped 60.99 m short of it, on a
disjoint navmesh island 3.3 m up.

**The reading** (consistent with that measurement, not traced in a run).
`LT_BotPlayerController` advances its route, and counts an arrival, when `_nav_finished()` is true. That is
`NavigationAgent3D.is_navigation_finished()`, which Godot sets at the end of the path the navigation server
returned. For a target the network does not reach, that is the closest point it does reach. Godot's question
"is the agent at the target" is `is_target_reached()`, and Laser Tag does not ask it.

**What follows.**
- A route point no body can stand at can read as reached.
- So Laser Tag's route completion is not a proof of reachability; the walk test's path proofs are.
- It is Laser Tag's to fix, and it is queued.

## Not proven

- **Whether an upstairs or a ground-floor objective makes the better level.** The old rule preferred ground
  floors by accident; the new one prefers neither. Sixteen of the moves are ties that now go to the lower
  seed: a different level, with no measured difference between the two.
- **The 9180 seed_9004 case:** Laser Tag BROKEN 7 at 0% on a candidate the walk test walked. Not attributed.
- **Whether Lot's finding should be major at all.** Its message's consequence is refuted here on 93 of 96.
  But Lot raises it before the walk test exists, so only a later stage can answer it. Its severity and
  message are Lot's, and roadmap 52's question; left.
- **The Laser Tag findings never seen as majors here stay counted by reading, not measurement:** MISSING_*,
  SPAWN_IN_COLLISION, UNREACHABLE_*, NO_WORLD_COLLISION, AIM_POINT_ABOVE_BODY.
- **The proof-of-concept's later steps are queued, not started:**
  - planted-defect fixtures scored for precision and recall;
  - findings attributed to the element that caused them;
  - a four-player congestion check, static first.
