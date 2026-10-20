---
name: levels-feel-static-make-them-alive
description: "Walker 2026-10-02 after walking 9131: gas station 'looks pretty good as a start' but feels frozen -- lit screens (ATM, video poker, register) never change. Wants levels to feel alive/dynamic."
metadata:
  type: feedback
---

The walker, 2026-10-02, after walking cold run 9131's gas station: "looks pretty good as a start for sure", then: "there is a relatively frozen/static feeling, where the lights in the atm, gambling machine, and cash register are just fixed with nothing dynamic/alive about them.... maybe something to lean into is how to make levels and buildings and setting feel alive/dynamic".

**Why:** every lit surface is a fixed emissive texture; nothing in a level moves or changes over time.

**How to apply:** treat "alive" as a direction to lean into, starting with lit screens. The performance rule shapes the how: motion must come from the shader clock (UV steps, flicker, scroll on the existing backlit `_Face` materials) -- no per-frame CPU that scales with prop count, no extra draws, no extra lights; price it the way the CRT screen-roll was priced. Keep the gas station's look (the walker likes it); add life to it, do not rework it. See [[performance-beats-graphics]], [[walker-taste-overrides-art-budget]].

**Queued 2026-10-02 (the walker: "queue the screens next, after the video store"):** animated screens on the ATM, video poker cabinet and cash register, shader-clock driven, priced. Then offered and not yet chosen: flickering tubes/neon, small moving parts (fan, slush paddle, roller grill), world changes (signals, cars), ambient sound.

**WHOLE LIST APPROVED 2026-10-02 (the walker quoted all four items and said "THIS"):** in order -- (1) screens that run (ATM, video poker, register); (2) light that is not steady (a flickering tube, a neon letter dropping out, the pump's price shimmer -- on the glowing surface, not the light); (3) small things that move (ceiling fan, slush paddle, roller grill, a swinging sign), shader-driven; (4) a world that changes on its own (streetlight cycling, a traffic signal that changes, a car passing). Each one priced and shipped separately. Item 4 touches gameplay (signals, moving cars are collision and cover): show the walker the specific design before building each piece.
