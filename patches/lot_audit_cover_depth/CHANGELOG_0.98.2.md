## 0.98.2 - the audit measures cover by its depth, not its height

**Roadmap 211.** `site_audit._cover_rects` read a cover record's `size` as
[plan x, plan y, ...]. Every planner writes [plan x, height, plan y], the
frame `lot.py:2123` stands each piece's box in, at half the middle number.
So since v0.17.1 the audit has measured every cover piece with its height
for a depth:
- 3.05 m for the getaway van's 6.8 m;
- 1.73 m for a parked car's 4.7 m;
- 6.0 m for a streetlight's 0.7 m.

It now reads the third number.

### What it moved: nothing on disk

One check reads the extent: `S_NAKED_ANCHOR`, the distance from the crew's
spawn and extraction to the nearest cover or building edge.

`patches/lot_audit_cover_depth/census_naked_anchor.py` audited every site
spec on disk both ways:
- 115 specs, 112 of them with cover: every drawn site in the workspaces and
  every spec under `specs/`.
- 18 `S_NAKED_ANCHOR` findings as shipped.
- **0 that the two readings disagree on.**

A constructed site flips -- a car 10 m off the anchor along its length -- so
the census can see a difference. None of the real anchors sat in the window.

### Corrected: two overstatements in 0.98.1

**"Two coarse checks."** 0.98.1's changelog said the error feeds two coarse
checks. It feeds one: `S_BARE_LEG` counts cover by each rect's centre, which
the error does not move.

**"One at a time from one side."** 0.98.1's comment in `place_enemies` said
the one-leg spread brings six enemies one at a time from one side. That held
on two sites of three.
- **The site where it failed.** Cold run 9199 played seed_9256 with the van
  for the first time. The line from its van to its vault runs through the
  spawn building, a parking garage, so the samples that fell in it were
  pushed out to either side: two enemies 17.7 and 23.4 m from the crew,
  94 degrees apart.
- **What it cost the crew.** It lost 41 in 25 runs (49 in 9197).
- **What crew losses track** is enemies arriving together from more than one
  direction, which the one-leg spread makes on some sites and not on others.

The comment now says so, and that the walker has decided the walk back:
responders arrive after the job, spawned by the gameplay layer (roadmap 212).

### Tests

`tests/test_audit_cover_depth.py` uses sites built so the two readings must
disagree. Each expected verdict is asserted from the piece's dimensions and
`ANCHOR_RADIUS`, beside the case.

**Results:** on 0.98.1 all 3 fail:
- the car's anchor is called naked;
- the streetlight's anchor is not;
- the car's rect is 1.73 m deep.

**Suite:** 687 passed (684 + 3), `python -m pytest -q`.
