## [0.204.0] - Heights by cause: the urban wall stands its lowest blocks across from the action and rises away from it

**Factory roadmap 241.** The comps (the factory root's `docs/reference/URBAN_MIDRISE_COMPS.md`): "the tallest
stand furthest away", the skyline stepping up with distance. The roadmap wrote the rule down: heights by cause,
taller away from the action, never by jitter. 0.203.0 dealt the wall's blocks off a shuffled bag, and their heights
fell where the deal put them: cold run 9291's seed_9104 stood 5, 7, 5, 10, 8, 6, 4, 12, 6 and 8 storeys from west
to east.

- **`empties.terrace(..., action=None, heights=None)`.** On a continuous wall given both, each block is the one on
  the bag whose height is nearest the height a block standing at its centre is drawn toward (`_target`). That is
  the shortest design's height across from the action's centre, rising with distance from it to the tallest's at
  the plate's farther end (`_by_height`).
  - Every design is still dealt once a bag, and no two neighbours are alike.
  - A block that does not fit before the plate's end gives way to the nearest-height one that does.
  - The strip's terrace, and an urban wall without both, are dealt exactly as before.
- **`street_line.shell_top`** reads a shell's height off its collider hulls. The factory's mid-rises read 13.2 m
  at four storeys to 38.7 m at twelve.
- **The compose stage**, for an urban brief, takes the action's centre as the middle of the span the spawn,
  objective and extraction buildings cover along the street, and the tops off the shells.
  - It says `URBAN_HEIGHTS_UNREAD` and deals as before when it cannot read either.
- **Measured, the test's street:** six designs, forty seeds, the action at three places. The rank correlation of a block's distance from the action with its height, over 120 walls, reads -0.69 to +0.77 (median +0.03) dealt alone and +0.58 to +0.92 (median +0.82) drawn by cause (`patches/lf_heights_by_cause/` in the factory root, previewed before it was applied); the test asks every wall at 0.5 or more and the median at 0.75 or more
- **`tests/unit/test_urban_heights_by_cause.py`** has 4 checks. All 4 fail on 0.203.0, on the new arguments and `shell_top` before any behaviour -- the behaviour is the measurement above. The suite: `python -m pytest -q`: exit 0, 2,387 passed (0.203.0's 2,382, `test_urban_heights_by_cause.py`'s 4, and the sibling-locator guard's case over the new file), 14 skipped (the real-tool smoke), 1 xfail, counted off the progress marks.
