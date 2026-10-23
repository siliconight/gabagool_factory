# Cold run 9382 -- 0 interventions; restaurant_row_001, seed 9003: the scout window focuses floors, tilts, spins on

**What it was for.** The factory's roadmap 295, the walker's first try of the scout window in cold run 9381's walk
copy: "the up and down isn't working? also is there a way to prioritize the view to focus on where you are as you
rotate it so there isn't corners that just stay covered", vertical tilt, a spin that carries on, a slow automatic
turn, the scroll wheel for floors. Level Factory 0.236.0 (f61a9f1, `patches/patch_lf_scout_focus.py`), the only tool
moved; staged from 9381.

**Every leg ran, `INTERVENTIONS: 0`**; 9.0 min (20:46:19 to 20:55:19).

**In game** (`patches/lf_scout_click/g9382_f6_next.png`, the walk copy `_runs/walk_9382_restaurant_row_001`, F6 and
the right arrow pressed as keys after `warmup_finished`): the window opens and steps to the pharmacy, its note line
"WHOLE BUILDING - DRAG TO TURN AND TILT - UP/DOWN: FLOOR"; the player held -- `pos x -2.2` before and after, where
9381's walked to -1.6. The first open's worst frame read 1,307 ms here against 239 ms on 9381 and 266 ms on 9383, on
the same package bar the window's script: one reading, not explained, kept with the first-open hitch owed.
