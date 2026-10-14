## [0.203.0] - A spent bag is not a full street: the near side deals afresh where a design fits

**Factory roadmap 241, the urban street's near side.** `empties.infill` deals the near side's blocks as the far
side deals them: every design once, then a new bag. 0.201.0 left a room open whenever what was left in the bag
was too wide for it, even though the next bag held a design that fits.

- **Cold run 9289's seed_9104** kept a 6.70 m room between two of the mission's buildings that its 6.6 m block
  fits, because that block had been dealt already.
- **Measured on this release's test street:** three rooms of 42, 22 and 32 m, designs 15, 24 and 6.6 m wide,
  forty seeds. 0.202.0 left 58 of the 120 rooms with a design's width or more standing empty, some of them whole.
- **Now:** where nothing left in the bag fits the room and some design does, a fresh deal goes BEHIND the bag's
  remainder and the room is tried again (`_fitting`).
  - The remainder still shows first wherever it fits.
  - A remainder no design fits asks nothing of the stream, so a street whose rooms the bag always fills deals
    exactly as before.
- **A strip brief runs none of it:** the near side is urban only. An urban street's near side stands more blocks
  than 0.202.0's: on the test street, each of the 58 rooms 0.202.0 left with a design's width or more now holds blocks to within less than the narrowest; on urban_row_001's own candidates, the factory's cold run 9291 records it.
- **`tests/unit/test_near_side_fresh_deal.py`** has 2 checks. 1 of the 2 fails on 0.202.0, the invariant; the guard holds on both, a property the old code also had. The suite: `python -m pytest -q`: exit 0, 2,382 passed (0.202.0's 2,379, `test_near_side_fresh_deal.py`'s 2, and the sibling-locator guard's case over the new file), 14 skipped (the real-tool smoke), 1 xfail, counted off the progress marks.
