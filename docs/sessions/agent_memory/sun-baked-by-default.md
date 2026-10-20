---
name: sun-baked-by-default
description: "Walker 2026-10-12 chose 'bake the sun by default' (roadmap 243): Lux 0.76.0/0.76.1, cold 9265 proved it (-1,854 draws, -3 ms); the backdrop is outside LF's bake so it takes the sun unshadowed; which tier is still the walker's"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-12T22:31:53.869Z
---

The walker, 2026-10-12, shown the four Lux tiers on cold run 9264's level
(High 2,642 draws a heading / Low 538) and then the High look without the
sun's live shadows: "Bake the sun by default". Lux 0.76.0 does it in
`_apply_sun_mode`: static in the editor (so LF's bake carries the sun),
static + unshadowed at run time while a lightmap shows, dynamic + shadowed
when none does (no lightmap, the power cut, baked lighting off). 0.76.1
fixed its comment only. Cold run 9265 (0 interventions) proved it:
-1,854.4 draws a heading, p95 -3.03 ms median, headings over 16.7 ms 5 -> 1;
frames = arm B2 within re-bake noise (docs/findings/lux_tiers/).

**Why:** the sun's live shadows were 70 % of a level's draws and 45 % of its
frame -- the largest single cost ever measured here.

**How to apply:** what the lightmap does not hold takes the sun with NO
shadow: anything that moves, and anything outside LF's `bake.tscn` (the
presentation scene only) -- notably `site_backdrop.tscn` (269 rowhomes +
water tower), which mission.tscn loads beside it. At a low sun that shows
(corner's far row lit, elev_N homes lit, the backdrop's long shadows gone).
Levers queued for the walker, none taken. Still the walker's: which TIER a
package runs. A light's shadow flag does not change the bake (arms B = B2);
I filed the opposite from an impression -- put every arm's numbers in a
table before filing a refutation. Related: [[light-tools-breakdown-and-check]],
[[lighting-spec-filed]], [[performance-beats-graphics]].
