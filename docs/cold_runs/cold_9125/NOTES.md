# Cold run 9125 -- the canopy's washes over the lanes

Deli Counter 0.167.0: with pump islands under a fuel canopy, one wash hangs
over each lane instead of evenly along the deck (which put them over the
islands). gas_station_a02: four washes at x -8.9, -3, 3, 8.9 where there were
three at -7.33, 0, 7.33. Same brief, same seed, same lot as 9124. Zero
interventions, one observation.

The art leg before export: 0 blockers, 63 findings -- identical to 9124's by
code. Export closure clean.

## The look (`forecourt_before_after.png`; 9124 left, 9125 right)

Six given stations, 9121's five and one more (`look_forecourt_*.json`), and
the pump's own pixels in two of them (`forecourt_regions.py`: luminance of a
fixed rectangle round the pump, sampled every other pixel):

                                       9124           9125
    the inner-lane face (04), p50       2.0           23.0
    the inner-lane face (04), mean     44.0           53.0
    the outer-lane face (05), p50      31.1           23.2
    whole frames 01-06, mean      10.0-22.8      10.0-23.1  (within 0.4 each)

The face that stood in shadow is lit -- its silver, red and gold panels read
where they were black -- and the two faces of one pump are now even (23 and
23) where they were 2 and 31. The outer face gave up some light: the wash it
stood under moved to its lane's centre. The means are held up by each face's
glowing wheels and header; the median is the read of the panels.

THE FORECOURT AS A WHOLE IS STILL DARK, and this run does not claim otherwise.
The lane-tarmac rectangle read 0 before and after and is NOT evidence: frame
03's lower band is the ground near its camera (x 107-110), outside the deck
(x 93.5-106.5). Moving the washes changed where the light falls, not how
much there is; how much is Lux's canopy-wash level, its own lever and its own
price.

## The price (`perf_9125.json`, against 9124's)

    total draws, 53 headings   61,263 -> 61,161  (-102: two headings,
                                                  extraction_3 yaw 270 -62,
                                                  defender_spawn_22 yaw 180 -40)
    worst heading              2,626 -> 2,626
    meshes over the 8-light cap 43 -> 44 of 4,455; worst 38 -> 39 lights

One light more on the forecourt REDUCED draws at two headings; the cause is
not established (a shadowed light's coverage moving is one candidate) and is
not asserted. The harness prints the over-cap count but not which meshes, and
its JSON does not keep either, so the one mesh that crossed the cap is not
named here.
