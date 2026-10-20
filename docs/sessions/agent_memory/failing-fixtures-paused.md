---
name: failing-fixtures-paused
description: "Lux 0.62.0 failing fixtures SHIPPED 2026-10-02 (one bad tube a room, a wavering bulb, every third streetlight cycling, lens moves with lamp); measured, priced within noise; first cold run with it is 9139."
metadata:
  type: project
---

The first "alive" item after the real-look rollout, shipped as Lux 0.62.0 on 2026-10-02 (commit 666ad92 in lux). Design approved by the walker: ONE failing fixture per anchor -- a fluorescent stutters, a pendant wavers -- and every third streetlight CYCLES (dims, dark, restrikes); everything else steady (the old 12 %/9 Hz wobble on every row is 0). The lamp AND its lens move together, on the lens's own material override.

Measured (docs/findings/failing_fixtures/NOTES.md, lux CHANGELOG 0.62.0): on 9137's walk export 12 of 146 rigs fail, 12 lenses bound, a tube 6.0 -> 3.65 with 10 drops in 24 s and its diffuser following; perf on 53 views: draws identical, frame time within the instrument's pass-to-pass spread. Selftest `lux/tools/failing_fixtures_selftest.gd` (55 checks).

Two refutations worth remembering: the zero lens bind was the spawner placing a rig AFTER add_child (bind deferred now), not the lamp mount height; and a probe comparing against the rig resource's `energy` could never fire because the preset scales the lamp (2.2 -> 6.0). Compare with the lamp's own first frame.

**How to apply:** the shipped level bakes the spawner's choice into `presentation/lux.applied.tscn` (run_lux_apply.gd runs the spawner at export), so `failing_kind` ships in the file. Cold run 9138 was a false start (batch without `briefs/`); 9139 is the first package with this Lux, to be priced against 9137 and probed in-level (scratch `failing_level_probe.gd`). Next in the queue: [[levels-feel-static-make-them-alive]] items 3 and 4 (moving parts; a changing world), designs shown first.
