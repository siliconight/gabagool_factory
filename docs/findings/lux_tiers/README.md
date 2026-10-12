# Lux's quality tiers on one level (roadmap 243)

**Why.** `LuxRoot.quality_tier` is never set by any factory tool, so every package runs Lux's High
tier -- on GL Compatibility, the renderer packages ship on as their low-end target. Asked which tier a
package should run, the walker (2026-10-12): "didn't know we had this... not sure". So the four tiers
were shown, not chosen.

**How** (`tier_frames.py`): one copy of cold run 9264's package (restaurant_row_001), the tier written
on the scene's LuxRoot node and nothing else, rewritten before each tier; each tier shot by
`tools/look_shots.py` at its derived cameras and three on the main street, and given one pass of Level
Factory's station harness (53 headings, GL Compatibility, the RTX 2060). One pass a tier and no control
pass: the draw counts are exact (they repeat), the frame times indicative only.

| tier | shadowed lights | sun shadows | post-fx, glow, film | draws a heading, mean / worst | p95 frame, median / worst |
|---|---|---|---|---|---|
| High (what ships) | 12 | on | on | 2,642 / 5,740 | 7.73 / 20.09 ms |
| Medium | 8 | on (45 m) | on, no volumetric fog | 2,457 / 5,159 | 7.21 / 18.71 ms |
| Low | 4 | off | off | 538 / 2,005 | 4.18 / 16.81 ms |
| Compatibility | 4 | off | off, no dithering | 538 / 2,005 | 4.32 / 15.70 ms |

**What the frames show** (`tiers.png`, a row a station, the tiers left to right). High and Medium read
alike: dark and contrasty, the sun's shadows and the film look -- and much of the frame crushed to
near-black, the spawn and objective views barely readable. Low and Compatibility read alike: brighter
and flatter, no sun shadows, no post look, every surface readable (the objective's brick wall plain
where High shows black).

## The High look without the sun's live shadows (`sun_variants.py`, `sun_variants.png`)

The walker, 2026-10-12: "yes, test the High look without sun shadows". Lux builds the sun at run time
(`LuxLighting.ensure_sun`, bake mode dynamic), so the lightmap holds only its bounce and its light and
shadows are drawn live. Arms, each from cold run 9264's package (`blue_hour`: the sun 4 degrees up in
the west-north-west, `sun_casters.gd`):

- **control** -- `tools/lux_rebake.py` with nothing changed. Against the shipped High frames: a mean
  difference of 1.6 to 2.4 levels at the six stations, at most 0.07 % of pixels over 16 -- the noise
  floor below. (The tool's docstring records 0.0 at every camera on cold run 9213; here it is near, not
  exact.)
- **A** -- the preset's `sun_shadows` off, nothing re-baked: the live sun lights everything unoccluded.
- **B** -- the sun built BAKE_STATIC and re-baked with `sun_shadows` turned off before the bake.
  **RETRACTED, KEPT:** this bullet said "REFUTED AS A TEST: the lightmapper honours a light's shadow
  flag, so the sun baked unoccluded and B came out as flat as A". B's frames were in no table when that
  was written. Measured since: B and B2 are one picture -- a mean difference of 1.6 to 2.5 levels at the
  six stations and at most 0.01 % of pixels over 16, a re-bake's noise -- and each differs from A by 3.3
  to 11.7. The flag does not change the bake, so B2 was not needed; Lux 0.76.0's comment repeated the
  claim, and 0.76.1 corrects it.
- **B2** -- the sun built BAKE_STATIC and re-baked WITH its shadows, then `sun_shadows` off in the baked
  copy: the lightmap carries the sun and its shadows, and no frame redraws them.

Mean luma (and mean absolute difference from High), 0-255:

    station     High    control         A               B2              Low
    line        37.4    37.4 ( 1.9)     37.3 (10.9)     33.0 (10.9)     39.2 (12.1)
    corner      51.8    51.9 ( 2.4)     57.7 (11.4)     51.6 ( 7.2)     60.2 (13.9)
    up          52.9    52.9 ( 2.4)     57.0 (17.6)     47.1 (13.5)     60.2 (19.3)
    spawn       20.7    20.6 ( 1.6)     25.7 ( 9.3)     18.1 ( 4.5)     27.6 (11.1)
    objective    6.5     6.5 ( 1.8)     15.0 ( 9.9)      6.5 ( 1.8)     18.4 (12.4)
    elev_N      57.3    57.3 ( 2.1)     64.8 (13.4)     63.9 (13.8)     67.0 (16.3)

