# What furnishing costs a route (roadmap 288)

The walker, 2026-10-21: rooms neither crowded nor barren, and above all "free nagivation and fun gun fights". The
guide filed the same day (`docs/reference/Lived_In_Levels_Clear_Navigation_4P_PVE_1999_PA.md`) asks for every width
measured after furnishing (section 5) and a dressing traversal cost: flag a route that grows more than 10 % from the
functional build to the dressed one (section 14). Nothing in the factory measured either. The nav gate asks whether a
marker is reachable, and roadmaps 148 and 281 shipped density changes with no number for what they did to movement
(`docs/findings/guides_2026-10-21/lived_in.md`, its first-ranked gap).

## The instrument

`route_cost.py`, over Deli Counter's library. Its docstring is the method. In short:

- **Three arms of one spec.** AUTHORED is the spec less every volume furnish and the shelter pass wrote
  (`migrate_furnish_recipes.furnished_by_this_pass`, `level_design._seeded_cover`). FUNCTIONAL is the spec less only
  furnish's dressing (`dressing`: a stem in the room kind's cluster pools and in none of its anchors, wall run, floor
  sets, rows or fixtures). FURNISHED is the spec as it ships. Every other obstacle is shared, so what differs between
  two arms is what those passes stood.
- **Two ratios, two questions.** FURNISHED / FUNCTIONAL is the guide's own section-14 measure: what the dressing (its
  "C") costs a route over the functional build (its "B"). FURNISHED / AUTHORED charges everything furnish stands,
  including a store's rows and an office's desks, which in the guide's terms are the building's function rather than
  its dressing. AUTHORED is nearer the guide's blockout, its "A".
- **Endpoints of a room:** its walkable doors (placed by `partition_bounds.host_openings`, the builder's arithmetic),
  its open edges, and its objective and loot markers.
- **Per pair of endpoints:** the shortest path for the contract's 0.35 m body on the bake's 0.10 m grid, shifted off
  round coordinates; and the widest-path bottleneck, read against the body, the bake's door floor (1.00 m, derived
  from the contract as the contract derives it) and the guide's two abreast (1.90 m on the contract's body, the
  guide's own margins).

**Controls** (`python route_cost.py --controls`, all five reading as they must, re-run at Deli Counter 0.250.0):

1. an empty room: both arms the same, the route its straight length;
2. furnish's own 0.90 m margin as a slot across a room: open to the body, closed to the bake, read within half a cell
   of 0.45 m;
3. a 0.60 m slot: closed to the body, no path;
4. a barrier with its gap at one end: the FURNISHED route over 5 % longer, the AUTHORED arm blind to it;
5. dressing against function: a 0.60 m slot across a room in cartons (the fallback recipe's cluster stem, placed
   nowhere else) is open to the FUNCTIONAL arm and closed FURNISHED; the same slot in shelf runs (its wall run) closes
   the FUNCTIONAL arm too.

**Refuted, kept:** the control first proposed for this instrument -- "a planted 0.9 m slot must read closed at 0.40
and open at 0.35" -- is wrong for geometry. A 0.90 m gap admits any body up to 0.45 m in radius; it is the bake's
quantised floor (`2 * ceil(0.4 / 0.1) * 0.1 + 0.2`, 1.00 m) that closes it, so the instrument reads two thresholds,
the body's radius and the bake's floor, and control 2 checks both.

## What it measured

### Deli Counter 0.252.0's library (`route_cost.out.txt`, `route_cost.json`, `by_kind.out.txt`, 523 s)

The library after a piece that seats somebody stands with its chair (Deli Counter 0.252.0, roadmap 284; the factory's
`patches/dc_table_chairs/`): a host the room left chairless is seated last, kept off the room's reserved routes, or
taken away. The same coverage: 580 rooms of 128 specs, 2,338 pairs.

- **All of furnishing.** Over 10 %: 28 pairs in 26 rooms -> 26 in 25; p99 1.108 -> 1.107; the worst unchanged at
  1.308. Narrowed to single file 150 -> 151; two abreast furnished 1,913 -> 1,912. Closures as before: none to a
  body, the same five to the bake.
