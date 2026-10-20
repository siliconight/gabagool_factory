---
name: performance-beats-graphics
description: Multiplayer online game, so frame cost outranks looks; present the tradeoff rather than refusing outright, and optimize later on runtime data.
metadata:
  type: feedback
---

The game is multiplayer online, so the walker will "always choose performance
over look/graphics... we don't need more bottlenecks where things could fall
over" (2026-09-16). But not binary: "you can present the tradeoffs when you
think we are leaving something on the table we could have... we lean towards
performance when we can", and "we can always optimize later once we have better
data from runtime tests."

**Why:** a look costs one machine a few ms in a walk and costs every client in a
session, on unknown hardware, every frame. A dropped feature costs a look the
walker may have wanted — so the call is theirs, with a price attached.

**How to apply:** price a look before shipping it (LF 0.89.0 priced the CRT pass
on/off with a control; Lux 0.38.0 refused sun shadows on measured cost). When
the cheap version loses something real, ship the cheap version AND say what the
expensive one would have bought, with the measured gap. Never refuse a look on
an unmeasured guess — measure, then let the walker choose. Ranks below
[[walker-taste-overrides-art-budget]], which is about chroma, not frames.
