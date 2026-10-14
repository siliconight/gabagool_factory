## [0.202.0] - What a pick counts: the grade breaks a tie, and two kinds of major are shown and not counted

**The walker, 2026-10-13**: "ties should go to the higher grade". Then they asked which finding types should
stop counting as majors when a candidate is picked, and left that call to the factory "for the moment". A
census decided it: the factory root's `docs/findings/pick_majors/major_census.py`, over the 62 cold
workspace missions on disk and their 186 candidates.

- **The grade breaks a tie** before the seed (`pick.pick`). It reads the report's score through
  `lasertag_report.report_score`; Laser Tag's grade is a pure function of the score. A report without a
  score sorts last among its ties.
  - The factory's copy of this rule (`tools/cold_drive/pick_candidate.py`) learned the tie-break on
    2026-10-13, and this file did not. For a day the cold runs and `level-factory pick` picked by two
    rules. That copy now reads this one.
- **Two kinds of major are shown and not counted** (`Candidate.not_counted`, on the candidate's line and
  in `pick --json`, beside `score` and `grade`):
  - **`ADVISORY`: Laser Tag's five verdicts on the fight its bots played.** These are TRIVIAL_ENCOUNTER,
    NO_REACTION_TIME, LT_NO_SURVIVABLE_OPENING, NO_ENGAGEMENT and NO_CONTACT.
    - **They are not verdicts on the level.** Its bots, weapons and time-to-kill are not the game's, which
      is `lasertag_report`'s reason LT_NO_SURVIVABLE_OPENING does not block.
    - **The fight moves when the level does not.** Laser Tag 0.31.0 changed only how its guards walk, and
      gas_block_001 seed_9181's crew survival went from 9.51 to 18.88 s.
    - **They are one set.** Cold run 9283's three candidates carried one each: NO_REACTION_TIME twice
      (crews dead in 6.44 and 7.80 s) and TRIVIAL_ENCOUNTER once (a crew that lost nobody). Not counting
      either alone would have picked the other's failure.
    - **They still reach the pick through the score.** Taken together they change none of the 62 picks.
  - **`ANSWERED_BY_WALK`: LOT_DESTINATION_ABOVE_FLOOR, where the walk test walked every leg**
    (`walked_every_leg`). Lot raises it for an objective 3.3 to 4.0 m up, a storey, because it cannot tell
    offline whether a stair reaches it. The walk test walks a crew body to that objective.
    - **It was on 96 of the 186 candidates.** The walk test walked every leg on 95 of them, and Laser
      Tag's crew completed the route on 93.
    - **Where it did not walk the leg, the doubt was right.** On cold run 9185's seed_9003 the
      objective stood on a navmesh island 60.99 m from the main network, and the walkers had
      credited that leg as a ladder. It counts there.
    - **Counted, it chose 28 of the 62 picks.** On 12 of them it took a lower route completion or score
      than this rule now picks, on 16 an equal one, and on none a higher. For example, cold runs 9263 to
      9265 took restaurant_row_001's 0.72 at PASS_WITH_TUNING 78 over 1.00 at PASS 90.
  - **"Walked every leg" is stricter than the walk test's `ok`.** Each crew walker must read exactly "ok"
    with every target reached. The director's `ok` also passes a leg it credits as vertical access without
    walking it ("ok(N vertical leg(s) via ladder)"). A walk test that names no crew walker has answered
    nothing, and the doubt counts.
- **Still counted:**
  - the out codes: a walk test not ok, LT_ROUTE_NEVER_COMPLETED, ENEMY_PATHING_BROKEN;
  - the structural findings: a spawn missing, in collision or cut off; no world collision;
  - every other tool's majors;
  - TRAVERSAL. On both of the two candidates that carried it, the crew was wiped in 20 and 21 of 25 runs,
    which is a fight outcome. But a crew held by the geometry reads the same way, so it stays counted.
- **What it invalidates:** on this disk's workspaces the new rule picks a different seed in 28 of 62
  missions, and in no mission but these three:
  - restaurant_row_001 in 23 of its 42 runs, every run since 9263 among them: seed_9104 to seed_9003, or to
    seed_9205 on 9263 to 9265;
  - urban_row_001 in all 3: seed_9104 to seed_9003;
  - club_block_014 in 2 of 4: seed_9181 to seed_9282.
  - **The 16 equal moves are ties** on completion and score that now go to the lower seed.
  - **Any A/B against an earlier run must name its seed:** `cold_drive.sh N PREV mission 9104`, not
    `auto`. `docs/findings/urban_street/ab_record.sh` compares the two runs' packages, and was sound only
    because both had picked seed_9104.
- **`tests/unit/test_pick_counts.py`** has 6 checks, and 5 of them fail on 0.201.0: the grade, the doubt
  answered, the doubt still counted where a leg was credited, the fight verdicts, and `--json`. The suite:
  `python -m pytest -q`: exit 0, 2,379 passed (0.201.0's 2,372, `test_pick_counts.py`'s 6, and the sibling-locator guard's case over the new file), 14 skipped (the real-tool smoke), 1 xfail, counted off the progress marks.
