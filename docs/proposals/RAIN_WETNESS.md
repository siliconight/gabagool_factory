# Wetness on what the rain lands on (roadmap 157, slices 2-4)

Rain falls in a shipped package (Lux 0.35.0, LF 0.83.0, walked in cold runs
9052 onward) and lands on nothing: every surface is as dry as it was. The
walker, 2026-09-16: "improve the rain effect to include wetness on surfaces
that are being rained on", with two references, transcribed and linked below.
This is what they say, what this pipeline would have to do, and what has to be
measured before any of it is believed.

## Reference A -- raindrops that sit on a surface and dry out

A Godot shader tutorial (the walker sent the transcript). What it does:

- **One texture carries four channels.** Red and green are the X and Y of a
  normal map for the drops; the Z is taken as 1.0 in the shader, on the
  argument that a drop's normal is near-vertical anyway. Blue holds a random
  grey value PER BIG DROP (baked in Blender with a geometry-node "mesh island"
  index feeding a random value, so every drop gets its own number). Alpha
  holds the small droplets that never move, because surface tension holds
  them.
- **The animation is arithmetic, not frames.** A drop's mix ratio is
  `fract(drop.b - TIME * k)`: it falls, its influence decays, and when it
  reaches zero it wraps to one and the drop "lands" again. Because each drop
  starts from its own grey value, they land and dry at different times. The
  ratio is multiplied by the blue channel again so that where there is no
  drop, nothing changes.
- **Wetness is more than a normal.** The drop normal is mixed into the
  surface's own normal; roughness goes to 0 where a drop sits (water is
  smooth) and specular up; the albedo underneath is distorted slightly through
  a noise-offset UV, as a real drop refracts what is behind it.
- **Rain does not fall on a ceiling.** The mix is gated on the WORLD-space
  normal, so downward-facing faces stay dry.

**How it fits here, and the catch.** It needs a ShaderMaterial (or a
`next_pass`) on the surfaces that get wet. Every surface a package ships is a
StandardMaterial3D -- 295 of 295 in the 9052 walk copy, 0 ShaderMaterials --
which is exactly why Lux's `surface_wetness` reaches nothing today. LF 0.89.0
established the mechanism for adding a pass at import (the CRT sync roll:
`zoo_worldskin.gd` attaches a `next_pass` to named materials, measured below
the noise floor in GPU cost, with the depth-offset trap recorded). The same
route can carry wetness: at import, exterior surfaces get a wet pass driven by
a Lux uniform. The texture itself is authorable in the factory -- Pixelcoat's
generation_7 pipeline already makes wet maps no grammar uses.

## Reference B -- puddles with ripples and reflections

`https://godotshaders.com/shader/rain-puddles-with-ripples-and-reflection/`
by shadecore_dev (CC0), which includes marcelb's SSR and Zavie's ripple
effect. A POST-PROCESS spatial shader on a fullscreen mesh under the camera
(the page also gives a single-triangle setup worth about 20% over a quad):

- Rebuilds each pixel's world position and normal from the depth buffer, so
  it needs `hint_depth_texture` and `hint_screen_texture`.
- Puddles are two octaves of value noise thresholded against the surface's
  upward-facing component, so puddles form only on horizontal ground.
- Ripples are Zavie's: rings hashed per cell, radius growing with TIME,
  contributing a normal offset.
- Reflections are screen-space ray marching, with a fallback puddle colour
  where the ray leaves the screen.

**The catch, and it is the important one.** This is a screen-space
post-process with a depth-texture read and a ray march. Packages ship on GL
Compatibility, where Lux already measured what does and does not exist
(no particle trails, no sub-emitters, no volumetric fog; box and heightfield
collision work). Whether `hint_depth_texture` and screen-space reflection are
available and affordable in Compatibility on this hardware is NOT known and
must be measured before this shape is chosen -- the shader's own page assumes
a renderer this pipeline does not ship. If it is unavailable, slice 3's
existing plan stands: puddles as flat Zoo species placed by Patina, with a
cheap ripple normal, no SSR.

## What each owner would do

