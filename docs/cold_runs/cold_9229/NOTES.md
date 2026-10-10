# Cold run 9229 -- 0 interventions, 0 retries; the borough in seven modules, and the ceiling rows laid to the work

restaurant_row_001, evening and clear, seed auto, staged from 9225's batch
and brief: the level 9225 built, rebuilt on the set that landed after the
recipe runs. It proves two things at once and prices each against its own
control:
- **Roadmap 228:** Lot 0.109.0's one depth a band, the fix 9225's draws
  found (18 rowhome modules, 69 MultiMeshes); and Lot 0.109.1 and Level
  Factory 0.175.1's tally lines.
- **Roadmap 229:** Deli Counter 0.206.0's ceiling rows laid to the room's
  work plane on the ceiling's grid, and Lux 0.74.0's one failing tube a
  room. Zoo 1.97.0 and Lot 0.110.0 (the tree) are in the set and do nothing
  on a borough.

Tool versions hashed at `--begin` (`_runs/cold/cold_9229/before.json`):

| tool | version |
|---|---|
| Deli Counter | 0.206.0 |
| Dispatch | 0.5.2 |
| Laser Tag | 0.25.0 |
| Level Factory | 0.175.1 |
| Lot | 0.110.0 |
| Lux | 0.74.0 |
| Patina | 0.30.0 |
| Pipeline | 0.6.0 |
| Pixelcoat | 0.62.0 |
| Zoo | 1.97.0 |

Against 9225: Deli Counter 0.205.0 to 0.206.0, Level Factory 0.174.0 to
0.175.1, Lot 0.108.0 to 0.110.0, Lux 0.73.0 to 0.74.0, Zoo 1.95.0 to 1.97.0.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0), **retries 0.**
- **Picked: seed_9104,** the seed 9225 picked: the same three buildings on
  the same lines, so the comparisons below are of one level.
- **The shell leg:** 0 blockers of 52. **The art leg:** 0 blockers of 74.
- **The bake:** 481 models and 1,420 primitive meshes, 225 steady rigs
  baked, 29 failing left live, 267 room fills, 4,446 users, **104.2 s**
  (9225: 91.7 s; the rigs more than doubled and the bake took 14 % longer).

## The borough, in seven modules (roadmap 228)

- **Lot** (`themed_site_assemble/1/job.log`): `LOT_BACKDROP_PLACED: recipe
  borough, 277 piece(s) (backdrop_rowhome 276, water_tower 1) by side (N 96,
  S 101, E 41, W 38), 7 module(s), 1 water tower(s)`: the pieces 9225 laid,
  in **seven modules where 9225's three band depths made eighteen**, and
  0.109.1's line counting pieces by species.
- **Level Factory** (`export.log`): `[export] backdrop: site_backdrop.tscn
  -- 277 instances of 7 module(s) on their sides, 25 draw calls` (9225: 69).
- Priced below against this package with the backdrop off, as the recipe
  runs were.

## The ceiling rows (roadmap 229)

- **Deli Counter's build line** for the picked candidate's shell:
  `19 row(s) laid to the work; 0 lamp(s) nudged, 0 dropped, 0 row(s) moved
  off a wall` (`deli_generate.candidate.seed_9104/1/job.log`).
- **The site manifest, 9225 against 9229** (`rooms_rows_before_after.txt`):
  17 fluorescent rows and 72 lamps over the three buildings became **44 rows
  and 174 lamps** (2.4 x); the 32 bulbs below grade are the same. By
  building: the deli (b0) 9 rows / 39 lamps to 25 / 97, the office (b1)
  6 / 23 to 15 / 60, the rail station (b2) 2 / 10 to 4 / 17. Room by room,
  fourteen of sixteen rooms took three rows and most of them the twelve-lamp
  cap (three rows of four); the deli's stairwell and stockroom took two; the
  station's agent wing kept one. The rows stand on the tile or joist grid:
  the deli's market aisles at x -63.6, -58.4, -53.6 across a room centred on
  -58.5, its kitchen at -49.0, -44.8, -41.2.

## Seen

`rooms_before_after.png`: the same six rooms from the same stations
(`tools/room_stations.py`: the deli's apartment hideout, market aisles,
manager's office and server room; the office's first floor and lobby) in
9225's package on the left and 9229's on the right, the ceiling in frame.
- **9225:** one row of troffers down the middle of every room, receding to
  a point: the market aisles, the office floor, the lobby and the server
  room all lit by the same line.
