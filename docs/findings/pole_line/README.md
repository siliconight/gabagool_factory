# The pole line (roadmap 240)

The walker's Philly comps (`docs/reference/PHILLY_STREET_COMPS.md`) put the
overhead network in two of three frames; the factory stood a steel lamp on
both kerbs every 25 m and not one pole. The walker's calls of 2026-10-12
(`docs/proposals/POLE_LINE_DESIGN.md`): one side of every street; the full
wire set without house drops; a transformer can every third or fourth pole; a
cobra-head on every pole.

Built in three steps, each its own release:

1. **Zoo 1.104.0, the pole** (`patches/patch_zoo_utility_pole.py`): a 40 ft
   wood pole, its crossarm and insulators, the cobra-head on a 6 ft arm, a
   `transformer` form; four materials, so four draws a pole (Blender 5.1.1:
   census 3 builds 0 coincident pairs; both forms PASS through the kit path).
2. **Lot 0.118.0, the line** (`patches/patch_lot_pole_line.py`): one kerb of
   every street, poles at the kerb no more than 36 m apart, every pole's light
   at its lens, a can every third or fourth pole by the buildings it serves.
3. **Lot 0.119.0, the wires** (`patches/patch_lot_pole_wires.py`, with Level
   Factory 0.194.0 keeping them out of the lightmap): the full set along every
   line and tied across each junction, unshaded, shadowless, in the themed
   site only; **0.119.1** (`patches/patch_lot_wires_pixel.py`) holds a far
   wire to a pixel and fades it by what it covers.

## The census (`pole_census.py`, `pole_census.out.txt`)

Each Lot checkout's planner on the four stored site fixtures of cold runs,
their cover dropped first:

    fixture                         0.117.0 lamps   0.118.0 poles / cans   lights      trees   hydrants
    bank_block_001 seed 9256        18              8 / 3                  18 -> 8     16      3
    club_block_014 seed 9080        20              9 / 3                  20 -> 9     21      3
    club_block_014 seed 9181        15              9 / 3                  15 -> 9     18      2
    restaurant_row_001 seed 9205    16              9 / 3                  16 -> 9     14      2

The street lights about halve, as the walker's option said they would (pools
with dark between); whether a street reads too dark is for frames, not this
table. The trees and hydrants did not move on these four. On Lot's kerb probe
they did: its first kerb now takes every corner hydrant the site's spacing
allows, its lamps having refused two of them (four across both kerbs became
three on one) -- the hydrant rule working alone, recorded rather than undone.

## In a real drive: cold run 9262 (`docs/cold_runs/cold_9262/`)

0 interventions; the picked lot stands 11 poles (4 with cans), every pole a
module and its light at the lens. Its Laser Tag route read 0.64 where 9261's
read 1.00 -- and `lt_pole_ab.py` (`lt_pole_ab.out.txt`), the job's command on
copies of both runs' staged projects, says the poles are not the snag:

    9262 as built (poles, no lamps)        route 0.64   player stuck 29   76
    9262 with its 11 poles removed         route 0.72   player stuck 45   78
    9261 as built (lamps on both kerbs)    route 1.00   player stuck  9   80
    9261 with its 19 lamps removed         route 0.88   player stuck 50   79

Both controls read their jobs in every field. No stuck event stood within
1.5 m of a pole; they stand at a kerb face (-66, -5) and beside a meter
between two parked cars (35, -17), where 9261's bot stuck too. The route on
this lot swings with any change to its furniture -- the navmesh it reshapes
decides which way the bot walks into two snags that were already there --
filed as roadmap 242.

## Found on the way (Lot 0.118.0's drafts)

- **A lost station doubles a span.** The first draft stepped a pole only up to
  6 m and lost one inside the probe's 20 m footpath cut: a 75 m gap. A pole
  now also tries a cut's or a shop band's ends (`site_poles._steps`).
- **Along-only spacing is wrong across two lines.** `site_furniture._free`
  compares stations along the road, right for pieces on one line. The
  corner's bin and blade stand on the furniture line 1.9 m across the band
  from the pole line, and read along-only they refused both ends of that cut.
  The pole reads plan boxes instead (`site_poles._room`); a tree keeps its
  crown's spread and a signal 5 m.
- **A band on one kerb moves the whole line.** `pole_kerb` takes the kerb with
  less to dodge, so the band tests put a matching band behind both kerbs.

## Found by the first cold run (Lot 0.118.1)

Cold run 9262's west side street stood 2 poles for 3 stations: no corner pole
at its T, so its first pole stood 35.7 m from the main road's nearest -- past
the reach a junction's wires take. Re-planned from the run's drawn spec, step
by step: `_runs` trimmed a road crossing by the cut's WIDTH where the kerb's
span reaches `site_streets.CUT_MARGIN` (0.6 m) further, so every run's first
station stood in the cut's clearance; and 0.118.0's 5 m circle round a signal
refused every step off it, though the signal stands on the furniture line and a
pole on its own line clears its arms by 1.63 m (REFUTED, KEPT in `site_poles`).
Lot 0.118.1 breaks runs at the kerb's spans, asks a signal's arm box, and reads
every road's pieces at a corner: the west street stands 3 poles, the first 7.05
from the crossing, and the fixtures' census 8/9/9/9 poles became 9/10/9/9.

