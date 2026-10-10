# The bake's texel density and denoiser, and the box truck's blotches (roadmap 224, step 2)

**Question.** Step 1 (`docs/findings/bake_quality/`) found the bake's quality
is not the lever: Low, Medium and High leave the same blotches in the same
places on the box truck's shaded side. The next two levers are the lightmap's
texel density and the denoiser.
- **Texel density:** `LightmapGI.texel_scale`, which Level Factory leaves at
  Godot's 1.0. Large texels, interpolated and then denoised, draw exactly
  the low-frequency blobs step 1 photographed.
- **The denoiser:** `use_denoiser`, which Level Factory sets on. Off, the
  frame shows whether the blobs are its smoothing of a coarse estimate.

**Status: the harness is written and checked; the measure has not run.**
`bake_texel.py read` reproduces step 1's face from its frame (p5 1, p50 1,
p95 6) and refuses step 1's reports, which predate the price. The bakes are
queued behind the Lux horizon glow (roadmap 228, step A), so the editor's
seconds are measured on a quiet machine.

## How it will be measured

- **The dials:** `tools/lux_rebake.py --texel-scale X` and `--denoiser off`,
  on cold run 9221's walk copy of club_block_014 (midnight, Delco Night),
  the copy step 1 used. Each report records the dial it set and what the
  bake wrote: `bake.exr`'s bytes, the lightmap's layers and their size, and
  the imported texture array's bytes, which is what the lightmap takes in
  video memory.
- **The control:** Level Factory's bake unchanged (`t1`), which must
  reproduce step 1's control.
- **The variants:** texel scale 2 (`t2`); the denoiser off at scale 1
  (`dn0`); and, if scale 2 moves the face, scale 2 by day
  (`--preset delco_summer_afternoon`) to see what a lit face does.
- **The frame:** step 1's truck-side station, read by `bake_texel.py read`
  over the box's face after an 8 px blur, as p5, p50, p95, mean and sd, with
  a sheet scaled so each face's p95 reads 200.

## Instruments

- `bake_texel.py run <walk copy> <out> NAME=OPTIONS ...`: one re-bake and
  one frame per variant, the copy deleted after each.
- `bake_texel.py read <out> [--sheet SHEET.png]`: the table and the sheet.
