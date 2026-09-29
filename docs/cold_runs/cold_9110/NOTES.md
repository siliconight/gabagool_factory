# Cold run 9110 -- the 3.4 m price pylon

The walker, 2026-09-29: "yes, make the pylon bigger". Zoo 1.26.0 (genome
default and DC_SIZES 3.4 x 0.7 x 9.0), Lot 0.81.0 (SPECIES), Lot 0.82.0 (a
cover's test point at a body's centre -- the fix for 9109's refusal). Zero
interventions, the art leg read BEFORE export: 0 blockers, findings identical
to 9108 code by code (58).

THE READ, square to the face at 12 / 20 / 30 m, aimed at each brand
cabinet's centre, night and noon (`pylon_distance_grid.png`: rows 2.4 m
night, 3.4 m night, 2.4 m noon, 3.4 m noon; columns 12, 20, 30 m):

  * at 20 m the 3.4 m pylon's name reads about as the 2.4 m one's did at
    12 m -- the stroke went 3 -> 5 texels (3.75 -> 6.25 cm), as predicted;
  * at 30 m a building stands between that camera and the pylon: the 6.5 m
    pylon is hidden entirely, day and night; the 9 m pylon's brand cabinet
    stands over the roofline -- the height puts the brand where it was not;
  * the digits are still soft at every distance.

An automatic green-mask measure of the brand region was tried and is not
reported: at noon it caught foliage (a 460 px "brand" on a 2.4 m sign at
12 m). The frames are the evidence.

COST: draws identical at all 53 headings (71,827 summed, both 9110 runs);
median p95 5.91 ms (9108) against 6.42 / 5.93 -- within the session's
spread; stations over the provisional budget 8 of 14 on both.