**Priced** (`sun_price.py`, `price_sun_A/`, `price_sun_B2/`: the shipped package as both controls, 53
headings, GL Compatibility, the RTX 2060):

    the level            draws a heading, mean / worst    p95 frame, median
    High as shipped      2,642 / 5,740                    7.95-8.00 ms (controls apart 0.26-0.37)
    A  sun unshadowed      788 / 2,805                    4.46 ms
    B2 sun baked           788 / 2,805                    4.42 ms   (-1,854.4 draws, -3.56 ms)

The sun's live shadows are the largest single cost measured on a level: 70 % of its draws and 45 % of
its median frame. Baking the sun with its shadows costs nothing at bake time (the editor 63.0 s against
the control re-bake's 67.8). What B2 gives up: anything that MOVES casts and takes no sun shadow -- a
body at dusk throws no long shadow -- and the baked shadows are as soft as the lightmap's texels. (And,
found after the decision, the backdrop: "What the baked sun changes" below.)

A reads as Low with High's post look: the sun's shadows are most of what makes High look like High.
B2 is the nearest to High at four of six stations (the objective within the noise floor) and keeps
High's overall brightness; where it differs, it lights sunlit facades that High's live shadow map leaves
dark -- at a sun 4 degrees up, the bake's traced occlusion and the live map disagree about what is in
shadow, and which is right is a question for the eye, not this table.

**What it means, as far as it goes.** The tier is the largest performance lever measured on a level:
Low and Compatibility draw about a fifth of High's submissions and spend about half its median frame.
What High's extra 2,100 draws a heading buy is most likely the sun's real-time shadows re-drawing the
scene (and the twelve shadow maps, `docs/findings/pole_line/`), unmeasured lever by lever. Not
measured: any tier on a weaker GPU, a variant keeping High's post look without the sun's real-time
shadows, and what a player's settings menu would offer -- which is the game's, not the factory's.
(Written before the sun's arms above; the variant without the sun's real-time shadows is B2, and the
sun's live shadows turned out to be 1,854 of those 2,100 draws.)

## The decision, and its proof in a real drive

The walker, 2026-10-12, from `sun_variants.png`: "Bake the sun by default". Lux 0.76.0
(`patches/patch_lux_sun_baked.py`) makes it Lux's behaviour, not a package edit: the sun static in the
editor, where Level Factory bakes; static and unshadowed at run time while a lightmap shows; dynamic with
the preset's shadows whenever none does (no lightmap, the power cut, baked lighting off). Lux 0.76.1
(`patches/patch_lux_sun_comment.py`) corrects 0.76.0's comment, which repeated B's retracted claim.

Cold run 9265 (`docs/cold_runs/cold_9265/`, 0 interventions) carried 0.76.0 through a real drive of the
same level. Its sun as the game runs it (`sun_state.gd`, 9264's package the control): static and
unshadowed with the lightmap bound, dynamic and shadowed with the power cut, static again with it back.
Its frames read as B2 to 0.1 of a level at every station, inside a re-bake's noise -- so the editor
baked the sun as a static light. Its price against 9264's package: -1,854.4 draws a heading (every
heading fewer), the median p95 7.62 and 7.09 ms -> 4.20 (-3.03 ms a heading against a 0.24 ms noise
floor), 47 of 53 headings faster beyond the noise and one slower by at most 0.37 ms, headings over
16.7 ms 5 -> 1.

## What the baked sun changes besides the price (`sun_occluders.sh`, `backdrop_split.sh`, `spec_arm.sh`)

B2's look differs from High's where they disagree about what is in shadow, and that was "a question for
the eye" above. Taken apart since, on 9264's and 9265's frames:

**What casts at run time that the bake cannot see.** Level Factory bakes `bake.tscn` -- the presentation
scene and its LightmapGI -- while the game's `mission.tscn` also loads the dressing and
`site_backdrop.tscn`. `sun_casters.gd`, headless on 9264's package: 3,382 shadow casters in the bake
(the tallest top 12.7 m, a 181 m shadow at this sun: 14.3 m of shadow a metre of height); the dressing's
4 MultiMeshes, 4,284 instances no higher than 0.1 m; and the backdrop's 25 MultiMeshes, 269 instances,
rowhomes 8 to 11 m high and a 40 m water tower -- none in the bake. `backdrop_casters.py` places them
from the scene file: a ring round the level, its rows 58 to 138 m north and south of the origin and 105
to 181 m east and west, the west and north sides between the sun and the level. **RETRACTED, KEPT** (`sun_casters_9264.first.out.txt`): the census's first run
put every backdrop box at the origin with a rowhome's top at half its height; headless, a MultiMesh's
instance transforms read as the identity, and the probe now says it did not read them.

**The arm** (`sun_occluders.sh`, `sun_occluders.png`: 9264 | the arm | 9265): 9264's live sun with only
the backdrop casting no shadow. It brightens line 37.4 -> 44.2, up 52.9 -> 59.4 and elev_N 57.3 -> 76.9,
and leaves corner, spawn and the objective as they were -- but it does not bring the live frames to
9265's: the three that move each move further from them (line 10.8 -> 12.9 levels from 9265, up 13.4 ->
15.3, elev_N 13.8 -> 14.3). The backdrop's shadow is part of the difference, not all of it.

