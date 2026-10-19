# Cold run 9326 -- urban_row_001 on Deli Counter 0.231.0 (2026-10-19): pharmacy_a01 holds two video poker cabinets

Staged from 9325. The tool change between them is Deli Counter 0.231.0 (50db4890). A store's video poker cabinet
may now stand against the partition it backs onto: `backs_on_partitions`, on for that piece alone, exempts the
one partition behind it from `_seed_clear`'s metre-off-a-partition rule. Every other rule still applies. The
library was stripped and refurnished, and 30 of 31 stores now hold two cabinets.

**Run:** 0 interventions (journal 0, unattributed files 0), drive exit 0, 12:05:54 to 12:15:26. The pick is seed
9104 again, PASS 100, route completion 1.00, 0 major. Findings 107 -> 107.

**The two mission stores,** counted off each building's composed scene in the package (`lot/<building>/site.tscn`):

| building | run | cabinets | stools | vending | file cabinets | poster boards |
|---|---|---|---|---|---|---|
| deli_a01 | 9325 | 2 | 2 | 3 | 9 | 1 |
| deli_a01 | 9326 | 2 | 2 | 4 | 10 | 2 |
| pharmacy_a01 | 9325 | 1 | 1 | 1 | 2 | 3 |
| pharmacy_a01 | 9326 | 2 | 2 | 1 | 2 | 3 |

pharmacy_a01 has its second cabinet, against the retail floor's partition. deli_a01's two cabinets no longer take
fillers' slots. Its vending machine, file cabinet and poster board come back.

**Found here, fixed in Deli Counter 0.231.1:** deli_a01's two cabinets now both stand in the customer floor, and
both instance one machine (`prop_video_poker_delco_1997_07_..._n1`, twice). A fixture's variant is its name's
crc32, and the two names drew the same one. The library held six such rooms, all delis. 0.231.1 makes the cabinet
`distinct`, a dial the poster runs already use, so the second one moves to a different variant; no placement
moves.

**The light bake** lists module files, not instances, so its dynamic set reads 8 -> 8. deli_a01's two cabinets
share one file there, and pharmacy_a01's two are two files. Baked models 352 -> 353, users 3,160 -> 3,171.

**The clean job** took one workspace, cold-9322-ws (1.4 GB), whose record is pushed and which is now beyond the
newest four.

Not priced on its own: the next run, on 0.231.1, is priced against 9325 for both releases together.
