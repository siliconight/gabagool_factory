# Two prices of one build disagreed on draws: one stray frame in a window

**Question (2026-10-29).** Slice 9's price (`docs/findings/slice_look/perf_s9_*`) read a controls' draw floor of 87:
two harness runs over the SAME package disagreed. The slice's changes ship on draw deltas, so a floor that moves can
hide a change or invent one.

**Answer.** `perf_stations.gd` reported each heading's draws as the MAXIMUM over its 60-frame window, and at two
headings the scene now and then submits one frame higher than it holds. Whichever stray frame a window caught became
the count. Level Factory 0.269.0 reports each window's p95 and keeps the maximum beside it as `draws_max`; three runs
of it over one package agree at all 53 headings, in both passes and across runs, and equal the earlier report at
every heading. Why the scene spikes is not established.

## Retracted, kept

1. **"The harness reads a heading's draws before the camera's turn reaches the renderer."** Read off a diff of
   `perf_s9_control_a.json` against `_b.json` that paired each station's headings BY POSITION. The harness writes
   `headings` sorted by p95, not by yaw (`per.sort_custom`), so the order differs between runs and the "swaps" at
   defender_spawn_20 and highest_vantage (43/32, 88/103) were the diff comparing different headings. Keyed by yaw
   they match. `tools/price_verdict.py` keys by `(station, yaw)` and was never affected. Two headings genuinely
   differed: attacker_spawn_9 yaw 0 (616 / 703) and camera_socket_0 yaw 180 (987 / 1008).
2. **"Lux's failing streetlights cut out and take their lit meshes' draw passes with them."** A CYCLING pole sits
   dark for seconds of every 40-70 s (`lux_failing.gd`). Refuted by `flicker_probe.gd`: with all 179 rigs
   `rest()`ed and stopped (`flicker_hold.json`, no light dark in any frame) the trace is the same as live
   (`flicker_live.json`).
3. **"The scene's first seconds draw more, and the frame-counted warm phase ends inside them."** The transient is
   real -- 158 draws more for the first 1,655 ms and 1,523 ms after the scene is added, live and held alike, and
   never after a later move (`flicker_move.json`) or turn (`flicker_turn.json`) -- and every disagreement on record
   was at the first two stations measured, which made it look like the cause. A 3.5 s time-based settle was written
   and run three times (`settled_run{1,2,3}.json`): measuring already began 7.5-10.8 s after the scene was added, the
   settle never waited, and the same two headings still disagreed. Not shipped.

## What was measured

`flicker_probe.gd` (camera alone, standing still, 80 s, windowed, vsync off, 1280x720) on slice 9b's package:

| station, yaw | after the first 1.7 s |
|---|---|
| attacker_spawn_9 (-17, 1.6, 22.91), 0 | 540 and 616 alternating every frame, nothing else |
| camera_socket_0 (-73, 4.4, -3.44), 180 | 927 and 948 alternating, every 60-frame window's maximum 948 |

Inside the harness's own sequence (`trace_run1.json`: a temporary `draws_frames` per window, reverted), the same two
headings show single frames above that alternation: attacker_spawn_9 yaw 0, 703 at frame 51 of one pass's window;
camera_socket_0 yaw 180, 987 at frame 4 of one and 1008 at frame 3 of the other. 3 of 106 windows held a spike, all
at those two headings; over all 53 headings each window's p95 agreed between passes and equalled the earlier report.
All 34 headings whose passes disagreed across the slice's prices were at those two stations.

## The change and its proof

Level Factory 0.269.0 (`patches/patch_lf_perf_draw_p95.py`): `_sample` reports the p95 of each window's per-frame
draws, primitives and objects, and `draws_max` beside the draws, in the heading and in each pass's record.
`p95_run{1,2,3}.json`: three runs over one package -- 53 headings, 0 disagreements between passes, 0 across runs, 0
against the earlier report; six spikes, all at the two headings above, visible only in `draws_max`.

## Instruments

* `flicker_probe.gd` -- one heading frame by frame; `--hold`, `--pre-yaw`, `--pre-pos`. Prints what it measured.
* `flicker_{live,hold,turn,move,cam0_live}.json` -- its traces (`trace`: [ms, draws, objects, dark lights]).
* `settled_run{1,2,3}.json` -- the retracted settle's three runs; `trace_run1.json` -- the per-frame windows;
  `p95_run{1,2,3}.json` -- the shipped change's three runs.
