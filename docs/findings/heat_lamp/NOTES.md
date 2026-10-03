# The roller grill's heat lamp, measured

The walker, 2026-10-03, walking the gas station at night: "can we add a dim
but warm warming light to bring a bit more light to the dogs"; on the first
cut: "light should show the buns too, not seeing those". Shipped as Zoo
1.57.0 + 1.57.1 and Lux 0.63.0 (`patches/patch_zoo_heat_lamp.py`,
`patch_zoo_heat_lamp_up.py`, `patch_lux_heat_lamp.py`).

## What it is

A red-orange rod the width of the pan under a chrome trough, hung under the
hood's top above the bun shelf, on its own lit face (`M_Roller_Lamp_Face`,
Lux cuts it with the power), and a `LuxEmit_heat_lamp` marker under it that
the fixture spawner stands an omni on: 1,900 K, 0.16 of a fluorescent, the
inverse square flattened to 0.6, reaching the hood. One surface and one
light a grill.

## The levels, measured (`lamp_*.png`, `up/`, `up2/`, `final/`)

`heat_probe.gd` (scratch; its approach is in Lux's 0.63.0 changelog) finds
the grill by its rollers' material and the lamp by its rig name, scales the
lamp through levels and falloffs from one camera, and prints the pan's
three columns' luminance left / middle / right:

    rod under the shelf, 16 cm over the dogs, a downlight:
      level 0.35, falloff 2 (the first cut)   blown out: the dogs white
      level 0.035, falloff 2                  0.106 / 0.216 / 0.084
      level 0.035, falloff 1                  0.095 / 0.131 / 0.080
    rod under the hood's top, 36 cm over the dogs, 12 over the buns, an omni:
      level 0.08,  falloff 1                  0.096 / 0.136 / 0.079
      level 0.16,  falloff 1                  0.100 / 0.154 / 0.077
      level 0.16,  falloff 0.6  (shipped)     0.115 / 0.140 / 0.084
      level 0.24,  falloff 0.6                0.109 / 0.162 / 0.090
      off                                     0.089 / 0.104 / 0.072

Two readings. The first cut's level was a floodlight because the rod was a
hand's width from the dogs and Godot's falloff is the inverse square; the
level came down twentyfold before the frame read as warm. And the middle
column always leads, because the lamp is one point over the middle of a
pan whose outer columns sit twice as far from it; a flatter falloff closes
the gap more than any level does. The frames of a nearby stuttering tube
add a few percent of noise to any one row.

`final/lamp_att0_6_x1_0.png` is the shipped lamp; `final/lamp_att0_6_x0_0.png`
the same camera with it off.

## Priced (`perf_crowns_a.json`, `perf_heat_lamp.json`, `perf_crowns_a2.json`)

| package | mean median ms | mean p95 ms | mean GPU ms | mean draws | lights |
|---|---|---|---|---|---|
| crown build | 4.83 | 5.56 | 2.16 | 1079.6 | 93 |
| heat lamp (first cut) | 4.80 | 5.66 | 2.23 | 1079.7 | 94 |
| crown build again | 4.58 | 5.00 | 2.13 | 1079.6 | 93 |

Draws +1 in the six views that see the store; median ms +0.22 against a
control of +0.24. The level changed since and the price does not: the
lamp count and the draw are what cost.

## Open

- One grill carried a lamp in this lot although the store's slot list names
  two; the second was not found by the probe or the census. Not chased:
  it is where the second grill is, not what the lamp does.
- The walker's eye on the shipped level.
