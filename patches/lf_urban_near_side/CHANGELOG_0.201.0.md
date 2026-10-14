## [0.201.0] - The urban street's near side: the mission's buildings stand among mid-rises

**Factory roadmap 241, the second cut.** The comps (the factory root's `docs/reference/URBAN_MIDRISE_COMPS.md`)
put the buildings at the sidewalk line, touching, on both sides of the street. 0.200.0 stood the far side as
that wall. Here the near side's frontage is filled the same way, between the mission's own buildings, so the
plate between them stops being the default.

- **`empties.infill(rows, extents, stream, roads, span_x, buildings)`** places Empties along the near
  building line, every front on it, facing the road (rot 0), dealt as the far side deals them. Three things
  stay clear:
  - **every mission building's sides,** `NEAR_PASSAGE` (4.0 m, `site_variation.CLEARANCE`, "a street you
    can move down") on each, so a side door, a side wall's dumpster and the way round to the back stay open;
  - **every road but the through road,** its band and frontage (a side street, the service lane);
  - **the plate's ends,** `CLEARANCE`.

  Where the next block dealt is wider than the room before an obstacle, the next narrower one is tried. A
  room no block fits stays open: a gap the street keeps. `building_rect` turns a footprint a quarter at a
  time.
- **The compose stage**, for an urban brief, stands both sides' Empties as blockers (`e*` across, `n*` near).
  It grows the plate for whichever side reaches further, and says how many stand on each. A strip brief
  runs none of it: its blockers, plate and log line are what they were.
- **Lot 0.121.0** keeps its fields, dumpsters, pads and cover clear of every blocker. Before it, near-side
  Empties would have stood where those planners put things.
- **`tests/unit/test_urban_near_side.py`** checks:
  - the near line and the facing;
  - every building's passage and the plate's ends;
  - the frontage filled, a narrower block taken where a wider will not fit, and no two neighbours the same;
  - a side street and a service lane never built over;
  - the quarter turn.

**Suite:** `python -m pytest -q`: exit 0, 2,372 passed (0.200.0's 2,365 and `test_urban_near_side.py`'s 7), 14 skipped (the real-tool smoke), 1 xfail, counted off the progress marks
