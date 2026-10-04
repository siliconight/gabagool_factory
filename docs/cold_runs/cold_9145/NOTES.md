# Cold run 9145 -- one building line a street, untouched

gas_block_001, 9144's brief and seed (9080), on Level Factory 0.135.0 (one
building line a street) and Laser Tag 0.23.2 (events logged at their
positions), otherwise 9144's stack, exported with `--bake-lights`.
**Zero interventions**. The same three buildings, now with their street
edges on one line.

## Findings, 63 -> 55

The shell leg's 45 -> 40 is the nine-candidate measurement's gas_block_001
row exactly (`docs/findings/landuse_line_before_after.txt`, attributed in
Level Factory 0.135.0's changelog); the art leg repeats the cover pair for
the shipped seed. Beyond those:

    DISPATCH_FINDING             8 -> 7    the "1 nav bridge link auto-added"
                                           notice 9141 brought is gone
    LT_MAP_TRIVIAL_ENCOUNTER     seed 9080, the shipped one: the crew never
    LT_MAP_ENEMY_STUCK           dies, and all 25 enemy-stuck events are at
                                 the gas station store's north-east corner,
                                 plan (-48, -1), with the objective inside
                                 that store and Enemy_1 1.2 m off its east
                                 wall. Located with Laser Tag 0.23.2; why the
                                 enemy cannot round the corner is not yet
                                 asked.

## Frames (`docs/findings/street_line_frames/`)

`before_9144/` shot from 9144's walk copy before this run replaced it,
`after_9145/` from this run's, each placed from its own site's through road
(`patches/lf_street_line/make_street_shots.py`). From above: before, the
freight terminal stood on the walk and the gas station and the bank stood
back on lengths of walk; after, the three storefronts stand on one line
behind the sidewalk. From the far sidewalk, looking down the row: meters,
trees and kerb cars, the storefronts close to the road -- and across the
street, the plate's perimeter wall, which nothing here addresses.
