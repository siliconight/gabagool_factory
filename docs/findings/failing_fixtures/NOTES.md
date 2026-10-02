# Failing fixtures (Lux 0.62.0), measured

The design the walker approved on 2026-10-02 ("one per room is fine, go
with cycling streetlights"): one fixture an anchor fails, a fluorescent
stutters, a pendant wavers, every third streetlight cycles; everything else
is steady, and a failing fixture's lens moves with its lamp. The build is
`patches/patch_lux_failing_fixtures.py` plus `patches/lux_failing/`.

## The probe (`patches/lux_failing/failing_probe.gd`)

A scratch copy of cold run 9137's walk export with the 0.62.0 scripts dropped
in, windowed, the fixtures re-spawned after the warm-up so the spawner's
choice runs. It prints what it measured and stops.

    FAIL respawn: Spawned 64 fixture light(s) from 64 marker(s)
    FAIL rigs=146 failing=12 kinds={ 1: 9, 3: 3 }
    FAIL lenses bound=12
    FAIL tube=true pole=true pole lenses=1
    FAIL tube base energy=6.0 lens base emission=1.86000001430511
    FAIL watched 3946 frames over 24.0 s: tube energy min=3.64978265762329
         max=6.0 drops=10 | pole energy min=0.45845380425453 max=2.49988961219788

`kinds` 1 = STUTTER, 3 = WAVER. The three cycling poles are chosen by the
loader at export time, which this probe does not re-run; it makes one pole
cycle by hand instead (seed 12345), and that is the `pole energy` line: a
24 s window of a 40-70 s cycle, from near dark through the restrike.

## Two refutations kept

- The first run: `lenses bound=0`, `tube=false`. The bind ran at `_ready`,
  and `LuxFixtureSpawner` sets a rig's `global_transform` AFTER `add_child`,
  so every lamp was at the container's origin when it looked for its lens.
  `_bind_lenses.call_deferred()` binds 12 of 12. The pause note's first
  guess (`FLUORESCENT_MOUNT` hanging the lamp out of range) was wrong.
- The second run: `drops=0` beside `min=3.65`. The probe compared the lamp
  with the rig resource's `energy` (2.2); the preset scales that to 6.0 on
  the lamp, so the 0.9 threshold sat at 1.98 and nothing crossed it. It now
  compares with the lamp's own first frame. Fixed, 10 drops in 24 s, which
  is two or three bursts of two to four, as the model says.

## Frames

`tube_bright.png`: the tube at frame 5, full. `tube_dim.png`: the first
frame of the first drop. The diffuser goes from white with a bloom to a warm
cream without one; the ceiling tiles around it darken with the lamp.

## Priced

In Lux's 0.62.0 changelog entry: 53 views, draws identical in every view;
median frame time within the instrument's own pass-to-pass spread (new minus
control mean -0.01 ms; the same bytes run twice differed by +0.68 ms mean).
Perf reports: `_runs/perf_inner/fail_a.json` (9137 as shipped), `fail_b.json`
(re-exported with 0.62.0), `fail_a2.json` (9137 again, the control).

## Not yet seen

A cycling pole in a level the pipeline exported, and a stuttering tube in a
level nobody re-spawned by hand. Cold run 9138 is the first package with
this Lux; its in-level frames are the check.
