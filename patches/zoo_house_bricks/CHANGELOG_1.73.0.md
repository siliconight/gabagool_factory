## [1.73.0] - a house's own brick

The walker's South Philly photograph: "every house a different brick:
brown, red, orange". A theme holds one grammar per kind, so Pixelcoat
(>= 0.57.0) paints the brown and the orange as kinds of their own,
`brick_brown` and `brick_orange`. Deli Counter (>= 0.183.0) builds two of
its rowhome Empties in them.

- **`skins.KNOWN_KINDS` lists both.** `dna.resolve_module_plan` keeps a
  slot's material only when it is listed. A kind missing from the tuple
  builds in the genome's default and says nothing, which is how
  `carpet_club` once came out concrete.
- **`materials.ROUGHNESS` gives both a brick's 0.90.** `test_kind_vocabulary`
  holds the two tables to the same keys.
- **A wall in a house brick carries it in its name** (`_mbrick_brown`,
  `_mbrick_orange`). Two houses of one wall size in different bricks are
  different modules.
