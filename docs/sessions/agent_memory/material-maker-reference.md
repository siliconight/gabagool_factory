---
name: material-maker-reference
description: Material Maker docs URL and CLI syntax; the walker wants it evaluated as a Pixelcoat backend/mix if it improves textures without runtime cost
metadata: 
  node_type: memory
  type: reference
  originSessionId: 4bb794c9-c366-4613-95bd-3c61e9a0d0f9
  modified: 2026-09-14T22:17:10.241Z
---

Docs: https://rodzill4.github.io/material-maker/doc/ (command_line.html, export.html). Material Maker (RodZill4, MIT) is a STANDALONE node-graph PBR authoring app built on Godot, not part of Godot. Files are `.ptex`; export writes PNG maps plus, for the Godot target, a `.tres` material. CLI: `material_maker --export-material --target Godot -o <out_dir> <files.ptex>` (wildcards ok); no size flag on the CLI, no documented headless flag (it opens a Godot window/GPU context).

SPIKE VERDICT (2026-09-14, scratchpad mm_spike, Pixelcoat branch material-maker-spike): do not integrate as a build backend. MM 1.7 CLI forces 2048 px, crashes (0xC0000005) on any map with no texture sampler and on every buffer node (normal_map/bevel/occlusion), needs Vulkan (headless/GL crash), ~9 s per material vs 0.1 s; bit-exact on the RTX 2060. Its real gain (joint-width variation on a bond, SDF vocabulary for printed figures) is two Pixelcoat primitives. Retro look = grain BEFORE posterize, not posterize alone. Zoo binds no normal maps on walls, so height work reaches no pixel.

The walker (2026-09-14) asked whether to mix it with Pixelcoat "if it improves our textures, without compromising performance". Runtime cost is texture size, not the generator; the fit is as a Pixelcoat backend whose output still passes Pixelcoat's posterize/quantize, tiling and art-standard audit. See [[walker-wants-retro-style-with-real-structure]].
