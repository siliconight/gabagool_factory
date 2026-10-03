## 0.89.0 - a walk between two doors is drawn square to the buildings

The walker, 2026-10-03, walking 0.88.0's lot, with two frames of the band
between the gas station's east door and the terminal's west door, and of
the same band's end against the bank: "these look goofy". 0.88.0 moved a
building path's ends to the doors and kept everything else about it: the
authored 8 m width (Level Factory's `STREET`, the clear ground its layout
reserves between two neighbouring shells) and one straight slab between the
ends. Between neighbours 8 m apart that fills an alley. Between two side
doors 18 m apart and 20 m offset it is a plaza laid across the lot on a
diagonal, with its squared ends cocked against both walls.

A building path whose two ends BOTH found a door is now drawn as a walk:
legs at the sidewalk's width (`_walk_width`: the narrowest `sidewalk` the
site's roads declare, 3.0 where there is none, never wider than authored),
out from each door along the axis the first door faces, and one jog on the
line halfway (`_walk_legs`). Doors within `ALIGNED_TOL` (0.25 m) of each
other across the walk get one straight leg; an offset under the walk's own
width gets one leg down the middle widened to reach both, not a kink. The
legs that run out from the doors own the corner squares and the jog is
drawn between them, so no two slabs lie coplanar over the same ground.

The authored record keeps its ids, takes the first leg's points and width,
and records what it was authored at as `route_width`; the further legs
follow it in the spec's list as plain point paths naming the route in
`leg_of`. Every reader already resolves a record through
`site_paths.endpoints`, so the surface zones, the step and kerb gates and
the route check follow the legs with no change of their own.

Left as they were: a path with an end that found no door (one straight band
at the authored width, as 0.88.0 and before), and two doors closer along
the leaving axis than the walk is wide (no room to run out and turn).

