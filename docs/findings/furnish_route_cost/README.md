# What furnishing costs a route (roadmap 288)

The walker, 2026-10-21: rooms neither crowded nor barren, and above all "free nagivation and fun gun fights". The
guide filed the same day (`docs/reference/Lived_In_Levels_Clear_Navigation_4P_PVE_1999_PA.md`) asks for every width
measured after furnishing (section 5) and a dressing traversal cost: flag a route that grows more than 10 % from the
functional build to the dressed one (section 14). Nothing in the factory measured either. The nav gate asks whether a
marker is reachable, and roadmaps 148 and 281 shipped density changes with no number for what they did to movement
(`docs/findings/guides_2026-10-21/lived_in.md`, its first-ranked gap).

## The instrument

`route_cost.py`, over Deli Counter's library. Its docstring is the method. In short:

- **Two arms of one spec.** AUTHORED is the spec less every volume furnish and the shelter pass wrote
  (`migrate_furnish_recipes.furnished_by_this_pass`, `level_design._seeded_cover`). FURNISHED is the spec as it ships.
  Every other obstacle is shared, so what differs is what those two passes stood.
- **Endpoints of a room:** its walkable doors (placed by `partition_bounds.host_openings`, the builder's arithmetic),
  its open edges, and its objective and loot markers.
- **Per pair of endpoints:** the shortest path for the contract's 0.35 m body on the bake's 0.10 m grid, shifted off
  round coordinates; and the widest-path bottleneck, read against the body, the bake's door floor (1.00 m, derived
  from the contract as the contract derives it) and the guide's two abreast (1.90 m on the contract's body, the
  guide's own margins).

**Controls** (`python route_cost.py --controls`, all four reading as they must):

1. an empty room: both arms the same, the route its straight length;
2. furnish's own 0.90 m margin as a slot across a room: open to the body, closed to the bake, read within half a cell
   of 0.45 m;
3. a 0.60 m slot: closed to the body, no path;
4. a barrier with its gap at one end: the FURNISHED route over 5 % longer, the AUTHORED arm blind to it.

**Refuted, kept:** the control first proposed for this instrument -- "a planted 0.9 m slot must read closed at 0.40
and open at 0.35" -- is wrong for geometry. A 0.90 m gap admits any body up to 0.45 m in radius; it is the bake's
quantised floor (`2 * ceil(0.4 / 0.1) * 0.1 + 0.2`, 1.00 m) that closes it, so the instrument reads two thresholds,
the body's radius and the bake's floor, and control 2 checks both.

## What it measured (Deli Counter 0.249.0's library, `route_cost.out.txt`, 331 s)

- **Coverage.** 580 rooms of 128 specs (9 m2 or more, two endpoints or more), 2,338 endpoint pairs.
- **Most routes are untouched.** FURNISHED / AUTHORED over the 2,252 pairs joined in both arms: median 1.000, p90
  1.026, p99 1.135, max 1.308. 50 pairs in 41 rooms are over the guide's 10 %.
- **Closures.** Furnishing closes no pair to a body. It closes five to the bake: four in gas_station_a01's back office
  (1.40 -> 0.99 m), and self_storage_a01's vault unit to its objective.
- **Narrowing.** 195 pairs go from two abreast to single file. Of 2,338 pairs, 1,868 stay two abreast furnished,
  against 2,063 authored.
- **By room kind** (`by_kind.out.txt`):

  | room kind | pairs | grew over 10 % | two abreast -> single file |
  |---|---|---|---|
  | corner store's selling floor (Deli Counter 0.247.0's rows) | 85 | 16 | 44 |
  | vault | 146 | 6 | 42 |
  | office | 324 | 14 | 25 |
  | hall | 172 | 6 | 19 |
  | every other kind | 1,525 | 8 | 65 |

  The corner stores' rows, shipped the same morning for roadmap 148, are the most of it. The gas stations'
  `sales_to_stock -> west_service` goes 22.5 -> 25.8 m. deli_a03's market goes 16.9 -> 19.2 m, and three of its routes
  go from 3.1 m wide to 1.33-1.54 m. That is the contract's 1.25 m aisle working as built: single file by the guide's
  formula.
- **Objective and loot routes**: 282 pairs; 17 grew over 10 %; 44 narrowed; median 1.000, p90 1.066, max 1.270. The
  longest detours in the library are small objective rooms, the route from the door to the marker: records offices,
  cash offices, artifact and deposit rooms, 3.5-6 m routes growing 20-30 %.
- **The 80 pairs no body joins in either arm** are each attributed (`unsnapped.py`, `unsnapped.out.txt`). None is
  furnishing's: each fails in the AUTHORED arm too.
  - **21 are this instrument's limits:** a door, or the midpoint of an open edge, landing on a stair's body (office's
    and office_stepped's lobby and bullpen meet across their stair); a vault's objective and loot markers standing
    inside their own block.
  - **11 are authored geometry worth a look of their own:**
    - cbp_town_finale_midbalanced_schemafixed's six club doors at x = 0 open onto authored slab holes;
    - a 2.2 m `cooler_run` stands across the sales floor's side of the `sales_to_office` door in all five gas
      stations;
    - `booth_seating_a` stands within 0.25 m of where a body stands inside primos_pizza's and strip_retail_a01's
      front door.

## Not measured

- **A route that leaves its room.** A path is confined to its room's bounds, so a detour through a neighbouring room
  is not seen.
- **Stair guards and the hole a flight cuts in the storey above.** Only a stair's body on the storeys it climbs
  through, and authored holes, are obstacles.
- **Door leaves, and anything a navmesh does that geometry does not.**
- **Chairs turned a few degrees** count unturned, as `_seed_clear` reads them.

## Files

| file | what |
|---|---|
| `route_cost.py` | the census; `--controls`; `--spec <name>` |
| `route_cost.out.txt`, `route_cost.json` | the library's census, summary and per room |
| `by_kind.py`, `by_kind.out.txt` | the census by room kind, and the objective routes |
| `unsnapped.py`, `unsnapped.out.txt` | every endpoint no body stands at in the AUTHORED arm, and what stands there |
