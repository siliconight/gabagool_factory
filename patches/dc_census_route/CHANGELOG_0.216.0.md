## [0.216.0] - the census's body-sized literals read the agent contract, and combat_audit reads the builder's openings

**For "singular changes" (the walker, 2026-10-13).** The factory's census of this repo's module-level
numbers (`docs/findings/agent_contract_follows/literal_census.py`) flagged 127 of 317 constants on a body
word or a contract number, and each was read. Eleven were a body's size written down with its rule beside
it, and each now reads the contract at the value it was:

- **A capsule's width,** two body radii: `enterability.MIN_PASS_WIDTH` and `stairwell._AGENT_PASS_WIDTH`
  (0.7).
- **The body's height and eye:** `enterability.STAND_HEIGHT` (1.8), and `sightlines.EYE` and
  `SIGHT_BLOCK_H` (1.6, the body's eye, `characters.player.eye_height_m`, not the camera's).
- **The step a controller lifts:** `guards.MAX_STEP_UP` (0.5).
- **Two agents abreast,** four body radii: `combat_audit.WIDE_DOOR` (1.4).
- **The door minimum:** `vault_room.DOOR_WIDTH` and `lights._AISLE_MIN_FALLBACK` (1.25).
- **The floor in front of a door,** two body radii and 0.3: `vault_room.APPROACH` (1.0). This is now one
  function, `agent_contract.door_approach()`, which `layout_lint.DOOR_APPROACH_M` also reads; it spelt the
  same formula itself.
- **A gap a bake-radius body cannot use,** two bake radii: `level_design._CLUSTER_GAP`'s upper end (0.8).
- **The ladder hole's clearance,** standoff, body radius and margin: `ladder_geom.HOLE_ALONG` (1.3). Its
  0.45 m margin is now named, `HOLE_ALONG_MARGIN`.

`agent_contract.py` gains the accessors they read: `body_height`, `body_eye_height`, `max_step_up`,
`nav_radius` and `door_approach`. Every value is the one it replaced, exactly in a float, so nothing built
moves.

- **`combat_audit` reads the builder's openings.** It kept its own copy of the opening defaults, and two
  were stale. A width-less door was read at 1.2, where the builder uses the contract's 1.25 since 0.214.0.
  A width-less vault was read at 1.4, where the builder uses 1.3 x 2.1. `_op_width` now asks
  `Opening.resolved()`, so a room whose widest opening is a width-less vault reads as single-file, as it is
  built (`combat_audit.py --all` over the library and `--all-presets`, run on clean copies of 0.215.0 and 0.216.0: byte-identical, 132 specs at 6 HIGH and 78 MED, and 19 presets at 0 HIGH and 8 MED. Neither stale default turned on a flag in the library or the presets; `_op_width` itself is held by the test).
- **Read, and left for the walker or later** (the factory's `docs/findings/agent_contract_follows/README.md`):
  - thresholds that disagree with the contract, such as `enterability`'s 1.1 m "can't even crouch through"
    against `crouch_height_m` 1.2, and the passes at 0.7, 0.8 and 0.9;
  - two door approaches, `circulation`'s 0.6 against `layout_lint`'s 1.0;
  - numbers whose rule names a margin it never derives;
  - one MEASURED against the bake (`stairwell.RAIL_OPEN_MIN`);
  - a comment that does not reproduce its number (`_CUSTOMER_LANE`).
- **`test_contract_census.py`** checks the accessors, each routed number as its rule, today's values, and
  `combat_audit`'s widths at the builder's. It fails to import on 0.215.0.

**Built:** `build.py --all` under Blender 5.1.1, 152 shells in 387 s, exit 0, no error in the log. Every manifest moves by `built_utc` alone, and each carries its outputs' sha256, so every shell is byte-identical to 0.215.0's. The presets as Level Factory makes them (228 combinations, the factory's `preset_digest.py`) digest d53248c1..., as on 0.215.0

**Suite:** 1,493 passed, 2 skipped (the bpy round-trip fixtures, run in their own process), exit 0: 0.215.0's 1,489 and `test_contract_census.py`'s 4, which fail to import on 0.215.0. `stair_regression.py --quick`: every variant clean
