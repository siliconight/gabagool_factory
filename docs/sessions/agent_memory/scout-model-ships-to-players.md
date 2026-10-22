---
name: scout-model-ships-to-players
description: "Walker 2026-10-22 -- the scout view must become a polished, artistic 3D model players rotate 360 degrees to scout buildings; SVG scout view (DC 0.258.0) is \"ok for now\""
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-22T21:07:30.621Z
---

The walker, 2026-10-22, after seeing Deli Counter 0.258.0's scout SVG: "its ok for now, but i want to make it look more polished and artistic so it could ship to players....They can scout out the buildings and rotate the schemas in a 360 degree way".

**Why:** scouting a building before the job is a player-facing feature, not a review aid -- so it is judged like art (polish, deliberate look) and priced like runtime content (multiplayer, GL Compatibility, every client) ([[performance-beats-graphics]], [[exploded-axonometric-view]]).

**How to apply:** this is roadmap 295's map mesh, carrying 296's signal set (walls, doors/windows, stairs, ladders, holes; no furniture/labels). The factory ships a per-building scout MODEL plus a reference viewer scene; the in-game screen stays the game's. Show the walker style frames and let them pick; price the viewer (draws, one material with vertex colour per [[CLAUDE.md]] colour rule) before shipping.
