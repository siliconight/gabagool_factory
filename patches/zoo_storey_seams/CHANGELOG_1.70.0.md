## [1.70.0] - no groove at a storey seam

### Fixed
- **Short pale-then-dark dashes along the storey line of an Empty's wall.**
  Seen on the stone rowhome's end wall in cold runs 9153, 9154 and 9155, at
  regular spacing.
  - **Measured on 9155's own module GLB**
    (`wall_delco_1997_01_w200_h310_mstone_idrywall.glb`). The panel's ends
    are square: 0.81.1's butt planes. Its top and bottom edges still carried
    the style's 3 mm x 3 mm chamfer: vertices at +-1.547 against the face's
    +-1.550.
  - **Where it showed.** An Empty stacks storey on storey; Deli Counter
    0.175.2 gives gs_empty_rowhome_d's end wall 0.0-3.1 then 3.1-5.9. So two
    chamfers met as a V 6 mm wide and 3 mm deep along the whole seam.
  - **Why dashes.** The frames' camera is 65 degrees vertical at 1152 x 648,
    so a pixel 10-15 m away covers 18-26 mm and the groove is a quarter to a
    third of one. A sub-pixel line at a slight slope aliases into regular
    dashes. The up-facing facet caught the fill light and the
    down-facing one did not, hence pale-then-dark.

  It is the same groove 0.81.1 removed from a run's vertical joints, turned
  on its side.

### Changed
- **`arch.butt_planes(species, w, h)` takes the module's height.** A run
  module's butt planes are its two ends plus its top and bottom
  (`z = +-h/2`).
- **Why the top and bottom count as joints.** In Deli Counter's model they
  always meet something:
  - the next storey's module, flush, on an Empty;
  - the slab's edge on an enterable building (bank_tower_a02: 0.0-4.3, the
    slab, 4.6-8.9).

  The height is required, so a caller cannot silently keep the old pair.
  The corners a person can see keep their chamfer: a jamb's reveal, a sill,
  a header's underside.

### Corrected
- **`butt_planes` said the top and bottom of a face "are not on these
  planes and keep their chamfer"** as real corners.
  `test_butt_joints.py` pinned it twice:
  - the top edge "lies in neither";
  - the built wall "keeps its top".

  Both pins are reversed, and each says what it used to assert.
