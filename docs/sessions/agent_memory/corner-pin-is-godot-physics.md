---
name: corner-pin-is-godot-physics
description: "FIXED 2026-10-12: LT 0.29.0 keeps the crew on the mesh; 0.28.x fixed crew counting; LT 0.30.0 bot-held guards = EnemyBlocked (182 -> 23); LT 0.31.0 guards keep to the mesh + step up via LT_Steering (23 -> 14); trace before believing a pin"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-13T00:02:15.041Z
---

Found 2026-10-12 (docs/findings/route_snag/): roadmap 242's "kerb face" was
a crew bot pinned at the deli register counter's corner (same float to 15
digits every run). The bot cuts corners (arrival radius ~0.44 m vs 5 cm
between the 0.4 nav erosion and the 0.35 body). On that lot Godot Physics
pins it and Jolt slides past (72 -> 7 stuck) -- I recommended Jolt to the
walker on that one lot, then the 16-lot, 7-family breadth run (today's LT,
Godot arms identical twice) showed Jolt pins MORE elsewhere (without that
lot: stuck 36 vs 53, pinned 8 vs 23). RETRACTED: the engine is not the fix.

**Why:** a recommendation from one lot was wrong across families; the walker
does not know the game's engine ("we are going to use Godot"); Godot 4.7
runs Godot Physics unless a project names "Jolt Physics" (engine_probe.gd).

**How to apply:** fix the grade's corner dice in Laser Tag's bot (keep the
path's clearance), measured on the 16 lots under both engines; grade with
whatever engine the game ships, default until chosen. Check breadth before
recommending anything off one lot. Probe pattern: snag_trace.py on a COPY of
the job's staging; keep `[LT slide]` lines. Also: Godot reads an integer
literal for a float shader uniform as null (Lot 0.119.2). The fix drafted
2026-10-12 as Laser Tag 0.28.0 (`_velocity_on_mesh`, 1 cm tolerance) and
HELD: stuck 108->45 / 60->44, pinned 74->9 / 25->14 over the 16 lots, but
bank_block_001 seed_9256 pins 7 under each engine and deli 9191/9393, gas
9282 (Jolt) score -10 (route_snag README; patch refuses the repo).
ATTRIBUTED 2026-10-12 night: 18 of those 21 were the STUCK DETECTOR
counting fights -- `_update_stuck` asks "enemy in sight?" only as its 4 s
window closes, so a bot standing to fight all window reads stuck (-10, and
a skipped route point). Shipped LT 0.27.0 over 16 lots: 23/108 (Godot),
28/60 (Jolt) stuck events are fights; 7 of 32 rows owe their whole -10 to
them. Fix drafted as LT 0.28.0 (patch_lt_fight_not_stuck.py: a stand to
fight restarts the window); tools: pin_trace.py census/--why/trace,
why_breadth.py. SHIPPED LT 0.28.0 (464db01, cold 9266: seed_9003 PWT 80
-> PASS 90, seed_9104 route 0.72 -> 1.00) and 0.28.1 (7ae7aa9): the
detector's SECOND false positive was round trips -- a body out to a route
point and back inside one 4 s window reads "moved 0" (net displacement);
an arrival now restarts the window too. 16 lots vs 0.27.0: 22 rows up, 0
down; stuck 108->70 (67 = the one real deli-counter pin), 60->3. The
breadth's "pinned" metric counts deterministic round trips as pins --
trace (--wide) before believing a pin. Keep-on-mesh SHIPPED as 0.29.0
(5b94ada) on 0.28.1: stuck 70->0, 3->0; cold 9267 all three PASS 90.
Left on 242: the swing's 9261/9262 lots were retired (engine_ab.py builds
names the retire rule can't see; task chip filed); 2 routes a run shorter. Related:
[[philly-street-comps]], [[walktest-crew-body-measurement]].

**2026-10-13, the enemy count:** Laser Tag's EnemyStuck also counts an enemy held by a TEAMMATE (`docs/findings/stoop_breadth/enemy_stop_trace.py`). It patches a copy's `_on_stuck` to print the agent state and this frame's slide collisions; the control is the job's report reproduced. On restaurant seed_9104, three enemies queue single file on one path, because in SEEK the brain re-sets the destination every frame and the enemies have no avoidance. The same class as 0.28.0's crew fix. Next: trace the WARN lots (warehouse 9206: 51 events, bank 9256: 23) before any Laser Tag change.

**2026-10-13, SHIPPED Laser Tag 0.30.0** (af09e20, pushed): as a held guard's window closes, `_held_by_a_body` leaves out floor contacts; all the rest bots (CharacterBody3D) -> EnemyBlocked, not charged by the score; any level contact -> EnemyStuck as before; handled identically, so fights replay exactly. 16-lot breadth (`docs/findings/route_snag/blocked_breadth.py`): enemy stuck 182 -> 23, 159 blocked, stuck+blocked == the old stuck on every lot, every other field identical; deli 9393 and bank 9256 WARN -> PWT, warehouse 9206 WARN 68 -> 73. Cold 9275: 0 interventions, seed_9104's 3 now blocked. The four-lot census said "73 of 75 held by another body": RETRACTED (74, and it asked ANY contact a body, not ALL). The 23 left, PLACED (root 28924fc): 21 at two spots -- warehouse 9206's 13 a guard 5 cm off the mesh against b1's wall end with a guard ahead; crossroads 9600's 8 a capsule on b2's stair ramp's low SIDE edge 0.18 m up, where the bake joins floor to ramp (the contract's 0.1025-0.15 band, left to step-up). The crew bot keeps to the mesh (0.29.0) and steps up (0.5); the guards (LT_EnemyMovement) do neither -> next: port both, price on the 16 lots.

**2026-10-13, SHIPPED Laser Tag 0.31.0** (05dd5e9; root 2b5e8ad): the crew's `_velocity_on_mesh`/`_try_step_up` moved into `LT_Steering` (static, both bodies call it); guards keep to the mesh + step up (scenario's player_max_step_up_m). Breadth control: 0.31.0 with guard steering OFF == 0.30.0 exactly on 16 lots. Enemy stuck 23 -> 14: the stair ramp's 8 gone; warehouse 9206's 14 remain at b1's wall end = a Godot Physics HOLD (velocity away from the wall, zero travel, falling speed growing, not falling). Fights moved on every lot (9206 WARN->PWT on OVEREXPOSED, gas 9181 -1). Cold 9276 0 interventions. Open: how a guard gets 5 cm off the mesh with keep-on-mesh on; gas 9181's route point 0.58 m past its path's end.
