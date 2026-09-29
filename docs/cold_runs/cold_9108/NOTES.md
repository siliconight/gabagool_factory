# Cold run 9108 -- the pylon's lettering

The walker, 2026-09-29: "do the pylon brand sign at night next". Zoo 1.25.0
sets the price pylon's name and prices as large as the face allows. Zero
interventions; findings identical to 9107 (58).

MEASURED FIRST (on 9107's walk copy, the pylon rebuilt with Zoo exactly as
Lot's cover kit asks for it and swapped in with the shipped texture import
settings; the rebuilt control reproduced the shipped frame to the decimal):
the green brand field DID read at night (luma 125 at 12 m); what read at
neither time of day was any letter. The cold run then reproduced the
prototype's figures exactly:

    at 12 m, square to the face (mean / standard deviation)
                       9107 (Zoo 1.19.0)    9108 (Zoo 1.25.0)
    brand, night       125.0 / 47.8         157.0 / 59.1
    brand, noon        143.2 / 26.1         161.6 / 32.8
    prices, night      250.8 / 10.5         250.3 / 11.0
    prices, noon       231.4 / 11.3         228.8 / 11.6

FLAPPHAS reads as a bold word at 12 m; the digits still do not resolve
there. THE LIMIT: eight 5-wide letters across a 2.3 m face cannot carry a
stroke over ~5 cm, which this frame keeps to about 12-14 m; at 20 m every
variant measured read as coloured blocks. A transmitted glow (emission the
square root of the artwork in linear light) was measured and not shipped:
field 125 -> 222, name detail 48 -> 17, the sign at noon 143 -> 196.

In the harness, two instrument traps worth keeping: a swapped GLB points at
its images in a shared `cover/_tex/`, and a PNG Godot sees for the first time
imports WITHOUT mipmaps -- the art then aliases to scattered dots. The first
two variant sweeps measured those artefacts and were discarded.

COST: draws identical at all 53 headings (71,827 summed, both 9108 runs).
Frame time not measurable this session (9107's median p95 read 7.61 ms here
against ~5 in earlier sessions; the two 9108 runs 7.61 / 6.49). 9107's summed
draws read 71,868 in the previous session and 71,827 in this one: summed
draw counts are not perfectly reproducible across sessions, while every
within-session comparison has agreed heading by heading.

`pylon_12m_before_after.png`: 9107 night, 9108 night, 9107 noon, 9108 noon.
