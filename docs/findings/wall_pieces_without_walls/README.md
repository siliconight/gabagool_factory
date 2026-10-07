# Wall pieces with no wall behind them

Found 2026-10-07, framing the deli case in cold run 9190's deli_a01. Two
things stood in front of the case's service front: the ATM, and two lottery
boards hanging in mid-air. All three were furnish's wall pieces, slotted
against the customer floor's north edge (y -3.0). No wall stands on that
edge: the customer floor and the deli counter room meet there across open
floor.

**Frames and units.** The spec's frame: metres, the footprint centred on 0,
x east, y north.

## Why

`level_design._wall_slots` offers a wall piece every edge of its room.
- **An exterior edge** is checked for its openings and its glazing.
- **An interior edge is assumed to be a wall.** Nothing asks whether a
  partition stands on it.

So wherever two rooms meet across open floor, a shelf, a cabinet, an ATM or
a paper poster is stood with its back against nothing.

This is the open-floor rule again. Layout_lint L12 and L24 learned it in Deli
Counter 0.197.0 (`tactical.shared_open_edge`); furnish never did.

## What was measured

`wall_pieces_without_walls.py` reads Deli Counter 0.201.0's 146 non-LF specs.
- **A wall piece** is a volume `furnish` wrote whose stem `_PIECES` places on
  a wall, fixtures included.
- **Its edge** is the room edge nearest its box.
- **A wall behind it** is a wall the builder stands (`layout_lint.built_walls`):
  on its storey, its centreline within 0.10 m of that edge, its built span
  covering at least half the piece's run along it.

**155 of 4,086 furnished wall pieces, in 18 shells** (`census_0201.txt`).
- Every one stands 0.18-0.19 m off its edge, `_wall_slots`' own spacing:
  half the wall plus the air.
- **By shell:**

  | shells | pieces each |
  |---|---|
  | the six delis | 12-14 (76 in all) |
  | apartment_walkup_a01 | 18 |
  | rowhouse_raid | 17 |
  | office_stepped | 8 |
  | harbor_score, parking_garage_a02 | 7 |
  | setback_demo | 6 |
  | office | 4 |
  | marina_a01, warehouse_a02 | 3 |
  | cr_garage, parking_garage, parking_garage_a01 | 2 |

- **By stem:** shelf runs 43, file cabinets 27, store poster boards 17,
  waiting chairs 10, service counters 10, vending 9, video poker 6, and the
  rest.

**deli_a01's 14:**
- on the customer floor's open north edge: the ATM, both lottery boards, a
  poker cabinet, a service counter and a shelf run;
- on the market aisles' open east edge (to the kitchen): shelf runs, a
  counter, a file cabinet, a poker cabinet and a poster board;
- one each in the kitchen and the utility room.

## What shipped (Deli Counter 0.202.0)

- **A wall piece needs a wall behind it.** `_wall_slots` offers a slot only
  where a built wall (`layout_lint.built_walls`) lies on the edge and holds
  the piece's whole run. Every slot is drawn and shuffled as before, and the
  unheld ones are dropped after the shuffle, so only pieces that stood
  against nothing move.
  - **Refuted, kept:** dropping them before the shuffle re-rolled 33 specs.
- **Furniture keeps off an authored hole in its own floor** (`_seed_clear`).
  The wall rule's refurnish re-rolled two dining rooms, and both sets landed
  over their drop holes.
- **The library, refurnished:** 20 specs moved: these 18, plus
  cbp_town_finale and final_stand for the hole rule.
- **After** (`census_0202.txt`): 3,998 furnished wall pieces, **0** with no
  wall behind them.

**Seen in a level: cold run 9192** (`docs/cold_runs/cold_9192/NOTES.md`).
deli_a01's ATM stands on the west wall and its two poster boards on the south
wall, and the case is clear in the frame. Laser Tag's PlayerStuck fell 9 -> 4,
and the four that went all stood on the customer floor.

**A regression it caused.** A piece that no built wall in its room holds is
dropped, not placed somewhere else. The six delis lost 18 of their 20 video
poker cabinets:

| spec | 0.201.0 | 0.202.0 |
|---|---|---|
| deli_a01 | 4 | 0 |
| deli_a03 | 4 | 1 |
| deli_a02 | 3 | 1 |
| cr_deli, night_deli, corner_deli_heist_01 | 3 each | 0 |

The walker decided two a store. Open in roadmap 196.

**Why furnish had used open edges at all.** On 0.201.0's library, 3,924 wall
pieces stood against exterior walls, 42 near a partition and 120 against
nothing. `_seed_clear` keeps every piece 1.0 m from a partition's line to
keep its doors clear, so partitions were almost never furnished. The
"interior walls" furnish used were the open edges. A partition is still
unfurnished: that rule would have to clear a partition's openings rather
than its length.

## Not yet established

- **How each piece reads in a frame.** The deli's two boards and its ATM are
  seen in 9190's `frame_9190_case_three_quarter.jpg` and
  `frame_9190_case_front.jpg`. The others are counted, not looked at.
- **Whether every open edge in the list is meant to be open.** The census
  asks the built walls, not the author.

## Instrument

`wall_pieces_without_walls.py [--list]`. It prints what it measured, not
why.
