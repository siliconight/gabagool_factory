# Phase 1 — Vertical Slice: Delivery Report (offline leg)

**Date:** 2026-07-19 · **Scope:** Production Package §19 Phase 1 — bank, deli,
warehouse, parking garage → 10 pvp_heist configurations + 1 standard +
1 hero mission. Offline gates complete; engine leg queued for one batch run.

## What was built

**10 configurations, all offline-green** (validate OK, built, evidence PASS,
round-trip on contract): BANK_BRANCH A02/A03/A04 (A04 = the Central Bank hero
anchor: 40x30 m, 4.2 m stories, basement vault + antechamber, 3 stairs, roof
ladder), DELI A01/A02/A03 (night_deli chassis; basement vault / story-1
server / story-1 apartment objectives), WAREHOUSE A01/A02 (new ground-up pvp
buildouts; ground cage / mezzanine office objectives), PARKING_GARAGE A01/A02
(booth cash office / deck-1 armored pen; single vs dual ramp).

**2 missions, site gates passed:** MSN_DELI_BLOCK_01 (standard; 200x150 m,
3 buildings, 2 objective approaches) and MSN_CENTRAL_VAULT_01 (hero; 240x180 m,
4 buildings — hero rule caps 2-4 — all four slice families).

**Registries:** 12 configurations, 3 missions, coherent. Sibling distinction
(>=2 tactical AND >=2 visual dims per same-family pair) enforced at
registration, not just planned.

## Findings the gates caught during authoring
- corner_deli chassis carries pre-pvp axis-swapped partitions + multi-objective
  roles: blocking under pvp_heist -> DELI A01 rebased onto night_deli.
- OBJ_ONE_DOOR on two objective rooms -> second openings (soft breaches) added.
- Hero bank through-stairs (-1 to 1) orphaned story 0 in the route graph ->
  split into per-story stairs.
- Roof ladders in public/objective rooms (spec s8.2) -> moved to staff rooms.
- Site attacker spawn 12 m from stage-building defender post -> restaged.
- Registrar rejected 5-building hero -> trimmed to 4.

## Pacing intel (carried constraint)
Both sites traverse in ~2.5 min (range 1.6-3.4) vs the 7-15 min mission
target. Mission LENGTH is owned by downstream objective mechanics (drills,
holds, waves) per the levels-as-input boundary; traversal share recorded in
each mission record.

## Engine leg (queued — one batch)
Per building: nav_gate + godot_gate x10. Per site: walktest + mp_smoke x2.
On green: runtime_walktest/godot_import/multiplayer_smoke_test -> "pass",
then visual pass (Zoo dressing, score >=4 / hero avg >=4.5) before any
record graduates to approved.

## Engine-leg round 1 findings (batch 1 -> batch 2/3)

The first engine batch surfaced two real defects, both now fixed:

1. **Stair discharge void at every story-crossing.** Phase 0 bridged only a
   stair's FINAL flight; the batch proved intermediate crossings void out
   identically. Generator now emits a flush discharge platform at every
   crossing (deli_counter.py).
2. **Multi-story switchback skips intermediate floors.** A stair spanning
   more than one story boundary (bank_job's -1..1, night_deli's -1..2) bakes
   its endpoints onto the top and bottom navmesh islands and never connects
   the floor(s) it passes through -- the ground-floor spawn island is cut off
   from the objective. Every PASSING building used single-story stairs only.
   Fix: the five affected slice configs (bank A02/A03, deli A01/A02/A03) were
   re-authored with per-story flights (mirroring the hero A04, which passed).
3. **Site ground slab sealed basements.** One solid ground box baked over a
   building footprint welds its basement shut. lot.py now tiles the ground
   AROUND footprints (inset so exterior walls stay seated).
4. **Walktest clock was a fixed 120 s** -- the hero's 18-target spine ran it
   out at exactly WALK_SPEED x 120 (a capacity limit, not a nav failure).
   Director now scales the sim cap to the measured spine length.

### PHASE 2 BACKLOG (generator)
The multi-story switchback should connect intermediate floors itself, so
authors can place one core stairwell instead of stacking per-story flights.
Deferred because the intermediate floor-plate connection is intricate
geometry that cannot be verified offline (no Godot in the build sandbox); the
per-story pattern is proven and unblocks Phase 1. Revisit with a live Godot
loop in Phase 2.

## PHASE 1 CLOSED (2026-07-19)

Engine leg complete. **10/10 configurations PASS both building gates**
(nav_gate + import_gate, Godot 4.7). **Standard mission MSN_DELI_BLOCK_01
fully green** (path proofs + physical walkers + 4-player mp_smoke). **Hero
mission MSN_CENTRAL_VAULT_01** accepted on all-18 path proofs + mp_smoke
(navmesh proven walkable end to end; QA-walker spine locomotion filed as
backlog per product decision). Registries coherent; all 12 records stamped.
Certified set: **factory 1.2.0** (deli_counter 0.80.0, lot 0.20.0,
pipeline 0.2.0).

### Engine-round findings (batches 1-5)
1. Stair discharge void at every story-crossing -> generator emits discharge
   at each crossing.
2. Multi-story switchback skips intermediate floors -> per-story flights
   (backlog: generator self-connect).
3. Site ground slab sealed basements -> lot.py tiles ground around footprints.
4. Fixed 120 s walktest cap -> spine-scaled sim clock.
5. Lone inter-level flight voids under surrounding geometry -> redundant
   flight (bank A03); story1-objective delis void 0->1 at site scale ->
   hero uses basement-objective DELI_A01 (backlog: revisit A02/A03 at scale).
6. Device-bridge read cache masked passing gates for several rounds ->
   read reports LOCALLY (phase1_status.py) as ground truth.

### PHASE 2 BACKLOG (carried)
- Generator: multi-story switchback self-connects intermediate floors.
- Site bake: story1-objective delis (A02/A03) 0->1 flight voids at site scale.
- QA harness: physical-walker locomotion across long (18+) multi-building
  hero spines with multi-story descents.
