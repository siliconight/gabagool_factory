# Failing fixtures (Lux 0.62.0) -- shipped, 2026-10-02

Picked back up from the pause the same day. The Lux working tree carries
0.62.0; `patch_lux_failing_fixtures.py` (one level up) applies every edit to
a clean 0.61.0 and copies the two new files from here.

## What is here
- `lux_failing.gd`: the model (STUTTER, CYCLING, WAVER) and `find_lens`.
  Installed at `lux/addons/lux/runtime/lux_failing.gd`.
- `failing_fixtures_selftest.gd`: 55 checks; installed at
  `lux/tools/failing_fixtures_selftest.gd`. Dies on 0.61.0.
- `failing_probe.gd`: the scratch probe that produced the measurements in
  `docs/findings/failing_fixtures/NOTES.md`. Copy a walk export, drop the
  new Lux scripts into its `runtime/lux/` with `res://addons/lux/` rewritten
  to `res://runtime/lux/`, put this at the copy's root, delete `.godot`,
  import headless, run windowed with `--script`.

## The design the walker approved
One failing fixture an anchor (a ceiling row is a room's): a fluorescent
stutters, a pendant wavers; every third streetlight CYCLES (dims, cuts out,
sits dark, restrikes). Everything else steady -- the loader's always-on
12 % / 9 Hz wobble on every row goes to 0. A failing rig moves its lamps
AND the nearest lit face to each lamp, on that face's own material override.

## What was wrong at the pause, and what it was
The fluorescent rigs bound no lens. Not the mount height: the spawner places
a rig AFTER `add_child`, so a bind at `_ready` searched from the container's
origin. Deferred, 12 of 12 bind. The probe's drop counter then compared the
lamp with the unscaled rig energy and could not fire; it compares with the
lamp's first frame now.

## Done
- The watch: 24 s, 10 drops, the lens following; frames bright and dim.
- The perf A/B with a control: draws identical in 53 views, frame time
  within the instrument's spread. Lux CHANGELOG 0.62.0.
- The selftest, and the existing eight pass unchanged.

## Next
Cold run 9138 on gas_block_001 (the first package with this Lux), priced
against 9137, with in-level frames of a stuttering tube and a cycling pole.
