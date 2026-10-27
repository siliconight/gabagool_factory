## [0.63.0] - a store's vinyl tile is one pale colour, polished

On 2026-10-26 the walker was shown seed 9205's supermarket under Deli Counter 0.274.0's lamps, with its floor
polished in a copy. They said: "better, it wouldn't be this tile pattern though...", and then "but the
finish/shine looks right".

The comps are filed as the factory's docs/reference/GROCERY_STORE_COMPS.md: pale VCT, polished until it mirrors the
fluorescent runs, one colour with faint joints. `vct_floor_beige` drew 25 cm tiles in a strong four-shade checker:
- per-tile tone variation 0.14;
- 2 % grout;
- roughness 0.35.

In the game that read as a dark tan checkerboard (the factory's docs/findings/shiny_floor/).

### Changed
- **`profiles/materials/vct_floor_beige.json`**, the `tile` of card_shop, delco_1997, industrial_flats and
  rockay_retail:
  - 12-inch tiles: `meters_per_tile` 1.22 over 4 x 4.
  - Off-white colours, `#dedad1` / `#e0dcd4` / `#dbd7ce`.
  - Per-tile tone variation 0.025, and a 0.8 % joint in `#c6c2b9`.
  - Quieter bands: 0.08 / 0.05 / 0.06, detail 0.03.
  - **Roughness 0.12 (variation 0.04)**: the finish the walker approved.
  - Rendered at 256 px: mean 204.7 -> 216.0, spread 14.1 -> 5.8.
- **`tools/art_standard_baseline.json`: `vct_floor_beige`'s row only, a deliberate regression in one metric.**
  - The finish is glossier, `rough_mean` 0.350 -> 0.120, because the walker asked for the shine.
  - Every other metric fell:
    - blown 5.2 % -> 0.16 %;
    - value range 0.192 -> 0.038;
    - chroma 0.023 -> 0.016;
    - edge energy 0.048 -> 0.019.
  - The full re-snapshot the test file describes would also have added three grammars the baseline has never
    covered (`brick_brown_delco`, `brick_orange_delco`, `chain_link_galvanized`). That is coverage, and not this
    change's to add.
  - A first, whiter cut (`#e9e6de`) blew 54 % of its pixels against the standard's L 0.94 line, and was pulled
    down.

### Tests
- `tests/test_plain_vct.py` (all 3 fail on 0.62.0):
  - the tile is pale and one colour;
  - its tiles are 12 inches and differ by under 8 levels;
  - its roughness is at most 0.15.
