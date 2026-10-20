---
name: contract-language-pinned
description: "Walker pinned for \"later later\": a contract language like protobufs for Level Factory's data; not to be started yet"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-15T01:29:29.270Z
---

The walker on 2026-10-14, after asking whether Level Factory's configuration is all JSON: "for later later....we'll want a contract language like protobufs for level factory...a pin in it".

**What exists today (measured that evening):**
- Data is JSON: briefs, batches, job manifests and reports, approvals; Deli Counter's specs and `agent_contract.json`; Zoo's genomes.
- A few JSON Schemas: `level_factory/schemas/mission.brief.schema.json`, `surface_dressing.v1.json`, Deli Counter's `schema/level.schema.json`. Versions live as strings such as `level_factory.batch.v0.1` and `level_factory.perf_stations.v1`.
- Tuning sits in about 330 module-level constants across 58 Python files of Level Factory's packages. The workspace index is SQLite, and Godot's own formats hold scenes.

**Why:** the deliverable is a pipeline strangers point at their own game, which needs typed, versioned contracts between the tools rather than JSON shapes each reader guesses at. CLAUDE.md's "never write a checker against a guessed schema" is the same lesson.

**How to apply:**
- PARKED. Don't start it without the walker's go.
- File it in the roadmap as pinned-for-later with the next roadmap patch (not yet filed as of 2026-10-14 21:40).
- When it comes up, start from the inventory above.

Related: [[agent-contract-single-change]], [[consumers-need-only-blender-and-godot]].
