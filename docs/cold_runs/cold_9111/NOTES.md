# Cold run 9111 -- the night grade

The walker, 2026-09-29: "do the night grade next". Lux 0.58.0: Delco Night's
contrast 1.08 -> 1.0, nothing else. Zero interventions; the art leg read
before export: 0 blockers, findings identical to 9110 (58).

WHY: the post stack's contrast pivots on mid-grey, so at 1.08 it subtracted
~0.04 (ten codes) from a frame that sits near zero and sent every pixel under
ten codes to black -- half a night frame. 1.08 arrived with the preset and
was never measured. The grade was swept one setting at a time first on 9108's
walk copy (`grade_sweep_9108_*.json`): contrast was the lever; white point,
colour levels and palette pull were not; the AgX row is VOID (mode 4 is not in
the preset's enum and fell through to Filmic).

    player's frame, night (mean / % crushed to black)
                          9110 (1.08)       9111 (1.0)
    street, 30 m          6.2 / 50.5        10.2 / 35.7
    store, 8 m            20.9 / 34.5       25.3 / 28.4
    forecourt, south      18.5 / 40.8       21.8 / 32.5
    inside sales floor    16.1 / 14.9       24.0 /  6.7
    pylon, 20 m           6.4 / 50.2         8.8 / 44.9
    spawn (darkest)       1.6 / 59.3         2.1 / 57.5
    elevation E           0.8 / 61.6         0.9 / 60.9
    objective (brightest) 128.7 / 20.3      119.5 / 20.3

Still night: the darkest shots barely move. The one cost: a contrast about a
mid pivot also pulls highlights toward it, so the brightest shot loses about
7% (128.7 -> 119.5).

NOT PRICED: a uniform's value in the same shader, same passes -- nothing to
submit or compute that was not there. Noon untouched: only delco_night.tres
changed.

REPORTED, NOT CHANGED: gas_station_fluorescent (1.08), gothic_street_night
(1.12), ps1_storm_night and mission_goes_hot (1.18) have the same shape
(`lux/tools/night_contrast_selftest.gd` prints them).

`night_contrast_before_after.png`: rows street 30 m, store 8 m, inside;
left 9110, right 9111.
