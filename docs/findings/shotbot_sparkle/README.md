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

## What would separate the two (proposed)

Judge connected regions, not a count. A z-fight is a contiguous region, many
pixels across. Sparkle is single pixels and short runs. The gate could
measure, for example, the largest connected region of changed pixels, or
the share of changed pixels that sit in regions above some size. It would
FAIL on that, and report the scattered remainder as sparkle, a finding of
its own rather than a verdict of z-fighting.
