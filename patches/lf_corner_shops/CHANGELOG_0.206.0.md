## [0.206.0] - Corner shops: an urban wall's runs open and close on a corner block

**Factory roadmap 241.** The comps (the factory root's `docs/reference/URBAN_MIDRISE_COMPS.md`): "Corners carry the
life. The corner building has the shop at grade (lit, awning), homes above. The middle of the block is
residential." Deli Counter 0.218.0 builds four corner blocks, `gs_cornershop_a` to `_d`: mid-rises whose
ground-floor front is a shop, which Zoo 1.107.0 paints from its shop atlas. This stands them where a block face
ends. Step 3 of the factory root's `docs/proposals/CORNER_SHOP.md`.

- **`building_library.CORNER_PREFIX`** is `gs_cornershop_`. Not `gs_corner_`: that is `gs_corner_station`'s, an
  enterable gas station.
- **An urban brief's Empties** are the mid-rises and the corner blocks, the corners as their own family
  (`empty_rows(..., family="corner")`). The planner themes each, as every Empty.
- **`empties.terrace` never deals a corner block along the wall.** On a continuous wall with one, `_cornered` takes
  each run of the wall -- between two roads crossing the far side, or a road and the plate's end, one block face:
  - It OPENS on the next corner block dealt that fits.
  - It CLOSES on the widest corner block left on the corner bag that fits, not the one it opened on while another
    fits.
  - Between them it is dealt as before, heights by cause where given. Before the run's end it keeps the narrowest
    closing block's width clear, so the run can close.
  - The wall's remainder stays where it always stood, at the run's end. A run no corner block fits is dealt
    plainly.
- **Without a corner row, every wall is 0.205.0's:** 320 walls read before this was written and after
  (`test_without_a_corner_row_every_wall_is_0_205_0_s`).
- **`empties.infill` stands no corner block.** The near side's corners are the mission's own buildings.
- **The compose stage says which shop opens and closes each run.** Where the lot library holds no corner block,
  it says `URBAN_WITHOUT_CORNERS` and the wall's runs open and close on mid-rises.
- **On urban_row_001** no road crosses the far side (`_blocked` reads none on cold run 9294's three candidates:
  both side streets leave the through road northward), so the wall is one run and its corners stand at the
  plate's ends.
- **`tests/unit/test_urban_corner_shops.py`:** 9 checks, pure. Against 0.205.0 six fail: a corner row is dealt along the wall like any other, through a crossing's two runs, on the strip and on the near side, and the library hands an urban brief no corner family. Three pass on both: the wall is continuous, its first and last blocks differ, and the control digest is 0.205.0's own.
- **The suite:** `python -m pytest -q`: exit 0, 2,399 passed (0.205.0's 2,389, the new file's 9, and `test_sibling_locator`'s guard over the new file), 14 skipped (the real-tool smoke), 1 xfail, counted off the progress marks, in 6 min 48 s.
