## [1.72.0] - an Empty's front door: painted per house, and an iron security door

The walker's photographs (the factory root's
`docs/reference/EMPTIES_COMPS.md`, "Window comps"):
- the South Philly row paints its doors house by house;
- one carries "a black iron security door with a grille".

Deli Counter (>= 0.182.0) authors each Empty's front-door finish and
security door. Patina (>= 0.28.0) orders the security door.

### Added
- **`core/doors.py`, `FINISHES`**: navy, oxblood, green, black, white,
  stained. Each is a skin kind and its tint: the paints are `metal_painted`,
  whose `metal_painted_neutral` pack is achromatic and tintable, and
  `stained` is the wood the leaf always wore. The order is the contract with
  Deli Counter's `empty_panes.DOOR_FINISHES`.
- **The finish rides in the module's name as `_e<finish>`** (`kit.module_stem`),
  after the pane's `_p`; `_d` is the depth's. `plan_kit` reads it only off a
  facade doorway and only when it is a known finish; `dna` carries it to the
  recipe. Two facade doorways of one size in different paints are different
  modules.
- **`_arch.build_slab` paints the leaf in it** (`doors.leaf_material`). A
  finish names its flat material for itself, so two painted doors built in
  one process cannot share the first one's colour through the material
  cache. No finish is the stained leaf, named as before.
- **`security_door`** (`dressing.security_door_parts`): hung in the
  doorway's reveal, 2 cm in front of the leaf and 2 cm behind the face.
  - Two stiles; three rails: top, bottom, and the lock rail at handle height.
  - Uprights about 11 cm apart, and a lock box.
  - In the bars' black iron (`IRON_COVERS`), so on a side with barred
    windows it merges into their mesh.

### Corrected
- **`FACADE_DOOR_COLOR`'s navy never showed.** It was the flat colour, and a
  skinned `wood_panel` takes no tint, so every Empty door rendered brown.
- **Cost:** a finish costs no draw. A doorway module is drawn once per
  placement either way. The comment that said per-house colour would have
  to be instance data now says why it is not.
