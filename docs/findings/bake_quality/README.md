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
