## [1.107.0] - a corner shop's window, painted: its own atlas of storefront states

**Factory roadmap 241.** The urban comps (the factory root's `docs/reference/URBAN_MIDRISE_COMPS.md`): "Corners
carry the life. The corner building has the shop at grade (lit, awning), homes above", and in their second frame,
"a lit restaurant at street level under an awning -- the warm light the eye goes to first". An Empty's windows are
paint (`window_panes`, 1.64.0): one atlas of sash states in portrait cells, full, appended to and never inserted
into. A storefront is wider than a sash and shows a different room, so it is its own atlas. This is step 1 of the
factory root's `docs/proposals/CORNER_SHOP.md`.

- **`core.shop_panes`**, pure: `window_panes`' machinery on a landscape cell, 112 x 96 px, three to a row, two rows.
  - Six states, appended only: `shop_deli` (warm tungsten, goods on shelves, a lit deli case), `shop_grocery`
    (cool fluorescent, aisles, a light strip), `shop_bar` (dim amber, bottles, a neon line low), `shop_laundry`
    (cool, a row of washers), `shop_gate` (a roll-down gate, unlit) and `shop_dark` (dark glass).
  - A 1990s aluminium storefront painted over the glass: the frame, a transom bar a fifth of the way down, two
    mullions and a kick plate.
  - The emission image is black wherever no shop light shows, the aluminium included.
  - `EMISSION` is 2.2 against a window's 1.6: the shop is the light the eye goes to first.
- **`recipes/_arch.py`**: `PANE_ATLASES` maps a pane's state to its atlas, its material and its images.
  - A facade window whose `pane` is a shop state wears `M_Shop_pane_Face` (images `shop_pane_albedo` and
    `shop_pane_emission`).
  - A window state builds as before, under `M_Window_pane_Face`.
  - Both names end `_Face`: Lux's power cut darkens them, and Level Factory's world-skin pass leaves them on their
    own UVs.
- **`core/kit.py`** honours a shop state on a facade window as it honours a window state: `_p<state>` in the
  module's name. Deli Counter's `themed_tscn.resolve_themed_stem` makes the same test against its own copy of the states,
  and learns the shop's when it authors one (the proposal's step 2).
- **It costs no light,** and one material where a shop front stands. Nothing stands one yet.
- **`tests/test_shop_panes.py`**: 14 checks, 13 pure and 1 in Blender. Run against 1.106.0 with the module alone added, the module's name and its build plan fail and the other eleven pass; without the module the file fails to import. Inside Blender 5.1.1 (the command in its docstring), beside `tests/test_window_panes.py`: 24 passed, the shop pane wearing `M_Shop_pane_Face` and the window pane still `M_Window_pane_Face`.
- **The suite:** `python -m pytest -q tests`: 4,627 passed, 456 skipped, 1 xfailed in 5 min 42 s, where 1.106.0 passed 4,614 and skipped 455: the new file's 13 pure checks, and its Blender check skipped outside Blender.
