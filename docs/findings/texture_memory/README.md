# Texture memory: what a package's textures cost, and in what form they ship

**Question.** The walker, 2026-10-11, on a texture explainer that offered
nothing else: "texture memory and compression, worth measuring on a
package". Nobody had. What does one shipped package hold in texture memory
on GL Compatibility, and in what form?

**Instruments.** `texture_census.py` walks a package: every image, its pixels
(Pillow), its bytes on disk, and the `compress/mode` its `.import` sidecar
asks for (the package ships sidecars, not the cache), with two estimates --
raw RGBA8 plus a mip chain, and block-compressed (BC1 opaque, BC3 alpha).
`texture_mem_probe.gd` opens a window (a headless run allocates no texture),
loads `mission.tscn`, waits 90 frames and prints the engine's own monitors
(`Performance.RENDER_TEXTURE_MEM_USED` and its siblings), then quits. Run on
cold run 9245's package twice: a pristine copy imported by `--import`
(`probe_9245_package.txt`) and the walk copy with its player and sky cycle
(`probe_9245_walkcopy.txt`).

**Result, 9245's package (restaurant_row_001, Level Factory 0.179.0).**

    census: 579 images, 100.8 MiB on disk, 108.6 Mpx
            sidecars: 546 lossless (uncompressed in VRAM), 33 vram_compressed
            raw RGBA8 + mips  552.6 MiB      block-compressed  69.8 MiB
    engine: texture 515.6 MiB, buffers 35.2 MiB, video 550.8 MiB
            -- the same on the pristine copy and the walk copy

    by folder (pixels):  runtime/skymint  140 images  73.4 Mpx  67.6 %  373 MiB raw
                         lot/deli_a01      61          5.6 Mpx   5.1 %   28.5
                         cover             38          4.9 Mpx   4.6 %   25.2
                         lot/pharmacy_a01  53          4.9 Mpx   4.5 %   24.9
                         lot/office        55          3.4 Mpx   3.1 %   17.2
                         skins              8          2.9 Mpx   2.7 %   14.7
                         each Empty        19          0.9 Mpx   0.9 %    4.8

**What it says.** The engine's 515.6 MiB is the census's raw estimate less
the mip chains the twenty 2048 x 1024 sky panoramas do not carry: every
texture the package references is resident at scene load, uncompressed. Two
things decide the number. First, the sidecars: 546 of 578 ask `lossless`,
which compresses the file and not the texture; `detect_3d/compress_to=1` on
456 of them would re-import as VRAM-compressed only when an editor detects
3D use, and the `--import` passes the walk and the harness run never trip it
-- the cache carries the `s3tc` form for the 33 that ask `vram_compressed`
and for no other. Second, the sky system: 140 images for every time of day
and variant, two-thirds of the pixels, all resident though one slot's sky is
shown (inferred from the total matching the whole census; not measured per
image).

**What it does not say.** Nothing about bandwidth or frame time (the price
harness measures those, and 9245 read none); nothing about a low-end card
with the game's own assets beside this; nothing about the 1.38.0 package,
which is the same export code and was not measured.

**The levers, to price.** (1) `compress/mode=2` in the sidecars the export
writes for 3D textures: the estimate is 69.8 MiB, a 7.9x cut; the cost is
block artefacts on Pixelcoat's pixel-art packs (4 x 4 blocks over Closest-
sampled texels), to be judged on frames at the fixed stations before it
ships. (2) The sky: only the slot's panorama resident, the rest loaded when
the cycle reaches them. Roadmap 238.
