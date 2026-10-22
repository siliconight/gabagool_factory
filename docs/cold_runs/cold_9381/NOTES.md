# Cold run 9381 -- 0 interventions; restaurant_row_001, seed 9003: scout models and the scout window ship, F6 in game

**What it was for.** The factory's roadmap 295 end to end: Deli Counter 0.260.0 (the scout model in the walker's
handheld palette, with the score and the props of interest), Level Factory 0.234.1 (a kept model is not waited
for -- cold run 9380 stopped without it) and 0.235.0 (every package carries the scout window; the walk copy calls it
on F6). Staged from cold run 9379, the last run that shipped.

**Tools** (`_runs/cold/cold_9381/before.json`, every repo clean at `--begin`): Deli Counter 0.260.0, Level Factory
0.235.0; the rest as 9379.

**Every leg ran and the level shipped, `INTERVENTIONS: 0`** (journal 0, unattributed files 0). Export log:
"scout window: res://scout/scout_window.gd, res://scout/README.md, 3 building(s) with a schematic"; closure verdict
ok, 0 issues over 84 resources.

**What it shows** (`patches/lf_scout_model/package_check.py 9381 9379`, `patches/lf_scout_window/cold_compare.py`):

- **The package is 9379's and eight files more**: the three buildings' `scout.glb` and their keep `.import`s, and
  `scout/scout_window.gd` and `scout/README.md`. Each model the bytes Deli Counter 0.260.0 builds today (deli_a03
  209,380 bytes, 672/1,132/1,096 triangles a storey; pharmacy_a01 36,556, 432; office 122,592, 648/568/472); none
  imported (the walk copy's cache, 2,875 entries, holds textures of the package's two icons only).
- **The level is 9379's**: the three staged scenarios byte for byte; the bake's 153 models and 2,947 users; 108
  findings, 107 identical and one whose message moved -- PRESENTATION_TINT_MATERIALS counts 1,163 material entries
  under 143 names in 516 GLBs against 1,159, 142 and 512: the census reads the composed presentation package, which
  holds four scout models (the three buildings' and the mission shell's at its root, which the export leaves out),
  each one material named `scout`.
- **In game**: the walk copy, F6 pressed -- the window opens over the level, deli_a03 then the pharmacy; 319 draws
  walking, 348 and 388 open; a first-open hitch of 239 ms (`patches/lf_scout_window/README.md`, its frames).

**The walk copy** is `_runs/walk_9381_restaurant_row_001` (renamed after `--end`).
