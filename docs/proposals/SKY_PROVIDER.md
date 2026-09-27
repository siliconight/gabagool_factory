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

## One defect in Lux, and one claim withdrawn

### 1. RETRACTED -- Lux DOES grade an adopted provider environment

**This section previously claimed Lux fails to write its grade onto a sky
provider's Environment. That was wrong, and the measurement behind it was an
artefact of how the probe loaded the scene.**

Measured properly -- scene loaded with `change_scene_to_packed`, which is how
the engine loads a main scene and what assigns `current_scene`, and with the
prototype's own `_sky_switch.gd` REMOVED because it writes these very values:

    WorldEnvironment node(s): 1
      SkyMint   ambient 0.55  exposure 1.05  bg 1.00  sky ShaderMaterial  <== LIVE
    delco_night wants ambient 0.55, exposure 1.05

One Environment, SkyMint's, live, carrying Lux's grade exactly. The
documented split works as written: `_sky_is_provided()` detects the
ShaderMaterial sky and skips the sky block, and `apply()` writes ambient and
tonemap outside that branch.

**Where the false reading came from, because the shape recurs.** Every
`ambient 1.00` came from a `--script` probe that instantiated the scene with
`add_child` and never set `current_scene`.
`LuxEnvironment._find_world_environment` searches
`get_tree().current_scene`, so with it unset Lux cannot see SkyMint, builds
its own WorldEnvironment, and grades that one while Godot honours the
other. The probe was measuring its own launch path -- for the third time in
this investigation.

Worse, the prototype then **printed the conclusion as a fact on every run**:
`_sky_switch.gd` logged "ADOPTED: Lux did not grade it; restoring ambient
0.55 / exposure 1.05" and wrote those values, having checked nothing. A line
that asserts a diagnosis it never tested, repeated every launch, is
indistinguishable from evidence -- and it was cited as evidence here.

Reading the source would have refused this before any of it: `apply()` writes
the grade unconditionally, and `apply_preset` defers correctly when the
setter fires before `_ready`. The code said so the whole time.

**Consequence for shipping: there is nothing to fix here, and the prototype's
sky-moving machinery is unnecessary.** A `SkyMint` node present in the scene
is adopted and graded on its own.

### 2. A night sky cannot have a moon -- REAL, and the only Lux work needed

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

### RETRACTED AGAIN, same day: not the art either -- the BAKE

The section directly below blamed the source art: the retro skyboxes' `up`
face is painted soft (moody 0.148 against 0.467 for `front`, source faces
measured), and "a soft face meeting sharp ones at the cube seam reads as a
hard edge". Half right. The face IS soft. **But the source cube, built as a
`Cubemap` from its six faces at runtime and sampled with `EYEDIR`, shows the
same clouds at the zenith with no edge at all** -- original faces, no
feathering, a top-edge step of 0.0001 against the equirect's 0.5895. The
soft face transitions smoothly in the cube; only the equirect has the step.

So the seam was **manufactured by SkyMint's cube-to-equirect bake**, and
the pole stretch turned it into a 90-degree square. A feathering experiment
that blurred the sides toward the top was run and is discarded: it fixed a
problem the cube never had.

**The fix, shipped as SkyMint 1.1 inside Lux 0.52.0, and verified in a
pipeline-shaped package** -- the localizer's rewrite applied to the script,
the faces mirrored to `runtime/skymint/cubes/`, zenith view, no geometry,
inside the old square against outside:

    sinister (shipped)    use_cube=true   ratio 0.982
    moody (worst case)    use_cube=true   ratio 1.065    (equirect: 0.069)

`cubes/<slug>/` carries the
six source faces, `skymint.gd` builds a `Cubemap` from them at runtime and
sets `use_cube`, and the shader samples it with `EYEDIR`. The equirect path
stays as the fallback for a skybox with no faces on disk. The zenith-contrast
ranking below is retired: it ranked bakes by how badly they showed a defect
the bake introduced.

### RETRACTED 2026-09-27: it is not the engine, it is the pictures (superseded above)

