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
## The census, 2026-10-13 (`literal_census.py`, `literal_census.out.txt`)

The walker: "go ahead with the census". `literal_census.py` lists every module-level numeric constant in
Deli Counter's 88 top-level modules -- 317 of them -- and flags one when its name or comment holds a body
word, or its value spells one of the contract's distinctive numbers: 127 flagged. The flags only pick what
to read. Each flagged constant's full comment was read, and each sorted by what its own words say.

**Routed: Deli Counter 0.216.0 (9fef728d).** Eleven were a body's size spelt beside its rule, and each now
reads the contract at the value it was, exact in a float:
- `enterability.MIN_PASS_WIDTH` and `stairwell._AGENT_PASS_WIDTH`, two body radii;
- `enterability.STAND_HEIGHT`, the body's height;
- `sightlines.EYE` and `SIGHT_BLOCK_H`, the body's eye;
- `guards.MAX_STEP_UP`;
- `combat_audit.WIDE_DOOR`, four radii, "two agents";
- `vault_room.DOOR_WIDTH` and `lights._AISLE_MIN_FALLBACK`, the door minimum;
- `vault_room.APPROACH`, with `layout_lint.DOOR_APPROACH_M` through one `door_approach()`;
- `level_design._CLUSTER_GAP`'s upper end, two bake radii;
- `ladder_geom.HOLE_ALONG`: standoff, body radius and a margin now named.

`combat_audit`'s private copy of the opening defaults is gone. Two of its values were stale (a door at
1.2, a vault at 1.4), and it reads `Opening.resolved()` now. Its audit of the library and the presets is
byte-identical before and after. All 152 manifests moved only by `built_utc`, the preset digest is
unchanged, and the suite passed 1,493.

**Read, and not routed**, each for a reason its own comment gives:

- **They disagree with the contract**, so routing them would change behaviour. That is the walker's call,
  not a mechanical one.
  - `enterability.MIN_PASS_HEIGHT` 1.1 ("can't even crouch through") against `crouch_height_m` 1.2.
  - Three "too narrow" thresholds below the contract's 1.25 door:
    - `enterability.CLEAN_WIDTH` 0.9 ("doc's minimum doorway", `docs/scale_guidelines.md`);
    - `tactical.MIN_OPENING_WIDTH` 0.8;
    - the capsule's 0.7, routed above.
  - Two door approaches: `circulation.DOOR_CLEARANCE` 0.6 ("clear approach depth on each side") against
    `layout_lint.DOOR_APPROACH_M` 1.0.
  - `stair_pitch.MAX_WALKABLE_PITCH_DEG` 40, beside `floor_max_angle` 45 and the bake's 55, the slope
    tension CLAUDE.md names.
- **Body-sized, with a margin nobody derived.** Routing the body part would leave the margin as the real
  decision:
  - `stairwell.LATERAL_ENVELOPE` 0.5 ("capsule + push/network margin");
  - `level_design._STAFF_MARKER_IN` 0.8 ("a body's radius and a little");
  - `roofs.LANDING_HALF_M` 1.5 (the hatch's half and "a stride", 0.85);
  - `level_design._STAFF_MIN_DEPTH` 1.85 ("a body plus a door leaf");
  - `guards.STEP_RISE_WARN` 0.4;
  - `enterability.VAULT_SILL_MAX` 1.2 (a vault-up reach the contract does not carry);
  - "waist high" twice: `combat_audit.COVER_MIN_H` and `level_design._COVER_MIN_Z`, both 0.6.
- **Measured, not derived.** `stairwell.RAIL_OPEN_MIN` 1.4: the narrowest rail opening the bake connected,
  measured at nine values. A change to the bake needs it re-measured, which its comment says.
- **A comment that does not reproduce its number.** `level_design._CUSTOMER_LANE` 2.0 says "`_SEAT` plus
  two radii", and `_SEAT` is 0.5 deep: 0.5 + 0.7 is 1.2, and with the bake's radii 1.3. The number and
  its stated rule disagree.
- **Other contracts and specs.** The ladder's climb contract (`ladder_geom.CLIMB_STANDOFF`,
  `docs/LADDER_CLIMB_CONTRACT.md`) and its spec section 8.3 (`ladder.LOWER_CLEAR_W`/`_D`,
  `HATCH_CLEAR_RADIUS`, `circulation.LADDER_*`). The stair reservation's own geometry:
  - `stairwell.SIDE_MARGIN` 0.4;
  - `WALKOFF_CLEAR` 0.8, whose note says it is NOT the same quantity as the hole's 0.8;
  - `_SOLID_BAND` 0.45;
  - `EXIT_STEP_OFF` 0.8.

  Two classifiers of library volumes: `vault_room.VAULT_MIN_HEIGHT` 2.0 and `level_design._HUNG_MIN` 1.8.
- **Not body-sized.** The rest: lamp and sign offsets, counts, art and tolerance numbers, and the one-shot
  migrations' constants.

Outside this census: Level Factory's `docs/extracted/combat.md` still lists `combat_audit.KIND_DEFAULT_W`,
removed in 0.216.0.
