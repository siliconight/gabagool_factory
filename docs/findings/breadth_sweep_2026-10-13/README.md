# The breadth sweep, 2026-10-13: seven missions, seven zeros

**Why.** Every cold run since 9264 has built restaurant_row_001. Since each other mission last ran cold --
from cold run 9169 (video_block_001) to 9246 (deli_001) -- the factory has shipped:

- the stoops and railings (Deli Counter 0.211.0-0.212.0, Zoo 1.105.0);
- the tar roofs (Deli Counter 0.210.0);
- the reflection atlas sized to the package (Level Factory 0.198.0);
- the price's memory (Level Factory 0.199.0);
- four grader releases (Laser Tag 0.28.0-0.31.0);
- the mid-rise family (Deli Counter 0.213.0).

None of it had been through a cold run on another mission. The zeros on one level are one level's zeros
-- the 2026-10-06 sweep's reason (`docs/findings/breadth_sweep_2026-10-06/`).

**How.** `tools/cold_drive/sweep_one.sh`, one cold run a call, each mission staged from its own last cold
run, the seed picked by the driver (`tools/cold_drive/pick_candidate.py`). The plan was the seven missions
longest without one: video_block_001, precinct_yard_001, convenience_001, gas_block_001, bank_block_001,
card_block_001 and club_block_014. `sweep_table.py` reads each run's row off its driver log and its picked
candidate's Laser Tag report. Every run on Level Factory 0.199.0, Deli Counter 0.213.0, Laser Tag 0.31.0.

## The result

    run=9278  mission=video_block_001    from=9169  interventions=0  seed=seed_9080  grade=PASS 90
              stuck=enemy 0, blocked 0, crew 0   findings=66 / 96   bake_users=2161  drive=8.5 min
    run=9279  mission=precinct_yard_001  from=9172  interventions=0  seed=seed_9001  grade=PASS 90
              stuck=enemy 1, blocked 27, crew 0  findings=77 / 107  bake_users=2994  drive=8.3 min
    run=9280  mission=convenience_001    from=9181  interventions=0  seed=seed_9181  grade=PASS 100
              stuck=enemy 2, blocked 22, crew 0  findings=54 / 78   bake_users=577   drive=3.8 min
    run=9281  mission=gas_block_001      from=9196  interventions=0  seed=seed_9080  grade=PASS 100
              stuck=enemy 1, blocked 3, crew 0   findings=70 / 105  bake_users=3191  drive=8.6 min
    run=9282  mission=bank_block_001     from=9215  interventions=0  seed=seed_9054  grade=PASS 90
              stuck=enemy 0, blocked 0, crew 0   findings=74 / 102  bake_users=3057  drive=8.9 min
    run=9283  mission=card_block_001     from=9216  interventions=0  seed=seed_9061  grade=PASS_WITH_TUNING 77
              stuck=enemy 24, blocked 0, crew 0  findings=74 / 109  bake_users=2746  drive=8.7 min
    run=9284  mission=club_block_014     from=9221  interventions=0  seed=seed_9181  grade=PASS_WITH_TUNING 79
              stuck=enemy 1, blocked 0, crew 4   findings=72 / 100  bake_users=3129  drive=8.1 min

**7 of 7 at 0 interventions** (journal 0, unattributed files 0 on every run), each DONE, each on its own
mission's last cold run's batch. Five picked candidates PASS at 90 or 100.

## The two under PASS, attributed

Each report's own categories, out of 100 (combat pacing, cover, NPC pathing, sightlines, traversal):

- **card_block_001, 77.** Sightlines 10 of 20: 40% of walkable positions visible to 3+ enemy spawns.
  Pacing 5: average survival 6.4 s, `LT_MAP_NO_REACTION_TIME`. NPC pathing 17 of 20: 24 enemy stuck
  events in 25 runs is 0.96 a run, past `LT_ScoreCalculator._score_pathing`'s 0.25, which then takes
  `round(20 x 0.16)` = 3 for 0.16 per enemy per run. Traversal and cover full.
