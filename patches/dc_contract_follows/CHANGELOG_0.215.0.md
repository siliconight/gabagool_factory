## [0.215.0] - the stair landing and the vault's opening follow the agent contract

**For "singular changes".** The walker, 2026-10-13: "continue to update the agent contract file so we can
make singular changes when we know the size of characters in the game". 0.214.0's
`clearances.re_derive_when` named the two body-sized numbers that did not follow the contract yet. Both
follow now, each as one function in `agent_contract.py`, read where it used to be spelt. The contract
writes down each rule. Today's numbers are the ones that were spelt, so nothing built moves.

- **`agent_contract.stair_flight_width()`** is `min_corridor_width_m` plus one `nav_bake.cell_size_m`:
  1.2 m.
  - `presets.STAIR_FLIGHT_WIDTH` read that formula inline. It now calls this function, so the formula is
    spelt once.
  - `stairwell.LANDING_DEPTH` was a literal 1.2, "a game-readability default". It now reads the same
    function.
  - The rule, in the contract's new `stair_landing_derivation`: a landing as deep as the flight is wide.
    That is IBC 2018 section 1011.6, which sets a landing's depth in the direction of travel at the
    stairway's width or 48 in, whichever is less. The 48 in cap is left out because it assumes a human
    body, and the contract sets the body.
- **`agent_contract.vault_aperture()`** is `min_door_width_m` rounded up to the next 0.1 m, by
  `min_headroom_m` plus 0.1, on the floor: 1.3 x 2.1 m, sill 0.
  - `vault_room.APERTURE` and `spec_types`' vault default were literals beside a comment giving this
    rule. Both read the function now.
  - The rounding guards the float that would round a door already on the 0.1 grid past it.
  - Deli Counter writes the opening into the vault door's slot (`fit.openings`), and Zoo builds the round
    door to it (`dna` passes the module's first opening to the recipe). Zoo's own default serves only a
    standalone build. The rule is in the contract's new `vault_aperture_derivation`.
- **`re_derive_when`** no longer lists a NOT YET FOLLOWING. It names what is WRITTEN and does not follow:
  the library's three vault rooms carry their 1.3 x 2.1 opening as written numbers, and no migration
  rewrites them yet.
- **`test_body_follows_contract.py`** checks:
  - the functions against stand-in contracts (a wider corridor, a finer cell, doors on and off the 0.1
    grid, more headroom);
  - the module-level copies against the contract in force, and the vault default as resolved;
  - every built vault slot's opening;
  - the contract's two derivations.

  It fails to import on 0.214.0.

**Built:** `build.py --all` under Blender 5.1.1, 152 shells in 385 s, exit 0, no error in the log. Every manifest moves by `built_utc` alone, and each carries `outputs_sha256_16`, so every shell is byte-identical to 0.214.0's. The presets as Level Factory makes them -- all 228 combinations of preset, mode and one to four floors on seed 9104 -- digest the same on 0.214.0 and 0.215.0 (sha256 d53248c1...). The control is 0.213.0, before the doors, which digests eae19d7f...

**Suite:** 1,489 passed, 2 skipped (the bpy round-trip fixtures, run in their own process), exit 0: 0.214.0's 1,480 and `test_body_follows_contract.py`'s 9, which fail to import on 0.214.0. `stair_regression.py --quick`: every variant clean
