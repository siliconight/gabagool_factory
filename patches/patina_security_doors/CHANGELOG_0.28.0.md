## [0.28.0] - an Empty's iron security door

### Added
- **`framing.door_fixture_orders`**: one `security_door` per opening of a
  facade doorway whose slot carries `security_door`, at the opening's centre
  on the wall face, sized to it.
  - Deli Counter (>= 0.182.0) writes it on the front door of a house that
    has one.
  - Zoo (>= 1.72.0) hangs it in the reveal, in front of the leaf.

  The walker's South Philly photograph: "a black iron security door with a
  grille".
- **The slot model reads `security_door`.**

### Changed
- **`--dressing` with a slots.json orders it** beside the window fixtures
  and the stone trim. Only on a facade doorway: a real door is a way in.
- **`openings.EXEMPT` names `security_door`.** `test_openings.py`'s pin
  moves to the six names.
