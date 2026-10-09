## 0.102.1 - the bus stop stands on its band before the corner is spaced against it

**Roadmap 219, the walker's note 6:** "newpaper stands inside of a bus stop
thing and pole?" On cold run 9213 (club_block_014):
- one news rack stood 0.11 m from the stop's flag post, so the post ran
  through it;
- the other's edge (x 7.79) passed the shelter's end (7.57), so the
  shelter's corner post ran through it.

**Why.** `plan_furniture` added `_bus_stop`'s pieces (the shelter, the
bench and the flag) to its output, but never to the band's `placed`.
`_stop_corner` spaces the mailbox, the racks and the payphone against
`placed` with `_free`, so it could not see the stop. When a marker or a tree
took a corner piece's station, `_nudged` stepped it up to 4 m, onto the
stop. The hydrant passes read the same `placed` (the band's record in
`bands`), so they could not see the stop either.

**Fixed.** The stop's pieces join `placed` as soon as `_bus_stop` returns,
before the corner and before the hydrants.

**Tests.** `test_no_stop_corner_piece_stands_on_the_stop`
(`tests/test_site_furniture.py`) sweeps one marker along the stop's band of
`coldrun_kerb_probe.json`, 81 positions 0.25 m apart. At each it asserts no
mailbox, rack or payphone footprint overlaps the shelter or the stop's flag.
On 0.102.0 it finds 22 overlaps, among them a rack 0.10 m from the flag
post and another over the shelter's end: 9213's two, on the probe. With the
fix, `tests/test_site_furniture.py` reads 28 passed, and the suite 714.
