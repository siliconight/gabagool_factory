# Doors against the contract's 1.25 m: a decision for the walker (roadmap 197)

Roadmap 197 ends on three of the generated deli's doors standing under `agent_contract.json`'s
`clearances.min_door_width_m`, 1.25 m, "flagged by a warning nothing reads". Grounding that found the number
itself out of step with the contract.

## The contract against itself

`clearances.derivation` reads: "min_door_width >= 2*ceil(agent_radius/cell_size)*cell_size + 2*cell_size ->
2*ceil(0.4/0.15)*0.15 + 0.3 = 1.2; ratified 1.25 for margin." That is worked at a 0.15 m cell. The
contract's own `nav_bake.cell_size_m` is 0.10, and Laser Tag's bake (`run_map_eval.gd`'s `NAV_CELL_SIZE`) and
the staged levels' navmeshes are baked at 0.10. At that cell the same formula gives 1.00 m.

## The library (`door_census.py`, `door_census.out.txt`)

Every door in Deli Counter's 152 library specs (the `lf_*` transients left out):

    enterable doors by width:   1.00 m: 13   1.10 m: 74   1.20 m: 113   1.25 m: 418   wider: 381
    under the contract's 1.25:  200 doors, in 32 of 132 enterable buildings
    under the formula's 1.00:   none
    shut doors in Empties:      36, not counted -- nothing walks through them

- **Width-less doors.** A spec door with no `width` builds at Deli Counter's default, 1.2 m
  (`meshlib_kit.DOOR_W`; read off the built shells: `bank`'s seven, all 1.2). That accounts for 47 of the
  113 at 1.2 m. The builder's own default is under the contract's minimum.
  *Owner retracted, 2026-10-13: the default is `spec_types.Opening.resolved()`'s, which `deli_counter.py`
  builds every opening from. `meshlib_kit.DOOR_W` is the optional GridMap kit's doorway and nothing
  imports it. The same 1.2, the wrong file.*
- **Not counted.** Two demos' shells do not account for their width-less doors (`kitbash_demo`,
  `rarity_demo`), and their doors are left out.
- **Who carries them.** The buildings with most: `foundry_heist_vertical` (24), `final_stand` (18),
  `cbp_town_finale_midbalanced_schemafixed` (13), `corner_deli_heist_01` (12). The rowhome-and-strip
  presets carry staff and office doors of 1.1 to 1.2 m.
- **They pass the bake.** Deli Counter's nav gate passes 150 shells at the contract's bake. Every one of
  these doors is at least the 1.00 m the formula gives.

## The decision

The 1.25 is used for more than the warning. Deli Counter builds from `min_door_width()`:

- the island aisle (`level_design.island_aisle_width`);
- the stair landing's opening (`stairwell`, `0.8 + min_door_width`);
- the staff door (`level_design._STAFF_DOOR_WIDTH = 1.25`, written as the contract's number).

So moving the number moves generated geometry in every building that has one of them, and every lot drawn
from them.

1. **Re-derive it at the contract's own cell.** That is 1.00 m by the formula, plus whatever margin is
   ratified as the 0.05 was. Most of the 200 stop being findings. Aisles, landings and staff doors could
   narrow, unless their callers are pinned to their present widths first.
2. **Keep 1.25 as a design minimum, not the bake's.** Write the derivation as such: two bodies passing, a
   readable doorway. Widen the 200 doors in their presets and the builder's 1.2 default, as a
   preset-by-preset change, priced and cold-run.
   *"Two bodies passing" retracted, 2026-10-13: two 0.35 m bodies side by side need 1.40 m. 1.25 m passes
   one body with 0.275 m a side, and that is what the derivation should say.*
3. **Leave it.** The warnings stay unread, which is the state 197 named as the defect.

The contract's own rule (CLAUDE.md) is that a changed field means re-deriving every field built from it,
not editing one number. Measured and not decided here.

## The walker's call, 2026-10-13

"If we change the door widths, that's ok, it should be called out in the agent contract." Read as option 2:
1.25 stays as a design minimum, the doors widen to it, and the contract says so beside the number. The
walker was asked to say if they meant the other way (lower the number, leave the doors); no answer yet.

## Option 2, measured in a scratch copy (Deli Counter 0.214.0, NOT APPLIED)

`_scratch/2026-10-13_door_width/deli_counter` is Deli Counter 0.213.0 with the change; `dc_head/` beside
it is 0.213.0 untouched (`git archive HEAD`), the control. The drafts are in `drafts/` there.

- **The library.** The draft `migrate_door_width.py` widens 152 authored doors in 29 specs, each about its
  own centre. One slides along its wall: `final_stand`'s `west_entry` failed L18 (a partition ending
  0.90 m from its centre where the lint needs more than 0.93), so it moves to 1.00 m clear. One is KEPT:
  `primos_pizza`'s `kitchen_stairs`, where 1.25 fails L18 in place and L21 (0.12 m over the basement
  stair's hole) slid clear, so it stays 1.20 m until the stair moves. The 47 width-less doors take the
  new default. `layout_lint --all`: 0 FAIL, 391 WARN, the same findings before and after. The 34 specs
  whose shells change were rebuilt; `door_fit.py` read 32 (the two demos have no build), 0 narrow, 0
  overlapping.
- **The presets** (`preset_door_sweep.py`). 61 literal doors in 15 enterable presets, 34 at 1.1 m and 27
  at 1.2, become `presets.DOOR_W`; the Empties keep theirs. Two seeds' modes: 304 variants, FAIL 768
  before and after, the same preset by preset and rule by rule, doors under 1.25 1,568 -> 0.
  `--variants`, the adapter's other inputs (three modes, 1 to 4 floors, basement or not where taken):
  432 variants, FAIL 1,044 both ways, the same by preset and rule, doors under 1.25 2,148 -> 0.
- **Stairs-first** (`stairs_first_doors.py`, on `stair_regression`'s own seeds). `stair_core` punches a
  door where an enclosure crosses a stair landing, at `_PUNCH_DOOR_W` 1.1 m: 20 in 140 variants. At 1.25
  it punches none -- every one of those crossings is shorter than 1.25 -- and `stair_regression`'s
  checks fail 21 times against 2. So it stays 1.1 and the contract names it. Level Factory never builds
  stairs-first. The same function sized a width-less door at a literal `or 1.2` when asking whether a
  crossing is already doored; read through `Opening.resolved()` instead, the 140 specs are byte-identical
  (sha256 35e2a857... both ways; the 1.25 run, the control, moves it to 6c417af7...).

## Found while grounding the patch, not attributed

- **Three spec doors missing from their built shells.** For the library's enterable shells the built
  `gameplay.json` files hold 197 doors under 1.25 where the specs resolve to 200. The three:
  `cbp_town_finale_midbalanced_schemafixed`'s `broadcast_to_scoreboard_maintenance` (1.2),
  `foundry_heist_vertical`'s `loading_south_to_north` (1.2) and an untagged 1.1 in `night_pawn`.
  Whether the builder drops them, and why, is not read yet.
- **Two orphan builds.** `deli_counter/build/` holds `fuel_stop_heist3` and `fuel_stop_heist4`, whose
  specs are not in `specs/`, with 12 doors under 1.25 between them. `gameplay.json` is ignored by git, so
  these are this machine's. A test over built shells must read the library's shells, not every file in
  `build/`.
- **A second spelling the change leaves.** `level_design._STAFF_DOOR_WIDTH` is a literal 1.25 commented
  "agent_contract min_door_width_m": the staff door does not follow the contract if the number moves.
  The island aisle and the stair landing's opening do (`island_aisle_width`, `stairwell`'s `0.8 +`).
- **The validator warns.** `navigability.check` reports a door under the minimum as a WARNING (and drops
  it from its agent graph). The factory's `docs/AGENT_CONTRACT.md` says the validator "enforces" it.
- **Lot carries the refuted cell.** `lot/site_cover._NAV_BAKE_FALLBACK` is `cell_size_m` 0.15, and its
  docstring derives 1.2 from it. Lot passes the contract's bake to `plan_cover`, so the pinch threshold is
  the contract's 1.00 -- but `LOT_COVER_PINCH`'s message calls `min_passable_gap()` with no bake and
  prints 1.2 m.
  **Fixed in Lot 0.120.2** (9be94e0, `patches/patch_lot_cover_fallback.py`): the fallback is the
  contract's 0.1; `CoverPlan.passable_gap` carries the threshold `plan_cover` derives from the bake it
  gives `pinches`, and `findings` states it; `lot/tests/test_cover_fallback.py` holds both copies Lot
  carries (`lot._AGENT_DEFAULTS` as well, 21 shared keys, no drift) equal to the contract, the shape of
  Deli Counter's `test_every_fallback_equals_the_ratified_value`. The comment's claim that Level
  Factory's `lasertag_contract` reported drift was false: it never reads `nav_bake`. Built sites do not
  move -- `cover_fallback_ab.py` (`cover_fallback_ab.out.txt`) replays cold run 9284's club_block_014
  seed_9080 Lot job from its `job.log`: 53 of 53 files identical before and after, and to the cold run's
  own. None of the 261 Lot job logs on this disk carries a `LOT_COVER_PINCH`, so the stale 1.2 m never
  reached one. One test moved with it: `test_site_cover_slots`' too-tight lane was a literal 11.0 sized
  at the fallback's 2.7 m clearance, and at 2.5 m a truck fit exactly.

## What is left

The anchored patch: `spec_types`'s default at the contract's number; `stair_core`'s resolved width; the
presets; the migration and the 29 specs; `agent_contract.json`'s `clearances.derivation` rewritten at the
0.1 cell with 1.25 called a DESIGN MINIMUM, and a `min_door_width_note` recording what widened and the
two doors that did not; `test_door_width.py`; the changelog. Then `build.py --all`, the gate, and cold
runs on the missions whose buildings change. The draft test reads every file in `build/` and must read
the library's shells instead (the orphans above).
