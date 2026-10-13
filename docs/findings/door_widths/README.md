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
3. **Leave it.** The warnings stay unread, which is the state 197 named as the defect.

The contract's own rule (CLAUDE.md) is that a changed field means re-deriving every field built from it,
not editing one number. Measured and not decided here.
