# Cold run 9248 -- the graders' fixed clock in a real drive, and the roofs by building

**What it tested:** five releases on 9245's lot and seeds (restaurant_row_001):
Laser Tag 0.27.0 and Lot 0.117.0 (the navigation map updates on the
grader's own thread), Level Factory 0.180.0 and 0.180.1 (Laser Tag's
evaluation under `--fixed-fps 60`; Lot's `walktest.py` passes the same),
and Zoo 1.102.0 (what a roof carries follows what the building is, and
fewer -- the walker's call on 9245's roofs). Deli Counter 0.209.1, Lux
0.75.0, Pixelcoat 0.62.0 and Patina 0.30.0 as in 9247.

**Result: 0 interventions, 0 tool files changed; the package baked on its
first attempt** (3,491 lightmap users). seed_9104 picked, as in 9241 to 9247.
Findings 122 -> 122.

## The drive: 24.3 -> 14.3 minutes

    leg                       9247 (waiting clock)   9248 (fixed clock)
    shell                     10.40 min              1.08 min
    shell + art (art.log)     15.0 min               5.7 min
    export                     7.6 min               7.0 min
    walk copy + retire         1.7 min               1.6 min
    the drive                 24.3 min              14.3 min

The graders, each job's own `duration=` (the walk tests include their
import pass):

    job                        9247       9248
    Laser Tag seed_9003        398.8 s    16.8 s
    Laser Tag seed_9104        593.2 s    21.7 s
    Laser Tag seed_9205        256.6 s    14.4 s
    walk test seed_9003        145.8 s     9.3 s
    walk test seed_9104        125.8 s     9.0 s
    walk test seed_9205        154.0 s     9.1 s

The export is now half the drive: roadmap 239's next lever (one import of
a package instead of several) is where the remaining time is.

## The graders read what they read before

Same build first: every `lot_assemble` output of the three candidates is
byte-identical to 9247's except `lot_navqa_setup.gd`, the walk test's setup
script that Lot 0.117.0 changed (4,654 -> 5,435 bytes).

- **Every Laser Tag report is identical to 9247's in every field**, all
  three candidates (9247 ran Laser Tag 0.26.0 on the waiting clock, 9248 ran
  0.27.0 on the fixed one). The candidates read 0.96, 1.00 and 0.48 route
  completion as in 9247, and seed_9104 was picked on the same findings.
- **Every walk test report is its 9247 job's** but the director's
  `map_iteration` diagnostic, 2 -> 1 (one synchronous commit of the
  navigation map instead of two), as the A/B on 9247's staged walk tests
  predicted (`docs/findings/grader_speed/walktest_setters_ab.py`).

## The roofs, by building

    building       9245 (Zoo 1.101.0)        9248 (Zoo 1.102.0)
    deli_a01       17 props                  3: an HVAC unit, a vent stack, an exhaust fan
    office         17 props                  3: two HVAC units, a vent stack
    pharmacy_a01   17 props                  4: two HVAC units, a vent stack, a dish

From each building's `<id>_roofprops.built.json`. The lightmap users fell
3,501 -> 3,491: 9245's 18 merged roof meshes are 8. Seen from the deli's
hatch and from the street (`roof_frames.sh`, the sheet `roofs.png`, 9245 on
the left): from the hatch the roof that carried a crowd now carries three
props at its far parapet and is otherwise open; from the street the roofs
sit behind the parapet in both runs (0.03 % of pixels moved more than 32
codes). Whether three is right for a deli's roof is the walker's eye.

**A gap, noted:** the plan records its `profile` (`scatter`'s return,
1.102.0), but the built manifest Level Factory keeps does not copy it, so a
reader of the job's output cannot see which profile a roof was dressed by.
A small Zoo follow-up.

## What is evidence of what

- 0 interventions, the bake, the findings, the drive's legs: this run's
  journal and logs; 9247's the same way.
- The grader comparisons: each run's own reports, field by field.
- The roof counts: each roof's built manifest; the look: two stations shot
  in both packages, nothing else running.
