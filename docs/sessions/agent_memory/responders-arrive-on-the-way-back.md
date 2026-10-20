---
name: responders-arrive-on-the-way-back
description: "Walker 2026-10-08: responders arrive AFTER the job, on the way back -- gameplay layer spawns them; factory makes assets + guarantees arrival. 212 CLOSED (cold 9206-9209): lanes steer, the cruiser ships; 215 open"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-09T13:04:26.702Z
---

The walker, 2026-10-08, answering roadmap 206's open question (what makes the
walk back to the getaway van dangerous): "have responders show up after the
job, on the way back (and this would be on the gameplay layer, but we can make
thee assets and ensure there is clearance and routes for their arrival)".

**Why:** cold run 9198 measured the van's there-and-back route with Lot's
provisional one-leg enemy spread. Laser Tag's enemies run at the crew from the
first frame, so all six arrived single file on the way in and the walk back
was empty: crew deaths in 25 runs fell 48 -> 1 (seed_9054) and 19 -> 0
(seed_9155, LT_MAP_TRIVIAL_ENCOUNTER).

**How to apply:**
- SPAWNING responders (when, how many, their AI) is the gameplay layer's, not
  the factory's -- see [[gameplay-layer-lives-outside-level-factory]]. Do not
  build a responder wave into Lot or Level Factory as if it were the game.
- The factory's half: the ASSETS (responder vehicles and kit, invented
  department branding, no real marks -- [[fake-delco-brands-funny-and-crass]])
  and the LEVEL'S GUARANTEE that they can arrive: arrival points with room for
  a vehicle to pull up, a drivable approach from the site edge, and a walkable
  route from there to the crew's return leg -- checked, and marked in the
  package (roadmap 204) so the game layer can find them.
- Lot already has `responder_spawn` site markers and audit rules
  (`S_RESPONDER_ARC`, `S_RESPONDER_CAMP`, `S_NO_RESPONDERS`); start there.
- Related: [[extraction-is-the-getaway-vehicle]].

**Status 2026-10-08 (roadmap 212 NARROWED):** phase 1 SHIPPED -- Lot 0.99.0
e5da82c `site_responders`: an arrival per open road end (inbound keep-right
lane, a stop for a stated 2.0 x 5.4 m cruiser + 1.0 m door room, nearest the
way back, outside site_audit.CAMP_RADIUS, reserved from parking and from
plan_cover's placement-only `keep_out`, read back as LOT_RESPONDER_BLOCKED),
written as responder_spawn site markers; the nav QA walks a bot from each.
Cold 9200: 0 interventions, 3 arrivals x 3 candidates, all bots reached.
Tradeoff seen: a reserved lane refused a cargo container on seed_9155 and
its fight went 0 -> 6 crew deaths. S_RESPONDER_ARC fires wherever the roads
lie to one side. PACKAGE DONE: LF 0.156.0 48a86e3 (site markers -> anchors:
responder_spawn = ai_spawn tagged `responder`; cold 9201) + LF 0.157.0
5c9d83f (`responder_arrivals.json`: entry/stop/forward/boxes keyed by anchor
id, Godot frame, in the manifest; cold 9202). CRUISER SHIPPED: Zoo 1.86.0
84f6bf1 (livery: the walker chose black_white, the default, 2026-10-09).
212 CLOSED 2026-10-08 by cold runs 9206-9209 (0 interventions each):
- Lot 0.100.0/0.100.1: the vehicle is the cruiser's genome; the lane steers
  round the van, 0.649 m on every candidate; the planner checks the boxes it
  records (a rounding phantom was found and fixed).
- Lot 0.101.0 + LF 0.162.0: the site kit builds the car; the package names
  it (`responder_arrivals.json` v3, `vehicle_scene`) and stands it nowhere.
- LF 0.162.1: the car's import is Dynamic (Godot 4.7 measured:
  light_baking 3 gives gi_mode DYNAMIC), so a spawned car takes the probes.
Roadmap 215 NARROWED 2026-10-09:
- **The site audit is now counted.** Lot 0.102.0 keeps it in the gameplay
  manifest, and LF 0.163.0 reads it into the validation report:
  LOT_SITE_AUDIT_UNREAD if it is missing, never blocking.
- **Cold run 9210:** findings 58 -> 72. S_RESPONDER_ARC fires on every
  club_block_014 candidate, at 33, 6 and 16 degrees.
- **Still open:** the arc question itself. Leave the rule, open road ends on
  more sides, or change its severity; the rule's premise is the gameplay
  layer's.
