# Distant scenery: the far band (roadmap 305)

The walker, 2026-10-24: "THings I want in the distance that you can't interact with are trains, oceans (with
marina), forest, malls, airports, ect ect (want variety but that it looks goood) (but hihgly performant)".

## What a level's sky is today (read 2026-10-24)

- **Who draws it.** A Lux preset names SkyMint as its sky provider (`sky_provider_script =
  "res://runtime/skymint/skymint.gd"`, with `day_sky` / `night_sky` indexes into
  `lux/addons/skymint/panoramas/_catalog.json`; `delco_night.tres` in cold run 9389's walk copy uses 12 for both).
  SkyMint owns the sky, Lux the grade (`lux/addons/lux/docs/skymint_integration.md`).
- **What it draws.** `skymint_sky.gdshader` samples an equirectangular day panorama and a night one
  (`base_sky_texture`, `base_sky_texture_2`, 2048 x 1024 RGB), blended by `base_sky_blend`, under procedural clouds.
  Twenty panoramas, some with `_land` and `_ocean` horizons -- the CC0 retro pack, baked.
- **Who chooses it per level.** Nobody: no Level Factory or Lot code sets `day_sky` or `night_sky`; the preset does.
- **What stands beyond the plate.** Lot's `site_backdrop.py`, five surroundings recipes, every piece within about
  100 m (roadmap 228). Nothing farther.
- **Whose shader.** SkyMint is the studio's own (`github.com/siliconight/skymint`, plugin author GabagoolStudios,
  its glue MIT; the cloud shader from godotshaders.com; the panoramas CC0). Lux vendors it; a change lands in Lux.

## The design this starts from (not built)

**The far band costs nothing per frame because it is part of the sky.** A level gets a HORIZON STRIP: an
equirectangular RGBA band, transparent above its skyline, rendered once at build time from Zoo silhouette species
(an airport's terminal, tower and parked planes; a mall over its lot; a forest ridge; a skyline; an ocean's horizon).
SkyMint's shader composites it over the panorama -- one more texture read per sky pixel, no geometry, no draw. It
comes in a day render and a night render (lit windows, a tower beacon, runway and lot lights), blended by the same
`base_sky_blend` the panoramas use, so it follows the time of day.

- **One vista a view, one landmark each** (the PA guide), the strip laid out by heading; chosen per level from the
  brief or the archetype, as the surroundings recipe is.
- **What a strip cannot do:** parallax. A marina's masts or a rail line seen from a moving player want depth, so they
  are the mid band (Zoo species, MultiMesh'd per side, as roadmap 228's are), and they are priced.
- **Motion** -- a train, a plane on approach, boat lights -- is one mesh moved by a shader or one transform per
  level, a constant cost, priced on its own.

## Open questions, to be measured rather than argued

- The strip's resolution against what reads at the horizon (2048 wide is 5.6 px a degree).
- Whether the sky's radiance update (the reflection of the sky) re-renders when the strip blends with time of day,
  and what that costs on the Compatibility renderer.
- How the strip meets the mid band and the fog: `fog_sky_affect` is Lux's dial for it.