- **club_block_014, 79.** Traversal 14 of 25: the crew walked 96% of the route and finished 88% of runs,
  stuck 4 times. Pacing 5: first fire at 2.7 s, `INSTANT_CONTACT`. The rest full.

## What the picker chose

Every candidate the two runs graded (`lasertag.report.json` of each `laser_tag_evaluate` job):

    9283 card_block_001   seed_9061  PASS_WITH_TUNING 77  1 major (NO_REACTION_TIME)        completion 1.00  PICKED
                          seed_9162  PASS_WITH_TUNING 84  1 major (NO_REACTION_TIME)        completion 0.96
                          seed_9263  PASS_WITH_TUNING 89  1 major (TRIVIAL_ENCOUNTER)       completion 1.00
    9284 club_block_014   seed_9080  WARN 73              1 major (NO_REACTION_TIME)        completion 0.88
                          seed_9181  PASS_WITH_TUNING 79  0 major                           completion 0.88  PICKED
                          seed_9282  PASS 90              1 major (LOT_DESTINATION_ABOVE_FLOOR)  completion 1.00

`pick_candidate.py` takes the fewest major findings, then the highest route completion, then the lowest
seed. It reads no score. In 9283 the three tied on one major each, seed_9061 and seed_9263 tied on
completion, and the lower seed won -- 12 points under the best-graded candidate, whose one major is that
nobody on the crew died in 25 runs (item 212's `TRIVIAL_ENCOUNTER`; "nothing here was tested under
pressure"). In 9284 the PASS 90 was held out by its major, an objective marker 3.60 m above the site's
ground plane (`LOT_DESTINATION_ABOVE_FLOOR`, roadmap 52's class; Laser Tag still finished it 100%).

Both picks follow the rule as written. Whether a tie should go to the higher score before the lower seed,
and whether `TRIVIAL_ENCOUNTER` should count as a major against a candidate at all, are questions about the
picker, not about these levels -- measured here, not changed.

**The walker's answer, 2026-10-13: "yes, ties should go to the higher grade."**
`patches/patch_pick_candidate_grade.py` changes the sort key to fewest majors, then completion, then the
report's `overall_score`, then the seed. Laser Tag's grade is a pure function of that score, and the
trivial-encounter cap lowers the score itself. A report without a score sorts last among its ties and
says so.

`pick_replay.py` ran the picker before and after on every cold workspace on this disk
(`pick_replay.out.txt`): 59 workspace missions, 3 picks changed, each to a higher grade:

    cold-9246-ws  deli_001            seed_9191 WARN 68              -> seed_9292 PASS_WITH_TUNING 80
    cold-9279-ws  precinct_yard_001   seed_9001 PASS 90              -> seed_9203 PASS 100
    cold-9283-ws  card_block_001      seed_9061 PASS_WITH_TUNING 77  -> seed_9263 PASS_WITH_TUNING 89

9284's pick does not move: its PASS 90 carries a major (`LOT_DESTINATION_ABOVE_FLOOR`), so it is not a
tie. Majors still come first. `TRIVIAL_ENCOUNTER` counting as a major was not asked, and is unchanged.

## The pause, and the clean

The sweep paused after 9278: `sweep_one.sh` refuses a run below 8 GB free on C:, the rule since cold run
9163 died on a full disk, and after 9278 C: had 4.3 GB. `tools/factory_retire.py` found nothing
retirable -- every cold workspace was among the newest it keeps or was named by a record. The largest
things no rule retires were Godot's shader and Vulkan caches and `_scratch/`.

With the walker's yes (2026-10-13, "approved, do a clean safely"), the caches and the unneeded scratch went,
old draft clones after their diffs were archived (`_scratch/archive/clone_diffs_2026-10-13`), keeping every
scratch item a record names: 7.15 GB freed, C: at 11.45 GB. The sweep resumed at 9279. After 9284 C: had
8.2 GB free -- one more run inside the floor.
