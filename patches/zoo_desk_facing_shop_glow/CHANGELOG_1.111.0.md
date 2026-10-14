## [1.111.0] - a desk's stock faces its sitter, and a shop's room glows under its goods

**The walker's walk of cold runs 9305-9307, 2026-10-14** (the factory's `docs/findings/walk_2026-10-14/`, findings 1
and 3).

### Fixed
- **Every cubicle's computer faced the panel.** The walker, in urban_row_001's office: "computers facing the wrong
  way".
  - `recipes/cubicle_bank.py` promises stock "facing that band's sitter", and `_surface_stock.plan_surface` reads
    `facing` 0 as "they stand at -Y".
  - `cubicle_forms.plan` stands a band's work surface on the `-out` side of its spine, its drawer fronts that way,
    and handed its stock `pi if out > 0 else 0`: every monitor, keyboard and phone turned toward the spine, on both
    bands of every bank.
  - Now `0 if out > 0 else pi`. `test_cubicle_bank.py`'s new test reads each bay's facing against its own drawer
    fronts. On 1.110.0 it fails at every bay.
- **A lit shop's window read as bars and dots up close.** The walker, at the corner grocery's glass: "not sure what
  I'm looking at here in the window".
  - `shop_panes._room` painted the room behind the goods into the emission map at its full colour, and the goods at
    `_scale(rgb, 120)`, 47 %. The emission dominates at night, so the goods glowed dimmer than the wall behind them,
    and the grocery's fluorescent room (232-242 at its middle) at `EMISSION` 2.2 clipped to white.
  - The room now paints its emission at `ROOM_GLOW` (90 of 255, 35 %) of its colour, so the goods, the shelves'
    shadows and the light strips carry the picture. `EMISSION` stays 2.2: a shop is still the brightest window on
    the street (`test_a_shop_glows_brighter_than_a_home`).
  - All four lit rooms take it, the deli, the grocery, the bar and the laundromat.
  - `test_shop_panes.py`'s new test reads each lit cell's whole emission against its paint: under half. On 1.110.0
    every lit cell reads above it.

**Suite:** `python -m pytest -q tests`: 5,354 passed, 462 skipped, 1 xfailed in 7 min 38 s, exit 0 -- 1.110.0's 5,352 and the two new tests. Both new tests fail on an archive of 1.110.0 with the new test files in it and pass on 1.111.0 (the factory's `patches/zoo_desk_facing_shop_glow/prove_tests_1110.out.txt`); each lit cell's glow over its paint went 0.62-0.76 to 0.24-0.37

**Blender:** inside Blender 5.1.1: `test_shop_panes.py` and `test_cubicle_bank.py`, 28 passed, the shop pane built wearing `M_Shop_pane_Face`; `test_coincident_faces.py`'s residue row for `cubicle_bank`, its three corners built with their office stock, 1 passed, the count as pinned