- **Dressing over the functional build** unchanged: 1 pair over 10 %, 26 narrowed. A host and its chairs are
  function, which both arms keep, so this ratio cannot see the change; the one before it can.
- **By room kind** (`by_kind.out.txt`, against `by_kind_0251.out.txt`): only offices and halls moved. Offices grown
  over 10 % 13 -> 12 and narrowed 15 -> 13; halls 5 -> 4 and 14 -> 17, five of those narrowings landmark_hall_a01's
  artifact_room, re-drawn by the shelter pass around a crate on the floor its taken-away table freed. Over the 282
  objective and loot routes, grown over 10 % 12 -> 9, narrowed 28 -> 28.
- **Every figure is the 55-spec census's arithmetic** (`patches/dc_table_chairs/census_changed.out.txt`: 15 -> 13
  over 10 %, 68 -> 69 narrowed, 856 -> 855 two abreast) on the rest of the library, unmoved.

### Deli Counter 0.251.0's library (`route_cost_0251.out.txt`, `route_cost_0251.json`, `by_kind_0251.out.txt`, 523 s)

The library after a room holding an objective or loot marker keeps its dressing off its routes (Deli Counter 0.251.0,
roadmap 288; the factory's `patches/dc_marker_routes/`). The same coverage: 580 rooms of 128 specs, 2,338 pairs.

- **Dressing over the functional build.** Over 10 %: 8 pairs in 8 rooms -> 1 in 1, the one left self_storage_a01's
  mid_aisle, door to side_exit (1.130), a room that holds no marker; the worst 1.270 -> 1.130, p99 1.046 -> 1.039.
  Dressing narrows 58 pairs from two abreast to single file -> 26.
- **All of furnishing.** Over 10 %: 34 pairs in 31 rooms -> 28 in 26; p99 1.116 -> 1.108; the worst unchanged at
  1.308 (gas_station_a01's back office). Narrowed to single file 179 -> 150; two abreast furnished 1,884 -> 1,913.
  Closures as before: none to a body, the same five to the bake.
- **By room kind** (`by_kind.out.txt`, against `by_kind_0250.out.txt`): the dressing's narrowings in offices 13 -> 0,
  storage 11 -> 5, vaults 7 -> 2, halls 7 -> 2; the corner stores' floors unchanged. Over the 282 objective and loot
  routes, grown over 10 % 17 -> 12 and the dressing's share of them 7 -> 0; narrowed 44 -> 28.
- **Every figure is the 50-spec census's arithmetic** (`patches/dc_marker_routes/census_changed.out.txt`: 18 -> 12
  over 10 %, 80 -> 51 narrowed, 7 -> 0 and 37 -> 5 for the dressing) on the rest of the library, unmoved.

### Deli Counter 0.250.0's library (`route_cost_0250.out.txt`, `route_cost_0250.json`, `by_kind_0250.out.txt`, 540 s)

The library after the corner stores reserved their routes (Deli Counter 0.250.0, roadmap 288), the first run with the
FUNCTIONAL arm. The same coverage as below: 580 rooms of 128 specs, 2,338 endpoint pairs.

- **Dressing over the functional build, the guide's own measure.** FURNISHED / FUNCTIONAL over the 2,252 pairs joined
  in both: median 1.000, p90 1.000, p99 1.046, max 1.270. 8 pairs in 8 rooms are over the guide's 10 %. Dressing
  narrows 58 pairs from two abreast to single file and closes none to a body.
- **All of furnishing.** FURNISHED / AUTHORED: median 1.000, p90 1.025, p99 1.116, max 1.308; 34 pairs in 31 rooms
  over 10 %, from 50 in 41. 179 pairs narrowed from two abreast to single file, from 195; 1,884 of the 2,338 stay two
  abreast furnished, from 1,868. Closures as before: none to a body, the same five to the bake.
- **By room kind** (`by_kind.out.txt`). Between the two runs only the corner stores' selling floors moved -- grown over
  10 % 16 -> 0, narrowed 44 -> 28. Every other kind's counts are identical.

  | room kind | pairs | grew over 10 % | two abreast -> single file | dressing: grew | dressing: narrowed |
  |---|---|---|---|---|---|
  | vault | 146 | 6 | 42 | 1 | 7 |
  | office | 324 | 14 | 25 | 3 | 13 |
  | corner store's selling floor | 85 | 0 | 28 | 0 | 2 |
  | hall | 172 | 6 | 19 | 0 | 7 |
  | every other kind | 1,525 | 8 | 65 | 4 | 29 |

- **The dressing detours.** Seven of the eight over 10 % are one route in an objective room, its door to its marker:
  funeral_home_a02's records_office (4.3 -> 5.5 m, 1.270), self_storage_a02's corner_unit, apartment_walkup_a03's
  garage_cage, supermarket_a02's manager_suite, train_yard_a01's dispatch_office, courthouse_a02's records_room and
  brewery_a01's recipe_lab (1.102). The eighth is self_storage_a01's mid_aisle, door to side_exit (1.130). Over the
  282 objective and loot routes, 17 grow over 10 % with all of furnishing and 7 with its dressing alone; 44 narrow.
  These rooms are roadmap 288's next step -- taken by Deli Counter 0.251.0, above.
- **Refuted, kept: they are not small rooms.** The reading below, of 0.249.0, called them small objective rooms from
  the length of the route. Read room by room they are 97 to 240 m2 and 3.0 to 7.3 % under furniture (the walker's
  band is 12 to 25 %); the route is short because the marker stands near the door, and what lengthens each is one to
  four carton piles, pallets or dust sheets standing in it.

### Deli Counter 0.249.0's library, before the reservation (`route_cost_0249.out.txt`, `route_cost_0249.json`, `by_kind_0249.out.txt`, 331 s)

The measurement roadmap 288 was filed and fixed from. Two arms: the FUNCTIONAL arm came after.

- **Coverage.** 580 rooms of 128 specs (9 m2 or more, two endpoints or more), 2,338 endpoint pairs.
- **Most routes are untouched.** FURNISHED / AUTHORED over the 2,252 pairs joined in both arms: median 1.000, p90
  1.026, p99 1.135, max 1.308. 50 pairs in 41 rooms are over the guide's 10 %.
- **Closures.** Furnishing closes no pair to a body. It closes five to the bake: four in gas_station_a01's back office
  (1.40 -> 0.99 m), and self_storage_a01's vault unit to its objective.
- **Narrowing.** 195 pairs go from two abreast to single file. Of 2,338 pairs, 1,868 stay two abreast furnished,
  against 2,063 authored.
- **By room kind** (`by_kind_0249.out.txt`):

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
  furnishing's: each fails in the AUTHORED arm too. The count is 80 at 0.250.0 as well, whose change moved only
  furnish's pieces.
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
- **Where dressing ends** is furnish's own recipe lists, not the guide's roles: a stem a room kind's recipe places
  both as a cluster and as function counts as function.

## Files

| file | what |
|---|---|
| `route_cost.py` | the census; `--controls`; `--spec <name>` |
| `route_cost.out.txt`, `route_cost.json` | the library's census at Deli Counter 0.252.0, three arms, summary and per room |
| `route_cost_0251.out.txt`, `route_cost_0251.json` | the same at 0.251.0, before a chairless host was seated or taken away |
| `route_cost_0250.out.txt`, `route_cost_0250.json` | the same at 0.250.0, before the marker rooms reserved their routes |
| `route_cost_0249.out.txt`, `route_cost_0249.json` | the same at 0.249.0, two arms: the census roadmap 288 was filed from |
| `by_kind.py`, `by_kind.out.txt`, `by_kind_0251.out.txt`, `by_kind_0250.out.txt`, `by_kind_0249.out.txt` | a census by room kind, and the objective routes (`python by_kind.py [census json]`), with the dressing columns where the census has the FUNCTIONAL arm |
| `unsnapped.py`, `unsnapped.out.txt` | every endpoint no body stands at in the AUTHORED arm, and what stands there (at 0.249.0) |
