# Cold run 9369 -- 0 interventions; restaurant_row_001, seed 9003: Deli Counter 0.247.0, the deli's market stands aisles

**What it was for.** Roadmap 148, the look review of 2026-10-19: the rooms "Too sparse". Deli Counter 0.246.0
(d94c6c0f: a room counts only what stands on its own storey) and 0.247.0 (e1cbd7e1: a corner store's selling floor
stands its aisle gondolas in rows) in a shipped package: cold run 9368's level -- restaurant_row_001 at seed 9003,
staged from it -- with Deli Counter the only tool that moved.

**Tools** (`before.json`, every repo clean at `--begin`): Deli Counter 0.247.0 (e1cbd7e1; the doctor's line agrees);
the rest as 9368 -- Zoo 1.120.1, Level Factory 0.228.0, Lot 0.126.0, Lux 0.79.0, Dispatch 0.5.3, Patina 0.32.0,
Laser Tag 0.32.0, Pipeline 0.6.0, Pixelcoat 0.62.0.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0, retries 0); 8.3 min (06:33:23 to 06:41:38).
Shell 0 blockers of 79 findings; art 108; **findings 108 -> 108 against 9368**. The export's bake: 155 models
lightmapped, 2,954 users against 9368's 2,907.

**What moved, read from the specs** (`docs/findings/denser_rooms_148/`): deli_a03's market aisles 9 -> 18 furnished
pieces and 5.7 -> 19.7 % of the floor under furniture -- nine 4.8 m snack gondolas in five rows, two continuing its
own aisles' lines, which are snack gondolas now too; and the count fix's rooms -- deli_a03's server room 9 -> 10
pieces, the office's floor_1 5 -> 18, its exec_lobby 16 -> 18 and exec_anteroom 10 -> 11. pharmacy_a01 did not move.

**The frames** (`rooms_9368_9369_lit.jpg`, `_inspect.jpg` there, from `tools/room_stations.py`'s stations, the same
in both): the market aisles go from two black shelves on an empty tiled floor to stocked aisles running the room; the
office's floor_1 gains carton stacks, a shelf run and three litter bins standing mid-floor -- the count fix filling a
room its id makes a SHOP floor (`floor` is a shop-floor word), which is the next defect, not this one's; every other
station within 1 % of 9368's pixels.
