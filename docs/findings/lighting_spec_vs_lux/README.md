# The lighting spec against Lux and Level Factory

The walker handed over a lighting spec on 2026-10-09: "this could help Lux
and you?". It is filed verbatim at
`docs/reference/Godot_4_7_Natural_and_Artificial_Lighting_Spec.md`
(41,663 bytes). This folder holds two things:
- what it says, set against the code that ships;
- the measurements that comparison asked for.

**The spec's core claim:** a lamp's output stays fixed. Its prominence
changes because the light around it changes and the camera adapts. The model
is illuminance = sun + sky + bounce + lamps, added before the display
mapping (its R-001 and R-002). Everything below is read against that.

## Where the code already agrees

- **A dusk-to-dawn sensor is a legitimate fixture schedule** (its section
  8.2, R-002). That is Lux 0.71.0: `LuxPreset.street_lamps_lit` and
  `LuxLightRig.dusk_to_dawn`.
  - **Its warning, that a day switch must spare lamps in shade or indoors,
    does not bite.** All 389 wall packs in Deli Counter's 131 built shells
    are `derived`, one over each exterior door, outside the wall
    (`wall_pack_census.py`, `wall_pack_census.txt`; `deli_counter/lights.py`,
    `_exterior_doors`).
  - **The switch reaches the bake.** Cold run 9214's shipped lightmap holds
    none of a hidden wall pack's light (its `NOTES.md`).
- **A baked light does not follow the sun** (R-010). A level is baked for
  its own slot (`docs/LEVEL_STANDARD.md` section 17), and another slot is a
  re-bake (`tools/lux_rebake.py`).
- **On Compatibility the tools are** lightmaps, probes and authored fills,
  with no SDFGI and no native auto-exposure (its section 7 table). That is
  the stack.
- **Inverse-square falloff** (R-007). Every fixture row in
  `lux_light_loader.gd` sets `attenuation = 2.0`, with two exceptions:
  - the bake-only room fills, `omni_attenuation = 0.0`, flat by design;
  - the heat lamp, `HEAT_LAMP_ATTENUATION := 0.6`.

## What it showed

**1. Level Factory bakes with no sky.**
- **The setting:** `level_factory/packages/exporting/light_bake.py:113`,
  `environment_mode = 0` (none). It arrived with 0.131.0 (`fa3968e`) and
  no recorded reason.
- **It is not made up at run time.** A lightmapped surface takes no ambient
  there (measured, `docs/findings/light_breakdown/`).
- **So no wall or floor ever receives sky light.** A shaded street and a
  window-lit room get sun bounce and lamps only. A character, which is not
  lightmapped, still gets the preset's ambient.
- **The test:** `tools/lux_rebake.py --bake-environment scene` bakes the
  same level with the scene's environment. If it ships, the runtime cost is
  nothing, because the light lives in the lightmap.

**2. Lux brightens fluorescent rigs as the slot darkens.** The preset's
`fluorescent_energy_scale`, `presets/*.tres`:

| preset | scale | sun | sun shadows | street lamps |
|---|---|---|---|---|
| Delco Summer Afternoon | 1.0 | on | on | dark |
| Delco Arcade | 1.0 | on | on | dark |
| SoF PC2000 | 1.7 | on | on | dark |
| Blue Hour | 3.7 | on | on | lit |
| Heavy Rain | 4.3 | on | **off** | dark |
| Mission Goes Hot | 5.0 | off | | lit |
| Gas Station Fluorescent | 5.7 | off | | lit |
| Delco Night, Gothic Street Night, PS1 Storm Night | 6.0 | (Delco Night: the moon) | | lit |

- **The spec's view:** a lamp's output is fixed unless a dimmer, sensor,
  schedule or a recorded artistic override changes it. Brightening every
  lamp as the sun dims is its explicit "don't" (section 8.2).
- **Why Lux does it:** Compatibility has no auto-exposure, and the scale
  stands in for one.
- **What it reaches:** only rigs that `scales_with_preset`
  (`runtime/rigs/lux_fluorescent_rig.gd:29`), which means fluorescent rows
  and `preset_scaled` ones.
  - Bulbs are exempt by the walker's call of 2026-09-28, written beside
    that function.
  - Street lamps, wall packs and the payphone hood are other classes, or
    `preset_scaled = false`.
  - **So the balance between a room's tubes and the street changes sixfold**
    between Delco Summer Afternoon and Delco Night.

**3. The light breakdown's drops are not shares.** Light adds before the
display mapping, and look_shots reads luma after it. The presets also add
filmic or ACES tonemapping, cut colour to 24 to 28 levels, and add dither,
grain, glow and a vignette.
- **A drop is how much darker the frame got,** not how much of the light
  that source gave.
- **What stands:** rankings, and "black without it".
- `docs/findings/light_breakdown/README.md` carries the correction.

## What it asks of the walker

- **The sky in the bake: ANSWERED 2026-10-09, "yes bake the sky in".**
  Level Factory 0.164.0 bakes `environment_mode = 1`
  (`patches/patch_lf_bake_sky.py`). Its cold run is next.
- **Heavy Rain's sun.** Three ways:
  - re-price its shadow on today's package;
  - build the free cull-mask split, which needs interiors on a layer of
    their own;
  - keep Lux 0.38.0's recorded trade.
- **The night boost.** Keep it as a recorded override, or move it out of
  the lamps.
- **Morning and noon presets** (LEVEL_STANDARD section 17).

## Not taken up

- **Physical light units:** re-tuning the whole library would make nothing
  visible on its own.
- **SDFGI, VoxelGI and native auto-exposure:** Forward+ only, and packages
  ship on Compatibility.
