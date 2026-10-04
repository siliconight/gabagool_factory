## [0.23.0] - a zone dresses only the ground it owns

### Fixed
- **Overlapping zones dressed the same ground twice.** `zone_for` has said
  since it was written that the precedence rule travels in the data and that
  "a placement counted against two budgets is counted against neither" --
  and `plan` never called it. Each zone scattered over its own bounding
  box, and Lot's `open_ground` box is the whole plate, so open-ground
  clutter at MEDIUM landed on the roads (LOW), the sidewalks, the perimeter
  and the walks, on top of what those zones placed. Measured on cold run
  9141's shipped manifest: 2,436 of 5,232 placements stood where the
  precedence rule gives the ground to another zone; across families,
  open_ground on road_0 445, on the perimeter 238, on the sidewalks 265, on
  road_1 115, on walks 58 -- and all 256 pieces on the parking fields
  (0.29 a m2), the pebble-strewn aisles in the walker's frames.
- A candidate point is now kept only where `zone_for` names a zone of the
  placing zone's own FAMILY (`zone_family`: Lot's `zone_family:<f>` tag, or
  the zone's id). By family, not identity, because Lot chops a corridor
  into boxes that overlap at their joins and a point on a join is the same
  ground either way. Asked after the asset, scale and yaw draws, so a
  refusal does not shift the points after it; refused as
  `DRESS_REFUSED_ANOTHER_ZONES_GROUND`, recorded in `keep_out`.

The site-level effect -- fewer pieces on every road, sidewalk and edge, the
fields at a road's density with Lot 0.95.0 -- is measured on cold run 9143
(`docs/cold_runs/cold_9143/NOTES.md`).

`tests/test_surface_dressing.py`: open ground places nothing on a road's
ground and still dresses its own; a corridor's boxes share their join; the
control -- every zone given one family -- does put open ground on the road,
so the first test can fail; `zone_family` reads the tag or falls back to
the id.
