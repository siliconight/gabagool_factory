---
name: no-ai-authoring-direction
description: Walker 2026-10-26 -- the factory becomes a no-AI level-authoring tool (Godot panel + Python services); first deliverable = one graphical Restaurant Row loop; progress record docs/AUTHORING_LOOP.md
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-26T09:15:58.696Z
---

The walker, 2026-10-26: develop Gabagool Factory into a level-authoring tool usable with imagination, Blender and
Godot -- no AI writing scripts, running commands or troubleshooting routine builds. Plan and guides filed in
`docs/reference/authoring/` (operating guide, no-AI authoring plan, Python/Blender/Godot contracts guide; all written
against factory-v1.41.0, so verify against current code).

**First deliverable:** one complete graphical creation loop on Restaurant Row -- configure tools, create a level,
generate + select a candidate, walk it, change a supported setting, save + reopen the project, export -- with no
terminal, JSON editing or AI.

**Why:** the metric is interventions per level; today an assistant is the missing operator UI.

**How to apply:**
- START each session by reading `docs/AUTHORING_LOOP.md` (the one progress record: milestone, evidence, blockers,
  decisions, exact next action) and verifying the source it names. Do not rely on memory.
- Small testable increments; for each: the user capability, the smallest complete change, checks + the real workflow
  where possible, what passed/failed/unverified, then continue.
- Every exposed control must affect generation or say it only records intent. Designer edits must become saved
  authoring data regeneration respects. Fix defects in owning tools.
- Decide routine things myself; bring the walker decisions that change UX, scope, architecture or compatibility.
- Godot is the primary authoring surface; PySide6 desktop stays a diagnostic surface (PySide6 not installed here).

Related: [[keep-it-rolling]], [[open-work-2026-10-09]], [[game-is-a-series-of-shooting-galleries]].
