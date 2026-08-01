# Phase 4 -- Mega-Structures & Library Completion: CLOSED (2026-07-21)

**The Production Package library is structurally complete: 100
configurations / 36 families / 20 missions / 8 heroes / ~57 placements /
every family placed in a mission.** All 25 new configs and all 8 new
missions went engine-green on their FIRST batch -- zero post-engine fixes
across the whole phase. Certified set: **factory 1.5.0** (DC 0.83.0,
Lot 0.23.0, pipeline 0.5.0).

## What shipped

**Wave A (13 configs, 4 new families):** STADIUM x4 (Citizens Bank Park
count room + concourse, Lincoln Financial cage, Subaru strong room,
premium club level), ARENA x3 (Xfinity), CASINO x3 (Rivers gaming-floor
cage + basement count room + high-roller suite), MARKET_HALL x3 (Reading
Terminal stall grid at 6.5 m). Engine: 13/13 nav + 13/13 import.

**Wave B (12 configs, 4 new families):** AIRPORT_TERMINAL x3 (PHL
check-in / baggage bond store / airside control), BANK_TOWER x3 (Center
City main vault / executive safe / teller cage), LANDMARK_HALL x3
(Independence Hall / Liberty Bell, timber-and-brick), TRAIN_YARD x3
(SEPTA shed / under-track store / signal tower). Engine: 12/12 + 12/12.

**Mission batch (8 sites):** 4 LARGE heroes -- Citizens Bank Park, Rivers
Casino, PHL Airport, Center City Bank Tower -- and 4 standards -- Xfinity
Center, Reading Terminal (brings CLINIC into the portfolio), Independence
Mall, SEPTA Yard. The bank tower hero uses a credit union crew home
(brings CREDIT_UNION in). Engine: 8/8 walktest (proofs + physical
walkers) + 8/8 mp_smoke (4 players), first pass.

## Why first-pass green became normal

The pattern book is now fully encoded: p2lib rules R1-R6, the tall-stair
run rule (>= 0.85 x story height), and Phase 4's stair_margin() clearance
rule (half-run + 1.2 m landing + 2.2 m approach off any wall) mean the
venue template emits engine-clean geometry by construction. The offline
sandbox leg (validate -> Blender build -> evidence -> roundtrip -> lot
assembly) caught every authoring defect this phase -- four site-level
issues (2x spawn separation, 2x single-approach objective) never reached
the machine.

## Venue boundary note

Stadium-class shells ship as their heist-relevant service interiors
(concourse sections, cage lines, count rooms, suite levels). The full
bowl / apron / runway is site-scale dressing owned downstream in
level_factory, per the levels-as-input boundary in ENGINE_GATES.md.

## What keeps the portfolio check from full green

`registry.py check --portfolio` counts APPROVED records; approval
requires every gate pass (done) AND visual_quality_score >= 4 (all still
null). The remaining work is the art leg -- Pixelcoat / Patina / Lux
passes + visual scoring -- which was always scoped as a separate
production activity. Structure, gates, and evidence are complete.

## Carried backlog (unchanged)
- Visual scoring / art leg across all 100 configs (the approval gate).
- Generator multi-story switchback self-connect.
- SEPTA train rolling stock (level_factory design conversation).
- central_vault hero re-run with the slope fix (upgrades pass_proofs ->
  full pass).
- gas_station_a01 forecourt-pad island (site-scale connected; open_issue).

## The convergence story, complete
Phase 0: 24 rounds to green one building. Phase 1: 5 batches. Phase 2:
3 batches + mop-ups. Phase 3: first-try waves + 1 straggler round.
Phase 4: **first-pass green on all 33 deliverables, zero fixes.**
