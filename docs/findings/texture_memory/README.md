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

## RETRACTED, KEPT ABOVE: the attribution. Measured 2026-10-13 on cold run 9273's package

**What was wrong.**

- **The sky is not resident.** At scene load the resource cache holds 457 of the package's 602 image
  files, and **none of the 140 under `runtime/skymint`** (`resident_9273.txt`). SkyMint loads two
  skyboxes, the day's and the night's, builds each into a Cubemap from its faces' images, and lets the
  face textures go (`skymint.gd`, `_assign_textures` and `_load_cube`).
- **The census counted the lightmap as nothing.** Pillow cannot open `bake.exr`, so it is a row of 0 x 0.
- **The two totals matched by accident.** The census's sky-inclusive estimate came out beside the engine's
  total, but it counted textures that are not resident and missed the largest one that is.

**The instruments.**

- `texture_resident_probe.gd` frees parts of a loaded level and reads the monitor after each.
  - The monitor does not come down with them: 314.7 MiB loaded, and 266.9 MiB with the whole scene freed
    and no image file left in the cache. Shrinking either shadow atlas afterwards moves nothing.
  - So a free is not a measurement here.
- `texture_split_probe.gd` builds the mission as its entry script builds it, in a fresh process an arm,
  with one part left out before it enters the tree.
  - It reads once the Warmup has finished; read mid-sweep, a monitor is the sweep's.
  - THE CONTROL: the package's own `mission.tscn` and the rebuild read the same 314.6 MiB, and the mission
    read the same twice.

