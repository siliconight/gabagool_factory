---
name: route-census-reads-furnishing
description: docs/findings/furnish_route_cost/route_cost.py measures what furnishing costs a route; report it beside the nav gate for every furnishing change; reserve routes first (DC 0.250.0)
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-21T15:01:09.005Z
---

Since 2026-10-21 the factory has a census of what furnishing costs a route, built from the walker's lived-in guide
(`docs/reference/Lived_In_Levels_Clear_Navigation_4P_PVE_1999_PA.md`, filed that day as the answer to "the balance
of lived in levels that look real and not barren, but prioritize navigation and fun").

`python docs/findings/furnish_route_cost/route_cost.py` (`--controls`, `--spec <name>`). Per room, two arms of one
spec: AUTHORED, less what furnish and the shelter pass wrote; FURNISHED, as shipped. For each pair of doors and
markers it gives the shortest route for the 0.35 m body and the widest-path bottleneck against the body, the bake's
1.00 m floor and two abreast (1.90 m). It runs the whole library in about 5.5 minutes. To census another checkout,
pre-import its modules first (`patches/dc_reserved_routes/census_arms.py`).

**Why:** the nav gate only asks whether a marker is reachable; roadmaps 148 and 281 shipped density changes with no
number for what they did to movement, and the walker's order is navigation first. The census found the corner stores'
rows (Deli Counter 0.247.0) the worst; 0.250.0's reserved routes fixed them (routes over 10 % 20 -> 4, none on a
corner floor).

**How to apply:**
- Any furnishing or density change reports the census before -> after beside its nav gate, then cover and
  sightlines, then frames. That is the walker's reporting order.
- The guide's rule is to reserve circulation BEFORE placing. Deli Counter's `protected_routes` does that, gated per
  room by `reserves_routes`; corner-store floors only so far.
  - Extend it one room kind at a time, each measured.
  - Next are offices, vaults, and small objective rooms (door-to-marker routes +20-30 %).
- Routes must be SQUARE (4 directions, a turn costs). Diagonal corridors cut rows into scattered pieces. This was
  measured, refuted, and recorded in the docstring.
- Do not ask wall fixtures to keep off routes: asked, two stores lost their video poker cabinets.
- The census measures rows against an EMPTY floor. In the guide's terms rows are the functional build, and its 10 %
  flag is meant for dressing. The next refinement is an arm that keeps anchors and rows and strips only dressing.
- Of the census's 80 no-path pairs, 21 are its own limits (stairs at doors, markers inside their blocks). 11 are
  authored defects still open (cbp doors onto holes, the gas stations' cooler run across the office door, booths at
  primos and strip_retail front doors).

Related: [[rooms-not-crowded-not-barren]], [[game-is-a-series-of-shooting-galleries]], [[open-work-2026-10-09]].
