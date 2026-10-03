## [0.63.0] - the roller grill's heat lamp

The walker, 2026-10-03, on the grill walked at night: "can we add a dim but
warm warming light to bring a bit more light to the dogs", and on the first
cut, "light should show the buns too, not seeing those". Zoo 1.57.0 hangs an
infrared element under the grill's hood and emits `LuxEmit_heat_lamp` just
below it; 1.57.1 moved the element up under the hood's top, above the bun
shelf, where a real one is. This is its lamp.

`heat_lamp` in the loader: an OMNI (the fluorescent rig's machinery, one
lamp, no row, no downlight cone), so the buns under it and the dogs through
the glass shelf both get it, at `HEAT_LAMP_LEVEL` (0.16) of a fluorescent's
energy, `HEAT_LAMP_ATTENUATION` 0.6 (the inverse square flattened, so the
outer columns of the pan see it as well as the middle), in
`HEAT_LAMP_RANGE_M` (0.9): the reach is the hood, not a drop. 1,900 K: an
infrared element glows red-orange, redder than any bulb. Not preset scaled
and steady.

Measured on the rebuilt gas station lot, the grill shot from the customer's
side, the pan's three columns' luminance left / middle / right:

    under the shelf, level 0.35, falloff 2 (the first cut)  blown out
    under the shelf, level 0.035, falloff 2                 0.106 / 0.216 / 0.084
    under the shelf, level 0.035, falloff 1                 0.095 / 0.131 / 0.080
    under the hood,  level 0.08,  falloff 1                 0.096 / 0.136 / 0.079
    under the hood,  level 0.16,  falloff 1                 0.100 / 0.154 / 0.077
    under the hood,  level 0.16,  falloff 0.6  (shipped)    0.115 / 0.140 / 0.084
    under the hood,  level 0.24,  falloff 0.6               0.109 / 0.162 / 0.090
    off                                                     0.089 / 0.104 / 0.072

A third of a troffer at a hand's width was a floodlight; the shipped value
lifts the outer columns a quarter and the middle a third, warms the buns
under the rod, and leaves nothing white. The level is the walker's dial from
here; every row above is kept so the next hand knows what each setting
looked like.

Priced on the fixed-station harness, fresh copies, idle machine, the crown
build before it as the control, one session (the first cut's energy; the
lamp count and the draw are what cost, not the level): draws +1 in the six
views that see the store (the element's lit face), the light census 93 to
94 (one grill carried a lamp in this lot), median frame time +0.22 ms a view
against a same-bytes control of +0.24 -- within the spread.

`tools/heat_lamp_selftest.gd` holds: the rig's energy, range and falloff,
its colour (redder than the incandescent), one lamp and no row, not preset
scaled, steady, an omni; the marker path spawns one lamp named for the
marker, standing on it; a power cut kills it and restores it; the counter
accent still scales and a fluorescent still takes its drop range.

