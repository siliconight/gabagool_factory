## [0.73.0] - the glow at the horizon: a town's light over dark land

**Roadmap 228, step A.** The walker picked the edge of the plate from the
six-option menu in `docs/findings/edge_menu/` at the factory root (E: a
chain-link fence, rowhomes and a water tower behind it, a sky-glow over
them), and asked for versions that differ by level. The glow is in every
version, so it lands first and alone: a level no longer ends where the night
sky meets the perimeter wall.

**What it is.** `LuxHorizonGlow`, a ring LuxRoot builds beside its other
modules and tunes from the preset on every apply:
- six rows of 65 vertices at `horizon_glow_radius_m`, coloured by height:
  opaque dark land below the horizon, `horizon_glow_color` at a standing
  eye's height, fading to nothing by `horizon_glow_top_deg`, the alphas
  scaled by `horizon_glow_energy`;
- unshaded, alpha-blended, read from both sides, no shadow, no GI, and the
  FOG IGNORED: the glow is the haze, and Delco Night's fog (density 0.006)
  leaves a tenth of anything 380 m out;
- one draw a frame; `horizon_glow_energy` 0 hides it, so a preset that says
  nothing draws nothing;
- the four fields blend (`_lerp_preset` is exhaustive by contract), and a
  re-apply keeps the mesh.

**Measured first, on the menu's mockup.** A ring that peaked at the horizon
and was gone by 4 degrees up showed in no frame, because from 26 m a 3.2 m
wall already covers the first 3.2 degrees. A town's sky-glow climbs 10 to 20
degrees, so the default top is 20.

**The presets,** each by its character, so every time of day carries one:
- sodium over dark land for the night skies, Delco Night at energy 1.0,
  Gothic Street Night, Gas Station Fluorescent and Mission Goes Hot at 0.8,
  PS1 Storm Night at 0.5;
- a warm dusk haze for Blue Hour (0.6, 14 degrees);
- a grey haze for Heavy Rain (0.5, 15 degrees);
- a pale day haze for Delco Summer Afternoon, Delco Arcade and SoF PC2000
  (0.35, 10 degrees).

**What it costs.** The menu priced six edges, each with this ring, at Level
Factory's fixed stations against two controls: none moved frame time past
the controls' own 0.65 ms spread (`price.txt` beside the mockup). Priced on
its own the same way, this release vendored into cold run 9221's walk copy
against two runs of the copy as shipped (`docs/findings/horizon_glow/` at
the factory root): draws +1.0 a heading; p95 frame time +0.19 ms median over 53 headings, inside the controls' own 0.23 ms spread; 8 headings over that spread by more than 0.5 ms, the worst +1.81 ms at extraction_4 facing 270, the level's heaviest frame (11.8 to 13.6 ms). The ring is one draw but a blended surface, so it costs fill rate wherever the sky fills the view; the cheaper form, the glow in the sky's own shader, would cost nothing a frame and waits on a provider whose shader Lux may write.

**Seen:** vendored into a copy of cold run 9221's walk copy of club_block_014 at midnight and shot at the edge menu's stations against the copy as shipped (`docs/findings/horizon_glow/` at the factory root): at eye level an orange band over the pale perimeter wall, fading up into the stars (the sky band's luma 0.9 to 5.5 across the open lot, 2.7 to 5.5 down the main road, warmth -0.5 to +4.2); from look_shots' elevated cameras the whole sky above the rowhome roofline goes sodium (0.9 to 25 to 27, warmth +26 to +29), the strongest it gets and the walker's dial; interiors and the stations facing into the level do not move.

**Selftest:** `tools/horizon_glow_selftest.gd`, 30 checks, exit 0, on the repo after its import pass (and on the draft copy before it, where the first run found `_ready` deferred a frame and the mesh storing its colours in 8 bits); the colocation and bake fill selftests exit 0 beside it.
