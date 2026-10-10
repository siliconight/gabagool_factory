## [0.62.0] - a business's sign in Blue Highway, smooth, at its band's shape

**Roadmap 223,** note 10 of the walk of 2026-10-09 generalised. The walker
decided "use Blue Highway for the shop signs", and Zoo 1.90.0 set the name it
paints over a door in Blue Highway Condensed. The pack Level Factory deals a
business still lettered its street band in Pixel Operator, and the band was
drawn wrong besides (`docs/findings/street_band_type/` at the factory root):
- **A 4:1 cabinet on a 6:1 band.** `theme-signs` drew `(size // 4, size)`,
  512 x 128, and Lot hangs it on `SIGN_ASPECT = 6.0  # width : height,
  matching the pack`. Every band's letters stood 1.5x too wide.
- **Thresholded and sampled nearest.** `_render_ttf` keeps a pixel as ink or
  nothing, which keeps a pack byte-deterministic, and every pack asked for
  `interpolation: nearest`.

A smooth face stretched 1.5x reads worse than a pixel one, so the font alone
was not the change.

### Added
- **`core/smooth_type.py` and `core/smooth_faces/highway_cond.py`.**
  - `tools/mint_smooth_type.py` rasterises Blue Highway Condensed, which
    Pixelcoat already vendors (`assets/fonts/blue_highway/`, CC0), ONCE, at
    64 px to the em, into a committed coverage table. `--check` says
    whether the table is still what the font gives.
  - The composer sets a line from those masters and area-resamples it to
    the cap height a sign asks for, in numpy: exact anti-aliasing, and the
    same bytes on every machine. A font drawn by the host's FreeType at
    build time would not give that.
  - **Measured:** the table is byte-identical to Zoo's
    `smooth_faces/highway_cond.py`, 162,355 bytes. So the band and the door
    are one face at one em.
- **`neon_sign` and `panel_sign` take `face`.** With one, the name is set
  smooth, as large as it fits inside `SMOOTH_MARGIN_W` (0.86) and
  `SMOOTH_MARGIN_H` (0.56). A name that does not set at a 4 px cap raises
  rather than crop.
- **`build_sign_pack` takes `interpolation` and `mipmaps`.** A smooth pack
  asks to be sampled `linear`, with a mip chain, since a filtered sign seen
  across a street is minified several times and shimmers without one.

### Changed
- **`theme-signs` draws a business's sign at the band's shape and smooth.**
  - The size is 1536 x 256, 6:1, about Zoo's 240 px a metre on a 6.4 m band.
  - Every panel and neon is set in the shop's face, `smooth_type.SHOP_FACE`,
    and asks for `linear` and mipmaps.
  - A fuel price board keeps its pixel figures, its `nearest` and its old
    512 width (`PRICE_WIDTH`): a board is not a band.
- **Measured on the delco profile's 47 businesses:** every name sets. The
  cap heights run from 112 px (DOWN THE SHORE BREWING) to 137 (the height's
  limit, 0.56 of 256), with a median of 137.

### The price
Texture memory, by arithmetic and not measured in a running level. A sign
is three maps, albedo, emissive and roughness, at 4 bytes a pixel lossless
or about 1 compressed:

| | lossless | VRAM-compressed |
|---|---|---|
| 0.61.0, 512 x 128, no mips | 0.79 MB | 0.20 MB |
| 0.62.0, 1536 x 256, with mips | 6.3 MB | 1.6 MB |

- **What lands in memory is the import's choice.** A package imported sign
  maps lossless and without mips (`LF_gas_block_001`'s, read 2026-10-10).
  A filtered sign wants them compressed with mips, as Level Factory already
  pins Zoo's filtered textures (`FILTERED_TEX_PINS`). Until it does the same
  for signs, a smooth sign costs the left column, and shimmers.
- **What it buys:** a name that reads across the street, and one face from
  the band to the door.
- A level deals a few businesses, so it carries a few of these.

### Fixed
- **`cli._ZOO_KINDS` gains `paint_matte`** (Zoo 1.82.0, the crew's van).
  `test_card_shop_surfaces::test_the_kinds_zoo_knows_are_the_kinds_zoo_knows`
  had failed on it since then.

### Tests
- **`tests/test_smooth_signs.py`:**
  - the shop face is what the font gives, and byte for byte Zoo's;
  - every business name sets at least 100 px tall on its band;
  - smooth lettering is anti-aliased, and the same every time;
  - the pixel path is unchanged;
  - a name that does not set raises;
  - a pack asks for one of two samplings;
  - `theme-signs` draws 6:1, linear, with mips, and the price board as it
    was. That last one fails on 0.61.0.

Suite: 675 passed, 0 failed: 0.61.0's 667, and the 8 new tests here. One of the
667 had turned red since, when Zoo 1.82.0 added `paint_matte`; it passes again.
