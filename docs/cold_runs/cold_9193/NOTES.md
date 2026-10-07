# Cold run 9193 -- 0 interventions; the bake lights a room

The measurement run for the night-interiors fix, on 9190's brief
(restaurant_row_001). Investigation: `docs/findings/night_interiors/`.

- **Lux 0.67.0:** a bare bulb's lamp hangs under its glass, not inside it.
- **Lux 0.68.1 and Level Factory 0.151.0:** the bake lays bake-only room
  fills over every untinted room probe, half in bulb-lit rooms, and frees
  them before it saves.

**Every leg ran, `INTERVENTIONS: 0`, and the package exported.**
- **Findings: 64**, the same as 9190 and 9192.
- **The draw is theirs:** seed_9104, picked on the walk test and Laser Tag's
  route findings. deli_a01, office, rail_station_a02 and the row homes.
- **Bake:** 267 room fills, 4,276 users, 96.2 s in the editor (9192: 86.5 s,
  no fills).

## In the package

Read in the walk copy, which is the export plus a player:
- `light_bake.json`: `room_fills` 267.
- The saved `bake.tscn` holds no `LuxBakeFill`. The fills were baked and
  freed.
- `presentation/lux.applied.tscn`: 33 rigs at `mount_height = -0.022`. That
  is the 32 bare bulbs and the counter accent, built by Lux's own loader.

## Night interiors, measured

`night_interior_census.py` on this run's walk copy against 9190's, the same
draw. One station a room, mean luma of 255 (`night_census_9193.txt`).

| rooms | 9190 shipped | 9193 | scripted target |
|---|---|---|---|
| 16 fluorescent rows | 15.5 | 39.2 | 39.1 |
| 8 bulb-lit rooms | 3.8 | 23.4 | 22.8 |
| rows with half the frame under 10 | 14 | 1 | |
| bulb rooms with half the frame under 10 | 8 | 1 | |

- **The scripted target** is `rebake_variant.py`'s v4 layout on 9190's copy.
  That number came from an experiment; this one came from the pipeline.
- **Besides the lighting, the furniture differs.** Deli Counter 0.202.0
  (9192's change) moved deli_a01's 14 open-edge wall pieces, across the
  customer floor, market aisles, kitchen and utility room, and the office's 4.
  A station whose frame holds one of them differs for that reason as well.
- **The darkest rooms left** are the deli's basement vault (6.9), the office
  lobby (14.0, its dark red carpet), the rail concourse (16.6) and the exec
  suite (15.2). These are bulb-lit or dark-floored, not unlit.

`frame_9193_rooms_before_after.jpg`: the deli's customer floor, deli
counter and basement corridor, the office's exec lobby and the rail
station's vault approach. 9190 left, 9193 right.

## Laser Tag

Every event count is identical to 9192's on all three candidates (1,678,
1,363 and 2,121 events). Grades are unchanged: PASS_WITH_TUNING,
PASS_WITH_TUNING, WARN. The light changed and the game did not.

## Not in this run

- **Lux 0.68.2,** a den of sin is a whole building. It shipped after this run
  began, and this level has no club. It is measured on club_block_014 in the
  finding.
- **The derived spawn shot** still reads 0.8, as in every variant. Its camera
  stands 3 cm inside the office lobby's west edge. Not investigated.
