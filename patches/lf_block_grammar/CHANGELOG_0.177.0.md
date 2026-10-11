## [0.177.0] - The `block` road grammar: a second side street and a service lane behind the row, one loop

**Roadmap 199 and 230 step 3.** Every site ever generated was a T: two
approaches and no cycle (`docs/findings/walkable_city/`, 22 of 22). The
walkable-city brief asks for a short loop; the adjacency guide prefers a
return loop and names the connector that makes one, a service lane behind
the row with an owner and users. Measured before it was laid
(`docs/findings/rear_lane/`, 27 cold workspaces): 21.5 to 28.5 m of empty
plate behind every strip row, the one side street already reaching into
it, the Empties always across the main road.

- **`block`** (spellings `block`, `loop`, `service_lane`, `rear_lane`,
  `alley`, `back_lane`): the T as it was, plus a SECOND side street past
  the row's end farther from the first, half a band off the last building,
  ending on the front road and running to the plate's far margin like the
  first; and a LANE between the two streets' centre lines behind the row,
  `LANE_WIDTH` (5 m, the guide's van-scale service lane), no sidewalk, laid
  `LANE_SETBACK` (8 m: Lot's dumpster pad and apron on that wall, 6 m, and
  this module's 2 m margin) past the deepest rear face. The lane ends on
  both streets, two T stems, so Lot resolves nothing it has not drawn since
  0.61.0; the road graph has one cycle where the T had none. The lane
  carries `kind: service_lane` and `serves` (the row's buildings) for the
  audit.
- **Doors:** the far building gets a side door onto the second street as
  the first street's flank does; every building gets a rear door path to
  the lane's edge, half a metre short of the carriageway, which Lot keeps
  where the shell has a ground door on that face and records as undrawn
  where it has none.
- **The plate** widens for the second street and deepens for the lane the
  way it already does for a street past the west end and for a
  crossroads' south arm.
- `T` and `cross` are byte for byte what they were; a brief that names
  nothing keeps its T.

**Lot 0.113.0 lands first:** a lane without a sidewalk stops at a street
and never gets a signal, and `S_TARGETS` counts the lane. **Tests:** 5 in
`tests/unit/test_road_grammar.py` (one reads Lot). **Suite:** RESULT_SUITE.
