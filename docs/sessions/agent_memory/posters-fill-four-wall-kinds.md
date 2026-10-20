---
name: posters-fill-four-wall-kinds
description: "Walker chose (2026-09-29) posters for strip club interiors, bar interiors, exterior alley walls/poles, and store windows/walls; guides in their Downloads set the art direction."
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-09-29T23:38:51.862Z
---

The walker wants procedural posters to fill walls in four places, chosen 2026-09-29: strip club interiors, bar/tavern interiors, exterior alley walls and utility poles, and store windows and walls. The card shop keeps its collector promos.

Their three guides are the art direction, committed in the root repo at `docs/reference/` with an index, `docs/reference/POSTER_GUIDES.md` (what to adopt, what GL Compatibility and the draw-call rule forbid, the measured baseline). The art guide's thumbnail / grayscale / blur tests are meant to become an instrument run on every generated poster.

**Why:** the existing Zoo `poster` was measured against the guide on 2026-09-29 and failed four of seven checks: one composition for every poster, identical neighbours (art keyed per size+variant, not per placement), titles unreadable at 5 m, no print character, and one texture plus material per poster (the shared atlas Zoo 0.98.0 named was never built).

**How to apply:** a poster RUN is one Zoo `poster_wall` module (one atlas, one material, one draw) -- that answered the atlas rule; placements are DC fixtures indoors and Lot HUNG slots outdoors (never Lot `cover`). The walker's later calls: club art DN3D-style with whites/blacks for depth, monogram italic titles, blacklight on club sheets (paper elsewhere); a layout must set its title at display size (the typography guide), never shrink. Lewd content: suggestive never explicit, adults only, never in youth-coded places (card shop), no real protected group as the punchline, invented Delco names only. Godot decals are out (GL Compatibility), so posters stay planes. See [[fake-delco-brands-funny-and-crass]], [[performance-beats-graphics]], [[references-fill-blanks-not-override]].
