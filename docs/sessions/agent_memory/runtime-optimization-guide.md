---
name: runtime-optimization-guide
description: "Walker's Godot 4.7 Runtime Optimization Guide filed 2026-10-03 at docs/reference/Godot_4_7_Runtime_Optimization_Guide.md; \"to be used in some fashion later\"; pointed at from docs/PERFORMANCE_CONTRACT.md"
metadata:
  node_type: memory
  type: reference
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-03T14:12:41.164Z
---

`docs/reference/Godot_4_7_Runtime_Optimization_Guide.md` -- the walker's guide
(2026-10-03, "this should be somewhere in our repo to be used in some fashion
later"). Sits beside `Godot_4_7_Draw_Call_Optimization_Guide.md` and the
`Multiplayer_Procedural_Level_Performance_Bible.md`; `docs/PERFORMANCE_CONTRACT.md`
now ends with a pointer at it.

What it is good for when the time comes: section 4's A/B protocol and its
**verification record** template (the shape a cold run's perf note should grow
into: cold/warm state, single change, p95/p99, hitch counts, mechanism
observed, rollback); section 5's symptom-to-experiment table; section 6's
twenty techniques each with mechanism / experiment / trap (6.4 HLOD and 6.18
first-use pipeline surprises are the two this repo has not touched); section 9's
ten requirements on a procedural generator (stress seeds, validation output,
runtime gate); section 12's review-rejection table. Its own labels: documented
/ project prescription / verified in project -- it claims no measured gains.

**How to apply:** cite it when pricing a look or writing a cold run's perf note;
do not treat its prescriptions as measured until the harness says so
([[performance-beats-graphics]], the draw-call rule in CLAUDE.md).
