## 0.90.0 - a dumpster at each building's service side

The walker, 2026-10-03, with two photographs of front-load containers: "we
should have some trash dumpsters next to buildings (sides or back where its
not in the way of where customers would naturally walk into the building)".
Zoo 1.58.0 builds the species; this decides where one stands.

`site_dumpsters.plan_dumpsters`, called in `assemble` after the street and
the pylons and before the cover planner: one a building, against a wall
that is not a street face. A wall is a STREET FACE when a road's band lies
in front of it within `FRONT_REACH` (30 m: Level Factory stands a face 2 m
from its sidewalk and a forecourt put one 15 m back on cold run 9139). The
BACK -- the wall opposite the nearest road -- is tried first, then the
others in an order the building's id picks, so a row does not put every
dumpster on its east side. Along the wall it stands toward a corner,
`CORNER_IN` from the end, stepping in a metre at a time until the station
is clear: `DOOR_CLEAR` (2.5 m) along the wall from any way in,
`WINDOW_CLEAR` (0.5 m) from any other ground opening, `APPROACH_CLEAR`
(1.5 m, the enterability gate's staging depth) from every entry's approach
point including the ones round the corner, off every path and walk
(`site_furniture.path_corridors`, which since 0.89.0 is the legs), off
every road band, clear of the other buildings, of what already stands and
of the mission's markers, and on the plate. Its back is `WALL_GAP` (0.25 m)
off the wall and its front faces away from the building.

A building with no wall that takes one prints `LOT_DUMPSTER_NO_ROOM` and
gets none; each one stood prints `LOT_DUMPSTER_PLACED`. The piece is cover
like the street's: a slot Zoo builds to, a box in the greybox, a solid in
the navmesh, and the cover planner counts it.

THE HAULER IS THE PIECE'S `variant`, picked by the building's id, and it
needed two rungs that cover did not have: `write_site_slots` writes a
piece's `variant` onto its slot (non-zero only, as Zoo spells `_n<v>`), and
`cover_module_refs` asks for the variant's module before the plain one, so
the second hauler's dumpster falls back to the first's and never to a box.

`DOOR_CLEAR` and `FRONT_REACH` are chosen and say so; neither has been
walked.

`tests/test_site_dumpsters.py`, nine tests: the back first, facing away, a
gap off the wall, toward a corner; never a street face; clear of a back
door and out from under a window; a neighbour's door across a gap not
boxed in; off walks, off what stands, on the plate; no room said and nothing
stood; a row gets one each, no two sharing a station, the same every run;
the slot carries the hauler and the module's name does; Lot knows the
species.

