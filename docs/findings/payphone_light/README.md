# The payphone lit: where its lamp hangs, and how bright (Zoo 1.89.0, Lux 0.70.0, roadmap 210)

**Question.** Cold run 9212 stood Zoo 1.88.0's booth at Lot's bus stop, and
at midnight it read as a silhouette: no light reached the card, the keys or
the stickers (`docs/cold_runs/cold_9212/NOTES.md`). The walker, 2026-10-09:
"yes light it". A lamp needs a place to hang and a level, and both were
guesses until measured.

**Frame and units.**
- Positions are Godot world metres, Y up.
- Brightness is luma, 0 to 255, over the frame, as `tools/look_shots.py`
  reports it. "Centre" is the frame's middle third.
- Lux levels are multiples of `REFERENCE_POOL`, 0.684: the value a tuned
  club wash puts on its floor.

## The probe

`make_probe_copy.py` copies cold run 9212's walk project and appends one
`SpotLight3D` under `presentation/lux.applied.tscn`'s root. It carries the
numbers Lux's fluorescent downlight gives:
- angle 89, rim 0.125, attenuation 2, no shadow;
- `LuxColorTemp.cool_fluorescent()`, worked by hand: (0.965, 0.874, 0.646).

The lamp is **live**: Godot's default bake mode over the package's own bake.

**Where it stood.** In `cover_101`, Lot's bus-stop booth.
- **Its facing.** Its transform, read as basis rows: the open front (Zoo's
  -Y, glTF's +Z) faces world -X.
  - *Corrected, kept:* 9212's NOTES say "its open front to +X". That line
    is wrong, and its own caller station, at x 33.05 looking toward +X,
    says so.
- **Its height.** Zoo 1.89.0's layout hangs the lamp 2.211 m over the
  pavement at the default slot, at one of two depths:
  - **mid-hood,** halfway between the header's back face and the
    instrument's face: Godot (34.3945, 2.3084, -2.075);
  - **behind the header,** the diffuser 10 mm off its back face: (34.273,
    2.3084, -2.075). The built GLB's marker lands exactly there: glTF (0,
    1.061, 0.177) in the booth's frame.

**Energy:** `energy_for(k x REFERENCE_POOL, 2.211, 4.0)`, which is 5.947 x k.

**Stations:** 9212's own two.
- `payphone_caller`: eye (33.05, 1.75, -2.08), aimed at (34.45, 1.30,
  -2.075).
- `payphone_walk`: eye (32.60, 1.70, -4.60), aimed at (34.45, 1.25,
  -2.075).

**The control.** The probe at energy 0 reproduces 9212's frames: the caller
view's centre reads 20.59 against 9212's 20.50, and the sidewalk view's
14.899 against 14.900.

| k | where | energy | caller, centre: mean / p50 / p95 | walk, centre mean | clipped |
|---|---|---|---|---|---|
| 0 | | 0 | 20.6 / 2 / 104 | 14.9 | 0 |
| 0.75 | mid-hood | 3.051 | 89.2 / 86 / 184 | 34.8 | 0 |
| 1.5 | mid-hood | 6.102 | 118.4 / 120 / 223 | 43.0 | 0 |
| 3.0 | mid-hood | 12.203 | 146.7 / 164 / 246 | 52.9 | 0 |
| 6.0 | mid-hood | 24.407 | 170.4 / 203 / 253 | 63.5 | 0 |
| 0.375 | behind the header | 1.525 | 68.5 / 62 / 150 | 27.8 | 0 |
| 0.75 | behind the header | 3.051 | 94.8 / 93 / 191 | 34.3 | 0 |
| 1.5 | behind the header | 6.102 | 123.9 / 127 / 227 | 42.5 | 0 |

**What the frames show.**
- **With no lamp** the booth is black: the caller view's centre median is 2.
- **At 0.75 every word on the instrument reads** (`instrument_zoom.png`):
  the card, the digits, 25 CENTS, COIN RETURN, YOUSETEL, and all three
  stickers.
- **Mid-hood,** the back panel's top (0.27 m from the lamp) goes cream at
  1.5 and white at 3 (`levels_mid_hood.png`).
- **Each doubling adds less** to the instrument: the tonemapper's shoulder.

**Why behind the header.** The geometry at the default slot, as the value
per unit of energy at each surface's own incidence:

| | the card | the back panel's top |
|---|---|---|
| mid-hood | 0.27 | 11.4 |
| behind the header | 0.42 | 5.9 |

So behind the header the hot spot halves, and the card gains half again. A
real booth's tube sits there too, backlighting its sign. `positions.png`
shows both rows.

**The choice: behind the header, at 0.75.** At that level the pavement under
the tube reads as the road under a streetlight, which is `STREETLIGHT_LEVEL`'s
ratio. In Lux it is a separate constant, `PAYPHONE_HOOD_LEVEL`, so tuning
one does not move the other.

