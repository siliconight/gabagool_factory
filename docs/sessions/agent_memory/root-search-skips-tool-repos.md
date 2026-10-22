---
name: root-search-skips-tool-repos
description: "The factory root's .gitignore excludes every tool repo, so Grep/rg/git grep from the root silently skip lot, level_factory, deli_counter, zoo, lux... -- search inside each repo"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-22T12:59:28.460Z
---

A search started at `C:\Projects\gabagool_studios\gabagool_factory` (Grep tool, rg, `git grep`) does NOT see the tool repos: the root `.gitignore` excludes `lot`, `level_factory`, `deli_counter`, `zoo`, `lux`, `patina`, `pixelcoat`, `dispatch`, `lasertag`. It returns no error, just fewer hits. Found 2026-10-22 by one of the narrowed-audit auditors mid-run ([[open-work-2026-10-09]]).

**Why:** "a grep found nothing" is the evidence for every "not built" claim, so a root search makes undone-looking work out of done work, silently -- the checker-that-cannot-see-its-field defect CLAUDE.md warns about.

**How to apply:** search each tool repo with `path` set to it (or `git -C <repo> grep`); tell any subagent the same in its brief. Treat an absence found from the root as unproven.
