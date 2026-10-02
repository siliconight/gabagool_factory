# Failing fixtures (Lux 0.62.0) -- paused mid-build, 2026-10-02

The walker asked for a safe pausing point. The Lux working tree was
REVERTED to 0.61.0 so a cold run can begin clean; everything built is here.

## What is here
- `patch_lux_failing_fixtures.py` (one level up): every edit to Lux, anchored.
  It expects `lux_failing.gd` at `lux/addons/lux/runtime/` first -- copy
  `lux_failing/lux_failing.gd` there, then run the patch.
- `lux_failing.gd`: the model (STUTTER, CYCLING, WAVER) and `find_lens`.
- `failing_probe.gd`: the scratch probe. Copy a walk export, drop the new
  Lux scripts into its `runtime/lux/` with `res://addons/lux/` rewritten to
  `res://runtime/lux/`, put this at the copy's root, delete `.godot`, import
  headless, run windowed with `--script`.

## The design the walker approved
One failing fixture an anchor (a ceiling row is a room's): a fluorescent
stutters, a pendant wavers; every third streetlight CYCLES (dims, cuts out,
sits dark, restrikes). Everything else steady -- the loader's always-on
12 % / 9 Hz wobble on every row goes to 0. A failing rig moves its lamps
AND the nearest lit face to each lamp, on that face's own material override.

## What the first probe run said (scratch copy of run 9137's walk export)
    FAIL respawn: Spawned 64 fixture light(s) from 64 marker(s)
    FAIL rigs=146 failing=12 kinds={ 1: 9, 3: 3 }
    FAIL lenses bound=0
    FAIL tube=false pole=true pole lenses=1

The spawner's choice works: 9 stuttering tubes and 3 wavering bulbs across
the lot, one an anchor. THE FLUORESCENT RIGS BOUND NO LENS, so a tube's
light would move while its diffuser stayed lit -- the exact failure the
design exists to avoid -- and the probe stopped there by design (it refuses
to watch a tube with no lens). The pole bound its lens (the same code),
so the difference is in where the fluorescent lamp sits relative to its
diffuser: `FLUORESCENT_MOUNT` hangs the lamp below the anchor, and
`find_lens` looks within 1.5 m of the LAMP. First thing to check: the
distance from a spawned fluorescent lamp to its own diffuser's box, and
whether the import merged the diffusers into one mesh (then the override
would dim every tube in the building and the bind must be per-surface of a
per-fixture mesh, or refused).

## Not done
- The lens bind for fluorescents (above).
- The watch: energy and lens traces, a bright and a dim frame, drop counts.
- The perf A/B with a control pass; Lux CHANGELOG; the cold run.
