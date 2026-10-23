# Cold run 9383 -- 0 interventions; restaurant_row_001, seed 9003: a building is clicked in the scout window

**What it was for.** The factory's roadmap 295, the walker: "(also clicking on the buttons in the screen should
change the buildings)". Level Factory 0.236.1 (ee4740e, `patches/patch_lf_scout_click.py`), the only tool moved;
staged from 9382. The walk copy handed to the walker to try.

**Every leg ran, `INTERVENTIONS: 0`**; 8.9 min (21:18:24 to 21:27:15).

**In game** (`patches/lf_scout_click/g9383_f6.png`, the walk copy `_runs/walk_9383_restaurant_row_001`, F6 pressed
after `warmup_finished`): the window opens on deli_a03, 348 draws, 5.28 ms a frame over 2 s, the first open's worst
frame 266 ms. The click itself was driven through the seam and as a mouse press on the overlay in the scratch project
(`patches/lf_scout_click/drive_click.gd`), not by the in-game probe, which presses keys only.
