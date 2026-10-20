# The open floors, sorted by room pair (roadmap 260, from 255)

The walker, 2026-10-19: "go ahead with the 255 table, your defaults are good" -- after being unsure how to sort the
49 open floors 255 left them, because "we aren't making the doors in level factory because we are going to have
networked doors added later", and after it was shown that a Deli Counter wall carries its own openings and that every
door opening already ships to gameplay as a door socket (`interactives.json`). Built as Deli Counter 0.234.0
(`patches/patch_dc_open_floor_table.py`, records in `patches/dc_open_floor_table/`).

## Measured first

`pairs.py` (Deli Counter 0.233.0's own functions, `pairs.out.txt`, `pairs.json`): 49 open floors in 26 specs, **20
pairs of room ids** -- not 17, the count first put to the walker, which grouped the three forecourt pairs, the three
cold-room pairs and the two deck pairs too loosely.

- **7 of them lay on a footprint's own edge**: every gas station's forecourt meeting its shop, stockroom or restroom
  along y -11. The exterior wall stands there, with two 1.8 m front doors and two windows; the open-floor rule read
  partitions only.
- **12 pairs already shared a door**: their wall stopped 1-4 m short of the exterior wall at its ends (the slop 0.222.0
  fixed in the delis' basement).
- The rest had no wall on the line at all: the delis' kitchens (20 m), corner_deli_heist_01's cold rooms (3.6-5.25 m),
  the office's lobby and bullpen (34 m), and the open-plan pairs.

## Two defects found on the way, both fixed in 0.234.0

1. **The open-floor rule did not count exterior walls.** `census.py` over the library's 128 specs with rooms, with
   that reading alone (`census_exterior_walls_only.json` against `census_0233.json`): L26 49 -> 42, the tactical graph
   1,362 edges -> 1,358 -- forecourt to stockroom in all three stations, forecourt to restroom in one, each through a
   wall with no door -- and L12 and L24 unchanged. `tactical.exterior_parts` / `exterior_sides`; layout_lint's
   `_story_parts` / `_exterior_sides`, which read `LevelSpec`'s defaults (`auto_exterior` defaults to true).
2. **A room could not carry `open_to` into the typed spec.** The schema has admitted it since 0.223.0, but
   `spec_loader`'s `Room(**r)` refused any spec naming it. Found by the census: the first run after the migration
   raised on all 16 specs given `open_to`. Nothing had used the field until now.

Also found: `census.py`'s first two runs compared nothing. `tactical.build_graph` returns the adjacency dict, while its
docstring said "(adjacency, info)"; unpacking raised on all 128 specs in both arms, so "no graph change" was two
identical errors. Kept as a lesson, not a result: the third run reads the graph, and 0.234.0 corrects the docstring.

## The calls the geometry made

Each row of `open_floor_rules.RULES` is the walker's default except three, all OPEN because a stair stands on the line:

- **The office's lobby and bullpen** meet along y 0, where `office_stair_0` stands at (0, 0); a wall would cut it.
- **corner_deli_heist_01's stair well and its two cold rooms**, found by the full lint (`full_lint.py`):
  - `main_stack` reserves y 6.05..12.65, so a wall on the well's south edge (y 6.25) runs inside the stair (L21).
  - A wall on its north edge (y 12.95) ends on the x -13.2 wall at the centre of `cold_n_access` (L18).

The first migration built both walls; the census looked only at L12, L24 and L26 and passed them. The **full** lint, run
on every migrated spec before and after (`lint_0233.json`, `lint_0234.json`), refused them. Two more findings came out
of that lint run:

- **All six delis' new kitchen walls** (x 7, y -14..6) ended 0.1 m from the stockroom gate's aperture on the y 6 wall,
  where L18 needs 0.3 m of jamb. L18's own prescription -- "nudge the opening along its wall" -- is now part of the
  table: each gate slides 0.5 m west, one grid cell, and it still joins the same two rooms.
- **The table now takes a WALL row back whole** when it would leave a spec failing any lint rule it passed, so it
  cannot write a wall the builder or the lint refuses.

After that, no new lint FAIL in any of the 23 migrated specs, and two new warnings, both expected:
- one fewer identical cover box in apartment_walkup_a01, from the refurnish;
- L24 on rowhouse_raid's basement vault. It is the objective, behind a reinforced door and a breach; the walker's rule
  of 2026-10-06 keeps an objective breach-only, and `walk_reach_baseline.json` says so.

## The library after

Read off `census_0234.json`, the proven clone, which the real repository matches byte for byte:

| | 0.233.0 | 0.234.0 |
|---|---|---|
| open floors nobody named (L26) | 49 | 0 |
| rooms nothing reaches (L12) | 0 | 0 |
| rooms reached only by breaching (L24) | 4 | 5 (the vault) |
| tactical graph edges | 1,362 | 1,358 (the four through the forecourt wall) |

Every walled pair kept a way through: no edge between two rooms was lost except the four that crossed a wall without
a door.

`stair_legs.py` (`legs_0233.txt`, `legs_0234.txt`) names the one stair leg the walls moved:
- the cold-room wall at x -16.8 stands where `main_stack`'s storey -1 side guard stood (x -16.6, y 6.05..6.25);
- the guard is dropped as covered, and the leg keeps its back;
- test_stair_back's pinned library counts move 34/17/15 -> 33/16/14 accordingly.

The refurnish moved three specs, all by the new doors; the untouched library refurnished moves none. Details are in
the CHANGELOG.

## Not shown yet (as of 0.234.0; see below for what has been since)

- A frame of any of it. *Since: cold run 9338's frames of deli_a03, `docs/cold_runs/cold_9338/`.*
- A cold run on a level whose lot carries one of the 23 specs. *Since: 9338, restaurant_row_001 on 0.234.0, 0
  interventions; 0.235.0's is the next.*
- The networked doors themselves, which are the gameplay layer's.

## The first cold run: a wall under the drop (Deli Counter 0.235.0)

Cold run 9338 (restaurant_row_001, whose lot places deli_a03) ran on 0.234.0 with 0 interventions. Its frames show
the kitchen wall and its door from the aisles, and the slid stockroom gate, as `plans/plans.html` drew them. They
also show the wall running up into the delis' 2.2 m drop at (8, -4), the "vertical attack angle". The hole spans
x 6.9..9.1 and the wall stands at x 7, 0.35 m thick, so its top shows 0.275 m into the hole along all 2.2 m of it, and
the new door sits under the hole. Level Factory's drop-edge gate saw it as 7 fewer unguarded edges on that slab: its
column probe read the wall's top as floor.

**Measured across the library before any fix.** `holes_over_walls.py` checks each authored partition against every
hole in its ceiling, the centreline deciding as `partition_bounds.hole_cuts` does. It finds 8 walls under a hole on
0.233.0's specs and 14 on 0.234.0's. The six new ones are exactly the six delis -- the kitchen wall under the drop --
and nothing else the table made (`holes_over_walls_0233.json`, `holes_over_walls_0234.json`, their `.out.txt`).

**That probe over-counted, and is kept as it ran.** It read partitions as authored, but the builder cuts a partition
over a hole in its own floor (roadmap 114). Two storey-1 walls of final_stand's and
cbp_town_finale_midbalanced_schemafixed's two-storey atriums, which it counted under the storey-2 hole, are cut away
over the storey-1 hole beneath them and stand nowhere under the one above. Its four stair rows are stair enclosures
0.05 m inside their hole's edge, which is L21's business. And it missed one: its strict centreline let through bank's
wall at x 4, whose centreline sits on its atrium's edge with half its thickness under the hole.

**The rule: layout_lint L27** (Deli Counter 0.235.0, advisory). It names every BUILT partition (`built_walls`) that
reaches past the edge of an authored hole in its own ceiling by more than a touch (0.02 m). Authored holes are
`slab_holes` plus the floor_hole and hatch links that cut the slab; a hole in both lists is one hole.
`l27.py` runs it over a folder of specs:

| specs | L27 rows |
|---|---|
| 0.233.0's library (`l27_0233.out.txt`) | 3: final_stand's ground-floor wall under its atrium (0.30 m into it, along 10 m), cbp_town_finale_midbalanced_schemafixed's (0.30 m, 28 m), bank's at x 4 (0.15 m, 6 m) |
| 0.234.0's library (`l27_0234.out.txt`) | 9: those three, and the six delis (0.275 m, 2.2 m) |
| 0.235.0's folder (`l27_0235.out.txt`) | the three; and, among Level Factory's `lf_*` transients, cold run 9338's three restaurant_row_001 shells (built on 0.234.0, rebuilt each run) and ten category5_baie_dore_001 shells of 2026-09-13 |

The baie_dore rows are `presets.casino_tower`'s: its count-room skylight, a 1.4 m breachable hatch at (14, 8) in
storey 1's floor, is centred on the storey-0 wall at y 8 between the gaming floor and the cashier cage. That predates
the table, and L27 is the first thing to name it.

**The fix: the hole moves, not the wall** (L21's rule for a stair: the rooms are the plan). `open_floor_rules` now
slides a hole off any wall its table lays: across the wall, whole grid cells, toward the side holding the hole's
centre, until it opens into the one room below and no wall stands under it. If it can't, the pair is refused. It also
slides a hole off a standing wall between a WALL row's pair, so running the migration again moved the six delis'
drops 0.5 m east, to (8.5, -4): x 7.4..9.6, all in the kitchen, slab hole and link together.

Refurnished (`refurnish_0235.out.txt`): in three delis the storey-1 dining table had stood within furnish's 0.3 m of
the new hole, so in each 6 pieces moved and a chair went. The rest of the library refurnished moves nothing. Lint on
the six before and after, with L27's code both times (`holes_lint_before.json`, `holes_lint_after.json`): no FAIL on
either side, and the only warning gone is L27's.

**Left as named:** the three library walls that stood under a hole before the table, and casino_tower's skylight.
final_stand's and cbp_town_finale's ground-floor walls cross under their atriums, their tops a 0.3 m strip across the
void; bank's shows half its thickness at its atrium's edge; the skylight drops onto a wall. L27 names each on every
lint. Moving them is the factory's next call on this rule, not this change's.
