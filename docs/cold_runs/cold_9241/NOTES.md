# Cold run 9241 -- the dome's fix on 9233's lot: two meshes a dome, and the glass under its canopy

**What it tested:** Zoo 1.98.1's two fixes to cold run 9239's dome -- the
frosted bowl laid by its depth below the canopy and closed inside it, where
1.98.0 had turned it up into the ceiling; and the canopy and finial one mesh,
where 1.98.0 built a dome as three meshes beside a troffer's two -- on the same
lot (restaurant_row_001, seed auto, 9233's brief). It ran on Zoo 1.99.1,
whose hemisphere helper now keeps the upper half: the dome lays its bowl by
|z| and built the same vertex for vertex on 1.99.0 and 1.99.1
(`docs/findings/hemisphere_half/dome_same_probe.py`). Priced against 9238's
package (troffers, the dome's control) and framed beside 9238's and 9239's.

**Result: 0 interventions, 0 stops.** Three candidates, seed_9104 picked as
in 9238 and 9239, findings 123 as both. The bake: 491 models and 224
primitive meshes lightmapped, 213 steady rigs baked and 29 failing left live
(as 9239: a dome is never chosen to fail), and **3,518 lightmap users -- 9238's
count, where 9239's three-mesh domes made it 3,524.**

## The layer (`docs/findings/fixture_merge/layer_count.py` on each run's shipped deli fixtures GLB)

| run | the deli's fixtures | submissions | dome metal | dome glass |
|---|---|---|---|---|
| 9238 | 91 troffers, 23 pendants, a sign box, a wall pack | 257 | -- | -- |
| 9239 | 85 troffers, 6 domes (1.98.0), the rest the same | 263 | 12 | 6 |
| 9241 | 85 troffers, 6 domes (1.99.1), the rest the same | 257 | 6 | 6 |

A dome is two meshes now, as the troffer it replaced: the canopy-and-finial
in the metal and the glass in the lens. 9239's +6 is gone at the source.

## The price (`price/`, 9238's package the control)

    measured control_1  53 headings  draws mean 2524 worst 5257  p95 median 5.81 ms
    measured glow       53 headings  draws mean 2524 worst 5257  p95 median 5.19 ms
    measured control_2  53 headings  draws mean 2524 worst 5257  p95 median 5.24 ms
    controls' spread, median over 53 headings: p95 0.39 ms, draws 0.0 (the noise floor)
    draws vs controls' mean: median 0.0  min 0.0  max 0.0
    p95 ms vs controls' mean: median -0.20  min -6.62  max +0.58

**+0 draws at every one of 53 headings**, where 9239 read +6 at 24 of them
(one a dome in view): six domes now cost what the six troffers they replaced
did. The p95 at -0.20 ms sits inside the controls' 0.39 ms spread; this
run's first control was noisy (one heading at +7.23 ms against its own
second pass), which widened the spread and is not the subject's.

## Seen (`fixtures.png`, `dome_zoom.png`; `fixture_frames.sh`)

Inside the deli's apartment hideout, 3 m off each row's first lamp: 9238
(troffers), 9239 (1.98.0's dome) and 9241. The room reads warm in 9239 and
9241 as 9239 first showed. The FIXTURE now reads as a dome: `dome_zoom.png`,
each frame's brightest blob in its upper half cropped and enlarged, shows
9238's troffer diffuser, 9239's dark canopy with its finial hanging alone and
a sliver of glass above its rim, and **9241's lit frosted bowl under the
canopy's rim with the finial at its bottom** -- the flush-mount dome the
species was written to be.

## What is evidence of what

- The draws, the layer counts and the lightmap users are this run's
  package's and its jobs' (Zoo 1.99.1, Lux 0.75.0, Deli Counter 0.208.0).
- The look is two stations in one room on one lot; a residence-heavy lot
  is still the look owed for homes at large.
- Roadmap 229's species step stands as landed and proven: the dome is the
  first species, and the pendant, strip light, sconce, high-bay and exit
  sign are its remainder.

## Instruments

- `price/`: the perf reports, `price.txt`, `vs_mean.txt`, `price_vs_mean.py`.
- `fixture_frames.sh` and `tools/fixture_stations.py`: the frames, the sheet
  `fixtures.png`; `dome_zoom.png` crops each frame's brightest blob.
- `docs/findings/fixture_merge/layer_count.py`: the layer table above.
