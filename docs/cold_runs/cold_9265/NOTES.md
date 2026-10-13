# Cold run 9265 -- the sun baked, in a real drive

**What it tested:** Lux 0.76.0 in a real drive of restaurant_row_001 -- the sun static with the
preset's shadows in the editor, so Level Factory's bake traces them; static and unshadowed at run time
while a lightmap shows; dynamic with its shadows when none does (roadmap 243, the walker's call of
2026-10-12 after `docs/findings/lux_tiers/`). And Lot 0.119.2's wires writing their pixel floor as a
float. Everything else as in 9264.

**Result: 0 interventions, 0 tool files changed.** seed_9104 picked, as in 9241 to 9264, at the same
Laser Tag route completion 0.72.

## As built

- **The export:** 497 models and 224 primitive meshes lightmapped, 6 kept dynamic, 1 spawned set
  dynamic, 210 steady rigs baked and 27 failing left live, 215 room fills, 3,338 lightmap users -- as
  in 9264; the bake 32.7 s against 29.0 and the editor 60.9 s against 56.8. Findings 119 -> 119.
  **RETRACTED, KEPT:** this line said the extra seconds were "the sun's shadows now traced". Cold run
  9266 baked the same sun the same way in 28.9 s and 55.8 s, under 9264's: run-to-run variation.
- **Lux:** the package's vendored `runtime/lux/runtime/lux_lighting.gd` is 0.76.0's, byte for byte
  but its line endings.
- **Lot 0.119.2:** `shader_parameter/min_px = 1.0` in `site.tscn` and in Lux's re-saved
  `presentation/lux.applied.tscn`, where 9264's re-save wrote null: the float survives the re-save.

## The sun as the game runs it (`sun_state.gd`)

Headless on an imported copy of each package: the game's main scene, Lux's lightmaps bound, then the
power cut and back. 9264 is the control -- a probe that cannot read "dynamic, shadowed" there cannot
see the change.

    9264 (Lux 0.75.0)  frame 5, frame 35   dynamic, shadowed; lightmaps with data 1 of 1
                       power cut           dynamic, shadowed; 0 of 1
                       power back          dynamic, shadowed; 1 of 1
    9265 (Lux 0.76.0)  frame 5, frame 35   static, unshadowed; 1 of 1
                       power cut           dynamic, shadowed; 0 of 1   (daylight stays with the lamps out)
                       power back          static, unshadowed; 1 of 1

## The editor's case, proven by the frames (`luma.py`, `sun_baked.png`)

Lux's self-test cannot set `Engine.is_editor_hint()`, so whether the bake traced the sun WITH its
shadows rests on the frames. 9265 against the findings' arms on 9264's package -- B2, the copy whose
sun was built static with its shadows and re-baked (the arm 0.76.0 was written from), and the re-bake
control (nothing changed: the noise floor of a re-bake):

    station    9264 live        9265 baked      B2              re-bake control
    line       37.4 (10.8)      33.0            33.0 (1.9)      37.4 (10.8)
    corner     51.8 ( 7.2)      51.6            51.6 (2.4)      51.9 ( 7.2)
    up         52.9 (13.4)      47.2            47.1 (2.4)      52.9 (13.4)
    spawn      20.7 ( 4.5)      18.1            18.1 (1.6)      20.6 ( 4.5)
    objective   6.5 ( 1.7)       6.5             6.5 (1.7)       6.5 ( 1.8)
    elev_N     57.3 (13.8)      63.9            63.9 (2.5)      57.3 (13.8)
    (mean luma 0-255; in brackets the mean absolute difference from 9265's frame)

9265 reads as B2 to 0.1 of a level at every station, inside the re-bake's own 1.6 to 2.5. So the editor
baked the sun as a STATIC light: left dynamic there, the lightmap would hold only its bounce, and at run
time 0.76.0's static sun lights no lightmapped surface. The frames: `sun_baked.png`, 9264 left, 9265
right, a row a station.

**RETRACTED, KEPT:** this section first said a sun baked without its shadows reads flat, "the findings'
arm B, the objective 15.0 where this reads 6.5". 15.0 is arm A's -- the LIVE sun unshadowed -- and B,
the sun baked with its shadow flag off, reads as B2 within a re-bake's noise at all six stations
(`docs/findings/lux_tiers/README.md`): the flag does not change the bake. Lux 0.76.1 corrects the same
claim in Lux's comment and changelog.

## The price (`sun_price.sh`, `price/`)

9264's package as both controls, 9265's the subject (the harness names it `glow`), Level Factory's 53
station headings, GL Compatibility, the RTX 2060:

    controls' spread, median over 53 headings: p95 0.24 ms, draws 0.0 (the noise floor)
    run        draws +mean   draws +min   draws +max   p95 +median ms  p95 +max ms
    control_1          0.0            0            0            -0.03         0.68
    subject        -1854.4        -3472          -30            -3.03         0.37
    control_2          0.0            0            0             0.03         0.54

Draws 2,642 -> 788 a heading, every heading fewer, the worst 5,740 -> 2,805; the p95 frame's median
7.62 and 7.09 ms -> 4.20; 47 of 53 headings faster beyond the noise and one slower, by 0.37 ms at most;
headings over 16.7 ms at p95 5 -> 1, the worst 20.2 -> 17.3 ms. The same -1,854.4 draws as the
findings' B2, in the generator's own output.

## What it changes besides the price

At blue hour's sun, 4 degrees up, the baked sun and the live one disagree about what is in shadow; the
walker chose this look from B2's frames. Measured since, on this run's frames and 9264's
(`docs/findings/lux_tiers/`, "What the baked sun changes"): the backdrop is not in the bake. Level
Factory bakes `bake.tscn` -- the presentation scene and its LightmapGI -- and the game's `mission.tscn`
loads `site_backdrop.tscn` (268 rowhomes and a water tower, 25 MultiMeshes) beside it. Under the baked
sun the backdrop takes the sun with no shadow from anything (corner's far row, elev_N's homes), and its
long shadows no longer fall on the level (up, line). On the level's own sunlit faces the baked sun also
reads darker than the live one with the backdrop's shadow taken away (up 46.9 against 59.1), of which a
lightmap's missing specular is 1.6; the rest is not attributed.

## The tool versions

Lux 0.76.1 (a correction to 0.76.0's comment and changelog, no behaviour change) was committed after
this run ended; the run carries 0.76.0.

## The time

    run    shell   art     export   walk   retire   the drive
    9264   86 s    182 s   173 s    10 s   18 s     8.2 min (493 s)
    9265   88 s    200 s   181 s    12 s   18 s     8.7 min (524 s)

The export's 8 s is the bake's (32.7 against 29.0 s) and its editor's -- not the sun's (9266, the same
Lux behaviour: 28.9 s). The retire step removed one workspace (0.9 GB).

## What is evidence of what

- The sun's state: `sun_state.gd`, `sun_state_control.out.txt` (9264), `sun_state_subject.out.txt`.
- The editor's case and the look: `luma.py`, `luma.out.txt`, `sun_baked.png`; the PNGs under
  `_scratch/frames_9265/`.
- The price: `price/` (three reports and `price.txt`); `sun_price.sh` ran all of the above.
- The package: its `light_bake.json`, its vendored `lux_lighting.gd`, its two scenes' `min_px`.
- The result: `cold_run.py --end`.
