# Cold run 9390 -- 0 interventions; restaurant_row_001, seed 9003: the price of LF 0.240.0, which it refuted

**What it was for.** Level Factory 0.240.0 (71db7a4): one lightmap chart a wall run, the cure for the walker's bands
(finding 2 of their walk of 9386), shipped with its price owed to this run and a condition -- reverted if it costs
more than it buys.

**Every leg ran, `INTERVENTIONS: 0`.** The light check: FAIL 3, PASS 33, REPORT 1, as before.

**The price, against 9389** (each package's `light_bake.json` and `.lightbake.log`): the lightmap 1024 x 17408 ->
1024 x 16384 (one layer fewer), `bake.exr` 54.0 -> 51.7 MB; the bake 36.0 -> 52.7 s (`bake_ms`), the editor's whole
run 64.3 -> 88.8 s.

**What it was for, measured and NOT delivered** (the finding's `seams/`, from the walker's eye, both packages in one
session): the back wall IS one continuous row of the lightmap now (`wall_islands_9390.out.txt`), and the brightness
step across a module joint against one mid-module went 2.0x (9389) -> 3.0x (here). The bands are not separate
lightmap charts. Reverted as Level Factory 0.240.1 (bd1e5ab); the cause is open.

The walk copy `_runs/walk_9390_restaurant_row_001`.