## What shipped

- **Zoo 1.89.0** (`patches/patch_zoo_payphone_light.py`):
  - the header's face and a diffuser on a second, backlit atlas named
    `_Face`, which Lux's power cut takes;
  - `LuxEmit_payphone_hood` 30 mm under the diffuser, carrying `lux_type`
    and `lux_drop` as glTF extras, through `markers.add_marker(..., props=)`.
- **Lux 0.70.0** (`patches/patch_lux_payphone_hood.py`): the
  `payphone_hood` row.
  - **Range:** `fluorescent_range(drop)`.
  - **Energy:** what puts `PAYPHONE_HOOD_LEVEL` on the ground under it, at
    any drop.
  - **No preset scaling:** a street fixture.
- **Deli Counter 0.204.0** (`patches/patch_dc_payphone_wall.py`,
  `patch_dc_0204_release.py`): an indoor payphone asks for the wall form,
  and the library is refurnished and rebuilt (39 payphones in 38 specs).
  - **Also in this release** (`patch_dc_kind_paint_matte.py`):
    `material_kind` learns Zoo 1.82.0's `paint_matte`. The pin to Zoo's
    kinds had failed since 1.82.0.

## The builds

`build_check.py` builds every form at the genome's min corner, the default
slot and its max corner, and reads each back out of its GLB.
`docs/findings/payphone_redraw/form_census.py` runs the coplanar census over
the same builds. Outputs: `build_check.txt` and `form_census.txt`, on the
committed tree.
- **Each build:** two objects, two materials (one `_Face`), and the marker
  with its payload.
- **A default booth:** 1,052 paint triangles and 4 lit; a 79,620-byte GLB
  against 1.88.0's 76,928.
- **0 coincident pairs** over the 9 builds.
- **The marker's `lux_drop`:** 1.521 at the min corner, 2.211 at the
  default, 3.131 at the max.

## In the level: cold run 9213

Club_block_014, seed_9181, `INTERVENTIONS: 0`. The record is
`docs/cold_runs/cold_9213/NOTES.md`.

**The lamps.**
- **Spawned: three,** one for each payphone in the level.
  - The bus-stop booth's stands exactly where the probe's did.
  - The airport terminal's and the funeral home's are wall units
    (`..._fwall_mmetal`), from Deli Counter 0.204.0.
- **The bake:** 79 steady rigs, against 9212's 76.

**At midnight** (`payphone_street_before_after.png`,
`payphone_indoor_wall_units.png` beside the NOTES):

| caller's view, centre mean | 9212 | the probe, live | 9213, baked |
|---|---|---|---|
| `payphone_caller` | 20.5 | 94.8 | 81.8 |
| `payphone_walk` | 14.9 | 34.3 | 29.1 |

- **The baked lamp reads 14% under the live probe.** The header's shadow
  and the 0.2 m lightmap texel are the candidates; neither was isolated.
- **Nothing clipped.**

**The price** (four runs against two 9212 controls):
- **The frame:** nothing measurable. The median moved -0.021 and +0.000 ms
  against the controls' own +0.039.
- **The draws:** 23 of 53 headings gain 1 to 4, one per payphone in view.
- **The 8-light cap, paired:** 0 over, as in 9212.

## What the probe could not show

- **Shadows.** The probe's lamp was live and unshadowed; the shipped one
  bakes, ray-traced, so the booth's own parts shadow it.
  - **The header shades the pool in front.** The lamp hangs 4.5 cm behind
    the header's back face, and the header reaches 10.6 cm below it. So a
    ray more than 23 degrees off straight down, toward the street, meets
    the header, and the lit pavement ends about 0.9 m out from the booth's
    mouth.
  - **The live probe lit the pavement past that.**
- **The bounce.** The bake adds the booth's walls bouncing the lamp, which
  the probe had none of.
- **Resolution.** The payphone's lightmap texel is 0.2 m, the cover pieces'
  import sidecars' `lightmap_texel_size`. Baked light on the instrument is a
  gradient a few texels across, not per pixel.
- **Moving bodies** take the lamp live: a Static light still lights dynamic
  objects in real time.

## Records beside this README

- **Instruments:** `make_probe_copy.py`, `build_check.py`.
- **The probe's shot manifests,** one per level and position: `shots/k*.json`
  (`f` is behind the header). Each shot's PNG path points into `_runs/`,
  which is not kept.
- **Frames:**
  - `levels_mid_hood.png`: the caller view at k 0, 0.75, 1.5, 3 and 6,
    mid-hood;
  - `positions.png`: mid-hood against behind the header;
  - `instrument_zoom.png`: the instrument at 0.75, 1.5 and 3, mid-hood.
- **The builds:**
  - `build_check.txt` and `form_census.txt`, on the committed tree;
  - `build_check_scratch.txt` and `form_census_scratch.txt`, the same
    measured on the scratch copy before the release. They match.
