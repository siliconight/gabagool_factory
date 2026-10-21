# Denser rooms: what "Too sparse" measured, a defect under it, and aisles for the corner stores (roadmap 148)

**What it was for.** The walker's look review of 2026-10-19, seven room frames from restaurant_row_001 (the deli's
market aisles, kitchen and stockroom, the pharmacy's counter and vault rooms, the office's bullpen and lobby):
"Too sparse" -- "these are ultimately shooting galleries for a video game, but the rooms still feel sparse and
boring....computer screens hsould be on...bring life to this dead world". The screens shipped the next day (Zoo
1.115.0, "Looks right"); roadmap 148's status named "denser rooms from the kinds already made" next.

## What sparse measured

`furnish_census.py` (`furnish_census_0245.out.txt`, Deli Counter 0.245.0): every library room's kind, area, the
furnish target and what it holds. Furnish's target is one piece per 16 m2 to ten, then one per 40 m2 to thirty, so
EVERY room between 160 and 400 m2 wants ten -- a density that falls from 16 to 40 m2 a piece across exactly the band
the seven frames were in (deli_a03's market aisles 300 m2, kitchen 240, stockroom 216; the office's bullpen and
lobby 408 each).

The floor tells it better than the count. The share of each frame's room under anything standing
(`level_design.room_floor_share`, 0.247.0): the market aisles 5.7 %, the kitchen 6.0 %, the stockroom 10.5 %, the
bullpen 14.4 % and the lobby 16.1 % (most of each an authored 8 x 6 m cubicle bank), the pharmacy's counter room
3.7 % and its vault 7.1 %. The convenience stores' authored sales floors -- two long gondolas, a cooler, a counter --
are 11 to 12 %.

**REFUTED, kept: more pieces.** `plateau_dry_run.py` (`plateau_dry_run_0245.out.txt`) refurnishes the library in
memory without the plateau: 7,777 -> 12,665 pieces (+63 %), and the market aisles go 5.7 -> 6.8 %, because what a
higher count adds is cartons and cabinets. What a room is known by stands in ROWS, and nothing in furnish laid any.

## A defect under it: Deli Counter 0.246.0

Laying the first rows, deli_a03's apartment UPSTAIRS lost nine of its twelve pieces. `_room_volume_count` -- what a
room already holds, so furnish tops it up -- asked `abs(z - (floor + size_z / 2)) < sh`: a foot anywhere between the
storeys below and above, both ends open. A piece standing on either of those floors is exactly `sh` away, so whether
it counted was float rounding: at sh 3.3 a 1.45 m gondola one storey down is 3.2999999999999994 off and counted.
740 volumes in 195 rooms of 55 specs sat in that window before anything here changed, each a piece the room it was
counted in went without. 0.246.0 (d94c6c0f) asks a volume's foot instead; the refurnish moves 44 specs and 109 rooms
and furnish's pieces in them go 1,034 -> 1,432 (`count_diff.py`, `count_diff_0245_0246.out.txt`). Shipped first, on
its own, so neither change's effect hides in the other's.

## The rows: Deli Counter 0.247.0

A corner store's selling floor (a deli's market aisles, a convenience store's or a gas station's sales floor) lays
rows of Zoo's `snack_gondola` -- both long faces shopped -- 1.40 to 1.45 m tall, over cover height and under shelter
height, so a row is cover a body crouches behind and an eye sees over. Rows run the room's long axis or, where the
room has its own island, along it at its depth and on its line; an aisle of the contract's 1.25 m round every
gondola, from wall FACES; whole rows from the middle out, to a quarter of the floor or until nothing clears. A deli
is a store to the gondola migration now, so its two authored aisle shelves are snack gondolas too.

`rows_diff.py` (`rows_diff_0246_0247.out.txt`): 14 floors, 126 gondolas, the floors' share 5.4-13.4 % -> 19.2-23.1 %,
no other room in the library moved. Plans (`plan_view.py`, 0.245.0 against 0.247.0): `plan_deli_a03_market_aisles.png`
-- nine 4.8 m gondolas in five rows, two of them on the authored aisles' lines; `plan_gas_station_sales_floor.png`,
`plan_stop_n_go_sales_floor.png`.

**REFUTED, kept, both in the changelog and in `_row_slots`'s docstring.** The first grid stood an aisle off the room's
BOUNDS -- a wall's centre line -- and every market-aisle slot beside a wall was refused, 1.07 m from the face. An
even grid stood its columns 1.1 m off the deli's authored aisles (12 of 30 slots refused), and the square gas station
floors ran the rows ACROSS their 10 m aisles. **Not changed, measured:** the card shop's single island keeps the
bound; on card_shop_a01 it stands 1.12 m from a partition's face, under its own 1.25 m claim.

## In a package

Cold runs on cold run 9350's level, restaurant_row_001 at seed 9003 -- deli_a03, pharmacy_a01 and the office, the
review's rooms -- every tool but Deli Counter as shipped (Zoo 1.120.1, Level Factory 0.228.0, Lot 0.126.0, Lux 0.79.0):

| run | Deli Counter | interventions | findings | light bake users |
|---|---|---|---|---|
| 9367 | 0.245.0, from a clone | 0, STOPPED at the shell leg | -- | -- |
| 9368 | 0.245.0, from a clone (the control) | 0 | 108 | 2,907 |
| 9369 | 0.247.0, shipped | 0 | 108 | 2,954 |

