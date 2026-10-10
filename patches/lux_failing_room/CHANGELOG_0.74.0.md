## [0.74.0] - one bad tube a room, not a row

**Roadmap 229.** Deli Counter 0.206.0 lays a wide room's ceiling in two or
three rows, `<room>_ceiling`, `<room>_ceiling_r1`, `_r2`, each split run
`_<i>`, where every room had one. `LuxFixtureSpawner.choose_failing`
(0.62.0) picked one failing lamp AN ANCHOR, so a three-row sales floor would
have stuttered three tubes, which is a fault in the building, not the tell
one bad tube is.

**What it is now.** `LuxFixtureSpawner.room_of(anchor)`: an anchor's room
is everything up to and including its `_ceiling` or `_bulbs`, and the
spawner groups the fluorescent and pendant markers by that, one failing
lamp a room, chosen by the room's hash among every lamp of every row --
deterministic, and an authored rename is still the only thing that moves
it. An anchor named otherwise (the selftest's `room_a`, a hand-authored
`foyer_pendants`) is its own group, as before.

**Selftest:** `tools/failing_fixtures_selftest.gd` adds the case: a sales
floor's three rows and a split run, eight markers under four anchors, choose
one lamp; a vault's two bulb runs choose one; the older cases hold. RESULT_SELFTEST.
