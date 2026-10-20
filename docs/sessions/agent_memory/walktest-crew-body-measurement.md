---
name: walktest-crew-body-measurement
description: "Roadmap 208 NARROWED 2026-10-09: the walk test re-walked with the crew's 0.35 m / 45 deg body (18/18) and with Laser Tag's step-up too (crew_full, 18/18, the dial confirmed); the mission order is what is left; never re-walk through walktest.py's main()"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-08T20:11:41.742Z
---

`docs/findings/walktest_crew_body/rewalk.py` re-walks the 18 distinct staged
walk tests in the kept workspaces (cold-9193-ws..cold-9204-ws) from patched
copies. 2026-10-08: `crew_body` (radius 0.35, floor 45, the director's step-up)
passes 18 of 18; the control reproduces a job exactly (sim seconds identical,
the walk is deterministic). 2026-10-09: `crew_full` (Laser Tag 0.24.0's step-up
too) passes 18 of 18; its refusal strings in 12 walks and 110 of 312 walkers
travelling differently prove the dial turned. Roadmap 208 NARROWED; left: the
mission's order (spawn, objective, extraction), which needs a director change.

**Why:** roadmap 208 -- the walk test picks candidates with a thinner, more
lenient body than the crew -- says measure before changing the gate.

**How to apply:**
- Never run a patched walk-test copy through `lot/walktest.py`'s `main()`: its
  `sync_addon` copies the checkout's addon over the copy first, so the patch
  never runs. Call its steps (`ensure_project`, `check_buildings`,
  `import_pass`, `run_one`) as `rewalk.py` does.
- A 0.35 m walker at 4 m/s on the contract's 0.40 bake (cell 0.10) has a
  0.05 m corner margin under the 0.067 m frame step: the director's waypoint
  rule (60% of the margin) gives 0.03, which froze every walker. Keep the
  default 0.072 for measurement; a real fix needs a slower walk, a higher
  physics rate or a different consumption rule.
- Related: [[open-work-at-1008-close]].
