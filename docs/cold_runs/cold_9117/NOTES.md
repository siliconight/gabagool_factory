# Cold run 9117 -- every handbill standing

9116 with Lot 0.84.1: a pole's handbill slot is one alley sheet tall (0.42),
which Zoo's planner fills in every variant. Same brief, same seed, same lot.
Zero interventions, one observation. The art leg before export: 0 blockers,
64 findings -- 9116's 65 less one `ZOO_PARTIAL_BUILD` (3 -> 2; the two left
are 9115's ATM and flat-top grill). Export closure clean. All 21 hung pieces
stand in the scene: 6 wall runs and 15 pole bills (9116: 6 of 21).

## What the frames show (`alley_posters.png`; every piece: `alley_posters_all.png`)

A station per piece, derived from its own slot: the camera on the side its
face points to (`plate_facing` of the slot's yaw), 4 m off a wall run and
2.5 m off a pole bill, at the piece's height. Handbill collages on the back
walls; single day-glo bills on streetlights and sign posts, on the sidewalk
side.

WHICH WAY A POSTER FACES DECIDES WHETHER IT CAN BE SEEN AT NIGHT. Measured on
the frames, the median luma of the 80 px window at each piece's centre:

    faces south or west   9 of 9     43.4 - 101.0
    faces north           8 of 8      0.0
    faces east            1 of 3     104.2 (a sign post), 0.0, 0.0

So the posters stand; this lot's night light reaches vertical faces turned
south and west and almost nothing else -- the same finding as 9116's north
walls, now over 21 pieces rather than two. Not changed here.

`merged["poster_plan"]` is not in `site.site.gameplay.json`: `assemble`
writes that file before the posters are planned. The slot manifest carries
every piece; the plan's hosts do not reach the package.

## Findings to act on

1. Night visibility by facing (above). Options, for the walker: Lot prefers
   a lit face (a pole has four; a building's rear may not be lit), which
   couples it to the night preset's light direction; or the night lighting
   reaches north and east faces (a look and a cost, Lux's); or leave it --
   they read by day and under a flashlight.
2. The poster plan does not reach the gameplay file (above).
