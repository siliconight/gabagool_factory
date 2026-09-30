# Cold run 9116 -- the club under blacklight, handbills outdoors

Zoo 1.33.0 (the club's posters are their own light: a `_Face` material on the
same atlas, no draw added) and Lot 0.84.0 (`site_posters`: Zoo's alley poster
runs on each building's back-of-house walls and on every other pole, as HUNG
slots that are never cover). Same brief, same seed, same lot (replayed before
--begin). Zero interventions, one observation.

The art leg before export: 0 blockers, 65 findings -- 9115's 64 and one more
`ZOO_PARTIAL_BUILD` (2 -> 3): "4 module(s) failed to build". Read, not assumed:
the site kit's four POLE modules, `prop_poster_wall_delco_1997_01_w30_d1_h52_falley`
and its `_n1`-`_n3`, each failing Zoo's exact fit, "height=0.420m != exact
target 0.520m". The two other partial builds (an ATM, a flat-top grill) are
9115's. Lot asked a lone sheet to fill `band_height("alley", 1)`, a band made
for a run whose sheets wander down it; Zoo refused rather than stretch, and
Lot drew nothing where the module was missing, as designed. Fixed after --end
as Lot 0.84.1 (the pole slot is one sheet's height, 0.42; Zoo's planner fills
it in every variant) with a test that asks Zoo's planner to fill every slot
shape Lot writes. 21 hung slots written, 6 drawn: the wall runs.

## What the frames show (`posters_night.png`)

- The club's posters, blacklit, through the whole pipeline: the art reads in
  its own colours on the dark walls (9115's probe shipped as Zoo 1.33.0).
- Handbill collages -- day-glo sheets in two courses -- on the strip club's
  west and south walls and the gas station's west stone wall, readable at
  4 m at night.
- The two north-facing runs (airport terminal, gas station) read black at
  4 m and 1.4 m, and at 12 x gain. A wide view from 12 m out and 5 m up shows
  the WHOLE north face of both buildings black -- wall and all -- beside lit
  windows and light pools on the ground (`north_faces_and_probe_control.png`,
  bottom row). Whether the runs are there, unlit, is not shown by a frame.
- REFUTED in the file: a probe OmniLight 1 m in front of each north run
  changed nothing -- and the same light in front of h1, a run that is
  visible, changed nothing either (top row, without and with). The probe
  cannot move the picture, so its black frames are not evidence.

## Cost

Fresh package copies of 9115 and 9116, four passes each, alternating:

    draws, heading by heading    60,814 -> 60,888 (+74) over 53 headings;
                                 19 identical, largest +4
    control, 9115 a against b    identical on all 53
    mesh instances               4,428 -> 4,434 (the six wall runs)
    positional lights            112 both; meshes over 8 lights 43 both
    median of medians            3.33/3.33/3.36/3.32 -> 3.30/3.32/3.28/3.31 ms

    worst p95, pass by pass      9115: 10.82 10.42 10.35  9.60
                                 9116: 17.24 12.61 10.02  9.74

The 9116 spikes are at one station, player_start_26 (17.24 ms facing 90 in
pass a, 12.61 facing 270 in b), in the first two passes after import only;
passes c and d are 9115's to the hundredth at the same headings, and that
station's draws rose by 4. Not reproduced, not attributed.

## Findings to act on

1. North-facing exterior walls receive no light at night in this lot, so a
   poster there reads as nothing. Which walls `site_posters` prefers could
   take the moon into account, or the lighting could reach them; neither is
   done.
2. The lot has roads and poles but, as generated, no true alleys: every run
   is on a rear or side wall (Lot 0.84.0's measurement: 0 alleys over 28
   sites and this lot).