## Frames (`docs/cold_runs/cold_9262/poles.png`, `pole_frames.sh`)

The same three stations in 9261's package and 9262's, at the level's evening
light: the line along the kerb, a can's pole from across the street, the
corner. For the walker's eye: the darker gaps between the pools (the "every
pole" call) and the wood's colour under sodium light.

## The wires in a real drive: cold run 9263 (`docs/cold_runs/cold_9263/`)

0 interventions. The run's own drawn spec through Lot's own functions
(`wire_spans.py`): 12 poles, 11 spans -- 9 along the lines and a tie across
each side street's mouth -- 7 cells and 7,392 triangles, the lowest cable 5.43 m
over the road; the wires in the themed scene and in none of the three graded
lots. Priced within the run's own package against a copy with the 7 wire nodes
hidden: +2.2 draws a heading (0 to +6, one a cell in view), p95 +0.05 ms at the
median inside the controls' 0.09 ms. The frames found what the price could not:
past about 60 m a 2.4 to 4.4 cm tube is under a pixel and drew as a dotted line.

## A far wire held to a pixel: Lot 0.119.1 (`wire_pixel_splice.py`, `wire_pixel.png`)

Each vertex carries its wire's drawn radius as its u; the material's vertex
shader finds the wire's centre from it, widens a wire thinner than a pixel to
one and fades it by the share it covers. Before the release the draft's output
for 9263's own cover was spliced into a copy of 9263's package and shot at the
same five stations (`wire_pixel_splice.sh`): the far dashes became faint
continuous lines and the near wires read the same. **Found on the way:**
`_tube`'s quads ran round each ring against their normals, so every face of
0.119.0 was wound inward and drawn from both sides; with a fade, two layers
would have drawn a far wire nearly twice as dark as it covers. 0.119.1 winds
them outward and culls the back.

**In a real drive: cold run 9264** (`docs/cold_runs/cold_9264/`), 0 interventions: the generator's
own 0.119.1 wires, shot beside 9263's at the same stations (`against_9263.png`) -- the far dashes
faint continuous lines, the near wires the same -- and priced in the run's own package at +2.2 draws a
heading and p95 -0.02 ms, inside the noise: the transparent pass and the vertex shader cost what the
opaque wires did. **Found in it:** Lux's re-save carried `shader_parameter/min_px = null`. Lot wrote
`= 1`, an integer literal for the float uniform, and Godot reads that as no value
(`min_px_resave.gd`, `min_px_resave.out.txt`: written `1` or `2` it loads and re-saves null, `1.0` or
`2.0` it keeps); the shader's default being 1.0 too hid it. **Lot 0.119.2**
(`patches/patch_lot_wires_float.py`) writes the float.

## The price of the pole line: 9261's lamps against 9262's poles (`poles_price.sh`, `price_9261_9262/`)

Builds 1 and 2 shipped without a price at the stations. Priced afterwards,
9261's package as the control (twice) and 9262's as the subject, the same lot
and byte-identical `gameplay_anchors.json`, 53 headings, GL Compatibility on
the RTX 2060:

    controls' spread, median over 53 headings: p95 0.16 ms, draws 0.0
    9262 against 9261: draws +170.3 a heading (median +135, -114 to +783),
                       p95 +0.39 ms at the median, +4.72 at the worst heading

48 of 53 headings gain draws, by 270 to 783 wherever the view runs along the
main road. The worst frame-time heading (`defender_spawn_9` facing 90) is a
hitch: `highest_vantage`, standing at the same draws, read -1.44. The first try
of this price was stopped and re-run: a file search ran beside its subject pass.

**Where the 170 come from** (`pole_cost_ab.sh`, `pole_cost_arms.py`: arms of
both packages, one station pass each; draws repeat exactly between passes, so
one pass attributes draws):

    9262 as built - 9261 as built                  +170.3 a heading
    9262's street lights' shadows (budget 0)       +300.1
    9261's street lights' shadows (budget 0)       +133.4
    with no shadows in either, 9262 - 9261           +3.5
    9262's 11 poles themselves (hidden)             +29.6

Lux shadows 12 lights in both runs -- the quality tier's `max_shadow_casters`,
street lights ranked first -- so the pole line did not add shadow maps; it moved
them. A cobra-head's lamp hangs at 7.50 m where a steel lamp's hung at 5.92 (the
light anchors of `site.site.lights.json`, 11 against 17 on the band roads), both
pointing down with the rig's 55-degree spot angle, so its cone reaches further
across the street and its shadow pass draws more than twice what the lamps'
did (300 against 133 a heading, twelve lights each). The poles' own meshes (four
draws a pole) are nearly paid for by the lamps they replaced. The live
light-pair census (`tools/mesh_light_census.py --json` on the price's two
copies, `price_9261_9262/light_pairs_926{1,2}.json`) says the same
from the other side: 1,950 pairs in 9261 against 1,272 in 9262, fewer lights
reaching fewer meshes -- the passes did not grow, the shadow maps did.