- **Lux** owns the weather state (`LuxWeatherProfile.surface_wetness`, already
  in the presets: Heavy Rain is 0.85) and would drive a single wetness value,
  plus a "rain is falling here" mask consistent with the rain colliders that
  keep interiors dry (Lux 0.35.0's boxes).
- **Level Factory** attaches the wet pass at import, as 0.89.0 does for CRT
  screens: choose the surfaces by the same evidence the vertex-colour pass
  used (a named material, not a guess), and keep interiors out of it.
- **Pixelcoat** authors the drop texture (four channels as above) and any wet
  albedo/roughness response, in its own grammar so the look stays the
  walker's and not a downloaded asset's.
- **Zoo / Patina** own puddles as geometry if the post-process route is
  refused.

## What the performance rule does to this proposal

The walker, the day after sending these references: performance over look, this
being a multiplayer online game, and "we can always optimize later once we have
better data from runtime tests." That does not refuse either reference — it
orders them, and it says what a slice has to carry when it lands.

- **Reference A is the cheap one and is the default.** A `next_pass` on
  exterior materials is a fixed per-pixel cost on surfaces already being drawn,
  with no extra buffer, no screen read and no per-frame CPU. It is the same
  mechanism that was measured below the noise floor for the CRT roll, so the
  measurement route already exists.
- **Reference B is the expensive one and must earn its place.** A fullscreen
  post-process with a depth read and a screen-space ray march costs every
  client every frame whether or not it is raining, and its availability on GL
  Compatibility is unmeasured (item 1 below). Measure it anyway rather than
  refusing it blind: the answer is a number the walker gets to spend or not.
- **If B is unaffordable, say what it would have bought.** Puddles as flat Zoo
  species with a cheap ripple normal (slice 3's existing plan) give standing
  water and lose the reflection of the neon above it — which in a 1997 Delco
  street at night is most of the effect. That is the tradeoff to put in front of
  the walker with the frame figures beside it, not a call to make quietly.
- **Record the budget, do not close the question.** There is no runtime
  telemetry from real multiplayer sessions yet. Whatever is deferred here is
  deferred against today's evidence and gets reopened when that evidence
  improves.

## What must be measured before building

1. Does GL Compatibility on this machine give a usable `hint_depth_texture`
   and screen texture at 1600x900, and at what GPU cost? (Reference B is
   unusable here without it.)
2. **MEASURED, 2026-09-24 — and it overturned the premise this proposal
   argued Reference A on.** Cost of a wet `next_pass` over the exterior
   surfaces of a real package, the way the CRT pass was priced: on/off,
   several stations, with the no-rain control. See "What item 2 measured"
   below. The short version: the pass does **not** cost per pixel, it costs
   per draw call, so the sentence above that calls Reference A "a fixed
   per-pixel cost on surfaces already being drawn" is wrong about this
   renderer and the design that follows from it changes.
3. Does the wet look survive the retro treatment? Pixelcoat's audit exists
   for exactly this, and a mirror-smooth puddle is not a 1997 Delco street.
4. Interiors stay dry: the same walk that proved rain stops at a roof
   (every under-roof frame rose 0 pixels) must prove wetness does too.
   **NOT measured by item 2's probe, and the probe cannot answer it.**
   `wet_ab.gd` names two of its stations `interior_a` and `interior_b`, which
   is a misnomer: they are eye-height views inside the site's bounding box,
   not inside a building. Item 4 is still open and needs the under-roof walk,
   not this.

## What item 2 measured

`level_factory/tools/wet_ab.gd` + `wet_ab_run.py`, on cold-run package
`LF_crossroads_9600.portable-godot`, GL Compatibility, 1280x720, vsync off,
3 rounds x 300 samples per station, 4 arms. The fragment is the cheap shape
this proposal calls the default: a per-pixel darken and sheen keyed on how much
a surface faces the sky, no screen read, no depth read, no per-frame CPU.

    station         dry     wet_ground      wet (named)     wet_all (bound)
                  draws  ms  draws     ms   draws     ms    draws     ms
    street_along   1954 7.51  2473   9.47    2830  10.77     3481  12.85
    interior_b     2781 12.08 3357  14.44    4055  17.29     5043  21.78
    exterior_high  4385 19.16 5283  22.67    6391  27.22     7936  33.02
    street_down     146 1.55   193   1.72     233   1.81      276   1.96
    interior_a      147 1.52   195   1.71     235   1.81      278   1.94
    ground_near      75 1.17   101   1.22     119   1.31      141   1.37

    materials wet    0          133            172            802
    worst station           +3.51 ms       +8.05 ms       +13.85 ms


> **WITHDRAWN 2026-09-26, and the retraction is above the result on purpose.**
> The figures below priced a pass that almost certainly never shaded a pixel.
> A `next_pass` rasterises the same triangles at the same depth the base pass
> already wrote, and GL Compatibility's depth test rejects it --
> `assets/godot/zoo_worldskin.gd` measured that in the club at 1600x900 before
> this probe was written: `blend_mix` with `depth_draw_never` and no offset
> reads "not drawn", and `VERTEX` along `NORMAL` at 2 mm draws while still
> occluding correctly. `wet_ab.gd` declared exactly the first and offset
> nothing.
>
> The control could not have caught it. "Draw calls must rise" proves a
> SUBMISSION, not a shaded fragment -- the same distinction that same file had
> already paid for, its first render probe "reporting pixel-identical from
> frames that were 99.7% black".
>
> Re-measured with the offset and with a control that reads the frame back
> (LF 0.115.0), on cold run 9080's package:
>
>     wet worst  +8.05 ms -> +6.00 ms
>     us/draw     3.51 median, FLAT 2.27-4.29
>              -> 5.75 median, spread 3.79-12.63; ground arm 3.22-21.11
>
> **The shape is what changed.** The flatness was the whole argument for "per
> submission, not per pixel". A 6.5x spread whose cheapest per-draw arm covers
> the LEAST screen is fill cost behaving like fill cost. That conclusion is
> withdrawn.
>
> What survives is the architectural call: a baked variant costs zero extra
> submissions and a pass costs at least one, so choosing the variant for the
> ground was right whatever the fragment costs. The reasoning published beside
> it was not.

### The finding: this is submission cost, not fill cost

Marginal cost of the extra pass, per added draw call, over 18 station-arm
pairs: **2.27 - 4.29 us, median 3.5**. Flat — across stations spanning 26 to
3,551 added draws, baselines from 1.17 to 19.16 ms, and three arms whose wet
surfaces cover wildly different fractions of the screen.

That flatness is the whole result, and it is the control. If the pass billed
per pixel, `ground_near` — camera 2.5 m up with road filling the frame — would
be the most expensive per draw and `exterior_high` — a distant aerial where wet
surfaces are a small share of pixels — the cheapest. It is the other way round
(2.27 vs 4.10 in the ground arm) and only by 1.8x. Render-CPU is 92-96% of
frame time at the three loaded stations. This is the 2026-09-16 draw-call
finding reappearing in a different measurement: **frame time tracks the number
of submissions.**

### What follows from it

- **Narrowing the surface set works, proportionally.** Ground-only (road,
  sidewalk, kerb, asphalt, ground slabs, road paint) costs 45-59% of the named
  set's added draw calls and cuts the worst station from +8.05 to +3.51 ms.
  Note the asymmetry: dropping 39 of 172 materials removed over half the added
  draws, because a wall material is used by far more mesh instances than a road
  material is.
- **A wet variant folded into the base material costs zero extra draw calls.**
  If the bill is per submission, a second pass is the expensive way to do this
  and a second *material* is free — the same triangles are submitted once
  either way. That makes "Pixelcoat authors a wet skin variant, the build picks
  wet or dry per surface" the cheap option on this evidence, not the laborious
  one. The cost moves to build time and to whether wetness can then vary
  per-frame, which the `next_pass` gets for nothing and a variant does not.
- **Reference B's cost model is untouched by this.** A fullscreen post-process
  is one submission; its cost is fill and bandwidth, and item 1 is still
  unmeasured. Nothing here prices it.

### What was built on the strength of it

**Pixelcoat 0.46.0, 2026-09-24 -- the producer, not the chooser.** Ten ground
grammars declare a `wet` block and their packs carry `wet_albedo`,
`wet_roughness` and `wetness`: asphalt (x2), sidewalk (x2), cobblestone,
flagstone, gravel, tar, dirt, road paint. Measured at 256 px, 23-37% darker and
18-52% less rough.

It had to be grown on the grammar path, which is NOT where Pixelcoat's wetness
already lived. `pipeline_generation_7.py` has carried these exact map names for
a long time and both importers wire them -- but the factory calls
`theme-library` -> `build_material_pack` -> `synthesize`, and 0 of 86 shipped
material profiles enabled wetness, so none of it was reachable from a level
build. The new code emits the same names, so no importer changes.

The response comes from `material_response.PRESETS`, which keeps one wetness
model in Pixelcoat. `wet.floor` is new and exists because the first build
measured wrong: `asphalt_delco` at `amount: 0.9` came out 17% darker, mask mean
0.36 -- damp, not raining, because `wetness_mask` normalises to its own maximum
and its mass sits near 0.4 whatever `amount` says. A wall wants that
distribution; a road under rain wants a floor.

**Nothing downstream picks the wet maps up.** Zoo resolves packs through a
fixed `MAP_KEYS` allow-list, so no shipped pixel has changed, and the draw-call
check that would prove a variant beats a pass has nothing to measure yet. The
chooser is the next piece, and it is Zoo's and Level Factory's, not Pixelcoat's.

### What the wet roughness does, measured — and one gap that is not one

**`wet_detail_normal` was named as a gap and is not one.** The reasoning was
that gen7 emits a fourth map the grammar path does not, so a wet road's
aggregate would not visibly smooth out. Checked before building: all ten wet
grammars declare `emit.normal: false`, and the grammar path emits no
`detail_normal` either. gen7's map softens a DETAIL normal by pulling micro
height toward flat inside the mask; with neither map present there is nothing
to soften and no dry counterpart for an importer to substitute. The aggregate
these surfaces show is carried by albedo and roughness variation. Withdrawn.

**What IS measurable is that the wet roughness is MORE varied than the dry
one.** The shipped model is gen7's, faithfully — `wet_gloss = gloss +
wet_gloss_boost * mask`, hence `wet_roughness = dry - boost * mask`, a SHIFT.
The mask varies spatially, so the subtraction writes the mask's own texture
into the roughness channel. At 192 px:

    grammar           dry sd    wet sd   change
    asphalt_delco     0.0192    0.0258    +34%
    sidewalk_delco    0.0227    0.0295    +30%
    pebble_gravel     0.0272    0.0452    +66%
    tar_neutral       0.0485    0.0507     +5%

Two readings, and the measurement does not choose between them. A partly wet
surface genuinely is more varied than a dry one — pooled hollows glossy, crowns
still rough, which is what the mask is for. Or the water film should even the
micro-roughness out, and the rise is the mask leaking into a channel that ought
to be smoothing.

The alternative is a LERP toward water rather than a shift,
`wet = dry + (water - dry) * boost * mask`, which narrows the spread instead —
asphalt 0.0193, sidewalk 0.0216, gravel 0.0366, tar 0.0313 at a water roughness
of 0.08.

**Neither model reaches water at full mask**, because `boost` is below 1:
asphalt saturates at 0.50 shifted and 0.56 lerped, against roughly 0.05–0.10
for standing water. A fully wet road does not currently read as one under
either.

Not changed. The shipped model is what `material_response.PRESETS` encodes and
what the gen7 path uses, reused deliberately so Pixelcoat has one wetness
rather than two. Swapping a shift for a lerp is a look decision against that
model, not a defect fix.

## What the drip fragment costs, measured

**2026-09-26, LF 0.116.0, and it is the first drip figure in this file that was
measured rather than derived.** The estimate it replaces -- "+0.15-0.4 ms on
4-8 vertical families" -- was arithmetic off the per-submission model withdrawn
above, and is wrong by 5-12x. Cold run 9080's package, GL Compatibility,
1280x720, 3 rounds x 300 samples, `wet_ab.gd` with the 2 mm offset and the
frame-luminance control:

    station                   dry        drip_few          drip
                      draws     ms   draws     ms   draws     ms
    street_along       3467  17.08    3712  18.58    4961  23.30
    exterior_high      4646  22.13    4911  23.72    6637  30.74
    interior_b         4200  20.35    4464  22.20    6032  27.62

    materials touched     0              19            250
    median delta                    +0.83 ms       +3.59 ms
    WORST station                   +1.85 ms       +8.60 ms

`drip_few` is the street-facing set a shipping drip would use: brick, siding,
stucco, corrugated, shingle. `drip` is the wide 15-pattern set and is an upper
bound. Both controls fired -- draw calls rose at 6 of 6 stations, and the frame
CHANGED at 5 of 6, which is the control the withdrawn figure lacked.

### The material count does not predict the cost

    material ratio   wide / few = 13.16x
    worst-station ms ratio      =  4.65x

Scaling the wide arm's +8.60 ms by the material ratio predicts +0.65 ms for 19
families. The measurement says +1.85 ms -- nearly 3x, in the unaffordable
direction. **Cost tracks screen coverage, not the length of the material
list.** Brick and siding are large surfaces; 19 of them fill far more of a
street frame than their 7.6% share of the list suggests. Keep this beside the
asymmetry already recorded above ("dropping 39 of 172 materials removed over
half the added draws") -- it is the same fact from the other end, and it means
a material count is never a stand-in for a price here.

### The walker's call, 2026-09-26

**+1.85 ms worst-station for 19 wall families is affordable enough to walk.**
That is roughly 8% of a 22 ms frame. It is a decision to look at the drip on a
real street, not an approval to ship it: the performance contract's budget
comes from a target profile that does not exist yet, so there is no allocation
to charge this against and nothing gates on the contract. What exists is the
number and the two controls that make it mean something.

Still unmeasured, and each is a reason the figure above could move:

- one package, one theme, six stations -- the contract asks for nine scenarios
  including worst encounter and rapid traversal;
- interiors staying dry (item 4), which this probe cannot answer for the same
  reason it could not answer it for the wet pass: its `interior_*` stations are
  eye-height views inside the site's bounding box, not under a roof;
- the drip shader itself, which does not exist yet outside the probe. The price
  is for the fragment; the pipeline that attaches it to the right surfaces at
  build time is unwritten.

### Correction: the 19 were one family, not nineteen

**2026-09-26, caught by the runtime node printing what it attached to.** The
table above is right and the words beside it were not. `drip_few`'s 19 are 19
material RESOURCES -- one copy per imported GLB -- and all 19 carry the same
name:

    narrow family   entries in this package
    brick                19   (1 distinct name, M_Skin_brick_delco_1997)
    siding                0
    stucco                0
    corrugated            0
    shingle               0

So **+1.85 ms is the price of drips on this package's brick.** Siding, stucco,
corrugated and shingle were not measured, because this package has none of
them; a package that wears them pays more and this figure does not say how much
more. An empty name pattern and a cheap one look identical in a total, which is
the ordinary trap of a name-matched set and the reason the node prints its
matches rather than counting them silently.

The rest of the package, from 295 GLBs: 908 material entries, 242 distinct
names, 55 distinct (254 entries) matching the wide arm's patterns -- glass 22,
drywall 22, concrete 20, brick 19, then a long tail of `metal_painted` colour
variants. The wide arm's 250 is consistent with that. **The non-proportionality
finding is untouched**: 250 resources against 19 still cost 4.65x rather than
13.16x.

That tail is worth its own look and is not wetness's business: 20+ materials
named `M_Skin_metal_painted_delco_1997_<hexcolour>`, which is colour-only
variation expressed as separate materials -- the first rule under "draw calls
are the budget", and the defect `pennant_row` shipped.

### What exists now

`level_factory/assets/godot/rain_drip.gdshader` (the fragment, extracted from
the probe so both read one text), `rain_drip.gd` (the runtime node),
`tools/drip_assets.py` (one stager for shader and atlas, shared by the
measurement and the walk), and `tools/walk_export.py --drip`, which puts all
three into a walk copy. Verified on cold run 9080's package: 19 of 880
materials, 12,189 mesh instances visited.

**The pipeline still attaches nothing.** A walk copy is not a package. When the
look holds up, the attachment belongs in the presentation compose step, gated
on the brief's weather the way Lot's wet ground already is.
