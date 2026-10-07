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

## Not yet established

- **How each piece reads in a frame.** The deli's two boards and its ATM are
  seen in 9190's `frame_9190_case_three_quarter.jpg` and
  `frame_9190_case_front.jpg`. The others are counted, not looked at.
- **Whether every open edge in the list is meant to be open.** The census
  asks the built walls, not the author.

## Instrument

`wall_pieces_without_walls.py [--list]`. It prints what it measured, not
why.
