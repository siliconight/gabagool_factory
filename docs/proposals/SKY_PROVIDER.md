# A sky provider for Lux, and the +Y square

PROPOSED. Prototyped on cold run 9088's package 2026-09-27 and judged at
runtime by the walker; nothing is in a tool repo yet.

The question was whether SkyMint — a Gabagool addon already vendored inside
Lux at `lux/addons/skymint/`, v1.0.0 — should replace Lux's procedural sky as
the backdrop. The walker's brief, after seeing it: *"keep the moon's light on
the level, just try the panorama behind it."*

The walk copy is `_runs/walk_9088_skymint`, driven by `_sky_switch.gd` with
every knob on a key so the look calls are made with eyes rather than by a
threshold.

---

## What the walker decided at runtime

- **SkyMint as a backdrop is better than the procedural gradient.** "Looks
  better", "this looks great", "awesome".
- **Procedural clouds OFF.** *"yeah clouds off just looks better."* The
  panoramas carry painted clouds already — the soft banded sheet in the dusk
  and night skies is part of the 2048x1024 image — and SkyMint's procedural
  layer draws on top of them, which is two cloud systems disagreeing before
  it is anything else. It is also the cheapest answer: `cloud_density` at 1.0
  resolves the mask to zero and the per-pixel cloud work goes away.
- **More panoramas that read as Pennsylvania are wanted.** See the authoring
  rule at the bottom, which is now a measured constraint rather than taste.

---

## Two defects in Lux, found by prototyping

### 1. Lux does not grade an adopted provider environment

`lux/addons/lux/docs/skymint_integration.md` states the split: SkyMint owns
the sky, Lux owns the grade, on one shared environment. `LuxEnvironment.apply`
implements the first half — `_sky_is_provided(env)` correctly detects a
non-Procedural sky material and skips the sky block, with a comment saying it
will "write only the grade (tonemap/exposure/fog/glow/adjustment) onto the
shared environment".

Measured on the running scene: it does not. With SkyMint present, Lux adopts
its Environment and the live values are SkyMint's defaults —

    ambient_light_energy  1.00   (delco_night wants 0.55)
    tonemap_exposure      1.00   (delco_night wants 1.05)

This is not only a sky problem. Ambient here is background-sourced, so a dark
night panorama collapses the **whole level's** fill: the first walk of the
prototype was black indoors and out, and the cause was the grade never being
written, not the sky being dark. `_sky_switch.gd` patches the two values at
runtime; the fix belongs in `lux_environment.gd`.

### 2. A night sky cannot have a moon

SkyMint's default profile (`SkyMintProfile.make_default()`):

    night_blend    1.0 only for t <= 0.20 and t >= 0.80
    sun_intensity  0.0 outside t in [0.23, 0.77]

Those windows never overlap, so **a night panorama never carries a disc**.
The moon the walker had praised two days earlier — "definitely reads as night
and the moons light is actually great now" — was Lux's `ProceduralSkyMaterial`
drawing its own `DirectionalLight3D`, and adopting SkyMint's sky removes it
while leaving the light.

The prototype writes the disc back and takes `sun_direction` from the
DirectionalLight3D rather than from `time_of_day`, which puts it at elevation
38.0 — exactly where the moonlight comes from. That is the right rule anyway,
and the same one the fixtures follow: light comes from a light source.

Shipping it means a Delco night `SkyMintProfile` in Lux plus a preset row
naming a sky provider, so the package carries both.

### Not a defect: which node owns the Environment

An earlier reading claimed the scene ends up with two WorldEnvironments and
that Godot's one-environment rule was being broken. **Withdrawn.** That came
from a `--script` probe that instantiates the scene itself and never sets
`current_scene`, so LuxRoot's search could not find SkyMint and built its own.
In a normal run Lux adopts SkyMint's environment exactly as documented. The
probe was measuring its own launch path. `_sky_switch.gd` now handles both
arrangements and reads the live environment from `World3D` rather than
inferring it from which nodes exist.

---

## The +Y square

A hard-edged dark square in the sky, which the walker raised twice — *"the
skybox square needs to not look like a hard square in the sky"*, and with a
drawn line, *"the way the squares cut and aren't blended"*.

### What it is

**A 90-degree square centred on world +Y — the up face of the sky cubemap.**
Measured: in a 1280x720 frame at 110 degrees vertical FOV looking straight
up, the square spans 496 px against a predicted 504 px for a 90-degree cone
(`720 * tan(45) / tan(55)`).

Inside it the sky is **14x darker** than immediately outside (0.0035 against
0.0490 at the zenith).

