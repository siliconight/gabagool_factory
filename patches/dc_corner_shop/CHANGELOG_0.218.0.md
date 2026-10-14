## [0.218.0] - the corner blocks: a mid-rise Empty whose ground-floor front is a shop

**Factory roadmap 241.** The urban comps (the factory root's `docs/reference/URBAN_MIDRISE_COMPS.md`): "Corners
carry the life. The corner building has the shop at grade (lit, awning), homes above. The middle of the block is
residential." The mid-rise Empties are homes from the pavement up. Zoo 1.107.0 paints a shop's window from its own
atlas (`zoo_keeper.core.shop_panes`); this authors which windows show a shop, and which shop. Step 2 of the factory
root's `docs/proposals/CORNER_SHOP.md`.

- **`presets.empty_midrise(..., security_door=False, shop=None)`.** With `shop`, every front bay at grade but the
  door's is a `SHOP_WINDOW`, authored in the shop's state. That is 2.4 m of glass from a 0.3 m bulkhead to the
  front door's 2.4 m head.
  - The front door is the shop's, in the bay nearest `lobby`; the homes above keep the service door behind.
  - `security_door` hangs the rowhome Empty's iron door on the front.
- **`EMPTY_CORNERS`**, four blocks under their own prefix, `gs_cornershop_`, so the urban street's deal
  (`gs_midrise_`) never draws one mid-block. Not `gs_corner_`: that is `gs_corner_station`'s, an enterable
  gas station Level Factory's clusters name as a corner store.

      gs_cornershop_a   15.0 m, 6 storeys, brick          a deli, black door, iron
      gs_cornershop_b   18.0 m, 8 storeys, brick_orange   a bar, oxblood door
      gs_cornershop_c   12.0 m, 5 storeys, brick_brown    a laundromat, white door
      gs_cornershop_d   16.5 m, 7 storeys, stone_ext      a grocery, green door, iron

- **An opening carries an authored state,** `Opening.pane`.
  - `_opening_to_hole` carries it, and a facade window's slot takes it before `empty_panes.choose` draws one.
  - `empty_panes.SHOP_STATES` is Zoo's shop atlas in its order. `empty_panes.authored` refuses a state outside
    both sets rather than dropping it.
  - A shop window hangs nothing: no bars and no air conditioner (`fixtures`).
- **`themed_tscn.resolve_themed_stem`** names a shop window as Zoo's `plan_kit` does, `_p<state>`.
- **`schema/level.schema.json`'s opening may carry `pane`,** a string or null. The value is checked by
  `empty_panes.authored` at build, so the schema keeps no third copy of the states.
- **Nothing stands one yet.** Level Factory deals them where a wall closes at a corner (the proposal's step 3).
- `navgate_baseline.json` has four UNJUDGED entries, as every Empty does. `specs/gs_cornershop_*.json` are written
  from the presets, and `specs/CATALOG.md` is regenerated.
- **Built:** `build.py --all`, 6 min 53 s, 159 shells. The four corner blocks are new, each validating clean with `facade` true (glb sha256_16: gs_cornershop_a 27217982b626dd13, _b 6478958475edf9b5, _c beaeac67c42d7f16, _d c1c1c084bad2cc04). Every other shell's outputs are byte-identical to 0.217.0's by its manifest's `outputs_sha256_16`, 155 of 155; `fuel_stop_heist2` and `_3`, June builds with no spec of their own, are not rebuilt and their manifests are unchanged. Read off `build/gs_cornershop_*.slots.json`: at grade 3 to 5 shop windows in the block's shop, with no bars and no air conditioner; the shop's door between them in its finish, an iron door on _a and _d; the service door behind; every upper window drawn as before. The first build of this change failed the four specs' own schema gate ("'pane' was unexpected"), read off their validation manifests: the schema now carries `pane`, and the shells rebuilt to the same bytes.
- **`test_empty_corner.py` and the suite:** 1,508 passed, 2 skipped, exit 0: 0.217.0's 1,497 and `test_empty_corner.py`'s 11. On 0.217.0 the file fails to import (no `EMPTY_CORNERS`). With every edit but the builder's, `test_a_shop_window_s_slot_carries_its_shop_and_nothing_hangs_in_it` alone fails; with every edit but the schema's, `test_every_corner_spec_passes_the_schema` alone fails. That check was added after the build found what the suite had not.
