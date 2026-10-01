# Cold run 9126 -- the canopy at 4.5 x the reference pool

Lux 0.61.0: `CANOPY_WASH_LEVEL` 1.5 -> 4.5 x `REFERENCE_POOL`, chosen by the
walker from a measured sweep. Same brief, same seed, same lot as 9125. Zero
interventions, one observation.

The art leg before export: 0 blockers, 63 findings -- identical to 9125's by
code. Export closure clean. The shipped wash energy is 93.42 where 9125's was
31.14: exactly 3x, as the level change says it should be.

## The sweep that chose it (`canopy_sweep.png`, `canopy_sweep.json`, `canopy_sweep.py`)

On 9125's walk copy, the four canopy washes' baked energies scaled by k
(`presentation/lux.applied.tscn`, rig `energy` and SpotLight `light_energy`,
8 numbers, guarded), the scene restored byte for byte after. k = 1 shot twice
as the control: identical to the decimal. Median luminance:

    k   the pad (07)   inner pump face (04)   outer face (05)   pad clipped
    1      10.7             23.0                  23.2            0.03%
    2      42.9             44.2                  43.4            0.05%
    3      53.8             54.4                  55.1            0.05%
    4      62.5             57.7                  60.6            0.06%

The first pass of the sweep scaled only the lights, not the rigs -- the scene
is CRLF and the rig pattern spanned lines on LF -- and its own guard (8 lines
expected, 4 changed) stopped it before a frame was shot.

## The shipped level (`look_forecourt_9126.json`)

    pad (07) p50 53.8 (sweep 53.8); faces 54.4 / 55.2 (sweep 54.4 / 55.1); pad clipped 0.05%

## The price (`perf_9126.json`, against 9125's)

    total draws, 53 headings   61,161 -> 61,201  (+40, one heading)
    worst heading              2,626 -> 2,626
    meshes over the 8-light cap 44 -> 44

An energy-only change was predicted to move no draws, and that prediction was
WRONG at one heading: defender_spawn_22, yaw 180, 770 -> 810. The same heading
went 810 -> 770 when 9125 moved the washes over the lanes, so it has toggled
twice and is back to 9124's count. The mechanism is not established and is
not asserted; a light whose reach crosses a mesh's culling or shadow test at
that station is one candidate.
