# Cold run 9370 -- 0 interventions; restaurant_row_001, seed 9003: Deli Counter 0.248.0, the office's floor is an office

**What it was for.** The factory's roadmap 281: the office preset's open storey over the bullpen, `floor_1`, read as a
shop floor by the word `floor`, and cold run 9369's frame of it showed litter bins standing mid-floor among cartons.
Deli Counter 0.248.0 (88422d0b) reads an office building's `floor_N` as an office. Cold run 9369's level again --
restaurant_row_001 at seed 9003, staged from it -- Deli Counter the only tool that moved.

**Tools** (`before.json`, every repo clean at `--begin`): Deli Counter 0.248.0 (88422d0b); the rest as 9369 -- Zoo
1.120.1, Level Factory 0.228.0, Lot 0.126.0, Lux 0.79.0, Dispatch 0.5.3, Patina 0.32.0, Laser Tag 0.32.0, Pipeline
0.6.0, Pixelcoat 0.62.0.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0, retries 0); 9.3 min (08:12:54 to 08:22:13).
Shell 0 blockers of 79 findings; art 108; **findings 108 -> 108 against 9369**. The export's bake: 153 models
lightmapped, 2,955 users against 9369's 2,954.

**What moved** (`docs/findings/office_floor_281/`): the office's floor_1, a service counter, three vending machines, two
filing cabinets, four shelf runs, four cartons and four litter bins -> four desks and their chairs, three shelf runs,
six filing cabinets and five cartons; the office's merged meshes 290 -> 302, every other building's the same. The
frames (`floor_1_9369_9370_lit.jpg`, `_inspect.jpg`): the desks stand where the bins stood, their screens lit; the
bullpen, the frames' control, does not move; every other station within 1.1 % of 9369's pixels.
