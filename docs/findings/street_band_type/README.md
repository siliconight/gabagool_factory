# The street band's lettering (roadmap 223)

**Question.** Note 10 of the walk of 2026-10-09 was "need better looking
fonts on these signs", and the walker decided "use Blue Highway for the shop
signs". Zoo 1.90.0 did that for the name Zoo paints over a door. A business
that Level Factory deals a Pixelcoat sign pack shows that pack twice:
- on the street band Lot hangs across its frontage;
- on Zoo's door box, which wears the pack instead of painting a name.

What would it take to letter those in Blue Highway too?

**Answer: more than the font, because the band is also drawn 1.5x too
wide.** Measured 2026-10-10, nothing changed:
- **The pack is a 4:1 cabinet, sampled nearest.**
  `theme-signs` renders `(size // 4, size)`, 512 x 128 at its default.
  Read off a real pack, `sign_flappahs` in cold run 9217's
  `club_block_014.pixelcoat_build`: 512 x 128 albedo, emissive and
  roughness. Its `import_hints.interpolation` is `"nearest"`.
- **Lot hangs it on a 6:1 band.**
  `lot.py`: `SIGN_ASPECT = 6.0  # width : height, matching the pack`. The
  band is 72% of the facade, 2.4 to 9.0 m wide. So every band's art is
  stretched 1.5x across, and its letters are 1.5x too wide. The comment's
  "matching the pack" is false.
- **Lot honours the pack's sampling hint.** A `nearest` pack gets
  `texture_filter = 2`; anything else gets Godot's filtered default.
- **Zoo's door box does not.** `materials.make_emissive_textured_material`
  sets every sign pack's texture `Closest`. `skins.load_pack` does not even
  pass the hint through.
- **Pixelcoat letters in Pixel Operator.** `_render_ttf` thresholds every
  pixel to ink or none, and that is what keeps the packs byte-deterministic
  across FreeType builds.

**A smooth face stretched 1.5x reads worse than a pixel face stretched
1.5x.** So doing the font alone would make the band look worse.

## Groundwork, kept here (not yet in Pixelcoat)

- **`mint_smooth_type.py`:** Pixelcoat's own mint tool, a port of Zoo's.
  - It rasterises Blue Highway Condensed from Pixelcoat's vendored OTF
    (`assets/fonts/blue_highway/`) once, into a coverage table.
  - Measured: the table it mints is BYTE-IDENTICAL to Zoo's
    `smooth_faces/highway_cond.py` (162,355 bytes, PIL 12.3.0, FreeType
    2.14.3). So the band and the door would be one face at one em.
- **`smooth_type.py`:** the numpy composer, a port of Zoo's `coverage` and
  `fit_cap`. A line is composed at the master size and area-resampled, so
  the same bytes come out on every machine. A font drawn at build time would
  not give that.

## Shipped 2026-10-10, as proposed below, in four releases

- **Pixelcoat 0.62.0:** `core/smooth_type.py` and its minted table (this
  folder's groundwork); `theme-signs` at 1536 x 256, with packs asking for
  `linear` and mips; `paint_matte`.
- **Zoo 1.94.0:** `load_pack` returns `interpolation` and `art_aspect`; the
  sign material samples as the pack asks; `fit_uv` keeps the art's shape on
  the door box. The library's 95 door signs are 0.6 m tall and 3.33 to
  8.33:1, 4.67 at the median.
- **Lot 0.105.0:** the pack's manifest is copied beside its maps.
- **Level Factory 0.166.0:** the export pins a sign map's import from that
  manifest, `compress/mode=2` and mips for a smooth pack. A shipped
  package's sign maps were lossless with no mips.

Proof: cold run 9222, restaurant_row_001.

## What the change needed (proposed 2026-10-10, kept)

1. **Pixelcoat renders the business signs smooth, at the band's shape.**
   Blue Highway Condensed, Zoo's shop voice, at 6:1, at about Zoo's 240 px
   a metre: 1536 x 256 covers a 6.4 m band. It marks the packs `linear`.
   The 48 signs of `profiles/signs/delco_1997.json` are 42 panels, 5 neons
   and 1 price board.
2. **Lot keeps 6:1,** and its comment becomes true.
3. **Zoo's door box fits a pack's art without stretching it** (it is about
   4:1 by the door's width), and samples it as the pack asks.
   `load_pack` passes `interpolation` through.
4. **The proof needs a level with dealt businesses.** club_block_014 has
   none.

**Found alongside:** Pixelcoat's
`test_card_shop_surfaces::test_the_kinds_zoo_knows_are_the_kinds_zoo_knows`
fails today. Zoo 1.82.0 added `paint_matte` to `skins.KNOWN_KINDS`, and
Pixelcoat's `cli._ZOO_KINDS` never gained it. It is a one-word fix with the
next Pixelcoat release.
