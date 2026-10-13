# Body-sized numbers follow the agent contract

The walker, 2026-10-13: "remember to continue to update the agent contract file so we can make singular
changes when we know the size of characters in the game". So a number that depends on the size of a body
is read from `deli_counter/agent_contract.json`, through `agent_contract.py`, and never spelt beside a
comment naming the contract. The contract writes down each rule. `clearances.re_derive_when` says:
- what one change to a body starts;
- what follows on its own;
- what is written into the library and needs re-running.

## Routed so far

- **Deli Counter 0.214.0** (`docs/findings/door_widths/`). Every walkable door its code writes reads
  `min_door_width_m`: the presets, a width-less door's default, and the staff door (a literal 1.25 until
  then). The stairs-first landing door reads `min_corridor_width_m` (a literal 1.1).
  `migrate_door_width.py` re-widens the library's written doors to whatever the contract says.
- **Deli Counter 0.215.0** (ebdb3cf4). The two literals 0.214.0 named as not following:
  - **The stair landing.** `stairwell.LANDING_DEPTH` (1.2) and `presets.STAIR_FLIGHT_WIDTH` read
    `agent_contract.stair_flight_width()`, the corridor plus one bake cell. A landing as deep as the flight
    is wide is IBC 2018 section 1011.6's rule. Its 48 in cap is left out because the cap assumes a human
    body.
  - **The vault's opening.** `vault_room.APERTURE` and `spec_types`' vault default (1.3 x 2.1) read
    `agent_contract.vault_aperture()`: the door minimum rounded up to the next 0.1 m, by the headroom plus
    0.1, sill 0. Deli Counter writes it into the vault door's slot (`fit.openings`), and Zoo's `dna`
    hands that to the vault recipe. Zoo's `vault_forms.DEFAULT_OPENING` serves only a standalone build.

  Same numbers, so nothing built moved:
  - all 152 manifests move by `built_utc` alone, and each carries its outputs' sha256;
  - `preset_digest.py` over the presets as Level Factory makes them (228 specs) gives d53248c1... on
    0.214.0 and 0.215.0. The control, 0.213.0 before the doors, gives eae19d7f....

## Not following yet

- **Written into the library.** The three vault rooms' openings (1.3 x 2.1, written by `vault_room`), with
  no migration to rewrite them. The library's door widths are written too, but `migrate_door_width.py`
  rewrites those.
- **Outside Deli Counter's code.**
  - Lot keeps a fallback copy of the contract, which `lot/tests/test_cover_fallback.py` holds equal to the
    live file since Lot 0.120.2. A changed NUMBER turns Lot's suite red until Lot follows.
  - `meshlib_kit.DOOR_W` (1.2) is the optional GridMap kit's doorway; nothing imports it.
- **Not censused.** Body-sized numbers nobody has named yet. These were seen while reading, not
  measured: `stairwell._SOLID_BAND` (0.45), `level_design._STAFF_MIN_DEPTH` ("a body plus a door leaf",
  1.85), `layout_lint`'s "a body needs 1 m of floor in front of a door". Each needs reading before it is
  called body-derived.
