---
name: eight-level-templates
description: Walker 2026-10-28 wants ~8 level templates in the authoring panel with great diversity/dynamics; Delco Ave (one avenue) is the second
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-28T14:40:42.597Z
---

The walker, 2026-10-28, of the authoring panel's templates (`level_factory/packages/service/templates/*.json`): "restaurant block doesnt feel right ... Try Delco Ave (for a simple 1 lane road level template)", then "my goal is to have like 8 of those templates with great diversity/dynamics".

Proposed set (axes: street shape, score, time/weather, surroundings, scale/verticality):
1 Restaurant Row (exists) 2 Delco Ave (LF 0.263.0: new `avenue` road grammar, one road; convenience store) 3 Bank Block (bank, block loop) 4 Warehouse Yard (yards) 5 Crossroads Gas (gas station, cross, noon) 6 After Hours (strip club/video store, midnight rain) 7 Rowhome Row (safehouse, block, night) 8 Precinct (police station, cross, high verticality).

**Why:** the panel is the no-AI authoring loop's front door ([[no-ai-authoring-direction]]); one template is no choice.
**How to apply:** each template ships only after a real level made+walked from it (the panel's own `brief_from_design` brief, run by the CLI); a generator gap a template finds is fixed in the tool, never worked around in the template. `main_street`/`strip`/`street` still alias T on purpose (repointing moves old levels).
