## [0.207.1] - a home's room takes a fixture a bay, not one whatever its size

**Cold run 9232** (roadmap 229): the deli's `apartment_hideout`, 21 x 16 m,
took the home rule's one fixture at its centre and read dark at both ends,
a hall lit like a bedsit. The guide lights a home a room at a time
(`docs/reference/INDOOR_FIXTURE_PLACEMENT_GUIDE.md`, "By room": a pendant
or flush mount over the sink, one pendant in a bedroom, flush mounts in
a hallway), and a hideout the size of four rooms is lit as four.

- **`_HOME_SPACING`** (7 m): a bay the size of an ordinary room, one
  ceiling fixture a bay. A home's room within one bay keeps its one
  fixture at its centre, byte for byte as 0.206.0 laid it (a 9 x 7 m
  living room, a 4 x 5 m bedroom); a bigger one takes a grid of bays by
  WOOD's row rule at that spacing, the fixtures at the bays' centres
  rather than on a tile line (a home hangs its fixture from the middle of
  the room, not from a grid), the room's cap thinning as everywhere. The
  hideout takes two rows of three.
- Nothing else moves: the home rule's words, the rows to the work, the
  aisles and the long hall are 0.207.0's.

**Tests:** 1 in `test_fixture_rows.py`. **Suite:** RESULT_SUITE. **The
library rebuilt:** RESULT_CENSUS.