### What it is not, each refuted by measurement

| Hypothesis | How it died |
|---|---|
| Level geometry | Survives `cull_mask = 0`, which draws no geometry at all |
| SkyMint's procedural clouds | Present with clouds off (`cloud_density` 1.0) |
| A hard latitude painted in the panorama | Every panorama's worst row jump is at row ~514 of 1024 — elevation 0, the painted horizon. Nothing near the zenith |
| Cubemap face **resolution** | Identical at RADIANCE_SIZE 128, 512 and 2048: ratio 0.069, 0.071, 0.072 |
| SkyMint's shader arithmetic | Reproduces with a stock `PanoramaSkyMaterial` on the same image |
| Mipmap selection at the pole | `mipmaps/generate=false` on every panorama, in all three projects; `detect_3d` only re-imports in the editor and these runs were headless |
| A per-face brightness or gamma step | A **uniform** mid-grey panorama gives ratio **1.000** — no square at all |

Two earlier "measurements" of this were themselves wrong and are recorded
because the shape recurs: a seam statistic and a dark-pixel fraction were both
taken on an OBLIQUE view where the frame is dominated by a genuinely dark
lower half, so neither could see the square, and both were briefly read as
"radiance size is not the cause". The conclusion happened to survive; the
evidence did not. **A number that cannot move is not evidence** — and the
third attempt, taken at the zenith where the square fills the middle of the
picture, is the one the table above rests on.

### Minimal reproduction

`scratchpad/skyrepro` — three files, no Lux, no SkyMint, no level, no lights:
a `WorldEnvironment` with a `PanoramaSkyMaterial`, a camera looking up, GL
Compatibility. The square appears. It is an engine-level artefact of
panorama-backed skies on this renderer and nothing this project built.

    panorama     centre 0.4579  offside 0.8124  ratio 0.564
    procedural   centre 0.3425  offside 0.3727  ratio 0.919
    flat         centre 0.5020  offside 0.5020  ratio 1.000

### The mitigation, and it is also the authoring rule for the PA skies

The artefact is **content-dependent**: uniform content shows none of it. Its
visibility tracks how much contrast the panorama carries in the top quarter
of the image (elevation 45-90 degrees, which is the cone the face covers).
Measured across the shipped set, standard deviation of luminance in that band:

    safe (< 0.03)   sinister 0.016, sunshine 0.019, empty_space 0.021,
                    netherworld 0.026
    mild (< 0.07)   clear 0.035, dawn 0.051, apocalypse 0.058, gray 0.066
    shows it        classic 0.079, moody 0.082, dusk 0.089, dusk_land 0.091,
                    techno 0.116

`moody` was the prototype's default and `dusk` is what the walker was looking
at in the sunset frames; both are in the worst group, which is why they saw
it so plainly.

**So, for a Pennsylvania sky: keep detail out of the top quarter.** A smooth
high overcast, a clean gradient, or thin haze at the zenith will not show the
square; a broken cumulus field directly overhead will. Detail from about 45
degrees down to the horizon — which is where a Delco sky's interest lives
anyway, in the low banded stratus and the sodium-lit underside of cloud — is
unaffected.

That is a constraint on authoring, not a reason to avoid panoramas.

---

## Cost

Not yet priced properly, and it should be before anything ships. What is
known: with clouds off the sky shader does one equirect lookup plus a disc,
and the per-pixel cloud work (7 texture fetches) is gone. `Sky` is set to
`PROCESS_MODE_INCREMENTAL` at 256 in the prototype rather than SkyMint's
`REALTIME` at 128, which costs a face rebuild per frame rather than all at
once; with a static sky neither should matter and neither has been measured
at stations.

Sky cost is also the wrong thing to optimise first on this content: the same
walk reads 5,739 draw calls at 29.90 ms in a busy view, and
`docs/DRAW_CALL_BUDGET.md` has that number.

---

## What shipping this needs

1. `lux_environment.gd` — write the grade onto an adopted provider
   environment. Defect 1 above.
2. A `delco_night` SkyMintProfile in Lux, with a moon disc at night and
   `sun_direction` driven from the scene's DirectionalLight3D. Defect 2.
3. A Lux preset row naming a sky provider and a panorama, so the exporter
   carries `runtime/skymint/` the way it already carries `runtime/lux/`.
4. A decision on `Sky.process_mode` and `radiance_size` defaults, priced at
   stations on the target renderer.
5. PA panoramas authored to the zenith-contrast rule above.

Roadmap item, unfiled.
