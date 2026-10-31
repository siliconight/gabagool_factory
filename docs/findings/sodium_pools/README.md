# The avenue's ground at evening: the sodium pools

**Question (2026-10-30, slice 21).** The walker: "keep getting us closer to that amazing vertical slice look". Judged
from slice 21's street frames, the largest thing wrong is the ground: at Blue Hour the avenue's asphalt reads as a
black void across the bottom third of every street view, and the street lamps -- lit, their lenses glowing -- put no
visible light on it. A 1999 Delco avenue at dusk is pools of orange sodium light under the cobra heads against a blue
sky. Why are there none, and what does it take?

**What the slice stands** (`presentation/lux.applied.tscn` of `workspaces/slice-21-ws`'s walk copy): eight
`Streetlight (baked)` rigs, `site_pole_25`-`32`, all on the south kerb line (Godot z 34.0), 35.1 m apart along the
avenue, lens at 7.50 m; sodium colour, energy 34.12, range 14 m, attenuation 1 (the rig's default), a SpotLight3D with
a fixed 55 degree cone (`lux_streetlight_rig.gd`, `lamp.spot_angle = 55.0`). Five bake static; three cycle
(`failing_kind` 2, every third pole) and are live.

**Instrument.** `arm.py`: a copy of the walk project, its streetlights edited as a Lux change would edit them, re-baked
with `tools/lux_rebake.py` (Level Factory's own bake) and shot from the slice's street stations plus `road_down` (eye
at x -35 looking west along the kerb lane, toward pole 27 at x -51.7). The control arm reproduces the shipped frames
exactly (bank_oblique 48.4, card_front 47.1, as slice 21's own shots).

**Measured** (frame mean, level light; the frames are `_scratch/sodium_pools/frames_<arm>/`, not kept):

| Arm | Change | ave_east | road_down | gas_front | card_front |
|---|---|---|---|---|---|
| ctl | none | 43.9 | 43.5 | 59.0 | 47.1 |
| range | static lamps lent a 19.85 m bake range (half the spacing, from the lens) | 44.8 | 43.7 | 58.8 | 47.1 |
| range_e25 | the same, energy x 2.5 | 48.6 | 44.9 | 64.8 | 48.6 |
| range_e4 | the same, energy x 4 | 51.9 | 45.9 | 66.8 | 49.8 |
| throw_e25 | x 2.5, the cone 70 degrees (streetlights only), 22 m baked | 55.5 | 50.3 | 67.7 | 51.9 |

- **The range alone moved nothing.** Its bake did take it (`ranges lent` 14 -> 19: the five static streetlights).
  The reason is the cone: from 7.5 m a 55 degree spot lands within 10.7 m of the pole, and its edge is 13.1 m away
  slant -- inside the 14 m range already. A longer range cannot reach ground the cone does not.
- **x 2.5 shows a pool**: a warm orange patch under pole 27 ahead in `road_down` and on the rowhome face beside it,
  and the gas forecourt's apron warmer. Between the poles the road stays dark: each pool is about 21 m across on a
  35 m spacing.

**Why it was dim, as far as is known.** `STREETLIGHT_LEVEL` was set as a ratio to the canopy and judged at midnight;
since then the Blue Hour preset's fill was lifted at the walker's call (Lux 0.81.0), and a pool tuned against a black
night reads as nothing against a lit dusk. Not proven: no arm re-baked at midnight.

**The decision, from the frames** (`arms_ctl_x4_throw.png`: control, x 4, throw_e25 across; `road_down`,
`ave_east`, `sidewalk_east` down). x 4 through the 55 degree cone lit the road hot near each pole and left the walls
dark. x 2.5 through a cobra head's 70 degree cone put pools on the road AND raked the rowhome brick beside each pole
orange against the blue dusk -- the warm-cool split the target asks for. Shipped as Lux 0.82.0: `STREETLIGHT_LEVEL`
x 2.5, `STREETLIGHT_THROW_DEG` 70 on a street pole only (a wall pack keeps 55), and a bake range that reaches the cone's
edge on level ground, `height / cos(cone)` -- 21.9 m here, the arm baked 22. The live range stays 14 m: a static lamp's
lightmap claims nothing at run time, so the cost is bake seconds. The three cycling poles are live; they take the
level and the cone, and their 14 m range still bounds them.

**Also found on the way: Lux 0.81.0 shipped with a selftest failing.** `fluorescent_scale_selftest.gd` derives each
preset's fixture scale from its `sky_energy`, and 0.81.0 lifted Blue Hour's to 1.5 for the bake's fill and kept the
fixtures -- so the test failed on Blue Hour, and 0.81.0's record says it was not run. 0.82.0 has the test judge Blue
Hour's fixtures against the sky they were tuned under (0.7), with the reason in the test. `streetlight_shadow_selftest`
opens a window by design and fails headless; run as its header says, it passes on 0.82.0.

## Midnight: is x 2.5 too hot? (`night.py`)

`STREETLIGHT_LEVEL` was judged at midnight and every preset that lights its lamps takes it. Slices 21 (Lux 0.81.0) and
22 (0.82.0) re-baked under `delco_night` and shot (frame mean, median, share of pixels with a channel >= 250):

| Station | slice 21 | slice 22 |
|---|---|---|
| ave_east | 4.5, 1, 0.003 | 8.7, 1, 0.003 |
| sidewalk_east | 2.7, 0, 0.001 | 3.3, 0, 0.001 |
| bank_oblique | 3.0, 0, 0.000 | 4.3, 0, 0.002 |
| road_down | 3.3, 0, 0.001 | 4.3, 1, 0.001 |

No clipping gained: the pools add light and blow nothing out. **Seen, not pursued:** at midnight the slice is near
black either way (means 3-9 of 255). The slice is set at evening, so midnight is not its slot; a level that ships at
midnight would need its own look.

## The asphalt's albedo (Pixelcoat 0.66.0)

Under the inspection light the road read mid-grey; in the level's light at dusk, black. `asphalt_delco`'s albedo map
measured 0.035 linear -- darker than fresh asphalt (0.05-0.10), a third of a weathered road (0.10-0.20) -- minted at
0.30.0 and never retuned for brightness; nothing records the walker choosing a dark road. A control mint at the
shipped settings reproduced the shipped map exactly (0.0348); base colours #52514d / #5a5955 / #4a4945 mint 0.095.
Arms on slice 22's walk copy, the map swapped in (`arm.py --skin`), re-baked: ave_east 48.9 -> 57.0, gas_front 61.6
-> 72.1 (p50 41 -> 78), road_down 45.0 -> 46.4, card_front 48.7 -> 50.7. `asphalt_ctl_aged.png`: control left,
weathered right -- the cracks and aggregate read inside each sodium pool and the forecourt apron catches the orange.
A map cannot move a draw.
