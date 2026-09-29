# cold run: 9109

begun 2026-09-29 15:33:09
3554 source files hashed across 10 tools

| when | kind | what |
|---|---|---|
| 2026-09-29 15:48:24 | observation | Zoo 1.26.0 + Lot 0.81.0 shipped: the pylon slot is 3.4 x 0.7 x 9.0. Export closure ok. |
| 2026-09-29 15:50:01 | correction | THE OBSERVATION ABOVE IS FALSE, kept above what replaced it. It was written by a chained command that did not check the art leg's result: the art leg ended BLOCKED (1 blocker, 56 findings) -- JOB_PREFLIGHT_REFUSED, Laser Tag's ground-contact pre-flight: LT_CoverTestPoints/Cover_147, the 9 m pylon's cover test point, written by Lot at half the cover's height (4.5 m), over Level Factory's MAX_DROP of 4.0. The export and the walk export both FAILED (exit 2); nothing was exported. No file was touched by hand, so 0 interventions is true -- but this run did not produce a level: a FAILED run, blocked by a Lot defect (cover test point height), not a zero. |
