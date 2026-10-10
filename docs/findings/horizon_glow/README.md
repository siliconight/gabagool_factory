# The horizon glow, seen and priced (roadmap 228, step A; Lux 0.73.0)

**What shipped.** `LuxHorizonGlow`: a ring LuxRoot builds from the preset,
380 m out, opaque dark land below the horizon and the preset's colour at a
standing eye's height fading out by 20 degrees. Sodium at night, a haze by
day. One draw, unshaded, fog ignored. The walker's pick from the edge menu
(E) has it, as every option did; it is the part that lands first and alone.

**How it was seen.** Lux 0.73.0, as drafted, vendored into a copy of cold
run 9221's walk copy of club_block_014 (midnight, Delco Night), the copy
re-imported, and `tools/look_shots.py` run on it and on the copy as shipped
at the edge menu's five stations plus look_shots' own eight cameras.
`sky_band.py` reads each pair: the band of rows 20% to 46% down the frame,
the sky from a little above the horizon up, as mean luma and warmth (mean
R - B).

| station | luma, as shipped | luma, glow | warmth, as shipped | warmth, glow |
|---|---|---|---|---|
| elev_N, E, S, W (look_shots' elevated cameras, out over the plate) | 0.87 to 0.88 | 25.4 to 26.9 | -0.3 | +26.3 to +28.6 |
| north_lot (across the open lot) | 0.94 | 5.46 | -0.5 | +4.2 |
| west_end (down the main road) | 2.73 | 5.49 | +0.4 | +3.3 |
| north_road1 (up the side road) | 4.25 | 6.95 | +0.9 | +3.7 |
| east_end | 1.53 | 3.00 | -1.5 | +0.1 |
| objective, south_rows, spawn, extraction (interiors and street level facing in) | unchanged | unchanged | unchanged | unchanged |
| overview (high, looking down) | 3.71 | 2.06 | -3.0 | +0.4 |

The full table is `sky_band.txt`; `edge_pairs.png` lays four stations out,
as shipped on the left and the glow on the right.

**What the frames show.**
- **At eye level** the glow is an orange band over the pale perimeter
  wall, fading up into the sky's stars: the town's light beyond the edge.
  The wall itself is still the brightest thing in the frame; that is step
  B's.
- **From the elevated cameras** the whole sky above the rowhome roofline
  goes sodium, and the houses' silhouettes and lit windows stand against
  it. It reads as a lit city's overcast sky rather than a clear starry one,
  and it is the strongest the glow gets. `horizon_glow_energy` is the dial,
  per preset; whether Delco Night's 1.0 is right there is the walker's call.
- **The overview** darkens a little: the ring's opaque land replaces the
  sky's ground colour under a camera looking down from high up.

**The price** (`price_glow.py`, this machine, windowed; `price.txt` and the
three reports beside it): Level Factory's fixed-station harness, 53 headings
at the level's 14 gameplay stations, the glow copy bracketed by two runs of
the copy as shipped.

| run | draws, +mean a heading | p95 frame, +median | p95 frame, +worst heading |
|---|---|---|---|
| control 1 | +3.0 | -0.11 ms | +0.61 ms |
| **glow** | **+1.0** | **+0.19 ms** | **+1.81 ms** |
| control 2 | -3.0 | +0.11 ms | +0.32 ms |

- **The controls' own spread** is a median 0.23 ms a heading, p90 0.51,
  worst 1.23. The glow's median, +0.19 ms, is inside it; its mean is +0.31
  and its p90 +0.93.
- **8 of 53 headings** exceed the controls' spread by more than 0.5 ms. The
  worst is `extraction_4` facing 270, +1.81 ms on the level's heaviest frame
  (11.8 ms as shipped, 13.6 with the glow); then `highest_vantage` facing
  90 at +1.62 and `extraction_7` facing 90 at +1.35.
- **Why a single draw costs anything:** the ring is a blended surface, so
  it pays fill rate wherever the sky fills the view, and the depth test
  rejects it only behind opaque geometry. The headings that pay are the
  ones looking along a street to the open sky.
- **The draws' ±78 at one heading** appear between the two controls too;
  the draw figure is the mean, +1.0.

**What the expensive version would buy, and the cheaper one.** This is the
provider-agnostic form: it works over Lux's own sky and over a sky provider's
panorama alike. The glow in the sky's own shader would cost nothing a frame,
and waits on a provider whose shader Lux may write. If runtime data from
real sessions says the fill matters on the low-end target, that is the
next form, and the dial until then is `horizon_glow_energy`, 0 drawing
nothing.

## Instruments

- `sky_band.py <control shots> <glow shots> [--sheet OUT.png]`: the table
  and the pairs.
- `price_glow.py <control copy> <glow copy> <out>`: Level Factory's
  fixed-station harness, control, glow, control, compared heading by heading
  as the menu was (`docs/findings/edge_menu/price_edge.py`).
- The vendoring: the scratchpad's `vendor_lux_from.py`, which copies the
  addon tree into the package's `runtime/lux/` with the localize rewrite and
  clears `.godot` so the new `class_name` enters the class cache on import.
