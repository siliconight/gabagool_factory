# Interior furnishing: rooms that read as what they are

The walker, cold run 9052, in `country_club_a01`'s basement: "need a lot more
species for this room, its just a bunch of chairs and tables with nothing on
it, boring". This is the plan the survey of 2026-09-13 produced, kept here so
the Deli Counter and Zoo work is built from a written spec, not a transcript.

## What was measured

- **The room is `wine_cellar`** (objective_room, 560 m2). "objective_room
  wine_cellar" contains no `_FURNITURE` keyword, so `furnish` fell to
  `_FURNITURE_DEFAULT` and round-robined `table_low` + `chair` 14 times
  (`deli_counter/level_design.py`, rotation `pieces[k % len(pieces)]`), and each
  table added up to two `chair_set` chairs: 27 pieces, 2 species.
- **272 of 691 library rooms hit the default row**: every kitchen (11),
  basement corridors (6), count rooms (5), deli counters (6), market aisles,
  stairwells, apartments. Substring matching also misroutes: "hall" sends
  `cellar_hall` and `under_hall` to lobby counters; "service" sends
  `food_service` to workbenches; `store` is not a keyword.
- **One size per species means one mesh repeated**: Zoo names a module by
  species, theme, style and exact dims (`zoo/zoo_keeper/core/kit.py`), so
  `country_club_a01` built six unique furniture GLBs for 97 pieces.
- **Nothing places items on furniture.** Zoo's sockets
  (`ATT_surface_center` on table and desk, `ATT_top_center`, `ATT_register*`)
  are read only by the Godot editor dock. Patina's dressing is exterior trim and
  site ground clutter; buildings are exclusions.
- **Species exist that nothing places or that routing blocks**: pallet_stack
  (`pallet` routes to a plain box), bench (caught by the chair row),
  water_barrel, crt_tv, flat_top_grill, queue_stanchion, litter_bin,
  security_camera, payphone.

## The plan

**Matching.** Split a room id on `_` and match whole tokens; id tokens first,
then role; storey < 0 is a basement modifier.

**Each kind is a recipe, not a round robin**: 1-2 anchors, about half the
target as a wall run, the rest as clusters of 2-4 pieces packed 0.3-0.8 m apart.

| Kind | Id tokens in the library | Anchors | Wall run | Clusters |
|---|---|---|---|---|
| Basement / cellar | basement, cellar, under, lower; any storey < 0 not matched below | furnace, water heater | stocked shelving, old filing cabinets, workbench | carton stacks, pallet stack, barrels, dust-sheeted furniture |
| Wine cellar | wine, barrel | wine racks | racks | barrels, tasting table with 2 chairs, cartons |
| Storage / stock | storage, stock, store, parts, supply, archive, records | shelving aisles | shelving, filing cabinets | cartons, pallets, hand truck |
| Mechanical / utility | utility, server, boiler, mech, plant | water tank or furnace | electrical panel, shelving | barrels, cartons, bin |
| Club lounge / bar | lounge, club, bar, dining | bar counter with stools, pool table | booth seats, trophy shelving, dartboard, cigarette machine | tables with mixed chair counts, TV on a stand |
| Office | office, manager, exec, suite, security, control | desks with chairs | filing cabinets, shelving, water cooler | CRT on desk, cartons |
| Kitchen / deli | kitchen, deli, prep, cooler | flat-top grill | counters, shelving, reach-in cooler | work table, bin; condiments and cups on counters |
| Locker room | locker; staff_only role | locker banks | lockers | bench, cartons |
| Vault / count / cage | vault, count, cage, safe, evidence | safe deposit boxes, safe | shelving | count table with cash stacks, security camera |
| Lobby / waiting | lobby, waiting, reception, concourse | counter | waiting chairs, ATM, vending, payphone | queue stanchions, bin, low table |
| Garage / bay / dock | garage, bay, dock, loading, workshop | workbench | shelving, tool cabinets | drums, pallets, hand truck |
| Apartment | apartment, bedroom, living | sofa with TV | dresser, shelving | table with 2 chairs, cartons |
| Corridor / stairwell | corridor, approach, landing, stair | none | at most 1-2 wall pieces | none |
| Fallback | anything else | none | wall run | one cluster |

**Variety rules.** At most 3-4 pieces of one (species, size) per room; 0-4
chairs per table from the seed, some pulled out or turned 10-20 degrees; a
small size palette per species (about 3 per building); tall pieces stay on
walls and the shelter piece still goes first in combat rooms.

**Items on surfaces are built into the host recipe** (Zoo `_surface_stock`,
the `_shelf_stock` precedent), with the flavour chosen by DC from the room kind
(office, bar, kitchen, vault, storage) and carried in the slot and the module
name on both sides (`zoo_keeper/core/kit.py` and `deli_counter/themed_tscn.py`
`module_stem`), or tables of one size keep sharing one GLB.

**New Zoo species, by impact**: carton_stack; furnace / water heater;
dust_sheet; pool_table; booth seat / sofa. Next: wine rack, reach-in cooler,
dartboard, hand truck, water cooler.

## Status

2026-09-13: Zoo branch `interior-species` in progress (the five species and
surface stock). Deli Counter's furnish rewrite follows once that lands.
