# Cold run 9379 -- 0 interventions; restaurant_row_001, seed 9003: every building's package carries its scout view

**What it was for.** The factory's roadmap 296, the walker's answer on the drawings review page: the axonometric is too
busy to scout from on two of three buildings -- "simpler but carry all of the signals needed". Deli Counter 0.258.0
(fa09f52b) draws each building a second way, with only what a body finds its way by, into its package as
`drawings/scout.svg`; Level Factory 0.233.0 (b2a6ec5) names it in `buildings.json`. Cold run 9378's level again,
staged from it, those two tools the only ones moved.

**Tools** (`_runs/cold/cold_9379/before.json`, every repo clean at `--begin`): Deli Counter 0.258.0, Level Factory
0.233.0; the rest as 9378 -- Lot 0.126.1, Zoo 1.120.1, Lux 0.79.0, Dispatch 0.5.3, Patina 0.32.0, Laser Tag 0.32.0,
Pipeline 0.6.0, Pixelcoat 0.62.0.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0); 11.4 min (16:04:01 to 16:15:27). The `--end`
line's FAILING is the factory root's hygiene counting this block's own records before they are committed, not the run.

**What it shows** (`patches/lf_scout_view/package_check.py` and `cold_compare.py`, each with its `.out.txt`; 9378 read
from its own workspace, still on disk):

- **The level is 9378's**: the three staged scenarios byte for byte, the 108 findings by code, candidate and message,
  the bake's 153 models, 118 primitive meshes and 2,947 users.
- **Every building carries its scout view**: deli_a03, pharmacy_a01 and office each name `scout` in `buildings.json`,
  each `scout.svg` present beside the keep `.import`, none made a texture (the walk copy's import cache, 2,875
  entries, holds textures of two SVGs only, the package's icons), and each the same bytes Deli Counter draws from its
  spec today (49,399, 9,144 and 41,907 bytes). The 26 Empties say null, a facade's reason kept. The closure verdict
  clean.
- **Nothing else moved**: the package has six files more than 9378's -- the three scout views and their imports --
  and none fewer.

**The walk copy** is `_runs/walk_9379_restaurant_row_001` (the drive wrote it to `_runs/walk_export_restaurant_row_001`
and it was renamed after `--end`, as 9378's was).
