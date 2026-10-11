## [0.208.0] - a home's room hangs a dome

**Roadmap 229's species step, beside Zoo 1.98.0 and Lux 0.75.0.** A home's
room has been laid by its own rule since 0.206.1 -- a fixture a 7 m bay
since 0.207.1, in a residence or in a residence-like room inside a shop --
and every one of those fixtures was still a 2 x 4 office troffer with a
cool fluorescent row behind it.

- **A home's room writes `dome` anchors** where it wrote `fluorescent`:
  the same rows, ids, drops and positions, a different type. Zoo hangs a
  flush-mount dome on each and Lux lights it warm from under its bowl.
  `_home_room` decides, as it already decided the rows: the building
  (`residence`) or the room's own words (`_HOME_WORDS`).
- A shop's own rooms keep their troffers, and the below-grade and objective
  rooms their bare bulbs: the bulb branch says it is no home.

**Library:** RESULT_LIBRARY.

**Tests:** 1 in `test_fixture_rows.py`; its row helper reads a dome as a
row. **Suite:** RESULT_SUITE.
