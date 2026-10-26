# Which library families a brief can anchor (roadmap 309)

Cold run 9394's `funeral_row_001` brief was refused at the shell leg: a brief's anchor is generated from a Deli Counter
preset (Level Factory's `adapters/deli_counter._preset_for`), and the funeral homes exist only as authored specs.
Before choosing a cure, the item asked how far the gap reaches.

## Measured (2026-10-26, Deli Counter 0.270.0, Level Factory 0.242.0)

`families_without_preset.py` takes each built shell (`deli_counter/build/*.manifest.json`, lf_ specs excepted), strips
its `_aNN` suffix to a family, and asks `_preset_for` for it (`families_without_preset.out.txt`):

- **97 families, 161 shells; 37 anchorable (55 shells), 60 not (106 shells).**
- The 60 split into two groups:
  - **Real building types with no generator.** airport_terminal, apartment_walkup, arena, brewery, casino, clinic,
    construction_site, country_club, courthouse, credit_union, depot, freight_terminal, funeral_home,
    landmark_hall, mansion, marina, market_hall, museum, pharmacy, rail_station, self_storage, stadium,
    strip_retail, supermarket, train_yard: 25 families, 3 shells each, give or take one.
  - **Fixtures and one-offs.** `cr_*`, `gs_*`, `*_demo`, the heists, `final_stand`, `pvp_station_ref`.
- Some of the second group are name misses, not real gaps. `gs_midrise_*` is presumably an `empty_midrise` and
  `gs_cornershop_*` a corner deli, but `_preset_for` matches by name and neither contains a preset's.

## What it means for the two cures in the roadmap item

- **Presets** (Deli Counter generates the building): the general cure, and the only one that makes a funeral home
  procedurally. It is about 25 generators, each with its own layout grammar.
- **Anchoring an authored family** (Level Factory draws a library shell as the anchor without generating one):
  cheaper, reaches all 60 at once, and is limited to the three or so variants each family was authored with.
  `building_library.anchor_families` already matches a themed lot's anchor by family name.

Neither is built. The measurement is the item's first step, and the choice is still open.
