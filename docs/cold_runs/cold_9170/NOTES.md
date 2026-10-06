# Cold run 9170 -- STOPPED at export: a blocker on a candidate nobody chose

Breadth sweep, run 5 of 10. card_block_001's brief as last run cold (9061),
on Level Factory 0.144.0, with the seed picked by the driver.

**Shell and art passed.**
- **Shell:** 3 candidates, all distinct; 0 blockers of 50 findings.
- **Art:** 0 blockers of 68 findings.
- **The driver picked seed_9263** "on the walktest and Laser Tag's route
  findings". It was the best of the three:

  | candidate | buildings | Laser Tag |
  |---|---|---|
  | seed_9061 | card_shop_a01, pharmacy_a01, setback_demo | exit 2 in 2 s, 0 runs: `UNREACHABLE_SPAWN: Enemy_5 could not path to the player spawn`; BROKEN, 0/100 |
  | seed_9162 | card_shop_a01, pvp_station_ref, stadium_a01 | 25 runs, WARN, 59/100 |
  | seed_9263 | card_shop_a01, parking_garage_a01, supermarket_a03 | 25 runs, PASS_WITH_TUNING, 78/100 |

**The export refused** (exit 2), with `INTERVENTIONS: 0`:

    [export] refused: card_block_001 has 1 open blocker(s) -- LT_NOT_EVALUATED at laser_tag_evaluate: Laser Tag never evaluated this map (0 runs completed) ...

**The blocker is seed_9061's**, from the validation file:

    {"blocking": true, "candidate_id": "card_block_001.candidate.seed_9061",
     "code": "LT_NOT_EVALUATED", "location": "", ...}

**Two queries of one question disagreed, as at cold run 9074.**
- `cmd_run`'s `aggregate` reads the finding's `candidate_id`, and discounted
  it as belonging to a candidate that was not chosen. Hence "blockers open: 0"
  at shell and at art.
- The export's `_open_blockers` read the candidate only from `location`,
  found none, and failed safe.

**Fixed in Level Factory 0.144.1:** the export reads `candidate_id` first.
card_block_001 runs again on it.

**Not a defect:** seed_9061 failing Laser Tag. A bad candidate is what three
candidates are for, and the picker avoided it.

**Open, for the walker:** seed_9061 drew `setback_demo` and seed_9162 drew
`pvp_station_ref`. Both are complete Deli Counter builds with every
manifest, and the library draws any complete non-facade shell by design.
Whether demo and reference shells belong in real levels is the walker's
call. If they don't, the house way is a Deli Counter flag like `facade`,
not Level Factory matching names.
