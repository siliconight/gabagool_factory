# Cold run 9218 -- 0 interventions, 0 retries; the club's light and the sign's bar on the walked level

club_block_014, seed 9181 at night: the level the walker walked on
2026-10-09 (cold run 9213). It is staged from 9217's batch and brief, and
proves two fixes:

| note | fix |
|---|---|
| 219 note 1, the club too dark | Lux 0.72.0 |
| 220, the bar on the door sign | Patina 0.29.2 |

Tool versions hashed at `--begin` (`_runs/cold/cold_9218/before.json`):
Deli Counter 0.205.0, Dispatch 0.5.2, Laser Tag 0.25.0, Level Factory
0.165.0, Lot 0.102.2, Lux 0.72.0, Patina 0.29.2, Pipeline 0.6.0, Pixelcoat
0.61.0, Zoo 1.91.0.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0), **retries 0.**
- **Picked: seed_9181,** as 9213 and 9217 picked it. It carries
  strip_club_a01, funeral_home_a03, airport_terminal_a02 and the 12 empty
  rowhomes.
- **The shell leg:** 0 blockers of 51 findings. **The art leg:** 0 blockers
  of 71.
- **Findings 71 to 71.**

## The club's light (Lux 0.72.0)

The export's bake (`export.log`):
- **256 room fills,** against 9217's 172: the club's 30 den fills and 54
  wall washers. None of it ships; the bake frees them before the save.
- **95.5 s in the editor.**

`tools/look_shots.py` on the walk copy at midnight, at the stations
`docs/findings/club_light_trials/` measured (`club_rooms.png`). Mean / p50,
luma of 255:

| station | 9217 (0.71.0) | 9218 (0.72.0) | the release baked on 9217's copy |
|---|---|---|---|
| main floor | 3.7 / 1 | 14.5 / 8 | 14.51 / 8 |
| VIP wing | 2.2 / 0 | 12.9 / 7 | 12.95 / 7 |
| the bar | 3.1 / 1 | 17.1 / 9 | 17.10 / 9 |

- **The cold pipeline reproduces the release's own bake to the decimal.**
- **In the frames:** coloured scallops on every wall, each in its nearest
  wash's colour. An amber ceiling over the main floor and a pink one over
  the VIP wing. The stools, tables and stage read as shapes, on a dark
  carpet.
- **From the street,** the washers glow magenta through the club's open
  door (`door_signs.png`, top).

The 9217 column is from the trials' control on 9217's walk copy, which
reproduced 9217 exactly. 9217's walk copy itself is gone: this run's walk
export replaced it.

## The bar on the door sign (Patina 0.29.2)

All three signed buildings, framed head-on from 3.2 m (`door_signs.png`):
- **strip_club_a01:** MOM THINKS I'M AT BINGO;
- **airport_terminal_a02:** TERMINAL A, in the civic face;
- **funeral_home_a03:** STIFF & SONS FUNERAL HOME.

**No bar on any.** In 9217 each of the three carried a 0.27 m conduit stub
through its face (`docs/findings/sign_bar/`).

## Still open

- **The club's ceiling is the office tile.** A fill brighter than share 2
  greys it into a grid.
- **The washers have no hardware.**
- **The brighter tinted fill at 4** is the walker's call (the sheet is in
  the findings).
- **Item 221,** Patina's covers facing into the building, is untouched by
  this run.
