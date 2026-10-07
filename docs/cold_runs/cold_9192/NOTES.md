# Cold run 9192 -- 0 interventions; the deli's customer floor stands clear

The measurement run for Deli Counter 0.202.0, on 9190's brief
(restaurant_row_001). 0.202.0 stops furnish standing a wall piece against a
room edge with no wall behind it (`docs/findings/wall_pieces_without_walls/`).
9190's frames had caught three of them in front of deli_a01's case.

**Every leg ran, `INTERVENTIONS: 0`, and the package exported.**
- **Findings: 64, the same as 9190.**
- **The draw is 9190's.** Three distinct candidates, seed_9104 picked again
  on the walk test and Laser Tag's route findings: deli_a01, office,
  rail_station_a02 and the twelve row homes.
- **Bake:** 4,276 users (9190: 4,310), 479 models lightmapped (482), 4 kept
  dynamic (6), 86.5 s.

## deli_a01, in the package

Read in the export's `lot/deli_a01/site.tscn`. The walk copy's is
byte-identical. Building frame, Godot axes (x, y up, z = -spec y).

| piece | 9190 | 9192 |
|---|---|---|
| `atm_store` | (-10.98, 0.725, 3.46): 2.3 m in front of the case | (-18.54, 0.725, 6.81): the west wall |
| two `poster_wall_store` boards | (-17.56, 1.4, 3.19), (-15.34, 1.4, 3.19): mid-air on the open edge | (-15.02, 1.4, 13.81), (-4.87, 1.5, 13.81): the south wall |
| four `video_poker_store` cabinets | two in each of two rooms | **none** |

**The poker cabinets are lost, not moved.** When no built wall in a piece's
room holds its run, 0.202.0 drops the piece rather than finding it another
place. Across the library that is **100 video poker cabinets in 38 specs ->
82 in 34**. The walker decided two a store when the cabinets shipped
(2026-10-01, Zoo 1.39.0), so this is a regression and is filed as one
(roadmap 196).

**Frames** (`tools/look_shots.py` on this run's walk copy, 9190's three
stations, site frame):

| frame | station (eye -> target) | mean (/255), 9190 -> 9192 |
|---|---|---|
| `frame_9192_case_front.jpg` | (-69.09, 1.6, 3.6) -> (-69.09, 0.85, 0.19) | 7.6 -> 5.5 |
| `frame_9192_case_three_quarter.jpg` | (-74.0, 1.6, 3.2) -> (-68.5, 0.85, 0.19) | 7.5 -> 7.7 |
| `frame_9192_case_deck.jpg` | (-68.0, 1.5, 1.9) -> (-68.6, 0.85, 0.3) | 17.5 -> 17.7 |

- **The case stands clear.** 9190's three-quarter frame looked at it past the
  LOTTO HERE and OPEN 24 HRS boards and a shelf run. Nothing stands between
  the case and the customer floor now.
- The front frame's mean fell because the lit ATM it was half filled with
  has gone. It is a darker picture of an emptier floor, not a lighting change.
- **The room is dark.** That is the walker's note of the same day, interiors
  too dark when the sun is down. It is measured across this level's rooms
  in `docs/findings/night_interiors/`.

## Laser Tag

Event counts by the report's own `event` field, 9190 -> 9192:
- **seed_9104 (picked):** PlayerStuck **9 -> 4**, RouteProgress 199 -> 203,
  every other count identical. The four that went all stood at site
  (-73.35, 0, 6.44), times 52-56 s. That is building (-15.35, 7.45):
  deli_a01's customer floor, the room whose pieces moved. One of the four
  at (-8.3, 0.08, 15.05) went too. The basement one, (-54.2, -3.3, -5.2),
  is still there.
- **seed_9003:** identical.
- **seed_9205:** PlayerStuck 5 -> 4, ShotBlocked 779 -> 782, ShotHitPlayer
  370 -> 371.
- Grades unchanged: PASS_WITH_TUNING, PASS_WITH_TUNING, WARN.

**Attributed, not proven:** the four customer-floor stalls are assumed to be
the pieces 0.202.0 moved off the open edge. They stood 3-4 m south of the old
boards' line, and nothing else in the room changed between the runs.
