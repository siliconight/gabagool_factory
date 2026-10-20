---
name: dumpsters-beside-buildings
description: "SHIPPED Zoo 1.58.0 + Lot 0.90.0 (2026-10-03), awaiting the walker's eye. Walker: put front-load trash dumpsters beside buildings, at the sides or back, out of the way of where customers walk in; two reference photos (green and dark blue steel bodies, black ribbed plastic lids, hauler sticker)"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-03T17:08:24.970Z
---

The walker, 2026-10-03, with two photos: "we should have some trash dumpsters
next to buildings (sides or back where its not in the way of where customers
would naturally walk into the building)".

The references: a front-load commercial dumpster, 2-4 yard. Steel body,
painted one fleet colour (one photo forest green, one dark navy), sides
leaning out toward the top, fork pockets (channels) on both sides, a rim
bar, two black ribbed plastic lids hinged at the back and sloping to the
front, small casters, a white hauler sticker with name and phone on the
front, a yellow caution label. Format only: the hauler is an invented Delco
brand per [[fake-delco-brands-funny-and-crass]], never the photos' names.

**Why:** levels feel generated without the service clutter real lots have;
this is "props for cover AND life" ([[game-is-a-series-of-shooting-galleries]]).

**How to apply:** Zoo owns the species (`dumpster`), Lot owns where it
stands (a wall with no ground door, away from openings, clear of paths and
walks; never the street face). It is a walk-into solid, so it must read
against wall and ground ([[props-must-contrast-with-floor-and-walls]]). One
mesh per material, colour not a new material per dumpster (draw calls are
the budget). Related: [[walk-feedback-2026-10-03]].

**Shipped 2026-10-03:** Zoo 1.58.0 `dumpster` (one atlas, one draw, 92 tris;
haulers DELCO DISPOSAL green, JAWN HAULERS blue, MACDADE REFUSE maroon,
TINICUM TRASH CO orange) and Lot 0.90.0 `site_dumpsters` (one a building,
back first then a side, never a street face; `DOOR_CLEAR` 2.5 m and
`FRONT_REACH` 30 m are chosen, not walked). Walk copy
`_runs/walk_export_dumpsters`; frames `docs/findings/dumpster/`. Open: the
walker's eye on look and placement; whether some buildings want two, or
none (homes).
