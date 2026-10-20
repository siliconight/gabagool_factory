---
name: realism-replaces-retro-look
description: "Walker 2026-10-02: 'looks like it is made with a 90s GPU' -- replace the retro look with better/more real, without destroying performance. Trial first on ATM, video poker, register."
metadata:
  type: feedback
---

The walker, 2026-10-02, on the animated-screen test frames: "this looks like it is made with a 90s GPU, what can we do to make these things look better/more real without destroying performance?" Asked whether that replaces the 2026-09-13 retro faceted style or cleans it up, they said: "replace the retro look, do the first three as a trial".

The first three: (1) hero surfaces painted at 2-4x resolution with a smooth typeface and filtered sampling; (2) shading baked into the art -- corner darkening, edge highlights, grime, a gradient on a screen; (3) bevelled edges, curved CRT glass, rounded cabinet corners. Trial on the ATM, video poker cabinet and cash register, with before/after frames and the texture-memory figure, before rolling out.

**Why:** the chunky pixel textures, flat faces and hard boxes read as dated to them, not as a deliberate style.

**How to apply:** this SUPERSEDES [[walker-wants-retro-style-with-real-structure]] on style (its other half still holds: real structure, and a half-finished technique reads worse than a clean one -- show a frame before calling a look done). Still bound by [[performance-beats-graphics]]: draws are the budget, triangles are not; no screen-space post effects. Offered and not yet chosen: per-material gloss/normal maps, fake glow halos, baked lighting. Looks the walker has liked (the gas station "as a start", the club's posters) get the new treatment added, not reworked blind.

**Status 2026-10-02:** trial SHIPPED as Zoo 1.46.0 (video poker, ATM, cash_register species, and the counter till in `counter_register.py` -- the one stores actually stand). The walker on the before/after frames: "looking much better". Tools: `core/smooth_type.py`, `core/paint.py`, `core/machine_parts.py`. Costs measured in a scratch project: draws unchanged except service counter 7 -> 8; texture memory +1 to +3.6 MiB a prop uncompressed. Lessons: check a hairline display face on a frame (first cut was dimmer than the pixel digits); a painted body must be colour-matched to the old frame, not converted from the flat material's linear colour. Open: frame time in a level, import compression, the extra counter draw, rolling out to other species.

**Rollout log (2026-10-02, later):** Zoo 1.47.0 lottery dispensers (first prop built to the authorship guide's brief), 1.48.0 cigarette rack + machine (rack stocked in blocks), 1.49.0 the owner pass (Aileron/Vegur/MFB Oldstyle vendored as Pixelcoat 0.55.0; `smooth_type.OWNERS`; screens back to the pixel face via `Img.pixel_text` -- walker: "keep the pixel screen"), 1.50.0 candy rack (stocked by the box, header cards), 1.51.0 cooler wall (products in metres, stocked by the case). Level Factory 0.128.0 ships filtered textures VRAM-compressed; the flicker is gone. In-level A/B: frame time within the instrument's noise; draws back to pre-look level after the dispensers moved into the till's image. Cold runs 9135/9136 on `gas_block_001`, zero. Still pixel-look in the store: frozen-drink machine, sandwich case. Then the "alive" queue (unsteady light next). Open walker calls: the candy rack's 1 m repeat; cooler glow strength (flattens the new shading).
