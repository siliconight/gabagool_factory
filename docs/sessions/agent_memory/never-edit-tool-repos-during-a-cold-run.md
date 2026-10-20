---
name: never-edit-tool-repos-during-a-cold-run
description: "A cold run hashes every tool repo at --begin; editing or committing one while it runs is counted as an intervention and voids the run's zero"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4bb794c9-c366-4613-95bd-3c61e9a0d0f9
  modified: 2026-09-13T11:27:17.447Z
---

Before any edit to a tool repo (zoo, lot, level_factory, pixelcoat, patina,
lux, deli_counter), check whether a cold run is in flight. If one is, draft
in the scratchpad and land it after the run ends.

**Why:** On 2026-09-13 cold run 9037 came back with seven unattributed
changed files — Pixelcoat 0.33.0, edited and committed mid-flight. Its art
stage ran on a Pixelcoat the `--begin` snapshot had never seen, so the run
could not be counted as a zero even though every stage passed. The rule is
in CLAUDE.md; the failure was forgetting a run was still going while
working on the next feature.

**How to apply:** Keep one background cold run at a time, and gate tool
edits on its log showing `== end`. Drafting the next layer in the
scratchpad while a run finishes is the right use of that time — just do
not copy it into the repo until the run has ended.
