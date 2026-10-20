---
name: target-minutes-is-not-a-hard-rule
description: "Walker 2026-10-07 -- target_minutes is not a hard rule yet; a real level length must count fighting, drilling/acquiring the score, and more"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-07T18:38:35.899Z
---

The walker, 2026-10-07: "target minutes is a tough metric for us now,
because it should account for fighting, the 'drilling' or acquiring of the
score time, and other. So not a hard rule now."

**Why:** since Level Factory 0.153.0 Lot's pacing estimate reads the
brief's window and counts a heist's travel, and every level reads about
3 min against 25-35 ("likely TOO SHORT"): the estimate counts travel, setup
and one objective's 120 s, and nothing for combat.

**How to apply:**
- Keep `LOT_PACING_OUTSIDE_TARGET` non-blocking; never gate on it.
- Read the estimate as a structural floor, not a session length.
- A real session estimate needs a combat term and real score-acquisition
  times (e.g. Deli Counter objective `duration`s, drills at 90 s) -- not
  built; roadmap 200.
