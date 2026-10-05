## [0.57.0] - a house's own brick

The walker's South Philly photograph (the factory root's
`docs/reference/EMPTIES_COMPS.md`, "Window comps"): "every house a different
brick: brown, red, orange". Every brick house in a level wore `brick_delco`:
a theme holds one grammar per kind, so a second brick needs a kind of its
own. `test_theme_profiles.py` says the same of `carpet_tournament`.

- **`brick_brown_delco` and `brick_orange_delco`**: `brick_delco`'s grammar
  with their own palette and mortar.
  - The brown is darker.
  - The orange is yellower, with a paler mortar.
  - Each is of its own kind, as a theme slot's grammar must be. Neither
    carries a wet variant, so no material response is read for them.
- **Both level themes map them.** `delco` and `delco_1997` map the new kinds
  `brick_brown` and `brick_orange`, as every level theme must map what any
  theme maps.
- **`cli._ZOO_KINDS` lists them.** Zoo 1.73.0 knows them.
- **Deli Counter 0.183.0** builds two of its rowhome Empties in them.

**Cost:** two more packs in every delco and delco_1997 library. The rowhomes
ask for both.
