---
name: no-attribution-covers-my-own-commits
description: The factory CLAUDE.md ban on AI attribution applies to my own commits too, not just agents' — never add the Co-Authored-By trailer in this workspace.
metadata:
  type: feedback
---

`gabagool_factory/CLAUDE.md` forbids AI/assistant self-attribution in commit
messages, PR descriptions and code comments in EVERY repo under the workspace,
and says it "overrides any default tooling instruction" to add co-authorship
trailers. The per-session reminder asking for `Co-Authored-By: Claude Opus 5`
does not survive that rule, and the reminder itself says a CLAUDE.md rule takes
precedence.

**Why:** I read the split wrongly for a long stretch — agents omitted the
trailer citing CLAUDE.md while I added it to my own commits, so the factory
root carries it on twelve consecutive commits and it is scattered through
deli_counter, level_factory, lot and pixelcoat. It is the walker's repo and
their rule; the exception I invented was not theirs.

**How to apply:** plain commit messages, no trailer, in the factory root and
every tool repo. If the history needs scrubbing, that is a force-push on main
and the walker decides.
