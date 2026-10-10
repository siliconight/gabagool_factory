## [0.207.0] - ceiling rows over the aisles, between the shelf runs

**Roadmap 229, the second step.** 0.206.0 laid a room's rows to its work
plane across its width, on the ceiling's grid; in a room organised by its
shelving the rows crossed the gondolas as readily as the aisles. A real
store's ceiling is laid to its aisles: the fixture runs over the lane a
body walks, and a troffer over a gondola lights its top shelf and leaves
the aisle beside it to spill.

- **`_lanes_for_room`:** in a room whose words say it sells or stores
  (`_AISLE_ROOM_WORDS`), the visible volumes standing on its floor whose
  name carries a shelf word (`_SHELF_WORDS`: shelf, gondola, rack, pack
  wall) are projected across the room's long axis, the spans clipped to
  the bounds and merged, and every gap between them and the bounds at
  least an aisle wide (`level_design.island_aisle_width`, the contract's
  door width, 1.25 m) is a lane. A sign hung over an aisle is not a shelf
  (`_SHELF_FOOT_MAX`).
- **`_rows_for_room(..., lanes=)`:** each lane is laid as a floor of its own
  width by WOOD's rule, its lines snapped to the pitch and kept inside the
  lane, the lamps along the room's length as before and the room's cap
  thinning every row alike. A room with no shelving, an office with a shelf
  unit against its wall, a home's room, and shelving that leaves no lane
  are laid exactly as 0.206.1 laid them: the default band is the room's
  width and the arithmetic is the same, which the library diff below
  proves.
- The light manifest line counts the rooms laid over their aisles
  (`rows_over_aisles`).

**Tests:** 6 in `test_fixture_rows.py`. **Suite:** RESULT_SUITE. **The
library rebuilt:** RESULT_CENSUS.
