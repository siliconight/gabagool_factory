# Cold run 9375 -- 0 interventions; restaurant_row_001, seed 9003: roadmap 292, the enemy's body is the contract's

**What it was for.** The factory's roadmap 292, shipped across three tools: Level Factory 0.231.0 (d3cf8d5) writes
the enemy's eye from the contract's NPC body -- `characters.npc_standard`'s, the player's while it states none --
into every Laser Tag run; Lot 0.126.1 (dc4e2a6) drops its contract fallback's mirror of the NPC's two numbers; Deli
Counter 0.253.0 (ca7e45a8) settles the NPC body and the sight heights in the contract, the bodies deciding and the
`sightlines` copies checked against them. With the shipped contract's one body nothing in the level should move:
cold run 9374's level again, staged from it, those three the only tools that moved.

**Tools** (`before.json`, every repo clean at `--begin`): Level Factory 0.231.0, Lot 0.126.1, Deli Counter 0.253.0;
the rest as 9374 -- Zoo 1.120.1, Lux 0.79.0, Dispatch 0.5.3, Patina 0.32.0, Laser Tag 0.32.0, Pipeline 0.6.0,
Pixelcoat 0.62.0.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0); 9.3 min (16:44:03 to 16:53:24). Shell 0
blockers of 79 findings; art 108. The `--end` line's FAILING is the factory root's hygiene counting this block's own
records before they are committed, not the run.

**What it shows** (`patches/dc_npc_body/cold_compare.py` and its `.out.txt`; 9374's staged scenarios and record read
from copies taken before its workspace was retired):

- **The scenario the run writes is the one it wrote.** Each of the three Laser Tag candidates' `mission_scenario.tres`
  is byte for byte 9374's, 1,326 bytes, with `player_eye_height_m = 1.6`, `enemy_eye_height_m = 1.6` and
  `aim_height_m = 1.0`: the enemy's eye now comes from the contract, and the contract's NPC states no eye, so it is the
  player's 1.6 -- the stock's own figure. What a stated body does is proven by the tests (Level Factory's
  `patches/lf_enemy_eye/prove_tests_on_0230.out.txt`, Deli Counter's `patches/dc_npc_body/prove_tests_on_0252.out.txt`).
- **The findings are 9374's**, 108 by code, candidate and message.
- **The bake is 9374's**: 153 models and 118 primitive meshes lightmapped, 2,940 users.

**The walk copy** is `_runs/walk_9375_restaurant_row_001` (the drive wrote it to `_runs/walk_export_restaurant_row_001`
and it was renamed after the run, as 9374's was).
