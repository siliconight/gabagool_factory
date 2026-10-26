# The bake's quality, and the box truck's blotches (roadmap 224)

**Question.** Cold run 9219 found the box truck's side blotchy at midnight.
- **Where:** a large pale face in the moon's shadow, lit only by the bake's
  bounce.
- **How much:** luma runs 1 to 6 of 255, p5 to p95 after an 8 px blur.
- **Whose blotches:** with the lightmap switched off the face is black all
  over, so they are the bake's.

Level Factory bakes at `LightmapGI` quality 0, Low (`light_bake.QUALITY`). Do
the blotches go at a higher quality, and what does that cost?

**Answer: no. The quality is not the lever.** Medium and High each move the
face's p95 from 6 to 5 and leave the blotches where they were. They cost
+24% and +137% of the editor's bake time.

## How it was measured

- **Re-bakes:** `bake_quality.sh` re-baked cold run 9221's walk copy of
  club_block_014 three times, through `tools/lux_rebake.py --bake-quality Q`.
  - Each used Level Factory's own `light_bake.bake()`, Lux's preset and the
    shipped spawned set, with only `QUALITY` changed.
  - Each report records the dial it set. Quality 1 reads
    `"bake_quality": {"set": 1, "was": 0}`. `light_bake` formats its bake
    scene from `QUALITY` at bake time, and the editor's bake time rose with
    each step, so the dial is the one being read.
- **Frames:** each copy was shot at the truck's side station,
  `truck_side:-31.9,1.7,-4.5,-39.9,1.7,-4.5`.
- **The measure:** `blotch.py` reads luma over the box's face, the rectangle
  9219's notes measured, after an 8 px blur.
- **The control:** quality 0 is Level Factory's own, so its copy must
  reproduce the shipped frame. It does: p5 1 and p95 6, as 9219 measured.
  9219 gave the median as 2 and this reads 1; that is one level of 255 on a
  different run of the same level.

| quality | editor's bake, s | p5 | p50 | p95 | spread |
|---|---|---|---|---|---|
| 0, Low (Level Factory's) | 94.1 | 1 | 1 | 6 | 5 |
| 1, Medium | 117.0 | 1 | 1 | 5 | 4 |
| 2, High | 222.7 | 1 | 1 | 5 | 4 |

**What `truck_side_by_quality.png` shows** (`sheet.py`):
- the same rectangle at each quality, brightened 20 times so luma 1 to 6 can
  be seen at all. At the shipped exposure the face is near black;
- the same blobs in the same places at all three. A sampling artefact would
  shrink with more rays, and these do not, so they are a property of what
  the bake is given;
- what the bake is given: `MAX_TEXTURE` 4096 on one layer, the denoiser on,
  and no texel scale set.

## What was not measured

- **Texel density.** Neither `LightmapGI.texel_scale` nor the truck's
  `lightmap_size_hint` was moved. Large texels, interpolated and then
  denoised, would draw exactly this kind of low-frequency blob.
  - It is the next lever.
  - It is priced in lightmap memory, not in draw calls.
- **The denoiser off.** That would show whether the blobs are its smoothing
  of a coarse estimate.
- **Whether anybody sees them in play.** At the shipped exposure the face
  reads 1 to 6 of 255.

## The wall's blotches, 2026-10-25 (the walker's walk of cold run 9386, finding 2)

**Question.** The office back room's north wall reads mottled -- soft dark patches a metre or two across -- and the
walker: "textures have visible seams and it doesn't look as continous as it could be". The two levers this item left
open after the quality was ruled out: the texel density and the denoiser.

**Measured** (`wall_blotches.sh`: cold run 9391's walk copy re-baked by `tools/lux_rebake.py` three ways, each shot
from the `shelf` station square on the wall; `blotch_index.py`, the band between the bookshelf's top and the ceiling,
the plaster's grain blurred away, sd over mean; `wall_blotch_index.out.txt`, `wall_rebake_ctrl_tex2_nodn.webp`):

| arm | bake.exr | index (lower is smoother) |
|---|---|---|
| control (Level Factory's own bake, Low) | 54.9 MB | 0.293 |
| `--texel-scale 2` | 170.3 MB | 0.338 |
| `--denoiser off` | 63.9 MB | 0.329 |

Both levers make it WORSE, not better: three times the texels for the same rays is noisier per texel, and the
denoiser was already taking some out. The frames differ (336,750 and 371,215 pixels past 8 codes from the control),
so the bakes are real. Bake seconds were not read: another job shared the machine.

**The blotches are not the bake's.** The same wall with the bake switched off, under the inspection light (cold run
9388's frame, `wall_bake_off_inspect_9388.webp`), shows the same mottle in the same places: it is the plaster's
albedo -- Pixelcoat's concrete skin, its grime and stains -- world-projected, so continuous across every joint, and at
that contrast read as patches. The lever is that skin's stain scale or contrast, a look for the walker to call, not
anything in the bake. Level Factory keeps its bake as it is.
