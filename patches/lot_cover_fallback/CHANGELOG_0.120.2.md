## 0.120.2 - the cover fallback is the contract's cell, and the pinch message states the threshold its check used

**Found 2026-10-13 by the factory's door-width finding** (`docs/findings/door_widths/README.md`, "Lot
carries the refuted cell"). `site_cover._NAV_BAKE_FALLBACK` said `cell_size_m` 0.15 against
`deli_counter/agent_contract.json`'s 0.1. It was the contract's cell on the day it was written
(5d7f4b4, 2026-07-27); on 2026-07-29 the contract moved to 0.1 and recorded why in its own
`cell_size_derivation` -- 0.15 capped the connected slope at 45 deg against a stated 55, and eight path
proofs failed as disjoint islands. `lot._AGENT_DEFAULTS` was refreshed the next day (97366fc) and this
copy was not. Its comment said Level Factory's `lasertag_contract` would report drift; that module
checks the opening range and the sight heights and never reads `nav_bake`, so for 76 days nothing
compared the two.

**What it cost was one number in one message.** `lot.py` (3981-4006) has given `plan_cover` the
contract's bake since the commit that wrote the fallback, so the room grown beside a wall (2.5 m) and
the pinch read-back's threshold (1.0 m) were the contract's. `findings` stated `min_passable_gap()` --
no bake, the fallback's -- so `LOT_COVER_PINCH` said "less than the 1.2 m" over lanes measured against
1.0 m: two spellings of one number. Under a bake whose gap is neither, it listed a lane wider than the
number it said the lane was under. It never reached a log: of the 261 Lot job logs on the factory's
disk, 154 carry `LOT_COVER_PLACED` and none carries `LOT_COVER_PINCH`.

- **`_NAV_BAKE_FALLBACK`**: `cell_size_m` 0.1. The comment keeps the 0.15 and the drift claim, and
  names the comparison that exists now.
- **`min_passable_gap`'s docstring** derives 1.0 m at the contract's cell. It said "0.15 m cells ...
  1.2 m, which is why the ratified door is 1.25" -- the contract's `clearances.derivation` still
  evaluates the formula at 0.15, and whether the door follows the bake is the factory's roadmap 197,
  the walker's call, not this module's.
- **`CoverPlan.passable_gap`**: `plan_cover` derives the narrowest lane once, from the bake it gives
  `pinches`, and `findings` states it. A plan with pinches and no `passable_gap` -- one `plan_cover`
  did not make, and nothing in Lot makes one -- is refused with a `ValueError` rather than given the
  fallback's number.
- **`BUILDING_CLEARANCE`**, the clearance for a caller that passes no bake, is 2.5 m (was 2.7 m).
  Nothing in Lot reads it but a test; `plan_cover` derives its own.
- **`tests/test_cover_fallback.py`**: both copies Lot carries -- `lot._AGENT_DEFAULTS` (21 keys shared
  with the contract) and `_NAV_BAKE_FALLBACK` (2) -- equal the contract on every shared key, the shape
  of Deli Counter's `test_every_fallback_equals_the_ratified_value`; with no bake, the gap and the
  clearance are the contract bake's; the message states the threshold the read-back used, under the
  contract's bake and under a 0.25 m cell (1.5 m, where 0.120.1 listed a 1.3 m lane as "less than the
  1.2 m"). On 0.120.1 the guard names exactly one drift, `cell_size_m` 0.15 against 0.1.
  `tests/test_lot.py`'s pinned gap is 1.0, its docstring keeping the 1.2 it pinned.
- **`tests/test_site_cover_slots.py`'s too-tight lane** is derived from the clearance the plan uses,
  midway between what a car and a truck need across it. It was a literal 11.0 sized by hand at the
  fallback's 2.7 m ("6.0 + 2 x 2.7 does not"); at 2.5 m a truck needs exactly 11.0 and stood in it,
  `{'box_truck'}` placed -- the suite's one failure on the change without this. The test passes no
  bake, so it had measured the fallback all along; its docstring's "9 m" went with the literal.

**Built sites do not move.** Measured by the factory's `docs/findings/door_widths/cover_fallback_ab.py` on cold run 9284's
`club_block_014` seed_9080 Lot job, replayed from the two commands its own `job.log` records (the job's
interpreter and working directories, its out dir swapped for one scratch path): on 0.120.1 the replay
matched the cold run's own out dir in all 53 files, and a second replay matched the first (53 of 53, its
log 85 of 85 lines); on 0.120.2 all 53 files match both, byte for byte, and the log every line.
`plan_cover` was called once, with the contract's bake, on arguments equal before and after. The site
places two pieces and reports no pinch, so the message is not in it.

**The cover plan, module against module** (0.120.1's `site_cover.py`, blob b22d30f, beside 0.120.2's, on
that call's own arguments): equal in every field 0.120.1 has -- as the job asked, and with the room
beside a wall forced to 2.0, 1.5 and 1.0 m, two pieces and no pinch each time -- with `passable_gap` the
only addition. With no bake the gap and the clearance move 1.2 -> 1.0 m and 2.7 -> 2.5 m; with the job's
bake both modules derive 1.0 and 2.5. On the new tests' fixture (one piece, a wall a set lane off it) the
pinches are the same under both: under the job's bake a 0.5 m lane is stated against 1.2 m on 0.120.1
and 1.0 m on 0.120.2, and a 1.1 m lane is no pinch on either; under a 0.25 m cell a 1.3 m lane is stated
against 1.2 m on 0.120.1 and 1.5 m on 0.120.2.

**Each new test fails on the defect it owns**, on copies with half the source change withheld
(`--without=` with `LOT_ROOT`): with both halves withheld (0.120.1's source) 5 of the 6 fail -- the guard
(`site_cover._NAV_BAKE_FALLBACK cell_size_m: fallback 0.15, contract 0.1`), the no-bake gap (1.2 against
1.0), both messages (1.2 stated against 1.5, and against 1.0) and the refusal (did not raise); with the
fallback alone withheld, the guard and the no-bake gap; with the message alone withheld, the 0.25 m
cell's message (1.0 stated against 1.5) and the refusal. The contract-bake message passes with either
half, as it must: there the two numbers agree once the fallback does. The sixth test pins the shared
keys (21 and 2) and passes on all four. `tests/test_site_cover_slots.py`'s derived lane passes at both
clearances.

**Suite:** 833 passed (827, and the six new). With the source change and `test_site_cover_slots.py` as it was: 1
failed, 832 passed -- `test_a_lane_too_tight_for_a_truck_gets_a_car`, `({'box_truck'}, 2.5)`.
