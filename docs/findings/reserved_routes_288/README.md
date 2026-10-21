# The corner stores reserve their routes before their rows (roadmap 288, Deli Counter 0.250.0)

**Why.** The walker, 2026-10-21: rooms neither crowded nor barren, and above all "free nagivation and fun gun
fights". The census of what furnishing costs a route (`docs/findings/furnish_route_cost/`) found the corner stores'
rows, Deli Counter 0.247.0's of the same morning, the most of it. Of their 85 door-to-door routes, 16 had grown over
the 10 % the walker's guide flags, and 44 had narrowed from two abreast to single file. The guide
(`docs/reference/Lived_In_Levels_Clear_Navigation_4P_PVE_1999_PA.md`) answers that in its section 3 and its builder's
third step: reserve circulation before placing. Its own market is "a broad cross-aisle and at least two tested ways
around the central fixtures".

**What Deli Counter 0.250.0 does** (f0ab57ca; the patch, its instruments and every refuted variant in
`patches/dc_reserved_routes/`). Before furnish places anything on a corner store's selling floor, it reserves square
routes between the floor's doors and markers. They are a greedy spanner at the guide's 10 %, with corridors two
abreast (1.90 m, the guide's formula on the contract's body). Rows, floor pieces, clusters and chairs keep off them;
wall pieces and wall fixtures stand where they did. The plans (`patches/dc_reserved_routes/plan_*.png`) show
deli_a03's market aisles as two banks of gondolas with one cross-aisle between them, and the gas stations' rows as
two aligned banks with their front clear.

**In a package: cold run 9371** (restaurant_row_001 at seed 9003, cold run 9370's level, Deli Counter the only tool
that moved). 0 interventions; findings 108 -> 108.

| station | lit | inspection | what it is |
|---|---|---|---|
| `cross_aisle` | 26.0 % | 27.8 % | from deli_a03's west door's line, looking east along the reserved cross-aisle |
| `market_aisles` | 2.2 % | 1.5 % | down the room's long axis; the lower bank, the store's own aisles, stands as it did |
| `kitchen` | 0.4 % | 0.2 % | control |
| `ground_bullpen` | 0.0 % | 0.0 % | control, the office's |
| every other station | 0.3 % or less | 0.1 % or less | |

These are shares of frame pixels that moved by more than 15 of 255, from `frame_change.py`.

- **The cross-aisle frames** (`cross_aisle_9370_9371_lit.jpg`, `_inspect.jpg`). From the west door's line, 9370 faces
  a wall of gondola fronts, the route behind it a zigzag through staggered gaps. 9371 looks down a lane two abreast to
  the far wall's door, gondolas either side.
- **The market aisles' own station** barely moves. The store reads at eye height as it did, which is what the change
  was meant to keep.

## The station

`cross_aisle` is not one `tools/room_stations.py` prints. It is that script's transform (the building's `at` and
`rot` in the themed drawn spec, deli_a03 as b0 in both runs, the market aisles' floor at 0.0), asked of two plan
points on the reserved route's line: the eye at (-7.0, -4.1) 1.6 m up and the target at (6.5, -4.1) 1.2 m up, so
the lane's floor is in frame. Look_shots' frame: `--station cross_aisle:-58,1.6,1.59,-44.5,1.2,1.59`. The local
line is the route `protected_routes` reserves on deli_a03's market aisles, from its west door north to y -4.1 and
east to the kitchen door (`patches/dc_reserved_routes/`).

## Files

- `shots.sh`: the market aisles and the two controls, from `docs/findings/denser_rooms_148/shots.sh` with its rooms
  changed. The cross-aisle station was shot beside it by `tools/look_shots.py` with the station above.
- `compose_pair.py`, `frame_change.py`: copied from `docs/findings/office_floor_281/`.
- `cross_aisle_9370_9371_lit.jpg` and `_inspect.jpg`: the cross-aisle and market-aisles stations.
- `market_aisles_9370_9371_lit.jpg` and `_inspect.jpg`: the market aisles and the two controls.
- `frame_change_9370_9371.out.txt`: every station, both lights.
