# Gameplay events, end to end (roadmap 323)

The walker, 2026-10-28: score locations should declare "gameplay events ... part of what would trigger police coming
or stuff like that for the dispatch layer" -- data a game may ingest or ignore -- behind a switch: "flip the switch,
turn gameplay events on, and then the gameplay layer could ingest if warranted".

**Shipped:** Dispatch 0.6.0 (47a1647, an anchor's `event`: name, `fires`, `repeat`, `audible`); Deli Counter 0.289.0
(6270b5a1, `score_alarms.ALARM_FIXTURES` and an `alarm` marker at every such fixture); Level Factory 0.265.0 (e72c14b,
the brief's `gameplay_events` and the panel's switch, off by default) and 0.265.1 (bfce96a, below).

**Measured, end to end** -- Bank Block made from the panel's own brief (`design.brief_from_design`) with the switch
on (`workspaces/events-on-0265-ws`): its `gameplay_anchors.json` (Dispatch 0.6.0) carries 6 triggers, each with its
event, firing rule and room -- the level's 2 ATMs (`alarm.atm_tampered`, audible), 2 drop safes (`alarm.safe_opened`),
2 cash carts (`score.cash_moved`) -- exactly its alarmed fixtures, none lost or invented. Its bank, `bank_tower_a03`,
has no teller line, vault door or deposit wall, so no panic button, vault or deposit event: a content gap in the
tower, not in the hooks.

**Refuted and fixed: "off, every package is what it was."** Held to the same mission built on Level Factory 0.264.0
(`workspaces/template-bank_block-0264-ws`), the shared anchors' contents matched and six ids did not (`lot:01_17` ->
`lot:01_21`, an objective, both ladders): a shared id's suffix is the record's index, and 0.265.0 counted the alarms
in it, staged or not. Level Factory 0.265.1 indexes them apart. Re-measured on two fresh makes
(`event_ids_check.sh`, `.out.txt`): events off -- the same 32 ids and every record identical to 0.264.0's; events on
-- 38 anchors, the 6 triggers added and every other id unchanged.

**The getaway's end zone** -- Dispatch 0.7.0 (1401f26, a `zone.*` event must carry a positive `radius`), Lot 0.136.0
(b288c56, the getaway's extraction states `zone_radius`: spawn to the van body's kerb side, 1.40, plus the contract's
player radius, 0.35), Level Factory 0.266.0 (e202411, the extraction anchor carries `zone.extraction`, `on_enter`,
`edge`, behind the same switch). Measured on Bank Block made fresh with each setting (`zone_check.sh`, `.py`,
`.out.txt`, against `events-off-02651-ws` / `events-on-02651-ws`): off, the same 32 anchors, every record identical
to 0.265.1's; on, the same 38 ids, and exactly one record changed -- `lot:getaway_van_extraction_0` gained
`{"event": "zone.extraction", "fires": "on_enter", "radius": 1.75, "repeat": "edge"}`, still tagged `extraction`. The
van's slot edge stands 1.250 m from the zone's centre, inside it.

**What each bank can send** (Deli Counter 0.289.0's built library, `build/bank*.gameplay.json`, alarm markers by
event; measured 2026-10-28):

| bank | panic | vault door | deposit | safe | ATM | cash moved |
|---|---|---|---|---|---|---|
| bank_branch_a02 | 1 | 1 | 7 | 4 | 1 | 4 |
| bank_branch_a03 | 1 | 1 | 7 | 4 | 1 | 2 |
| bank_job | 1 | 1 | 4 | 4 | 1 | 3 |
| bank_branch_a04 | 1 | - | - | 4 | 1 | 3 |
| bank_tower_a01 | 3 | - | - | 2 | 1 | 1 |
| bank_tower_a02 | 3 | - | - | 2 | 1 | 2 |
| bank_tower_a03 | - | - | - | 1 | 1 | 2 |
| bank (preset) | 1 | - | - | - | - | - |

Four of eight banks have no vault door and no deposit wall, so they can never send the two events a vault job turns
on. `bank_tower_a03` -- the bank the Bank Block template draws at seed 9003 -- has no teller line either: its
`teller_cage` is furnished as a cash room (racks, a floor safe, carts) behind an ordinary door. Its own lint already
says so and nobody reads it: `layout_lint.py specs/bank_tower_a03.json` prints `L8 'bank_tower' spec has no room
matching 'vault|safe' (signature program)` as a WARN. The towers predate the score program (Phase 4's hand-authored
venue configs). The gap is in the library's content, not in the hooks.

**Vault doors and drill zones.** Deli Counter 0.290.0 (659179cc, `migrations/migrate_bank_vault_doors.py`) turns
the `vault_gate` door into a vault door in bank_branch_a04, bank_tower_a01 and credit_union_a03; credit_union_a01
keeps its door, because the leaf would swing across its stair `cu01_stair_w` (layout_lint L22) -- which this repo's
own commit gate caught on the first apply, after the clone's suite and nav gate had passed (now `ship_change.py
gate`). The walker then asked for the drill: "opening the safe should be a gameplay event where you have to stand in
an area for a certain amount of time close to the 'drill' and then the door opens", and "no drill time from the
factory ... These will be networked events programmed somwhere else...we just want the seams/hooks in place on some
level so we can invoke them visually on peoples clients if needed later (muiltiplayer game)". Dispatch 0.8.0
(100ff86): `fires` may list `["on_enter", "on_exit"]`, and `target` names the interactive an event acts on. Deli
Counter 0.291.0 (c10c4f5f): every vault door and deposit wall writes a `drill` marker, `score_alarms.drill_zone` --
centre half the slot's depth plus the contract's body radius out along its facing, radius half the opening's width
plus that radius (1.0 m at a vault door) -- naming the interactive it opens. Checked on the built library before
shipping: both vault doors' zones in bank_branch_a02 and bank_job stand in the room the door is entered from
(vault_west, vault_room_east); every deposit wall's inside the vault. Level Factory 0.267.0 (1079e61) stages them as
triggers behind the switch. NOT YET MEASURED in a package.

**Left:** a package made with events on, read for its drill zones; floor safes, which have no openable states and so
nothing for a drill to open; a score room's zone; `bank_tower_a03`'s missing teller line.
