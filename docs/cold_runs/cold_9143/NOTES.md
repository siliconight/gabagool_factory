# Cold run 9143 -- the dressing on the ground that exists, untouched

gas_block_001, 9142's brief and seed (9080), on Lot 0.95.0 (the dressing
reads the site as drawn; a parking field is its own zone) and Patina 0.23.0
(a zone dresses only the ground it owns), otherwise 9142's stack, exported
with `--bake-lights`. **Zero interventions**. Findings 63 -> 63, identical:
dressing carries no collision and the layout did not move.

The surfaces job read the drawn site (`LOT_SURFACE_SPEC_AS_DRAWN`).

## The dressing (`patches/patina_zone_owner/dressing_compare.py`)

                                9142        9143
    pieces                      5,232       2,226
    on another family's ground  1,430       0
    on the fields, a m2         0.288       0.065
    walk zones                  54          50 (at the walks the scene has)
    exclusion refusals          493         2,061

Two effects, one wanted. Ownership removed the double dressing. Reading the
drawn site also brought its 164 cover pieces into `exclusions` for the first
time, each a 3 m circle (`site_cover.MARKER_CLEARANCE`) the rule was written
with and never ran under -- so every kerb line went bare: sidewalk pieces
1,822 -> 351, and in the frames (`docs/findings/dressing_frames_9143/`) the
sidewalk under the lamp that carried litter in 9141 is empty. Lot 0.96.0
makes a piece exclude only its own footprint; re-run on this run's inputs it
restores the sidewalks to 1,421 with nothing on another zone's ground. Cold
run 9144 ships it.
