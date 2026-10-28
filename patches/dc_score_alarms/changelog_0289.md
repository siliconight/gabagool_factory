## [0.289.0] - a score's alarm hooks

The walker, 2026-10-28, of score locations: "gameplay events or something that doesn't mean much for level factory but
is part of what would trigger police coming or stuff like that for the dispatch layer"; "they could mean nothing,
but they could also be ingested/used by the gameplay layer of who is building this game" (the factory's roadmap 323).

### Added
- **`score_alarms.ALARM_FIXTURES`** (a new, Blender-free module): which fixture carries which event, keyed on the
  slot's `role` or `species` -- a teller line's `alarm.panic_button` (silent), a vault door's `alarm.vault_door`
  (audible), every deposit unit's `alarm.deposit_drilled` (silent), a drop safe's `alarm.safe_opened` (silent), an
  ATM's `alarm.atm_tampered` (audible) and a cash cart's `score.cash_moved`. Data only: no heat, timer or response.
- **`_Builder._score_alarms`**: one `alarm` marker per slot a row names, at the slot's centre, in the innermost room
  on its storey that holds it, its event in `meta` (`event`, `audible`, `fixture`). Lot carries markers whole into
  the site; Level Factory 0.265.0 hands them to Dispatch as `trigger` anchors when a brief turns gameplay events on.
  Keyed on what the generator placed, so every fixture of a kind carries its hook in any building, and a new score
  location adds rows, not code.

### Tests
- `tests/test_score_alarms.py` (new; fails on 0.288.0): every alarmed fixture in three banks has its hook, at its
  slot, with its event; a hook sits in its room; the vocabulary is data and nothing more.