**The control is not a shipped run.** Deli Counter was read from a clone at 0.245.0, its library built and nav-gated
there, named by the workspace's `tools.local.json`; `before.json` hashes the real repos and says 0.247.0, the doctor's
`tool:deli_counter` line says what the workspace read. 9367 stopped because the clone had never been nav-gated:
`building_library` judges a shell fit from its `navgate.json`, and "127 of 127 indexed shell(s) are unfit -- 127 with
absent" (its NOTES).

**What moved in this level** (the specs, 0.245.0 against 0.247.0): deli_a03's market aisles 9 -> 18 furnished pieces,
5.7 -> 19.7 % of the floor; and the count fix's rooms -- deli_a03's server room 9 -> 10 pieces, the office's floor_1
5 -> 18, its exec_lobby 16 -> 18 and exec_anteroom 10 -> 11. pharmacy_a01 did not move.

**Frames** (`shots.sh`, `compose_rooms.py`; stations from `tools/room_stations.py`, the same in both runs, the review's
own): `rooms_9368_9369_lit.jpg` and `rooms_9368_9369_inspect.jpg`, the market aisles, the office's floor_1, the server
room and the kitchen, the control on the left. The market aisles go from two black shelves on an empty tiled floor to
stocked aisles running the room under the ceiling's rows -- 70.6 % of the frame's pixels moved by more than 15/255 in
the level's light, 58.8 % in the inspection light. The kitchen is the frames' own control: no piece moved there, and
every station but the market aisles and floor_1 stays within 1 % (the light bake's atlas repacks when a user is added).
**The office's floor_1 shows the next defect:** filled to its target by the count fix, it gains litter bins standing
mid-floor among carton stacks, because `floor` makes it a SHOP floor (roadmap 281).

## What it costs: priced

`_runs/perf_inner/run.py`, Level Factory's fixed-station harness, GL Compatibility, windowed: 9368's package twice (the
control) and 9369's once, in one session, nothing else running -- 14 stations, 53 headings, two passes each
(`price_9368_a.json`, `price_9368_a2.json`, `price_9369_b.json`).

- **Read by passes, not the headline** (`price_passes.py`, `price_passes.out.txt`). The harness reports a heading's
  first pass, and where its two passes disagree -- a failing light live in the frame -- the headline difference is
  partly which state the first pass caught: `price_headings.py` (`price_headings.out.txt`, the car-wear price's
  instrument, kept) read extraction_16 at yaw 90 as -94 draws, and it is 1,322/1,230 before and 1,320/1,228 after,
  -2 in each pass. Pass by pass, the control's two runs differ at no heading in their smaller pass and 2 in their
  larger; the change moves 38 of 53, median +6.
- **Where the draws come from: merged meshes** (`merged_counts.py`, `merged_counts_9368_9369.out.txt`). Level Factory
  merges a building per room cell and material, so a count of pieces is not a count of submissions. The office's
  merged meshes go 238 -> 290 -- the count fix's pieces in its floor_1 and executive rooms -- and the headings that see
  it draw +12 to +61 (both attacker spawns beside it, every eastward heading at x 4 to 39; a heading looks along
  `(-sin yaw, 0, -cos yaw)`, `perf_stations.gd`, so yaw 270 is +x, toward the office at x 54, and 90 is -x). deli_a03's go 480 -> 464:
  its two authored aisle shelves were stocked shelving, several materials a cell, and are two-material snack gondolas
  now, which the nine new ones share -- the patrol point inside its market draws 4 to 12 fewer at every heading, and
  the westward headings of the two camera sockets 24 and 29 fewer. pharmacy_a01's, 89 -> 89.
- **Frame time does not move past the instrument's floor.** Where draws moved, 9369's median frame is +0.058 ms over
  the mean of 9368's two runs; elsewhere -0.008 ms; the control's own spread is -0.242 to +0.113 ms. The largest,
  +0.372 ms at camera_socket_0 yaw 270, is the largest draw increase (+61).
- **Memory:** mesh instances 2,980 -> 3,027 (the light bake's users 2,907 -> 2,954 agree); texture memory +1.74 MB;
  buffers +4.59 MB; video memory 141.9 -> 148.2 MB.

So the rows cost nothing a frame can show and fewer submissions in the deli than its old shelving, and the count fix
costs a merged mesh per new piece-and-material in the rooms it fills: the office's +52 is the price of a room holding
the furniture its target always asked for.

## Files

- `furnish_census.py` (`furnish_census_0245.out.txt`), `plateau_dry_run.py` (`plateau_dry_run_0245.out.txt`, REFUTED),
  `count_diff.py` (`count_diff_0245_0246.out.txt`), `rows_diff.py` (`rows_diff_0246_0247.out.txt`): the library.
- `plan_view.py`, `plan_deli_a03_market_aisles.png`, `plan_gas_station_sales_floor.png`,
  `plan_stop_n_go_sales_floor.png`: the rows in plan.
- `shots.sh`, `compose_rooms.py`, `frame_change.py` (`frame_change_9368_9369.out.txt`), `rooms_9368_9369_lit.jpg`,
  `rooms_9368_9369_inspect.jpg`: the frames.
- `price_headings.py`, `price_passes.py`, `merged_counts.py` and their outputs, the three `price_*.json`: the price.
