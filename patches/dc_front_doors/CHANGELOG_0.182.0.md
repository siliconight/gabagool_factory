## [0.182.0] - An Empty's front door: a painted finish per house, and two iron security doors

The walker's photographs (the factory root's
`docs/reference/EMPTIES_COMPS.md`, "Window comps"):
- the South Philly row's doors are painted house by house;
- one carries "a black iron security door with a grille".

Every Empty door rendered the same brown wood. Zoo 1.61.0's navy was a flat
colour that a skinned wood panel never takes.

- **The spec says what each house's front door is.** It is authored per
  house, like `vacant`:
  - `door_finish`: one of `empty_panes.DOOR_FINISHES` -- navy, oxblood,
    green, black, white, stained;
  - `security_door`.

  A seeded draw over the six rowhomes gave three finishes, two of them
  twice, and no iron door, the same way a drawn vacancy left none vacant.
  The family now authors six different doors, with iron on two:
  - a, navy, iron;
  - b, white;
  - c, oxblood;
  - d, green;
  - e, black, iron (the vacant one, secured);
  - f, stained.
- **The front door's slot carries them**, as `door` and `security_door`
  beside its `glazing`. The opening's `tag` now rides on the hole, so the
  front door is the one the preset tagged `front_door`. The back door
  carries nothing and keeps the stained wood.
- **The finish is in the module's name** as `_e<finish>`, after the pane's
  `_p` and before `_g`. That mirrors Zoo 1.72.0's `kit.module_stem`, because
  two doors of one size in different paints are different modules. (`_d`
  is the depth's.)
- **An unknown finish is refused**, not dropped.

Zoo (>= 1.72.0) paints the leaf in the finish and builds the security door
Patina (>= 0.28.0) orders. The six rowhome specs are rewritten from the
preset.
