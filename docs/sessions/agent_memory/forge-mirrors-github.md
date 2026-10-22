---
name: forge-mirrors-github
description: "Walker 2026-10-21 chose a PULL MIRROR: forge.internal.vaultinteractive.net/BMONEY/LevelFactory mirrors github.com/siliconight/gabagool_factory (repo + releases); nothing is pushed to the forge from here"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-22T02:18:57.300Z
---

The walker wants their internal Forgejo (forge.internal.vaultinteractive.net/BMONEY/LevelFactory, private) to be "essentially a clone of the Gabagool Factory Repo/Releases", and chose option 1 on 2026-10-21: the forge pull-mirrors the public GitHub repo via New Migration (mirror + Releases), set up by the walker in the forge's web UI. No `forge` remote is added here and nothing is pushed to it from this machine; the GitHub release flow ([[github-push-and-releases]]) is unchanged.

**Why:** least work -- the forge keeps itself in sync from GitHub.

**How to apply:** after the next factory release (1.42.0), check the forge's Releases tab: whether the new release's notes and zip arrived by themselves or only its tag (a pull mirror's release sync was not certain when chosen). If only the tag arrives, offer the walker the push option (a `forge` remote + `tea release create`), which needs their forge token in Git Credential Manager and their allow-list entry -- never handle the token.
