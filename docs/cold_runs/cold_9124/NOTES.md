# Cold run 9124 -- the remainders' room face

Zoo 1.38.1 and Deli Counter 0.166.1: the unit `wallEnd` remainders of an
outside-only exterior wall get the room face too. Same brief, same seed, same
lot as 9123. Zero interventions, one observation.

The art leg before export: 0 blockers, 63 findings -- identical to 9123's by
code. Export closure clean. gas_station_a02 places 13 room-face remainders
(`wallEnd_delco_1997_0{1,2}_mstone_idrywall`): its 9 stone remainders and 4
more on the back-room stretch of the shop front, which the manifest writer
turns from glass into stone wall.

## The look (`stone_inside_remainders.png`; 9122, 9123, 9124 left to right)

The stockroom, the sales floor's west wall and the walk-in cooler, from the
stations 9123 used. The stone strips 9123 left -- the stockroom frame's left
edge, beside the sales floor's window, the cooler's corner -- are drywall.
No stone shows inside the gas station at these stations.

## The price (`perf_9124.json`, against 9123's and 9122's)

Same harness, fresh package copy, 53 headings:

    9122 -> 9123 -> 9124 draws, all headings   61,006 -> 61,202 -> 61,263
    9123 -> 9124                               +61, 10 headings, at most +13
    9122 -> 9124 (the room face in all)        +257 (+0.4%), at most +50 at one heading
    worst heading on the map                   2,626 throughout

Frame time is not resolved by this harness at this size (9123's control moved
2.5 ms on identical bytes); no frame-time claim is made.
