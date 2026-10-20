---
name: pick-moved-name-the-seed
description: "LF 0.202.0 changed the pick on 28 of 62 cold missions (restaurant_row/urban_row 9104->9003); an A/B against an older run must pass the seed, not auto"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-14T03:19:58.614Z
---

Level Factory 0.202.0 (2026-10-13, roadmap 245; the walker left the call to me "for the moment"):
the picker no longer counts LOT_DESTINATION_ABOVE_FLOOR where the walk test walked every leg, nor
Laser Tag's five fight verdicts, and breaks ties on the LT score. Replayed: 28 of 62 picks move.
That covers restaurant_row_001 (23 of 42 runs, seed_9104 -> 9003, or 9205 on 9263-9265),
urban_row_001 (3/3, 9104 -> 9003) and club_block_014 (2/4, 9181 -> 9282).

**Why:** a cold run's level is its picked candidate. `ab_record.sh` and price comparisons across runs
were sound only because both runs picked seed_9104. After 0.202.0 the same brief ships a different
seed's level.

**Since:** urban_row_001 picked seed_9003 in 9290 (a three-way tie at PASS 90) and seed_9104 in 9291
(PASS 100; one enemy moved 5 m by a new block). The grade decides ties, and it moves with the fight.

**How to apply:** for an A/B against a run before 0.202.0, run
`cold_drive.sh N PREV mission 9104`, the seed explicit, not `auto`. Say so in the run's NOTES. If the
walker disagrees with the call, the two sets are `ADVISORY` and `ANSWERED_BY_WALK` in
`level_factory/packages/pipeline/pick.py`. The root `tools/cold_drive/pick_candidate.py` only reads
that module now; never give it a rule of its own again.

Related: [[urban-level-type]], [[laser-tag-rabbit-hole]].
