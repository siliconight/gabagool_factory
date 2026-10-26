---
name: licences-mit-and-download-at-setup
description: "Walker 2026-10-26: every factory repo is MIT; releases bundle no third-party package, setup downloads them from PyPI"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-26T14:41:59.789Z
---

Walker's calls, 2026-10-26:
- **Every factory repo carries MIT**, holder "Siliconight / GabagoolStudios" (done: level_factory 6ef9fc0, patina,
  deli_counter, lasertag, lux, dispatch, pipeline, root 5d66324; lot/pixelcoat/zoo already MIT).
- **Bootstrap = download at setup.** Releases (git archive) contain no third-party Python package. `setup --venv` /
  Prepare environment fetches the 12 pinned packages from PyPI on the user's machine. Inventory with measured
  licences: `docs/THIRD_PARTY.md`. Level Factory 0.255.0 says the downloads first and refuses a pin whose licence
  moved (`interpreter.LICENSES`).

**Why:** the walker asked that any new dependency come with a legal way to bootstrap from the released packages on
GitHub and the forge.

**How to apply:** before adding any dependency, prefer none (the 0.252.0 schema check is built in for this
reason). If one is unavoidable, add it to PINNED/CONSTRAINED *and* LICENSES and docs/THIRD_PARTY.md in the same
change, and confirm a permissive licence from its metadata. Bundled third-party ASSETS (fonts, textures) are not yet
audited. Related: [[github-push-and-releases]], [[forge-mirrors-github]], [[no-ai-authoring-direction]].
