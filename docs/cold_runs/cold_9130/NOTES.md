# Cold run 9130 -- the snack gondola sells more than chips

Zoo 1.40.0, the walker's 90s snack references ("fruit snacks, lunch kits,
snack cakes on shelves, candy") and their own first brand, YUMMYJAWNS. Same
brief, same seed, same lot as 9129. Zero interventions, one observation.

The observation is the driver's, not the pipeline's: a scratch script that
chains the legs treated `run`'s non-zero exit at the approval gate as a
failure and stopped. The leg had reported 3 candidates and 0 blockers; the
run was resumed from the approvals with nothing re-run and nothing edited.

The art leg before export: 0 blockers, 63 findings -- identical to 9129's by
code.

## The gas station (`gas_sections.png`, `gas_cakes_and_chips.png`)

Both frames stand in the lanes between gas_station_a02's gondolas. One long
face of each is the chip aisle as it shipped; the other is sections a bay
each -- lunch kits (HOAGIE KIT, PIZZA KIT), fruit snacks (GUMMY GEESE, FRUIT
TAPE, JUICE BOMBS), bagged candy, and YUMMYJAWNS cartons, one flavour a
shelf. The end caps are chips.

Seen and not fixed: the boxes are 0.18 m on shelves pitched 0.37 m, so there
is air over them; a lunch kit is a cooler item standing on a dry shelf.

## Priced (`perf_9129.json`, `perf_9130.json`)

The fixed-station harness on fresh copies of 9129's and 9130's packages, 53
headings: 61,545 draws -> 61,545, no heading changed, worst heading 2,648
both. Predicted (the gondola is still two submissions) and measured.

9129 had not been measured before; against 9127 it reads 61,627 -> 61,545
on four headings, which is Deli Counter 0.168.2's cabinet and stool gone
from the storefront glass. Frame time is not claimed: the harness's noise
is about 2.5 ms.