The arms, verbatim in `split_9273.txt`:

    arm                                       texture   the part's share
    empty (no scene: the window's floor)        5.7
    mission (the package as it runs)          314.6
    full (rebuilt, the control)               314.6
    -bake (the lit site: Lux, the lightmap)     7.8     306.8
    -restaurant_row_001_dressing              313.3       1.3
    -site_backdrop                            313.9       0.7
    -lightmap (its LightmapGI only)           293.3      21.3
    -warmup (no sweep: nothing renders)        57.3     257.3
    -patlas / -datlas / -shadows              314.6       0
    mission, reflection_size 64 (override)     73.5     241.1

**The reflection atlas is 82 % of it.**

- **What forces it:** the Warmup's sweep, and in play the player's camera, renders the level's 23
  ReflectionProbes. Every one is Lux's, an interior room's ambient, updating once.
- **The default atlas:** Godot's project default holds 64 probes of 256 x 256 x 6 faces in half-float.
  That is 192 MiB, 256 with mips: the warm-up's 257.3, and the 241.1 the 64-pixel override takes away
  (64 x 6 x 64^2 half-float with mips is 16 MiB).
- **How it acts:** the atlas belongs to the window, not the level, which is why it outlived the freed
  scene. The shadow atlases are none of it.
- **What is left:** the lightmap is 21.3 MiB (1024 x 1024 x 16 layers, BC6H), and the level's own
  textures about 30 MiB. The `-warmup` reading is that, plus the lightmap, plus the 5.7 MiB floor.

**What it does not say.**

- **Fewer slots than probes is not a lever:** at 4 slots for 23 probes the engine raised
  `Condition "rpi->atlas_index < 0"` 113,494 times and the run never finished its warm-up in 600 s
  (`split_9273.txt`, its last lines). The atlas must hold every probe.
- **Nothing here judges the look:** a probe's resolution is the sharpness of a room's reflections and
  ambient, to be seen in frames before the atlas shrinks.

**The levers, revised.**

1. **The reflection atlas, sized to the level.** The package's `project.godot` already carries one
   setting derived from its own content -- `max_renderable_lights`, the package's light count. The atlas
   count is the same kind of number: the probe count, rounded up. Its size is a look to price at
   interior stations: 32 slots of 256 are 128 MiB, of 128 32 MiB, and of 64 8 MiB.
2. **Compression of the level's own textures:** now a lever on about 30 MiB, not on half a gigabyte.
3. **The sky lever is withdrawn:** the sky is not resident.

## The face size, priced (2026-10-13, `atlas_frames.sh`)

Cold run 9273's package was rendered four times, each a copy with the atlas's face size set in an
`override.cfg`. The count stayed at the default 64, which holds the 23 probes. The four copies:

- `s256`: the package as it ships.
- `s256b`: the package again. This is THE CONTROL, the floor every difference is read against.
- `s128`: a 128-pixel face.
- `s64`: a 64-pixel face.

Each was shot by `look_shots.py` at its derived stations and twelve interiors (`in_<skin>`, rooms facing
an interior wall, where the probes are), then read by `texture_split_probe.gd -- mission`. All twenty
shots' diffs against `s256` are in `atlas_frames.log`.

    texture memory after the warm-up:   256: 314.6   256b: 314.6   128: 121.8   64: 73.5   (MiB)
    pixels moved, of each frame:        past 8 codes            past 32 codes
      control (256b)                    0.000 - 0.064 %         at most 0.015 %
      128                               0 - 1.565 %             at most 0.001 %
      64                                0 - 2.680 %             at most 0.019 % (spawn; control 0.015)

The largest move at either size is one drywall room, `in_drywall_delco_1997_2`. Brick rooms do not move
at all, and concrete and drywall rooms move 0.11 to 0.35 %. `atlas_frames.png` is that room and the
most-moved concrete room at 256, 128 and 64; side by side they read the same. The full twelve-interior
sheet is 17 MB and is not kept.

**Shipped as Level Factory 0.198.0:**

- the atlas's count is the package's probe count, rounded up to a power of two;
- its face size is 64.

For 9273's 23 probes that is 32 x 64, an 8 MiB atlas. **What 128 or 256 would buy back:** a sharper
reflection on a glossy surface. The interiors measured are rough. The face size is one constant,
`godot_project.REFLECTION_ATLAS_SIZE`.

The first cold run after it reads its own package with `texture_split_probe.gd`.

## In the price (2026-10-13, Level Factory 0.199.0; `perf_memprobe.py`)

Level Factory 0.199.0's fixed-station harness reads the engine's texture, buffer and video memory once
every station is warm, and its runner prints them beside the passes, so every price carries the package's
memory. On an imported copy of cold run 9276's package:

    instrument                                         when it reads                          textures   buffers
    perf_stations_run.py (perf_9276_runner.txt)        every station warm                     76.0 MiB   48.0 MiB
    texture_split_probe.gd mission (split_9276_mission.txt)   after the package's own warm-up, 1 draw   65.6 MiB   48.0 MiB

**When two instruments disagree, one is wrong or they read different things.** These read different
moments. `perf_memprobe.py` writes a copy of the harness's probe that prints at three points
(`perf_memprobe_9276.out.txt`, and two runs before it kept in the 0.199.0 entry):

    the main scene in, 60 frames on                   67.9 MiB
    the probe's camera at the first station, drawn    67.9 MiB
    every station warm                                76.0 MiB

The figures are the same in every run, as built and with the positional shadow atlas at 0 and the
directional at 256 (`--no-shadow-atlases`), so the shadow atlases are not the gap. The window accounts for
about 1.3 MiB: the harness draws 1280 x 720 and `texture_split_probe.gd` Godot's default 1152 x 648, whose
empty window is 5.7 MiB. The rest grows while a camera stands at the stations, and is not attributed.
Buffers are not steady from run to run at one moment: 48.0, 52.0 and 56.1 MiB have all been read after the
warm-up. **The price's figure is the level in play** -- after a camera has stood everywhere a station
stands -- and it is the one to compare between prices.

Found on the way, not fixed: the harness sets `current_scene` before it adds the scene to the tree, and
the engine refuses it (`set_current_scene: Condition "p_scene && p_scene->get_parent() != root"`), so
that line does nothing. Fixing it may change what the package's own scripts see, so it waits for a
change that is priced on its own.
