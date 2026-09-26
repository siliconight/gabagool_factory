# Pricing a wet `next_pass` — roadmap 157 slice 2, RAIN_WETNESS.md item 2

Package: `LF_crossroads_9600.portable-godot` (cold-run export, unmodified — the
probe stages a copy per arm and never touches the package).
Renderer: the package's own, GL Compatibility. 1280x720, vsync off,
`Engine.max_fps = 0`, `viewport_set_measure_render_time` on.
3 rounds x 300 samples per station, 4 arms, 6 stations.

Produced by `level_factory/tools/wet_ab_run.py` + `wet_ab.gd`.

## Files

- `wet_ab_4arm_3round.json` — the result. `run.txt` is its console output.
- `SUPERSEDED_blind_instrument.json` — **do not quote this one.** Kept because
  the refutation is cheaper to keep than to rediscover.

## Why the superseded run is superseded

Its probe omitted the four setup lines `occlusion_ab.gd` has carried since it
was written — window size, `Engine.max_fps = 0`, vsync disable, and
`viewport_set_measure_render_time`. Three of its six stations came back pinned
at 6.066-6.073 ms in every arm and every round, which is a refresh interval and
not a frame time, and `cpu_ms`/`gpu_ms` read 0.00 everywhere. Its frame-time
deltas at the three unclamped stations were close to the corrected run's
(+3.29/+5.38/+7.39 vs +3.26/+5.21/+8.06 ms), so it was not wrong so much as
unable to say anything — in particular it could not distinguish submission cost
from fill cost, which is the question that decides whether narrowing the surface
set helps at all.

The runner now refuses a run whose stations all report a zero CPU/GPU split,
for the same reason it already refused one whose draw calls did not rise.

## WITHDRAWN 2026-09-26 -- do not quote these figures either

The superseded run below was superseded for a blind instrument. The run that
replaced it had a second, larger problem nobody saw at the time: its
`next_pass` was `blend_mix, depth_draw_never` with no vertex offset, which GL
Compatibility's depth test rejects. `assets/godot/zoo_worldskin.gd` had
measured exactly that variant as "not drawn" before this probe existed.

So BOTH runs in this directory priced submissions with a fragment that never
ran. The corrected measurement is in LF 0.115.0's changelog and was taken on
cold run 9080's package, not this one.

The whole directory is kept because the retraction is the useful part: a
control that proves the instrument can SUBMIT is not a control that proves it
can DRAW.

## The finding

The pass bills **per draw call, not per pixel**: 2.27-4.29 us per added
submission, median 3.5, flat across 18 station-arm pairs whose wet-surface
screen coverage differs wildly. See RAIN_WETNESS.md, "What item 2 measured".
