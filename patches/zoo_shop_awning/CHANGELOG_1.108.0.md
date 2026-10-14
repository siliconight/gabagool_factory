## [1.108.0] - a corner shop's canvas awning, `shop_awning`

**Factory roadmap 241, the corner shop.** The comps: "Corners carry the life. The corner building has the shop at
grade (lit, awning), homes above"; the Empties comps (the factory root's `docs/reference/EMPTIES_COMPS.md`) list
the awning as Zoo's to build. Deli Counter 0.218.0's corner blocks have the shop and not the awning.

- **`core.shop_awning_forms`**, pure, drawn from a slot's box alone: the common storefront shed.
  - A canvas slope from the wall down to a 10 in valance along its front, closed at each end by a triangular
    cheek.
  - The canvas is a 2 cm box, not a face, so it reads from below as from the street.
  - The frame is Zoo's: the wall at +Y, the street at -Y.
- **The forms are `<shape>_<colour>`:** one shape, `shed`, in four canvas colours -- red, green, navy, black. The
  colour is the form's because it is the shop's. Each colour is its own material, one a module and one module a
  building, so no merge is lost by it.
- **No face of one part lies on another's.**
  - The slope stops 4 mm inside the valance and 6 mm short of either end, inside the cheeks.
  - The cheeks stand 3 mm inside the ends, 4 mm off the wall plane and 3 mm over the valance.
  - So `prims.coincident_pairs` reads none over 54 sizes before Blender does. Every part is closed and wound
    outward.
- **The recipe** builds the lists through `bpylayer.prim_mesh` on `M_ShopAwning_canvas_<colour>`: Pixelcoat's
  `canvas`, tinted. No collision.
- **Measured in Blender 5.1.1, on a copy of 1.107.0 with these files in it** (`patches/zoo_shop_awning/census.log`,
  `kit.log` in the factory root):
  - `coplanar_census.py --species shop_awning bollard`: the awning's three corners are 40 / 40 / 40 tris with 0
    pairs, and the bollard's known 2 / 2 / 1 is the control.
  - `zoo_cli --build-kit` on four slots at the corner blocks' widths: every module PASS -- one mesh, one
    primitive, one material, 40 tris, and bounds the slot's to the millimetre.
- `CENSUS_BUILDS` 393 -> 396, and the species is in `genome/minted.json`.
- **`tests/test_shop_awning.py`** fails to import on 1.107.0 (no `core.shop_awning_forms`).
- **The suite:** `python -m pytest -q tests`: 4,968 passed, 458 skipped, 1 xfailed in 5 min 46 s, where 1.107.0 passed 4,627 and skipped 456. Passed: the new file's 338 pure checks and the three material sweeps over the new genome. Skipped: the new file's Blender check, and `test_recipe_reads_its_genome`'s, which skips a recipe that builds through `prim_mesh` as it does the railing's.
- **Blender:** `tests/test_shop_awning.py` inside Blender 5.1.1 (the command in `tests/test_shop_panes.py`, on this file): 339 passed, the awning built through `build_module` wearing `M_ShopAwning_canvas_green`.
