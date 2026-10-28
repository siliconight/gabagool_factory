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

**Left:** zone events (the getaway's end zone, a vault, a score room) on the same block; the towers' missing teller
line and vault.