- **9229:** three rows across every one of these rooms, the troffers
  standing left, centre and right over a lit ceiling. The market aisles
  read as a store's ceiling grid and the office floor and lobby as an
  office's; the server room and the manager's office carry three short rows
  of four. Nothing is skewed or jittered: each row sits on the tile grid,
  and the look is "a ceiling laid out", not "a line down the middle".
- **A refinement the frames ask for:** the deli's `apartment_hideout` (a
  residence-like room inside a shop building) took an office ceiling of
  twelve troffers, because the home rule keys on the BUILDING being a
  residence. A room named apartment, hideout, bedroom or living inside any
  building should take the home rule's one fixture, or bulbs. One line in
  `_work_plane`'s table; the next Deli Counter release.
- **For the walker's eye:** whether three rows of four at the twelve-lamp
  cap is the density a 12 x 11 m room wants, or two rows of five; and the
  grids being perfectly regular where the roadmap item asked for structural
  causes (the tile snap is the only one so far).

## Priced

Two prices, each against its own control, through
`docs/findings/horizon_glow/price_glow.py` (control, subject, control; the
harness calls the subject `glow`): 53 headings a run on a heavy level (9225's
package stands at 2,914 draws a heading mean and p95 6.6 ms before anything
here).

**The borough's seven modules** (`price/`, this package against itself with
the backdrop off):

| run | draws +mean | +min | +max | p95 +median ms | +max ms |
|---|---|---|---|---|---|
| control_1 | 0.0 | 0 | 0 | 0.07 | 0.65 |
| subject | 27.0 | 10 | 40 | 0.29 | 1.21 |
| control_2 | 0.0 | 0 | 0 | -0.07 | 0.16 |

The controls' spread is 0.18 ms. **The backdrop costs +27 draws a heading
where 9225's eighteen modules cost +52** (2,966 against 2,914 then): Lot
0.109.0's one depth a band halved it. Its p95 +0.29 ms median is over this
run's spread, where 9225's read inside; the level is 4 % heavier now (the
rows, below) and the frame 6.7 ms.

**The rows** (`price_rows/`, 9225's package against 9229's, both with the
backdrop scene off, so the tool set is the only difference and the rows are
most of it):

| run | draws +mean | +min | +max | p95 +median ms | +max ms |
|---|---|---|---|---|---|
| control_1 | 0.0 | 0 | 0 | -0.17 | 0.12 |
| subject | 121.9 | 0 | 276 | 0.27 | 1.66 |
| control_2 | 0.0 | 0 | 0 | 0.17 | 1.38 |

**The rows cost +122 draws a heading mean (0 to +276), 4 % of the level's
2,914**: the troffer hardware (174 lamps where 72 stood) and the floor and
ceiling tiles Zoo splits per light budget. The p95 +0.27 ms median is
INSIDE this pair's 0.35 ms spread (the two controls' medians differ by
0.67 ms between themselves, 6.34 against 7.01), so no frame time can be
attributed to the rows at these stations; the bake took 12.5 s longer
(104.2 against 91.7). The draws are the price to watch as the species grow
(roadmap 229's next steps): a strip light or a sconce is hardware too.

## What this run does not prove

The rows by day, or in a building whose rooms are narrow (every room here
took two or three rows); the trees, which are not in a borough (9230, staged
from 9227, shows them).

## Instruments

- `tools/recipe_run_record.sh 9229 restaurant_row_001`: the control copy,
  the edge stations, the frames, the sheet and the backdrop's price
  (`record.log`, `price/`).
- `room_frames.sh`: the same interior stations (`tools/room_stations.py`,
  the deli's four largest rooms and the office's two) shot on 9225's package
  and on 9229's (`rooms_before_after.png`; frames in
  `_scratch/frames_9229_rooms/`, not tracked).
- The rows' price: 9225's package and 9229's, both with the backdrop scene
  off (`tools/backdrop_off.py`), through `price_glow.py` into `price_rows/`,
  so the only difference between the two is the tool set's, the rows above
  all.
- `rooms_rows_before_after.txt`: the per-room table.
