## [0.75.0] - a home's dome lights its room

**Roadmap 229's species step, beside Zoo 1.98.0 and Deli Counter 0.208.0.**
A home's room was laid by its own rule, a fixture a 7 m bay, and lit as an
office: a 2 x 4 troffer and its cool row. Deli Counter writes it as `dome`
anchors now, and Zoo hangs a flush-mount dome on each.

- **The `dome` rig:** the pendant's machinery and its warm incandescent
  colour, at `DOME_ENERGY` (1.6: the bare bulb's 1.3 and a second bulb, less
  what frosted glass keeps). Its lamp hangs `DOME_LAMP_DROP_M` (0.17 m) under
  the anchor, below the deepest bowl Zoo builds, for the pendant's reason --
  a lamp inside a closed shell bakes to nothing. Its range is derived, not
  chosen: the pool reaches its bay's corner, sqrt(drop^2 + (HOME_BAY_M /
  sqrt 2)^2), with `HOME_BAY_M` Deli Counter's 7 m home spacing, so two
  neighbours' pools meet. Steady, so it bakes, and never chosen to fail.
- A dome ranks with the bulbs for a shadow map (`LuxLighting`), and the leak
  meter names its class.

**Self-test:** `tools/dome_lamp_selftest.gd` -- RESULT_SELFTEST.
