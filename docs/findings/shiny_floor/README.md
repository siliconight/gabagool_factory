# The supermarket's floor: what would make it shine

The walker, 2026-10-26: "shiny floor, bright lights, isles, glowing freezer section, stacked high". The comps are
in [`docs/reference/GROCERY_STORE_COMPS.md`](../../reference/GROCERY_STORE_COMPS.md): pale vinyl tile polished
until it mirrors each fluorescent run as a streak down the aisle.

## What the floor is (`floor_material_probe.gd`)

Run headless on the walker's walk copy (`levels/restaurant_row`, seed 9205, Deli Counter 0.272.0, Level Factory
0.257.0) at the walker's station, the floor point (24.4, 0.05, -6.8) in Godot metres:

- **The floor:** `MergedR_117`, a 44 x 24 m merged slab, surface `M_Skin_tile_delco_1997`. Roughness 1.0 times
  `vct_floor_beige_roughness_*.png`, which is Pixelcoat's `vct_floor_beige` with a roughness base of 0.35.
  Metallic 0, specular 0.5.
- **The room's ReflectionProbe:** `b1_sales_floor_ambient`, 44.2 x 4.4 x 24.2, intensity 1.0, interior, box
  projection OFF, updated once, ambient mode colour (Lux's `room_ambient`).

So the reflection is already there, at full intensity, and blurred by a roughness of about 0.35.

## Arms (`gloss_arms.py`, `gloss_arms.out.txt`)

Copies of the walk preview. An autoload changes the loaded scene; nothing is re-baked. The station is the walker's
view down the sales floor plus a low one. The frames are under `_scratch/shiny_floor/` and are not kept.

| arm | walker_sales mean / p50 | sales_low mean / p50 |
|---|---|---|
| shipped (the walk as it is) | 44.4 / 42 | 89.9 / 86 |
| noop (copy + an autoload that does nothing) | 44.4 / 42 | 89.9 / 86 |
| box projection on | 44.3 / 42 | 90.1 / 87 |
| VCT roughness 0.12 | 44.9 / 43 | 90.7 / 87 |
| both | 44.7 / 42 | 91.1 / 88 |

- The noop arm reproduces the shipped frame exactly, so the instrument can see a difference.
- Looked at, side by side: the polished arm shows one faint highlight near the stockroom door and nothing down the
  aisle. There is no streak under the fixtures.

## What it says

A polished floor reflects what the probe captured, and the probe captured a dark room. In this build the ceiling
over the walker's view is grey, a dozen small troffers 11 m apart are the only bright things in it, and the probe's
capture is taken once, at load, from the room's centre. Polishing alone moves the frame by less than one level. The
"bright lights" change, Deli Counter 0.274.0's 40 lamps where there were 12, is the precondition. These arms are
re-run on that build before anything about the floor ships.

Also seen in the frames, not measured: the tile reads as a strong 1 m checker of four shades. The comps' VCT is one
pale colour with faint joints.
