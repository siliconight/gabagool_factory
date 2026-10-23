---
name: forge-mirrors-github
description: "Walker 2026-10-23: releases go to GitHub AND forge BMONEY/gabagool_factory (ordinary repo, not a mirror) via tools/publish_release.py; backfill 1.36-1.41 once the walker's credential is stored"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-23T21:24:15.665Z
---

The walker wants their internal Forgejo to carry the same releases as github.com/siliconight/gabagool_factory: forge.internal.vaultinteractive.net/BMONEY/gabagool_factory/releases.

**History:** on 2026-10-21 they chose a pull mirror, then named BMONEY/LevelFactory. On 2026-10-23 the repo is BMONEY/gabagool_factory, a pull mirror, and its releases page had none of the zips. A pull mirror syncs code and tags, not releases. Both URLs 404 to the unsigned browser pane.

**Decision 2026-10-23 (walker):**
- Recreate BMONEY/gabagool_factory as an ORDINARY repo.
- Publish every release to both sites with `tools/publish_release.py` (root commit, 2026-10-23):
  - `python tools/publish_release.py factory-vX.Y.Z --zip <zip> --notes docs/releases/factory-vX.Y.Z.md`
  - `--backfill` copies each GitHub release the forge lacks. The walker chose a backfill of all of 1.36.0-1.41.0.
  - The forge's copy of each zip is downloaded back and held to the sha256.

**Waiting on the walker:**
- Recreate the repo.
- Push main to it once by hand (`git push https://forge.internal.vaultinteractive.net/BMONEY/gabagool_factory.git main`), so Git Credential Manager stores their forge username and access token.
- Add the script to `.claude/settings.local.json`'s allow list beside the gh entries.

**Never handle the token:** the script reads it from GCM and sends it only in a header.

Related: [[github-push-and-releases]].
