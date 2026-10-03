## 0.91.0 - a walk leads to a door, and a side door gets a landing

The walker, 2026-10-03, walking 0.90.0, with a frame of the bank's west
wall: "still have sidewalks going to walls", and of 0.89.0's square walk
between the gas station's east door and the terminal's west door, "looks
better, but you should do some research as to what looks more natural on a
path between the sides of 2 buildings (not the normal path that customers
would likely take)".

THE WALL WAS A BREACH. The bank's west wall has no door: it has a breach
(a wall a team blows through) and a high window, and 0.88.0 snapped to any
opening `site_enterability` counts as a way in -- a door, a garage, a
breach, a vaultable window. A walk now leads only to an opening of kind
`door` a body fits through.

WHAT THE RESEARCH SAID (sources and readings in
`docs/findings/entry_paths/NOTES.md`): design codes ask for a continuous
walk along a facade with a customer entrance, tied to the street sidewalk;
a site walk crosses open pavement only where it must, square to the aisle,
which is never itself the walkway; building codes put a level landing
outside every exterior door, at least the door's width and 36 in deep, 60 x
60 in where accessible, with the lot's own pavement past it. Two separate
businesses' side doors are not joined by a walk.

So `site_paths.snap_to_doors` now:

  * slides a door spur to the nearest DOOR facing the way it leaves and
    runs its near end up to the wall, `DOOR_BURY` (5 cm) into it, where it
    stopped a metre short;
  * leaves a spur that meets no door UNDRAWN (`drawn: False`) and says so
    (`LOT_PATH_END_OFF_DOOR`) -- the record stays, because the street graph
    reads it to know the building meets that road;
  * leaves every building-to-building path undrawn, record kept for the
    connectivity graph;
  * gives every door no walk reaches a LANDING: a slab from the wall out
    `LANDING_DEPTH` (1.525 m, 60 in) along the door's normal, the door's
    width plus `LANDING_SIDE` (0.3 m) each side, never under `LANDING_MIN`
    (1.525 m), appended as a point path naming its building in
    `landing_of`.

`site_paths.drawn(site_spec)` is the list the six readers that draw or
measure a walk now iterate: the slabs, the surface zones, the step gate,
the kerb crossings, the furniture keep-out, and the enterability route
check (which also skips landings, so its "no authored path leads to a clear
entry" warning keeps meaning that). The connectivity graph and the plate's
extent read every record, so which buildings connect and how big the
ground is do not move.

0.89.0's legs (`_walk_legs`, `WALK_WIDTH`, `ALIGNED_TOL`) are gone with the
walk they drew.

`tests/test_site_paths.py`, nine tests: a spur slides to its door and runs
to the wall; a breach, a vaultable window and a garage are not doors to
walk to; two neighbours' side doors get a landing each and no walk; a
narrow door's landing is still 60 in wide; a rotated building's landing
points out of its own wall; the street graph still joins buildings whose
walk is not drawn; endpoints; the route check counts a walk and not a
landing; every drawing reader reads the drawn list.

