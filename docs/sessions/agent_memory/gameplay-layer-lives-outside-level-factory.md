---
name: gameplay-layer-lives-outside-level-factory
description: "Spawns and other gameplay placement will live in a separate gameplay layer, not Level Factory, so level-quality measures must not depend on them"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4bb794c9-c366-4613-95bd-3c61e9a0d0f9
  modified: 2026-09-09T00:50:43.120Z
---

The gameplay layer — enemy/player spawns, objectives, and placement generally —
is expected to live OUTSIDE Level Factory in its own layer. Stated by the user
2026-09-08. The current spawns have had "almost no thought" put into them and
should not be treated as good or as fixed.

**Why:** it changes what a level-quality instrument is allowed to key off. A
measure of the LEVEL has to be a property of its geometry, because the factory
will not own the placement that a spawn-based measure depends on. Anything
weighted on spawn positions is measuring a gameplay artefact that is both
provisional today and somebody else's output tomorrow.

**How to apply:** when building or reading cover/exposure/sightline measures,
prefer spawn-independent readings (e.g. `LT_MapSampler`'s per-position max open
ray, `long_sightline_meters`) over spawn-relative ones (`overexposed_fraction`,
`blind_fraction`, both computed against enemy spawn points only). Keep the
spawn-relative numbers as secondary — they become meaningful again when a real
gameplay layer supplies real spawns — but do not let them be the headline or
the score driver. Same caution applies to Lot's spawn placement and to any new
gate that wants to ask "is this level fair".

Related: [[route-completion-rate-is-gated-by-corpse-collisions]]
