# Cold run 9144 -- the dressing on the ground that exists, kerbs dressed

gas_block_001, 9143's brief and seed (9080), on Lot 0.96.0 (a standing piece
keeps dressing out of its own footprint), otherwise 9143's stack (Zoo
1.59.0, Patina 0.23.0, Level Factory 0.134.0), exported with
`--bake-lights`. **Zero interventions**. Findings 63 -> 63, identical.

## The dressing against 9142 (before Patina 0.23 and Lot 0.95-0.96)

                                9142        9144
    pieces                      5,232       3,566
    on another family's ground  1,430       0
    sidewalks                   1,822       1,421
    roads (low)                 1,071       477
    on the fields, a m2         0.288       0.080
    walk zones                  54          50, at the walks the scene has

Identical to the direct re-run of 9143's inputs recorded in Lot 0.96.0's
changelog (3,566). The pieces gone are the double dressing: open ground's
scatter laid on roads, sidewalks, the perimeter and the fields on top of
their own.

## Price (`docs/findings/dressing_price/`)

9142's package against this one, 9142's again as the control:

    mean over 53 headings       draws    median ms   GPU ms
    9144 - 9142                 +1.0     +0.02       -0.06
    control (9142 twice)         0.0     +0.02       +0.01

No measurable cost either way: the dressing is MultiMesh, so a third fewer
instances is not a third fewer draws.

## Frames (`docs/findings/dressing_frames_9144/`)

The same cameras as 9141's (`docs/findings/fields_frames/`) and 9143's: the
aisles carry a light scatter instead of being strewn, and the sidewalk under
the lamp, bare in 9143, carries its litter again.

## Laser Tag, read again

Laser Tag 0.23.2 (committed after this run) logs a named event at the
position it carries. Read from the metadata of earlier reports, the
"positionless" stuck events of seed 9181 that 9140 and 9141 left
unattributed are 1,354 of 1,378 at one spot: the crew six metres up inside
`arena_a03`, plan (55.3, -13.1), short of an objective in the same building.
RETRACTED, kept here: 9140's and 9141's notes said those events "carry no
position" -- they always did, in `metadata.position`, and the notes read the
top-level field. Why the crew stops there is a traversal question for Deli
Counter's arena, not yet asked.