**REFUTED, KEPT -- two knobs with no effect.** The first shadows arm wrote
`shadow_enabled = false` on the 12 street lights in the scene and moved the
draws by exactly 0: Lux's `apply_shadow_policy` sets `shadow_enabled` at
runtime, so the scene's value is never read (`perf_9262_shadow_enabled_edit_REFUTED.json`);
Lux's own dial, `LuxRoot.shadow_caster_budget`, moved them by 300. The first
fade arm wrote Godot's `distance_fade_*` on the same nodes and moved them by
exactly 0 as well: `lux_streetlight_rig.gd`'s `_rebuild()` frees every saved
SpotLight3D and builds its lamps anew at runtime (`perf_9262_fade_30_scene_edit_REFUTED.json`).

**The levers, measured on 9262** (draws a heading saved, and where that leaves
it against 9261's lamps):

    shadow budget 8 (the Medium tier)      -118.2   +52.1 over the lamps
    shadow budget 4 (Low, Compatibility)   -240.9   -70.6 under the lamps
    street-light shadow cut beyond 30 m    -154.0   +16.2 over the lamps

The last is Godot's own `distance_fade_shadow` (the light kept, its shadow
meant to fade out over 5 m past 30 m from the camera), set in the vendored rig
where the lamps are built (`rigfade_30`). 30 m is one span of 9262's main line
(31.2 to 33.2 m): the light overhead, and both when between two.

**REFUTED AS A FREE SAVING, KEPT: what the fade does on GL Compatibility.** The
draws drop because the engine stops re-drawing a far light's shadow map -- not
because the shadow goes. Drafted as Lux 0.76.0 (`patches/patch_lux_street_shadow_fade.py`,
now refusing) with a windowed self-test, every control held and one case
failed: a slab's shadow seen from 44 m stayed black (0.000 against 0.499
unshadowed). `fade_order_probe.gd` (`fade_order_probe.out.txt`) read far FIRST
and the pool was lit (0.499); read far after a near look, black (0.000). Past
the distance the light keeps sampling its last map: a far shadow FREEZES as it
was last drawn, and a light never seen up close casts none. In a level, a stale
or missing shadow on anything moving through a far pool, and a failing (live)
light first seen from afar lighting through the walls beside it. Two instruments
disagreed -- the draws said the fade worked, the frame said it did not -- and
both were right about different things.

None of the three levers is applied. Each costs something a player can see on
the target renderer: the fade a frozen or missing far shadow, the budgets
twelve shadows cut to eight or four chosen by rank, not by nearness (243). The
untried shape that might cost neither: fade the whole LIGHT, not its shadow,
for steady street lights only -- they are baked, so past the distance their
real-time light shades only what moves, and a culled light samples no map.
Measure it before believing it.

**What the shadow maps buy, seen on bodies** (`shadow_options.py`, `shadow_options.png`,
`shadow_options_luma.py` and `.out.txt`; the walker, 2026-10-12: "What helps us learn?"). Two grey
capsules the crew body's size stand in the road under two STEADY lights of cold run 9264's package --
pole 22 (shadowed as built; the first to lose its map at a budget of 4) and pole 24, 60 m from the far
camera -- in four arms: as built, a budget of 4, a budget of 0, and every steady street light faded out
whole past 30 m. Mean luma, 0-255:

    region                        built  budget4  budget0   fade30
    near: the body                30.70    28.26    28.24    30.70
    near: the road around it     104.01   104.04   104.04   104.01
    far: the centre crop's road   14.58    10.84    10.87    14.59

- **Under a steady light the body casts no shadow on the road in any arm.** The road is lightmapped,
  and nothing at runtime darkens a lightmapped surface: a steady street light's shadow map can shade
  only what moves, never cast its shadow on the ground. The near frames read the same.
- **Cutting the budget darkens what moves:** the body 8 % darker, the far crop's road band -- the parked
  cars and what stands among them -- 26 %. Fewer shadow maps, less light on bodies. The likely
  mechanism, unmeasured: GL Compatibility draws a shadowed light in a pass of its own, while unshadowed
  lights share each object's list of `max_lights_per_object` (8), so taking street lights' maps away
  puts them in that list, and where many lights meet some are dropped. The light-pair census on a
  budget-0 copy would say.
- **The whole-light fade changed nothing measured** -- including the far crop, where the pole-24 body
  60 m off should have lost that light. Either nothing in the crop is lit by pole 24 in real time, or
  the edit did not take: a knob with no visible effect, so not yet a result.

So each cheap lever on the shadow maps costs light on players and enemies at night, which in a shooter
is visibility. Not applied.

**Found on the way: a package runs Lux's High tier.** `LuxRoot.quality_tier`
defaults to 0 (High: 12 shadow casters, sun shadows, post-fx, glow) and no tool
sets it -- only a Lux self-test does -- so every package runs High on the GL
Compatibility renderer that is its low-end target. Roadmap 60 priced the tiers
and built a Compatibility tier (4 casters, no sun shadows, no post-fx, no glow)
that no package has run. Which tier a package ships at is a look and a price
for the walker, not a default to change in passing.
