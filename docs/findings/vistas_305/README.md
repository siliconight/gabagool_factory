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

## Measured on a prototype, 2026-10-24 (cold run 9389's walk copy, copied to `_scratch/`)

**REFUTED -- "A Lux preset names SkyMint as its sky provider" above, as a statement about levels.** One preset does
(`delco_night`, and `ps1_storm_night`); a level runs the one its `lux.applied.tscn` names, and restaurant_row_001 runs
`blue_hour`, which names none -- read at run time, its WorldEnvironment draws a `ProceduralSkyMaterial` that LuxRoot
authors (`lux_root.gd`, `_spawn_sky_provider` returns early without a provider). The shader route above was built
(`proto_apply.py`) and drew NOTHING in that level, 15 to 23 pixels of 1.44 M changed from 30 m up: correct code on a
sky that was not on screen. A far band that lives in SkyMint's shader reaches two presets.

**A HORIZON RING draws under any sky** (`proto_ring.py`): one open cylinder 1,500 m out, faces drawn both sides, the
strip as its texture, unshaded, alpha-cut, no fog, no shadow, outside the bake -- one mesh, one surface, one draw.
From 30 m up facing west it puts the test skyline on the horizon (`ring_vs_shipped_9389.webp`, right column; the test
strip `strip_proto.py`, previews `strip_proto_*.webp`). Godot's default far plane, 4,000 m, holds it.

**What a player at street level sees of it: almost nothing, and that is a constraint, not a defect.** Four views
from the street at (7.9, 1.7, 16.7), one a heading, changed by 47 to 523 pixels of 1.44 M: the near backdrop --
rowhomes 8 to 11 m tall out to about 92 m, warehouses -- fills everything below about 7 degrees, and a far scene that
is real sits at 1 to 8 degrees. So a landmark must be PLACED ON A SIGHTLINE -- down the level's longest street, over
an open lot, from a roof or an upper floor -- or be tall enough to clear the roofs (a tower, a skyline), and the
vista recipe has to know which.

**Two more things the frames show:**
- The night test strip reads black against a blue-hour sky. A strip is rendered per level, in that level's sky and
  fog colours (each level has one time of day), so it carries its own haze; a fixed palette cannot.
- From any elevated view the world below the horizon beyond the backdrop's ground is BLACK -- a band under the
  horizon in every `up_*` frame, shipped as well as prototype. The ring's lower rows could close it (a strip whose
  bottom is ground haze), which is a reason for the ring of its own.

**Open:** the ring's price on the target renderer (one draw and its fill, measured against controls once cold run
9391 has ended, since a run in flight loads the machine); the strip rendered from Zoo silhouettes in the level's
colours; the sightline rule.
