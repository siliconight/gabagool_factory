## [0.26.0] - an Empty's windows: bars and air conditioners

### Added
- **`framing.window_fixture_orders`**: what Deli Counter (>= 0.181.0) hangs
  in a sealed window, as orders for Zoo (>= 1.69.0) to build.
  - `window_bars`: one per barred opening, at its centre on the wall face,
    sized to it (`size2`).
  - `ac_unit`: one per opening with an air conditioner, at its SILL on the
    wall face, where Zoo stands the unit and reaches it back to the pane.

  Only on a facade window (`glazing: "facade"`). A real window is a firing
  line, and bars a bullet passes through would lie about it.
- **The slot model reads `glazing`, `pane`, `ac` and `bars`.** It had
  dropped them.

### Changed
- **The slot is the opt-in, so there is no flag.** Deli Counter chose these
  per window, beside the pane, and only on an Empty. `--dressing` with a
  slots.json orders them wherever a slot asks.
- **`openings.EXEMPT` names them beside `frame`.** They stand IN the opening,
  so its keep-out box holds them. The opening is sealed: an Empty records no
  gameplay openings, so no body or shot uses that hole. Listed, not
  inferred, as the rule asks.

The walker's window photographs, in the factory root's
`docs/reference/EMPTIES_COMPS.md` ("Window comps"):
- "window air conditioners in nearly every photograph";
- bars proud of the frame on bolted straps.
