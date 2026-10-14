## [1.112.0] - a door under its building's band says the trade

**The walker's walk of cold runs 9305-9307, 2026-10-14, finding 4** (the factory's `docs/findings/walk_2026-10-14/`).
At urban_row_001's pharmacy: "double sign here looks...redundant". Its street band and the box over its door both
read DOC'S DISCOUNT DRUGS, which was 1.79.0's doing and the walker's own option A of 2026-10-06 ("one name on both
signs"). Level Factory deals each banded shell its business and passes the band's pack to the shell's fixtures, and
`sign_box` dressed the door in it. On a one-storey front the two stack, one over the other. Asked, the walker chose
the trade for the door.

### Changed
- **`storefront_names.TRADE` and `trade_for(business)`:** what the shop is, in plain words, in the colours
  `sign_for` gives its name.
  - PHARMACY, DELI, PIZZA, PAWN, BANK, CLINIC, GROCERY, CARDS, VIDEO, BREWERY, CASINO, FUNERAL HOME, CLUBHOUSE; a
    gas station's door OPEN 24 HOURS.
  - A civic building's words are its trade already, and a building of no kind says OPEN.
  - `all_strings` carries them, so `test_every_name_sets_on_every_sign_the_library_derives` sets each on every
    door the library derives.
- **`sign_box`:** a pack handed in is the sign that a band names the shop.
  - The door no longer wears it: it paints its trade, smooth, in the shop's voice, as a door of no band paints its
    name.
  - A door with no band is unchanged: a theme's sign pack where one ships, else its name.
- **Tests:**
  - `test_door_wears_the_band.py`'s third check now reads the trade's path. Its 1.79.0 form asserted the pack was
    worn.
  - `test_storefront_names.py` gains `test_a_door_under_a_band_says_its_trade`.
  - On 1.111.0 both fail.

**Suite:** `python -m pytest -q tests`: 5,355 passed, 462 skipped, 1 xfailed in 7 min 03 s, exit 0 -- 1.111.0's 5,354, the new trade test, and the rewritten band test in the old one's place. Both fail on an archive of 1.111.0 with the new test files in it and pass on 1.112.0 (the factory's `patches/zoo_door_trade/prove_tests_1111.out.txt`)

**Blender:** inside Blender 5.1.1, `test_door_box_fits_its_art.py`, `test_storefront_names.py` and `test_door_wears_the_band.py`: 60 passed -- among them the door box built with a band's pack, now painting its trade, its face still a filtered texture
