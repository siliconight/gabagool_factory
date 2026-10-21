# Cold run 9360 -- 0 interventions; club_block_014, seed 9014: the crowd barriers' feet stand proud of the carpet

**What it was for.** Cold run 9359 framed arena_a02's four crowd barriers with no feet: Deli Counter lays a room's
floor finish as a 2 cm skin over the slab and stands props on the slab under it (`floors.SKIN_THICK`), and Zoo
1.118.0's 9.5 mm flat-bar feet lay wholly under the carpet. Zoo 1.118.1 draws them as 2 x 1-1/2 in rectangular tube,
1.8 cm proud of the skin. This run made 9359's level -- the same brief and batch, seed 9014 named -- on 1.118.1.

**Tools:** Zoo 1.118.1 (ea536a5); the rest as 9359 -- Deli Counter 0.242.0 (3ec97799), Level Factory 0.227.0, Lot
0.126.0, Lux 0.79.0, Dispatch 0.5.3, Patina 0.32.0, Laser Tag 0.32.0, Pipeline 0.6.0, Pixelcoat 0.62.0.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0; `_runs/cold/cold_9360/diff.json`: nothing changed, added, removed
or unattributed across the 4,354 hashed files), read after `cold_run.py --end`; 7.9 min (22:19:22 to 22:27:18).
Shell 0 blockers of 101 findings; findings 101 -> 101 against 9359, this level.

**The export, line by line against 9359's** (the workspace's name and the bake's seconds set aside): the same, every
line, 27 of 27. The barricade is still one surface in each barrier's merge cell, so nothing the export counts moved.

**The frames** (`docs/findings/crowd_barrier_267/feet_9359_vs_9360_inspect.jpg`): at the stations 9359 was framed at,
in the inspection light. 9360's barricades stand on their feet -- two rectangular tubes each, clear of the carpet --
where 9359's legs went straight into it.

**What came after.** Shown these frames, the walker asked what the barricades were for, chose "queue lanes to the box
office", and then: "metal barriers are for outdoor concerts or riot protection from police" and "retractable belt
stanchion". Zoo 1.119.0 (`stanchion_run`) and Deli Counter 0.243.0 (`ticket_queue`) take the four barricades off
arena_a02's event floor and lay the box office's queue in stanchions; the steel barricade stays a species, for the
outdoors.