- **Fireworks** (its section 2.3).
- **Its acceptance tests T-001 to T-012:** not run as a set. T-004 (local
  daylight access) and T-006 (indirect state) are the ones the measurements
  below touch.

## Measured on cold run 9214's day package

bank_block_001: its brief is afternoon with rain, so it ships under Heavy
Rain, and the walk copy carries Lux 0.71.0. Every variant below is a
`tools/lux_rebake.py` copy of that walk copy, measured with
`tools/light_check.py` at its own slot. The numbers are frame means in luma
after the grade (0-255). `compare_checks.py` writes each table; the reports
and the re-bakes' logs are in `runs/`.

**The re-bake is its own control.** Forcing the street lamps on moved every
station by 0.2 or less (`heavy_rain_variants.txt`, `lamps_on`), which bounds
what re-baking alone can change. A no-change re-bake reproduced cold run
9213's frames to 0.0 (`docs/findings/light_breakdown/`).

### Heavy Rain as shipped: 12 of 16 interior stations outshine the street

The street's median is 47.5. The rooms read 36.6 to 83.8: 10 PASS, 12 WARN,
1 REPORT. Four candidates were taken in turn (`heavy_rain_variants.txt`,
`breakdown_heavy_rain.txt`, `heavy_rain_sun_shadow.txt`):

| candidate | how | what it moved |
|---|---|---|
| the fluorescent boost (4.3) | re-baked at 1.0 | rooms 0 to -11.8; all 12 still warn |
| the sky in the bake | re-baked with `--bake-environment scene` | +0.3 to +2.3 outside; rooms -0.1 to +0.1 |
| the sun | look_shots `--switch-off sun` | objective 67.8 to 39.9; a drywall room 57.5 to 35.5 |
| the sun's shadow | re-baked with `sun_shadows = true` | rooms -5.6 to -31.6; 12 WARN to 7 |

- **The sun is the leak.** With its shadow on, switching the sun off moves
  the rooms by 0.0 (`breakdown_heavy_rain_sun_shadow.txt`). The rooms then
  read by their own fixtures (`heavy_rain_sun_shadow_rooms.png`).
- **This was a recorded trade, not an accident.** `resources/lux_preset.gd`
  (Lux 0.38.0) refused Heavy Rain's sun shadow on price:
  - +3.2 to +8.1 ms GPU at the orthogonal 60 m setting, against a ~2 ms
    budget, measured on cold run 9054's walk;
  - "the cost is the shadow PASS re-drawing the site";
  - it names the rooms' price (47-65 unshadowed against 20-38) and an
    unpriced, free lever: a cull-mask split, the sun lighting exterior
    layers only, "a layering question for the geometry's owners".
- **That price is a month old.** Since cold run 9054 the light bake
  (-12 % frame), the Empties' merge (-686 draws) and the cover merge (-1.86
  ms at the median view) have cut what a shadow pass re-draws. Re-priced:
  not yet.
- **Outside, the fog carries Heavy Rain's day.** Fog off takes the overview
  from 95.2 to 32.6, and the facades fall 44 to 62
  (`breakdown_heavy_rain.txt`).
- **NOT ESTABLISHED.** With the shadow on, two elevation cameras changed
  colour as well as brightness: north +15.0, west +17.0
  (`heavy_rain_sun_shadow_facades.png`). A shadow only takes light away, so
  this is how something in front of those facades renders, not the sun's
  light. They look in from outside the site, across the perimeter fence's
  blended far fabric; that is a candidate, untested.

### A clear afternoon: the same level, and the sky in the bake

Re-baked under Delco Summer Afternoon, whose sun casts a shadow and whose
fluorescent scale is 1.0 (`clear_afternoon_sky.txt`):
- **The relationship comes right.** The street's median is 64.9, the
  facades 109 to 177, and 2 rooms warn (mezzanine 74.3, upper ring 67.9).
- **The sky in the bake** (`--bake-environment scene`):
  - the street cameras +15.1 and +21.4;
  - the facades +2.7 to +15.9;
  - the rooms -0.1 to +1.2, so a sealed room takes none;
  - 22 PASS, 0 WARN.
  - **What it buys is shade that reads as daylight.** Without it, every
    surface the sun misses is near black: the extraction alley, and the
    backlit south row (`sky_in_the_bake_clear_afternoon.png`).
  - **The bake took 90.2 s** against 91.2 s. At run time it costs nothing:
    the light lives in the lightmap.

### The sky in the bake where the sky is dark

Before baking the sky could be a default, it had to be seen at night and at
dusk (`night_sky.txt`, `dusk_sky.txt`):
- **Delco Night:** against the light check's own night re-bake, two outer
  facades gain +3.3 and +4.4, and every other station moves 0.2 or less.
  The verdicts are the same: 2 FAIL, 1 WARN.
- **Blue Hour:** outside +0.5 to +3.7, rooms 0.1 or less. The verdicts are
  the same: 3 FAIL.
- **The bakes took** 96.1 s (night, sky on), 81.3 s and 83.4 s (dusk, off
  and on).

So across four slots the sky changes only the outside, and changes it most
where a sun is up. Every room moved 1.2 or less in every slot.

### What the evening slot found

bank_block_001 re-baked under Blue Hour, the evening slot's preset, with
the sky in the bake or not, fails 3:
- the bank's grand lobby, p50 3, against the ROW floor of 10;
- the strip retail's stone vault, p50 2, against the MOODY floor of 5;
- **the extraction, p50 1: "collapsed to black".** That is the street where
  players leave at the van.

At night the same level fails on the grand lobby and the casino's gaming
floor (p50 9 each), and its north facade warns (p95 3).
