# The walk's jitter gate reads texture sparkle as z-fighting (roadmap 225)

**Question.** Level Factory 0.171.0 let the walk preview's shot bot see again.
It had been photographing under the shader warm-up's black cover. Seeing
again, it FAILED two of cold run 9222's ladder stations on jitter, over its
2.0% gate:
- **Ladder_ladder_0_base:** 3.60%;
- **Ladder_ladder_1_top:** 2.33%.

Its failure message says "coplanar surfaces are fighting for the depth test
here". Is that what these are?

**Answer: no. Every changed pixel is a scattered single pixel over textured
surfaces, and none of them form the solid block a coplanar pair makes.** The
gate's one number cannot tell texture sparkle from z-fighting.

## Measured, 2026-10-10

**The probe** (`make_pair_probe.py`) copies the preview's `shot_bot.gd` to
`shot_bot_pair.gd`, which also saves each station's second frame, the one
1 mm away. It was run over 9222's preview with `mission.tscn`, as `walk`
runs it. The verdicts are in `pair_out.json`: the same two stations FAIL at
3.60% and 2.35%. The jitter is a little different from run to run.

**`jitter_map.py`** paints every pixel that differs by more than the shot
bot's `DIFF_TOL`, 12 of 255, red over the first frame, dimmed. It also says
where the pixels fall:

| station | changed (of 230,400) | by fifth of the height, top first |
|---|---|---|
| Ladder_ladder_0_base | 10,319 (4.48%) | 49%, 27%, 7%, 7%, 10% |
| Ladder_ladder_1_top | 5,988 (2.60%) | 51%, 15%, 15%, 8%, 12% |
| Ladder_ladder_0_top (passes) | 2,157 (0.94%) | 0%, 0%, 40%, 13%, 46% |

The map counts every pixel, where the gate samples every second one, so the
percentages differ from the gate's.

**What the maps show** (`map_Ladder_ladder_0_base.png`,
`map_Ladder_ladder_1_top.png`):
- the changed pixels lie as a fine speckle and short horizontal streaks over
  the drop ceiling's acoustic tiles, which is most of the top two fifths;
- the near wall's texture and the floor carry the same speckle;
- a few rungs of the ladder carry it at their edges;
- no surface carries a solid red region.

A coplanar pair would flip as a block, where one face wins the depth test
over an area at one camera and the other face wins at the next.

**Why speckle, read and not measured.** A 1 mm move, at the 1.5 to 3 m these
surfaces sit from the camera, shifts their image by a small fraction of a
pixel. Under bilinear filtering that changes a pixel by that fraction of the
texture's local contrast. On a high-contrast, fine-grained texture, such as
the acoustic tile's speckle seen at a grazing angle, the change crosses 12 of
255. The gate was calibrated on a package with no such ceiling: "the worst
honest station measured 0.68% (edge aliasing along a ladder's rungs)", the
comment beside `JITTER_FAIL_PCT`.

## What is not known

- **Whether the sparkle shows in play.** It is measured at 640 x 360 from a
  still camera. Moving through the room at full resolution, the same texture
  would shimmer if its mips or its filtering do not hold it. That is a
  question about the ceiling texture's import and the renderer's anisotropic
  filtering. It is not answered here.
- **Whether any coplanar pair hides inside the speckle.** The maps show none,
  but they were read by eye.

## What would separate the two (proposed first, refuted, kept)

*As first proposed:* "Judge connected regions, not a count. A z-fight is a
contiguous region, many pixels across. Sparkle is single pixels and short
runs."

## A control, and what it refuted (2026-10-10, before 06:10)

**The control.** `zfight_control.tscn` is two 8 m quads, red and blue,
0.01 mm apart. That is inside the depth buffer's precision, the textbook
fighting pair. It was run through the shot bot in 9222's preview project.
- The first version used `PlaneMesh`, which lies flat. The exterior station
  stands at 0.6 of the scene's height, which is 0, so it saw the planes edge
  on and failed for "a single colour".
- `QuadMesh` stands upright and faces the station.

All the numbers below are in `measured.txt`.

**Refuted: judge the largest connected region.** `regions.py` joins changed
samples on the gate's grid:

| | largest region (samples) | share of changes in regions of 16 or more |
|---|---|---|
| the control | 54 | 54.5% |
| 9222's worst station | 28 | 3.8% |

- A gate at 64 samples, a 16 x 16 px patch, was written into `shot_bot.gd`
  and run. It **passed the control** at region 54.
- A precision-level fight breaks into stripes and fragments, not one block.
  Region size separates it from sparkle by less than two times, in the wrong
  place.

**Refuted: move the near plane instead of the camera.** This is
`make_near_probe.py`, near times 1.02.
- It leaves every pixel's position and texture sample where it was, so
  sparkle cannot appear. 9222's stations read 0.00% to 0.02%.
- But it flipped **0** samples on the control as well. A pure depth
  requantization keeps the two quads' order.

**Kept: the size of each flip.** `deltas.py` measures how far each changed
sample moves:

| | median change (of 255) | changes over 64 |
|---|---|---|
| the control | 255 | 100% |
| 9222's four interior stations | 16 to 19 | 0.8% to 7.6% of their changes |
| 9222's exterior (7 changed samples in all) | 42 | 1 of the 7 |

- A pixel that z-fights swaps between two surfaces' colours. One that
  sparkles shifts by a blend of one texture.
- Counting changes over 64 as a share of the frame gives 2.02% on the
  control and 0.00% to 0.12% on 9222's stations.
- A gate at 0.5% sits about four times from each.
- Run as `shot_bot.gd`'s verdict: **the control fails (fighting 2.02%), and
  all five of 9222's stations pass**, the two former failures noted as
  sparkle.

That is Level Factory 0.172.0.

**What it gives up: a fight between two surfaces whose colours are within
64 of each other.** A person can barely see that fight.

## Does the ceiling sparkle in play? Read off 9222's package, 2026-10-10

**Yes, and it is the look's own sampling, not a defect of this ceiling.**
- **The tiles:** `M_Skin_ceiling_tile_delco_1997` in Zoo's `ceiling_delco_1997_13_*`
  models, a 256 x 256 skin
  (`lot/deli_a01/art/zoo/_tex/ceiling_tile_delco_albedo_5bdf9004.png`).
- **Its sampler:** magFilter 9728, NEAREST, and minFilter 9984,
  NEAREST_MIPMAP_NEAREST. The drywall skin of the other ceilings samples
  the same way.
- **Its import:** mipmaps generated, lossless (`compress/mode=0`).
- **What follows from nearest sampling.** Each pixel takes one texel, so
  any sub-pixel camera motion swaps whole texels on a fine-grained skin.
  That is the speckle in the maps, and a camera moving at full resolution
  makes the same swaps every frame.
- **Why it samples that way.** Pixelcoat's pixel skins ask for `nearest`,
  and Zoo samples them so by design.
- **What would change it:** filtering the skins `linear`, as the business
  signs have done since Pixelcoat 0.62.0. That is a look decision, in the
  direction of "Realism replaces the retro look". It is the walker's to
  make and to price, not a fix to land here.
