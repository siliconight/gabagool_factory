## [0.222.0] - the delis' basement divider runs wall to wall, and the utility room gets a door

**The walker's walk of cold runs 9305-9307, finding 5** (the factory's `docs/findings/walk_2026-10-14/`). In
deli_a01's basement: "this wall supposed to stop here and have this big opening?".
- **Traced:** the divider along X at y 1.0 stood x -12..12, under rooms that meet across the whole basement,
  x -19..19. That left 7.00 m open at each end:
  - the corridor into cold storage;
  - the utility room into the vault, the objective room, beside the 1.4 m breach that was its way in.
- **Its origin:** 0.80.0's `presets.corner_deli` authored it so. Its other partitions all run wall to wall, and it
  was carried into all six delis.
- **Asked, the walker chose: "close the basement".**

### Changed
- **`presets.corner_deli`:** the divider runs `-half_x..half_x`. Its door and breach keep the positions 0.221.0
  built: snap(-0.35 * 24) = -8.5 and snap(0.3 * 24) = 7.0, now -8.5 / 38 and 7.0 / 38 of the run.
- **`migrate_basement_wall.py`,** new: the one-shot, idempotent migration bringing the library to the rule.
  - It touches deli_a01, deli_a02, deli_a03, cr_deli, night_deli and corner_deli_heist_01.
  - In each, the divider and its two openings' fractions move, and nothing else does.
  - A divider of another span is refused and named.
- **The library refurnished around the new wall** (`migrate_furnish_recipes.py`, 0.214.0's pattern). The library
  is held to be a fixed point of `level_design.furnish`, and the wall moves what furnish stands beside it.
  - Measured before anything was written (the factory's `docs/findings/door_widths/refurnish_delta.py`, on a copy):
    deli_a03 alone moves, 118 furnished pieces to 117.
  - It loses one chair set at the vault's count table, which stands 0.15 m from the new wall.
- **What it changes in play:**
  - The vault is entered by its cold-room door and by breaching.
  - The utility room's only open way in had been the vault's east gap. Its other two openings are reinforceable
    breaches, which build as solid panels with colliders. A room reached only by breaching gets a door unless it
    is the objective (the walker, 2026-10-06; layout_lint L24), and `test_walk_reach` refused the closed wall
    without one. Asked, the walker chose the door.
- **`presets.corner_deli` and the migration give the utility room a door from the corridor,** tagged
  `corridor_to_utility`, as wide as the cold-room door. It sits on their shared wall midway between that wall's
  breach at y -9.0 and the divider at y 1.0, so y -4.0. In all six delis the rooms a body reaches only by
  breaching are then exactly `walk_reach_baseline.json`'s: the four server rooms ruled objectives by design.
- **`test_walk_reach.py`:** `test_deli_a01s_utility_room_is_open_floor` is now `..._is_walked_into`. The gap that
  made it open floor is closed, and its door is asserted.

### Tests
- **`test_basement_wall.py`:**
  - the preset builds the divider wall to wall;
  - all six library delis are closed, with their door at -8.5 and their breach at 7.0;
  - the migration keeps every opening, adds the door, and is idempotent;
  - the preset and every deli give the utility room its door at y -4.0, and L24's walk search reaches it;
  - another span is refused;
  - no two basement rooms meet past the divider.
- On 0.221.0 it fails: there is no `migrate_basement_wall`.

**Proven to fail first:** `test_basement_wall.py` fails on 0.221.0, at collection, there being no `migrate_basement_wall`; on 0.222.0 it passes with the two furnish fixed points (`test_deli_window`, `test_club_fixtures`), `test_walk_reach.py` and the stair tests, 41 of 42 (the 42nd reads `build/`, which the copy lacks; its question, asked directly, matches the baseline exactly) (the factory's `patches/dc_basement_wall/prove_tests_0221.out.txt`, run on throwaway copies before the repo was touched). The refurnish lost deli_a03's `chair_set_r365b5162_9_1` at (14.72, 1.99), by the new wall, and placed its partner `_9_2` again

**Suite:** `python -m pytest -q`: 1,540 passed, 2 skipped, exit 0, in 117 s -- 0.221.0's 1,533 and `test_basement_wall.py`'s 7; `test_walk_reach.py`'s renamed test stands in its old one's place, and its two library checks pass on the built library, the walk-unreachable rooms exactly the baseline's

**Build:** `python build.py --all --blender C:/blender/blender.exe`: exit 0 in 404 s. Every changed file attributed, the build folder hashed before and after (the factory's `patches/dc_basement_wall/build_diff.out.txt`): 189 of 1,483 -- the six delis' GLBs and their gameplay, combat-audit and validation manifests, with a slots manifest (navigation for corner_deli_heist_01) each, 30 files; and every shell's manifest, its `built_utc`. No other shell moved
