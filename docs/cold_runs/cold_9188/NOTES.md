# Cold run 9188 -- 0 interventions; the presentation gates read every building, and say one true thing more

The measurement run for four releases on 9187's brief, restaurant_row_001:
- Lot 0.97.3: spawns out of the Empties.
- Deli Counter 0.191.0: the circulation gate reads parts, and excuses a
  stair's own guards.
- Deli Counter 0.192.0: L23, and 17 pieces moved off stair holes.
- Level Factory 0.149.0: every placed building's package is read.

**Every leg ran, `INTERVENTIONS: 0`, and the package exported.**
- **Findings 62 -> 64 against 9187, and the only change is the one
  predicted:** `PRESENTATION_ZFIGHT` 1 -> 3.
- **Themed fitness is unchanged at 102 of 127, so the draw is 9187's.** All
  three candidates hold the same buildings, and seed_9104 is picked again.
- **Bake:** 483 models and 1,478 primitives lightmapped (9187: 485). 4,310
  users, 92.9 s.

## The presentation gates, against 9187

| | 9187 (LF 0.148.0, DC 0.190.0) | 9188 (LF 0.149.0, DC 0.192.0) |
|---|---|---|
| `presentation_compose` exit | 6 | **0**, the first since at least 9164 |
| circulation line | "[FAIL]: 0 prop conflict(s) across ? circulation volume(s)" | "[OK]: shell 0 conflict(s) across 2 volume(s); dressing 0 conflict(s) across 2 volume(s)" |
| `PRESENTATION_ZFIGHT` | 1, deli_a01's | **3**: deli_a01 200 pairs, office 121, rail_station_a02 117, each named |
| `PRESENTATION_CIRCULATION` | (no such finding) | 0 |

- The two new z-fight findings were failing in 9187 too. One manifest of
  sixteen was read.
- deli_a01's pairs went 203 -> 200. Deli Counter 0.192.0 refurnished its
  upper hall around the moved counter islands.
- No circulation finding. The dressing arms pass on parts. deli_a01's shell
  arm, which named its counter island 0.8 m inside its stair, is clean now
  that the island has moved.

## Lot 0.97.3: nothing moved here, as measured beforehand

- Every enemy of all three candidates stands where it stood in 9187.
- Laser Tag reads identically on seed_9003 and seed_9104: PASS_WITH_TUNING
  79, 25 of 25 runs finished.
- seed_9205 read 0.88 -> 0.84 completion and 7 -> 5 stuck events, WARN
  either way. Its deli_a03 had its upper hall refurnished by 0.192.0.
- This run measures Lot 0.97.3 for regressions. Its fixture test on 9186's
  site is the proof of the fix.
