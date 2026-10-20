---
name: door-widths-widen-to-contract
description: "walker 2026-10-13: widening doors is OK, call it out in agent_contract.json; DC 0.214.0 measured in scratch, NOT applied; drafts in _scratch/2026-10-13_door_width/drafts"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-13T23:19:15.844Z
---

The walker, 2026-10-13 (roadmap 197): "If we change the door widths, that's ok, it should be called out
in the agent contract." My stated reading, not yet confirmed: keep `clearances.min_door_width_m` 1.25 as a
DESIGN minimum (the bake needs only 1.00 at the contract's own 0.1 m cell), widen every walkable door
under it, and write the change into the contract beside the number. CONFIRMED by the walker after the
pause: "yes, widen the doors and keep 1.25".

**Why:** 200 library doors and 61 preset doors sat under 1.25, flagged only by a warning nothing reads,
and the contract's derivation was still worked at the refuted 0.15 cell.

**SHIPPED 2026-10-13, roadmap 197 CLOSED.**
- Releases: DC 0.214.0 (2879716a), root e3afa59.
- Cold run 9285 (restaurant_row_001): 0 interventions.
- Cold run 9286 (deli_001): 0 interventions, enemy stuck 0 on all three candidates.
- Three patches went out: `patch_dc_door_width{,_vault_note,_refurnish}.py`.
- The refurnish was needed because the library is furnish's fixed point. Any door change means: run
  `migrate_furnish_recipes.py`, attribute with `docs/findings/door_widths/refurnish_delta.py`, and never
  read the migration's own -/+ summary as a loss.

Earlier plan, kept for the record: the measured plan was the "What is left" section of
`docs/findings/door_widths/README.md` (root 654e9c0). The drafts are in
`_scratch/2026-10-13_door_width/drafts/`, and the scratch DC with the change is beside them.
- The draft test must read only the library's shells, because `build/` holds orphan builds
  (`fuel_stop_heist3`, `fuel_stop_heist4`).
- Two doors stay under 1.25, and the contract must name both:
  - `primos_pizza` kitchen_stairs, blocked by L18 and L21;
  - `stair_core._PUNCH_DOOR_W` 1.1. That is stairs-first only, not on LF's path, and 1.25 breaks it: 2 → 21 failures.
- Never write "two bodies pass": two 0.35 m bodies need 1.40 m.
- If the walker meant lowering the number, the README's option 1 applies (aisles and landings narrow).

Related: [[open-work-2026-10-09]].
