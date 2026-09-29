# Cold run 9109 -- FAILED

Zoo 1.26.0 and Lot 0.81.0: the price pylon at 3.4 x 0.7 x 9.0. The art leg
ended BLOCKED -- one blocker, JOB_PREFLIGHT_REFUSED: Level Factory's
ground-contact pre-flight found `LT_CoverTestPoints/Cover_147` (the pylon's
cover test point) with no ground beneath it. Lot wrote the point at half the
cover's height, 4.5 m, over the pre-flight's MAX_DROP of 4.0; Laser Tag would
have refused the map and run nothing. The export and the walk export failed;
no level came out of this run.

THE JOURNAL'S OBSERVATION IS FALSE and is kept, with the correction beneath
it (`journal.md`): it was written by a chained command that did not read the
art leg's result before exporting and observing. No file was touched by
hand, so the tool's "0 interventions" is true of the count -- but this is a
failed run, blocked by a defect in Lot, and it is not a zero.

Fixed in Lot 0.82.0 (a cover's test point stands at a body's centre, half of
min(cover height, player height)); retried as cold run 9110, which passed.
