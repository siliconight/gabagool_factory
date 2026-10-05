## [1.69.0] - an Empty's windows: an air conditioner, bars

The walker's window photographs (the factory root's
`docs/reference/EMPTIES_COMPS.md`, "Window comps"):
- "window air conditioners in nearly every photograph": a white or beige box
  in the lower sash, standing out of the wall, so geometry;
- bars "proud of the frame on bolted straps". They were painted into the
  pane.

Patina (>= 0.26.0) orders both from the slot Deli Counter (>= 0.181.0)
marks, and `dress_cover` builds them.

### Added
- **`ac_unit`** (`dressing.ac_parts`): a 1990s 6,000 BTU window unit,
  52 x 36 cm, standing on the sill.
  - It stands 30 cm out of the wall and reaches back through the reveal to
    the pane, 13 cm behind the face.
  - Parts: fins across its back, which is the side the street sees; louvres
    down its flanks; accordion panels closing the sash out to the jambs; two
    L brackets under the overhang.
  - White painted metal: the gutters' material and colour. Since 1.68.0
    merges a building's covers per side per material, a unit on a side with
    gutters adds no draw call.
- **`window_bars`** (`dressing.bar_parts`): 18 mm square uprights about
  12 cm apart, standing 4 cm off the wall and running past the head and the
  sill.
  - Two flat straps behind them reach past the jambs onto the brick, bolted
    on standoffs.
  - Black painted iron (`IRON_COVERS`): the same painted metal in a second
    colour, so one more surface on a side that has bars, however many
    windows they cover.

Every part of both stands at least 1 mm off the wall face, and touching
parts overlap rather than share a face.

### Changed
- **A barred pane paints only its room.** The bars are geometry now, 3.5 cm
  off the wall with the pane 13 cm behind it. Painted as well, they drew a
  second grid that slid against the real one as the eye moved. `lit_bars`
  and `dark_bars` keep their names (Deli Counter's mix and the module stems
  ride on them) and now paint exactly `lit`'s and `dark`'s rooms.
  `_bars` and `BAR_RGB` are gone.

### Corrected
- **`METAL_COLOR` said it was "the flat colour, used only with no skin
  library".** It is also the tint. `make_material` tints a tintable pack and
  names the material for it, which is the `_dbdbd4` on every shipped
  gutter. The bars' black works for the same reason.

### Cost, to be priced
- **The unit:** none expected on a side with gutters.
- **The bars:** one surface per barred side.
- **Not done:** the NYC bellied grille that takes a unit behind it, and the
  cage around a unit. No unit is placed behind flat bars (Deli Counter).
