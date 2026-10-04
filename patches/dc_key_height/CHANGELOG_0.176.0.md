## [0.176.0] - One module name, one geometry, in every building

Cold run 9148 carried 0.175.2, which runs an Empty's walls the full storey
below its roof storey. They are now 3.1 m there and 2.8 m under the roof.

Zoo names a wall, doorway or window by its width alone. So both heights
built as `wall_delco_1997_01_w200_mbrick_idrywall`, and the kit listed it
twice: two buckets of 11 slots, one file. The file on disk was the 2.8 m
one, and every 3.1 m side wall stood a 2.8 m panel. The frames showed a
0.3 m strip at each storey line. A headless census of the walk copy measured
`Wall_Panel` at 2.80 m in 3.10 m slots.

Across the library as built, 14 names covered two sizes, every one in the 8
facade shells (walls and windows, 2.8 against 3.1 m; the storefront facade
3.1 against 3.4). No enterable building collides.

`themed_tscn.mark_height_keys(slots)` groups a building's slots by the name
`resolve_themed_stem` builds and marks every slot whose name covers more than
one height with `fit.key_height`. `write_slot_manifest` calls it before
writing. Two things follow from building on this module's own name:
- the mark cannot disagree with the name it repairs;
- only a colliding name is marked, so every other building keeps every
  name.

The mirror (`resolve_themed_stem`) and Zoo 1.60.0 add `_h<cm>` to a marked
slot. `docs/SLOT_MANIFEST.md` names the field. The manifest version is
unchanged: the field is optional, and an older Zoo ignores it and builds the
old collision.

`test_key_height.py`:
- two heights under one name are marked and split (fails on 0.175.2);
- the control: one height is left alone and keeps its name;
- across every built manifest, no exact-fit name maps to two sets of dims
  (14 on 0.175.2).
