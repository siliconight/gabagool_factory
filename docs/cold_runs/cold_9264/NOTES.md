# Cold run 9264 -- the wires held to a pixel, in a real drive

**What it tested:** Lot 0.119.1 in a real drive of restaurant_row_001: each wire vertex carries its
wire's drawn radius as its u, a vertex shader widens a wire thinner than a pixel to one and fades it by
the share it covers, the faces wound outward and the back culled. Everything else as in 9263.

**Result: 0 interventions, 0 tool files changed.** seed_9104 picked, as in 9241 to 9263, at the same
Laser Tag route completion 0.72 -- the graded lots carry no wires.

## As built

- **The export:** 497 models and 3,338 lightmap users, as in 9263; the 7 wire OBJs under
  `light_bake.json`'s `imports.unlit` and none under `baked`; the bake 29.0 s, the editor 56.8 s.
  Findings 119 -> 119.
- **The material:** both scenes that carry the wires -- `site.tscn` and Lux's
  `presentation/lux.applied.tscn` -- declare the Shader and the ShaderMaterial; each OBJ carries a `vt`
  for every vertex (364 in the first cell).
- **Found in it:** Lux's re-save wrote `shader_parameter/min_px = null`. Lot wrote `= 1`, an integer
  literal for a float uniform, and Godot reads that as no value (`docs/findings/pole_line/
  min_px_resave.gd`: written `1` or `2` it loads and re-saves null, written `1.0` or `2.0` it keeps).
  The wires drew as meant because the shader's own default is 1.0; any other `WIRE_MIN_PX` would have
  been lost. Lot 0.119.2 writes the float; not in this run.

## The price (`wires_price.sh`, `price/`)

The run's own package against a copy with the 7 wire nodes hidden in both scenes, Level Factory's
fixed stations, control / subject / control (the harness names the subject `glow`):

    controls' spread, median over 53 headings: p95 0.14 ms, draws 0.0 (the noise floor)
    run        draws +mean   draws +min   draws +max   p95 +median ms  p95 +max ms
    control_1          0.0            0            0             0.02         0.41
    subject            2.2            0            6            -0.02         0.94
    control_2          0.0            0            0            -0.02         0.66

The same +2.2 draws as 9263's 0.119.0 wires, and nothing the harness can tell from the noise in frame
time: drawn in the transparent pass by a vertex shader, the wires cost what the opaque ones did.

## The frames (`against_9263.png`, `wires.png`)

`against_9263.png`: 9263's 0.119.0 wires left, 9264's 0.119.1 right, at 9263's five wire stations,
then the far end of `line` enlarged three times. Within about 30 m the two read the same; past about
60 m, where 9263's wires break into dashes, 9264's are faint continuous lines. `wires.png`: 9264 with
the wires hidden and as built.

## The time

    run    shell   art     export   walk   retire   the drive
    9263   79 s    168 s   172 s    11 s   17 s     7.8 min (467 s)
    9264   86 s    182 s   173 s    10 s   18 s     8.2 min (493 s)

The retire step removed cold-9260-ws (0.9 GB).

## What is evidence of what

- The wires and the material: the package's scenes, OBJs and `light_bake.json`.
- The null: `docs/findings/pole_line/min_px_resave.gd` and its `.out.txt`.
- The price: `price/` (three reports, `price.txt`, `wires_off.txt`).
- The frames: `against_9263.png`, `wires.png`; the PNGs under `_scratch/frames_9264/`.
- The result: `cold_run.py --end`.
