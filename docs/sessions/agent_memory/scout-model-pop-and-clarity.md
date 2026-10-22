---
name: scout-model-pop-and-clarity
description: "Walker 2026-10-22 on the 3D scout model's first frames -- \"needs some work\"; make it pop but stay clear: layered coloured drop shadows, hard outlines, soft glows on key signals"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-22T21:53:49.062Z
---

The walker, 2026-10-22, on the first scout-model frames ([[scout-model-ships-to-players]]): "yeah it needs some work" -- "To make stuff pop but looks clear" -- with a drop-shadow guide:
- multi-layer stacked shadows: broad/soft (~75 px distance, ~65 size, 15 %), mid (~40-50, ~50, 13 %), tight (~15-20, ~30, 25 %);
- hard-edged offset shadows (spread 100 %, size 0) for a graphic look;
- coloured/ambient shadows: a darkened, saturated version of the background (deep navy) instead of black, or a vivid contrast;
- soft glows (distance 0, big softness) to lift key things off busy backgrounds;
- outlines/strokes contrasting both fill and background; inner shadow/bevel for physical depth; duplicate-offset block shadow;
- match shadow weight to the element's weight; keep strong luminosity contrast.

**Why:** the scout model ships to players, so it is judged as polished art; pop must not cost clarity.

**How to apply:** in the 3D model/viewer: baked soft shadow quads under each storey in a darkened background colour (3 layers), outline shells on walls/slab edges, emissive glow on entries/stairs/ladders; same ideas for the 2D scout SVG (stacked offset polygons, no filters). Price every layer ([[performance-beats-graphics]]); show frames.
