# Cold run 9293 -- the strip on Laser Tag 0.32.0: an arrival is at the point

**What it tested:** restaurant_row_001, the strip brief (9285's, unchanged), on Laser Tag 0.32.0 (a277dd9). In it a
route point counts as reached only where the bot's path reaches it (factory roadmap 246). Level Factory 0.204.0,
Lot 0.122.0, Deli Counter 0.217.0, the pick `auto`. Staged from cold run 9285.

**Result: 0 interventions (journal 0, unattributed files 0). On a strip level nothing the graders read moved.**

- **The control:** every Laser Tag summary field on all three candidates reads exactly as 9285's, and all grade
  PASS 90. Between the two runs stand:
  - Laser Tag 0.31.0 -> 0.32.0, a no-op where every route point is reachable (`docs/findings/lt_arrival/`);
  - Lot 0.121.0 -> 0.122.0, which moves only a row the fences leave open, and the strip has none;
  - Level Factory 0.201.0 -> 0.204.0, which moves the pick and the urban street only;
  - Deli Counter 0.214.0 -> 0.217.0, which rebuilt no strip shell.
- **The pick moved, as roadmap 245 said it would:** seed_9003, where 9285 took seed_9104.

      seed 9003: 0 major (not counted: LOT_DESTINATION_ABOVE_FLOOR), route completion 1.00, grade PASS 90
      seed 9104: 0 major, route completion 1.00, grade PASS 90
      seed 9205: 0 major (not counted: LOT_DESTINATION_ABOVE_FLOOR), route completion 1.00, grade PASS 90

  All three tie on the rule, and the lowest seed takes it. seed_9003's objective is a storey up, and its walk
  test walked to it.
- **Findings: 112.** The driver's delta reads "0 -> 112" because the workspace it compares against (9292) ran
  urban_row_001, so the delta says nothing here.

## The time

    run    shell   art     export   walk   retire   the drive
    9293   95 s    161 s   174 s    11 s    4 s     7.7 min (462 s)
