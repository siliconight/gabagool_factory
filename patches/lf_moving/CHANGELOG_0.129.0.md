## [0.129.0] - the import turns Zoo's turning parts and walks the slush's churn

Small things that move, items 1 and 2 of the design at the factory root
(`docs/proposals/MOVING_PARTS_DESIGN.md`). The walker, 2026-10-02: "start
with the roller grill, and i want some motion on the slurpee stuff too".
The rule the design set: a thing moves because something drives it, and
both of these are motors in a store that is open. Nothing moves a node and
no script ticks; it is all the shader clock, installed at import the way
the screens' pass and the shutters' clock already are.

### Added
- **`_turning_parts` in `zoo_worldskin.gd`, for every GLB.** Zoo 1.55.0
  builds a part that turns -- the grill's rollers, its dogs -- as a surface
  of its own, every vertex carrying its AXLE in its second UV set in this
  engine's axes, and names the material for its axis and rate:
  `M_Roller_metal_bare_turn_x36` is 36 degrees a second about +X,
  `..._turn_xn36` the other way. The surface's material is REPLACED (a
  second pass cannot move the first) by a shader carrying the flat
  material's own numbers -- albedo times the vertex colour, roughness,
  metallic -- that turns VERTEX and NORMAL about the axle in UV2 on TIME,
  phase per node from NODE_POSITION_WORLD so two grills are not in step.
  Zoo keeps a turning kind off the skin library for exactly this: there is
  no texture to carry. Only a name that names a rate is read; a `_turn_`
  name without one is warned about and left.
- **`_churn_passes`, for every GLB.** Zoo's slush tile is the flavour and
  its ice now; the diagonal bands it used to paint are drawn here, moving:
  a darkening next_pass over every `M_Slush_*_Face`, a hair proud like the
  CRT pass, walking the same diagonal (three bands round, one and a half
  up; the dark band 3/16 where 2/16 was painted, because four pixels of a
  96-texel tile vanish under motion at a metre) round the barrel once every
  6 s. The facets say where they are in their second UV set (u round, v
  up); every other corner carries v = 2 and is discarded. DARKENS ONLY, for
  the CRT pass's reason: a barrel Lux has cut the power to stays black under
  it, and the face's own material is kept so Lux's binder still finds it.
  The light band the tile painted is what that costs.
- `tests/unit/test_worldskin_moving_parts.py` holds the shape: the name
  pattern, which UV set, the sentinel, replacement with the flat numbers
  for one and a kept face with a pass for the other, darkening only, phase
  per node, both before the kit branch, nothing touched twice.
  `test_worldskin_crt_motion.py` admits `_turning_parts` to the replacers.

### Measured
On a rebuild of cold run 9139's lot with Zoo 1.55.0, walked as shipped
(nothing respawned), three frames half a second apart at each thing and at
a still control, the pixel difference between consecutive frames (mean over
the frame, 0-255, and pixels moved by more than 8):

    grill, customer's side    1.72 / 1.29 mean    7,113 / 5,695 moved
    grill, close              4.39 / 6.23 mean   23,773 / 33,299 moved
    slush barrels             0.66 / 0.66 mean    3,119 / 3,013 moved
    control (the ceiling)     0.00 / 0.00 mean        0 / 0 moved

The import did what it says in the shipped scene: both turning surfaces
are the shader with rate +/-0.628 rad/s about axis 0; the slush face is a
standard material with the churn pass as its next_pass at period 6.0.

Priced on the fixed-station harness, fresh copies, idle machine, 9139's
package run before and after as the control, all in one session:

    package        mean median ms   mean p95 ms   mean draws
    9139           4.35             5.07          1080.9
    this           4.09             4.41          1081.2
    9139 again     4.00             4.22          1080.9

    draws: 9 of 53 views differ, by +1 to +3 -- the views that see the
           store: two surfaces a grill, one pass a slush machine
    median ms, this minus 9139's second pass:  mean +0.09, max |2.43|
    median ms, 9139's first minus its second:  mean +0.34, max |3.81|

Within the instrument's own spread. The vertex stage runs on 1,696
vertices a grill; the churn pass on one surface a machine.

### Refuted on the way, kept
The first shipped build turned the rollers 0.7 m off their axles: Zoo had
written the pivots in the engine's axes at build time, then re-centred the
module, and the vertices moved while the pivots did not -- the shipped
scene read vertex y 0.24..0.32 against pivot y 0.95..1.00. Zoo 1.55.0
carries the layer with the vertices and converts it at export; this side
was right and is unchanged by it. The lesson belongs to item 3's wind
weights too and is written into the design.