Everything below this heading down to "Minimal reproduction" described the
square as an engine artefact of panorama skies. **Withdrawn.** Measured in
order, each with an instrument that could see the edge:

| test | result |
|---|---|
| Forward+ instead of Compatibility | square present |
| `sky_rotation` 45 degrees about Y | the square becomes a **diamond** — it rotates with the panorama, so it is not a world-axis cube face |
| tilt 30 degrees about X | it moves and skews with the content |
| looking +Z, -X (side faces) | no square straight ahead — only at the pole |
| nearest filtering, 512x256 image, anisotropy 0, `textureLod(0)` | identical |
| radiance size 32 / 256 / 2048, edge metric | 0.5895 / 0.5895 / 0.5895 |
| exact `atan`/`acos` from EYEDIR instead of `SKY_COORDS` | **identical square** |
| `moody.png` reprojected to cube faces, no engine at all | **+Y face sharpness 0.304; +Z 0.757; -X 0.801** |

The last row is the answer. SkyMint's README: *"the `panoramas/` here are
baked from that CC0 pack"* — Vladislav Zhukov's retro skyboxes, distributed as
**512x512 cube faces**. The equirects were baked from six-face cubes, and the
bake carried the source cube's +Y face into the pole rows blurrier than its
neighbours, with the cube seam preserved as a hard edge at exactly 45
degrees. Reprojected back to a cube, the +Y face is a featureless smear and
the +Z face is sharp cloud. It is in the image. The three-file "engine
reproduction" reproduced it because it used the same image.

**The fix the right way, not by choosing a dark sky:** ship the cubes AS
cubemaps. A sky shader samples `samplerCube` with `EYEDIR` directly — no
equirect, no pole, no seam, one fetch — and 6 x 512^2 is 1.5 MB against the
2 MB equirect. That needs the CC0 source pack rather than SkyMint's bakes,
and it sets the rule for the PA skies to come: author cube faces or a
high-resolution equirect, never bake one from the other.

The zenith-contrast ranking further down stays useful as a description of
which bakes show it worst; it is no longer the mitigation.

### What it is (as first described, superseded above)

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

**PRICED 2026-09-27, cold run 9090, and the paragraph below it was wrong.**
Same package, sky provider on and off, same harness back to back: **about
1.3 ms GPU and 0.2–1.7 ms p95 at every station, on identical draw counts.**
The table is in `docs/DRAW_CALL_BUDGET.md` § "The sky, priced".

RETRACTED: "with clouds off ... the per-pixel cloud work (7 texture fetches)
is gone." It is not. Read the shader rather than the profile: the five noise
fetches, the `pow` and the cloud lighting run on every pixel, and
`cloud_density = 1.0` zeroes the resulting MASK, after the work. Clouds off
is a look, not a saving. The saving is one branch around that block, which
would move `glow_occlusion` slightly (it reads cloud thickness even at zero
coverage) and is unpriced.

What was known before that, kept for the record: `Sky` is set to
`PROCESS_MODE_INCREMENTAL` at 256 in the prototype rather than SkyMint's
`REALTIME` at 128, which costs a face rebuild per frame rather than all at
once; with a static sky neither should matter and neither has been measured
at stations.

Sky cost is also the wrong thing to optimise first on this content: the same
walk reads 5,739 draw calls at 29.90 ms in a busy view, and
`docs/DRAW_CALL_BUDGET.md` has that number.

---

## What shipping this needs

1. ~~`lux_environment.gd` — write the grade onto an adopted provider
   environment.~~ **Withdrawn: it already does.** See §1.
2. A `delco_night` SkyMintProfile in Lux, with a moon disc at night and
   `sun_direction` driven from the scene's DirectionalLight3D. Defect 2 --
   now the only code change this needs.
3. A Lux preset row naming a sky provider and a panorama, so the exporter
   carries `runtime/skymint/` the way it already carries `runtime/lux/`.
4. A decision on `Sky.process_mode` and `radiance_size` defaults, priced at
   stations on the target renderer.
5. PA panoramas authored to the zenith-contrast rule above.

Roadmap item, unfiled.
