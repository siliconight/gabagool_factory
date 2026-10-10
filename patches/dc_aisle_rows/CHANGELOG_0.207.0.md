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
  (`_SHELF_FOOT_MAX`), and a merged span wider than a run is deep
  (`_SHELF_SPAN_MAX`, 2.0 m: a twin island is 1.2) is a field of islands
  staggered along the room, not parallel runs -- the furnish's own layout
  for a selling floor, 66 of the library's 98 shelved selling and storage
  rooms -- and such a room keeps its grid, because the first build kept
  the gas station's rows off its island band and left 14 m of floor
  between them. The 32 rooms with runs (the deli's authored aisle shelves,
  the warehouses' racks, a stockroom's wall run) take the lanes where rows
  light them: 15 in the library's derivation, the rest being objective
  rooms on bulbs or below grade.
- **`_rows_for_room(..., lanes=)`:** each lane is laid as a floor of its own
  width by WOOD's rule, its lines snapped to the pitch and kept inside the
  lane, the lamps along the room's length as before and the room's cap
  thinning every row alike. A room with no shelving, an office with a shelf
  unit against its wall, a home's room, and shelving that leaves no lane
  are laid exactly as 0.206.1 laid them: the default band is the room's
  width and the arithmetic is the same, which the library diff proves
  (`docs/findings/fixture_rows/aisle_rows_diff_0207_draft.txt` in the
  factory: 363 rooms identical, 124 changed, the 15 laid over their aisles
  and the 110 where the cap bound; rows moved 359, removed 110, none
  added; lamps 4,374 to 4,154 in a flat derivation).
- **The long hall:** where the room's twelve-lamp cap binds, WOOD's rule
  cannot hold in both directions at once, and 0.206.0 kept the rows across
  and thinned the lamps along, so a 58 x 20 m hall stood three rows of four
  with 14.5 m between lamps. Now rows across are traded for lamps along
  while the larger of the two spacings shrinks, a row at a time from the
  band that loses least: that hall is two rows of five at 11.6 m along and
  10 m across; a 12 x 11 m office keeps its three of four, whose across
  spacing is the larger and would only grow. Nothing changes where the cap
  does not bind.
- The light manifest line counts the rooms laid over their aisles
  (`rows_over_aisles`).

**Tests:** 8 in `test_fixture_rows.py`; the gas station's storefront reach
test asserts the shape (every sales-floor row reaches the glass from its
own line, the nearer the shorter) rather than three pinned numbers, since
the built floor is now laid to its gondolas and the pure case beside it
has none. **Suite:** RESULT_SUITE. **The library rebuilt:** RESULT_CENSUS.
