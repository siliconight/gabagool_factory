---
name: agent-contract-single-change
description: "walker: keep routing body-derived numbers through agent_contract.json, so one edit re-sizes everything once character sizes are known"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-13T22:57:49.393Z
---

The walker, 2026-10-13: "remember to continue to update the agent contract file so we can make singular
changes when we know the size of characters in the game".

**Why:** character sizes are not final. When they are, one edit to `deli_counter/agent_contract.json`
must carry through every tool, without anyone hunting literals.

**How to apply:**
- Code that writes a body-derived width, height or clearance reads it through `agent_contract.py`
  (`min_door_width`, `min_corridor_width`, `body_radius`, ...). Never a literal beside a comment naming
  the contract.
- Record new derived numbers in the contract with their derivation. `clearances.re_derive_when` (DC
  0.214.0) lists what follows a body change on its own and what does not yet.
- DC 0.214.0 routed the staff door and the stairs-first landing door through the contract.
- DC 0.215.0 (ebdb3cf4) routed the last two named literals:
  - `agent_contract.stair_flight_width()` feeds `LANDING_DEPTH` and `STAIR_FLIGHT_WIDTH` (IBC 2018
    1011.6, no 48 in cap);
  - `vault_aperture()` feeds `vault_room.APERTURE` and the vault default; Zoo builds to the slot's
    `fit.openings`.
  Proof pattern for a same-value routing: every manifest by `built_utc` alone, plus
  `docs/findings/agent_contract_follows/preset_digest.py` (with a control version that differs).
- Known gaps, to route when touched (`docs/findings/agent_contract_follows/README.md`):
  - the library's 3 vault openings, WRITTEN (no migration rewrites them);
- CENSUS DONE 2026-10-13: DC 0.216.0 (9fef728d) routed 11 more and fixed `combat_audit`'s stale
  defaults. Instrument: `docs/findings/agent_contract_follows/literal_census.py` (317 constants, 127
  flagged, all read).
- Open TENSIONS (they change behaviour, so the walker decides):
  - crouch 1.1 vs the contract's 1.2;
  - passes at 0.7 / 0.8 / 0.9 vs the 1.25 door;
  - door approach 0.6 vs 1.0;
  - walkable pitch 40.
  The README has the full list, plus the underived margins, the measured RAIL_OPEN_MIN and the
  `_CUSTOMER_LANE` comment.
  - ~~Lot `site_cover._NAV_BAKE_FALLBACK` (cell 0.15)~~ CLOSED by Lot 0.120.2 (9be94e0, the chip's
    session): cell 0.1, and `LOT_COVER_PINCH` states the threshold its check used. Lot's
    `tests/test_cover_fallback.py` compares `lot._AGENT_DEFAULTS` (21 keys) and that fallback (2) to the
    LIVE contract, so changing a NUMBER Lot copies (nav_bake, characters, clearances, qa) turns Lot's
    suite red until Lot follows: run Lot's suite with any contract change. Text-only edits pass;
    DC 0.214.0's in-flight contract passed it (6/6) on 2026-10-13;
  - `meshlib_kit.DOOR_W` (the optional GridMap kit; nothing imports it).

Related: [[door-widths-widen-to-contract]].
