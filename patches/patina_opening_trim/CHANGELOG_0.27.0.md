## [0.27.0] - an Empty's openings: stone lintels and sills

### Added
- **`framing.opening_trim_orders`**: for every opening on a facade slot
  (`glazing: "facade"`), orders for Zoo (>= 1.71.0) to build.
  - `lintel` over every window and door, at the opening's head on the wall
    face.
  - `window_sill` under every window, at its sill on the wall face. A door
    has none; its threshold is the sidewalk's.

  The walker's South Philly photograph (the factory root's
  `docs/reference/EMPTIES_COMPS.md`, "Window comps"): "white stone lintels
  and sills over and under every window".

### Changed
- **`--dressing` with a slots.json orders them beside the window fixtures.**
  The facade slot is the opt-in, so no flag.
- **`openings.EXEMPT` names `lintel` and `window_sill`.** They sit on a sealed
  opening's own head and sill, inside its keep-out margin, for the same
  reason the window fixtures are exempt. `test_openings.py`'s pin moves to
  the five names.
