## 0.100.1 - the responder planner checks the boxes it records

**Roadmap 212.** Cold run 9206 (club_block_014, 0 interventions) brought
back the arrival cold run 9204 lost: `LOT_RESPONDER_ENTRY_NO_STOP` 2 to 0.
It also carried one new major finding, on seed_9080, a candidate it did not
pick: `LOT_RESPONDER_BLOCKED`, "step_van at (-9.0, -26.9) stands in
responder arrival 0's lane on road 0".

**The van is not in the lane.**
- **What the planner did.** 0.100.0 steered the lane round the van, 0.648 m
  as on 9204, clearing the van's edge by 1e-6 m. It checked the box it
  computed.
- **What the record did.** `plan` writes boxes to three decimals, and the
  rounding put the box's edge on the van's: -28.22, against `cover_rects`'
  -26.92 - 1.3 = -28.220000000000002.
- **What the read-back saw.** `blocked` checks the recorded box, and found
  3.6e-15 m of overlap.

So one number had two spellings, and a threshold was asked of each.

**The fix: the planner checks the boxes it records.**
- **One rounding.** `RECORD_DIGITS` (3) is the record's precision.
  `_recorded` rounds a box to it once, and `_best_stop` and `_lane` check
  that rounded box, which `plan` then writes unchanged. 0.100.0 rounded in
  `plan` with its own literal.
- **One clearance.** A steered lane clears what it passes by
  `RECORD_PRECISION` (10^-3 m), so rounding cannot bring an edge back onto
  what it cleared.
- **What it moves.** A steered lane shifts 1 mm more than it needs: 0.649 m
  on 9204's site, where 0.100.0 recorded 0.648.

**Tests.**
- **A new fixture,** `club_block_014_seed_9080.site.json`: cold run 9206's
  input site with the getaway van as placed. The replay reproduces the
  job's three stops and its phantom finding on 0.100.0.
- **`test_what_the_planner_keeps_the_read_back_finds_clear`**, on that
  fixture:
  - the read-back finds nothing;
  - the steered lane clears the van by at least half a millimetre;
  - every box in the record is already at the record's precision.

  On 0.100.0 it fails on the phantom finding itself.
- **The 9204 test's shift** is the need plus `RECORD_PRECISION`.

**Suite:** 706 passed (705 + 1), `python -m pytest -q`.
