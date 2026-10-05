## [0.184.0] - Twelve rowhome Empties

Cold run 9159's terrace placed 26 Empties from six variants, one of them
seven times. Level Factory's `empties.terrace` picks a variant per house at
random, never the same as its neighbour, so the repeats fall with every
house the family adds. The comp's rule: a terrace reads as houses because
each one differs.

- **Six more rowhomes, `gs_empty_rowhome_g` to `_l`**, authored like the
  first six. Each a different width (5.6-6.4 m), with 2 or 3 storeys, door
  side, cornice height, wall and front door.
  - Across the twelve, every wall kind (red, brown and orange brick,
    siding, Formstone, painted block) and every door finish appears exactly
    twice, and no two houses wear the same wall and door.
  - Four have iron security doors. One is vacant, as before.
- **The six new shells join `navgate_baseline.json`'s unjudged list** with
  the first six's reason: an Empty is sealed, with no interior for a spawn
  marker, so zero markers checked is correct. `unjudged` goes 15 -> 21 and
  `navigable_null` 14 -> 20.
- **The tests that counted six now read the family:**
  - `test_empties.VARIANTS` lists the twelve;
  - the doors test holds every finish to two and the iron doors to two to
    four;
  - the bricks test holds the three bricks, each worn.

The twelve rowhome specs are rewritten from the preset.

**Cost:** six more Empties' art jobs in a run that places them, and their
modules in memory. No draw a house is added: each placement draws its own
modules either way.
