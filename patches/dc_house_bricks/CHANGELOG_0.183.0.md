## [0.183.0] - A house's own brick

The walker's South Philly photograph (the factory root's
`docs/reference/EMPTIES_COMPS.md`, "Window comps"): "every house a different
brick: brown, red, orange". The family's three brick rowhomes all wore the
one red. Pixelcoat 0.57.0 paints a brown and an orange as kinds of their
own, and Zoo 1.73.0 knows them.

- **`material_kind`**: `brick_brown` and `brick_orange` are skin kinds, and
  each material id maps to itself.
- **`OUTSIDE_ONLY`** holds them beside `brick`, so an exterior wall in one
  carries its building's interior finish on its room face (0.166.0).
- **The family:**
  - `gs_empty_rowhome_a` (placed x2) is orange;
  - `gs_empty_rowhome_c` (x5) is brown;
  - `gs_empty_rowhome_f` (x7) keeps the red.

  The six rowhome specs are rewritten from the preset.