**The split by pixel** (`backdrop_split.py`): the backdrop's pixels are where hiding it moves 9265's frame
more than 8 levels; 9264's mean absolute difference from 9265 is split into those pixels and the rest,
the parts adding to the whole. Luma as 9264 live / the arm / the arm with the sun's specular 0
(`spec_arm.sh`) / 9265 baked:

    station   backdrop  on the backdrop                  on the level                  |diff|  backdrop  level
    line         0.1%   141.8 / 141.9 / 128.2 / 103.9    37.2 / 44.1 / 42.8 / 32.9     10.8     0.0      10.7
    corner      14.3%    60.5 /  61.1 /  56.0 /  66.2    50.4 / 50.4 / 50.0 / 49.2      7.2     3.6       3.5
    up           0.5%   119.8 / 119.7 / 109.9 /  92.5    52.6 / 59.1 / 57.5 / 46.9     13.4     0.1      13.3
    spawn        0.2%    93.6 /  93.1 /  87.4 /  92.4    20.5 / 20.5 / 19.2 / 17.9      4.5     0.0       4.5
    objective    0.0%      --                             6.5 /  6.5 /  6.5 /  6.5      1.7     0.0       1.7
    elev_N      34.4%    15.6 /  57.8 /  39.5 /  36.5    79.2 / 86.9 / 83.3 / 78.3     13.8     7.3       6.5

What it attributes, and what it does not:

- **The backdrop as a receiver.** Not lightmapped, it takes the sun live, and under the baked sun with no
  shadow from anything -- the level's or its own. Half of corner's difference is on its pixels, the far
  row across the street 60.5 -> 66.2; half of elev_N's, its homes 15.6 -> 36.5.
- **The backdrop as a caster.** Its long shadows fall on the level under the live sun and not under the
  baked one: taken away in the arm, the level at up 52.6 -> 59.1 and at line 37.2 -> 44.1.
- **Specular.** A lightmap holds none and the live sun carries Godot's default (Lux never sets it): on the
  level 1.3 to 1.6 levels at line and up, on the backdrop 18.3 at elev_N.
- **Not attributed:** the rest of the level's sunlit faces reading darker under the baked sun -- up 57.5
  against 46.9 and line 42.8 against 32.9 with the backdrop's shadow and the specular both taken away.
  Unmeasured candidates: the live map's bias at a 4-degree sun (light where the bake traces shadow), the
  lightmap's texels and its denoiser.

Levers, none taken, the walker's: the backdrop in the bake as a caster (what Godot's lightmapper does
with a MultiMesh is not measured here), its own lighting by cause (a side facing the sun lit, one facing
away shaded, as Zoo bakes vertex masks), or nothing -- it is far scenery, and at a higher sun its
shadows are short. The live sun's shadow for the backdrop alone has no cheap form: a light's shadow map
draws all its casters.
