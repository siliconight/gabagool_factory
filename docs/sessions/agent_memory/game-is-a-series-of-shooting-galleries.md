---
name: game-is-a-series-of-shooting-galleries
description: "The game the factory builds for is a series of shooting galleries: buildings, roads between them, and props inside that give cover AND life without overkill"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4bb794c9-c366-4613-95bd-3c61e9a0d0f9
  modified: 2026-09-10T10:26:49.188Z
---

Stated by the user 2026-09-10. The game is **a series of shooting galleries**.
A level is:

- buildings,
- roads connecting the buildings,
- props within the buildings and the level that give it **cover and life**,
  enough to make it interesting **without making it overkill**.

**Why:** it settles what a level-quality instrument should optimise, and it
cuts both ways. A room whose every solid is too short to break a sightline is
furnished and cannot be fought in — that is a defect (roadmap 130, measured at
39 of 91 combat rooms in the shipped Deli Counter presets). But "raise every
piece of cover" is equally wrong: low furniture is the *life* half of the same
sentence, and Deli Counter's over-cover thesis (2-4 pieces per room, cap 5)
already argues against density.

**How to apply:** report the MIX rather than enforce a floor. A finding should
say "this room has no shelter at all", not "these pieces are too short". When
a threshold decides whether something counts as cover, derive it from the
firefight geometry — `deli_counter/agent_contract.json` `sightlines` block,
`cover_break_height()` — not from furniture plausibility. Roads between
buildings are Lot's `site_cover` domain; props inside are Deli Counter's
`level_design` / `combat_audit`.

Related: [[gameplay-layer-lives-outside-level-factory]]
