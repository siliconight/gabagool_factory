---
name: work-order-after-crowns
description: "Walker agreed 2026-10-03 to the order after the crowns shipped: (1) wind step 3b, the flyers; (2) the light-bake PROBE (roadmap item 31, one import value on one package, see if a UV2 appears); (3) the Empties' wiring (item 106) then dark interiors"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-06T08:47:25.701Z
---

Agreed by the walker on 2026-10-03 ("Agreed"), after Zoo 1.56.0 / Level Factory
0.130.0 shipped the swaying crowns:

1. **Wind step 3b: the flyers on the poles** (`docs/proposals/WIND_DESIGN.md`):
   stapled at the head, loose at the foot, weight by distance down the sheet
   cubed, UV2 as the crowns. Then step 4 (pennants, banners, hangers) when a
   brief places them.
2. **The light-bake probe**, roadmap item 31 (ANALYSIS, never scheduled): set
   `meshes/light_baking=2` (static lightmaps) in one shipped package's import
   sidecar, open it, see whether Godot generates a UV2 and whether the unwrapper
   survives 183 mesh resources a shell. A probe, not a feature; the roadmap says
   not to quote the one-line fix until that run has happened. If it works, the
   bake job is a new pipeline step (Godot with a RenderingDevice, after
   presentation_compose, before dispatch_handoff; `tools/godot_probe.py` is
   most of its body), priced on the harness; a baked rig already skips its own
   motion (Lux `bake_mode`), so the failing fixtures and screens stay dynamic.
3. **The Empties** ([[empties-get-dark-interiors]]): the wiring first (brief
   field, Lot edge-only placement, the gate accepting a doorless building),
   then see-through windows over a dark shell.

Still owed to the walker in between: their eye on the shipped amplitudes
(tube drop depth, pole dark spell, grill rate, churn speed, crown sway) from
walking `_runs/walk_export_moving`. Related: [[moving-parts-shipped]],
[[levels-feel-static-make-them-alive]], [[runtime-optimization-guide]].

**Progress 2026-10-03:** (2) the light-bake probe RAN: UV2 imports clean (3279/3328
meshes; the 7 moving props kept dynamic), an unattended editor bake works
(plugin presses the button, answers the save dialog; 22 s for the lot), and in GL
Compatibility the baked lot draws 6-22 % fewer calls with the same pools once Lux
0.65.0 moved the pole lamp out of the shaft. PRICED on a quiet machine: -0.8 ms median
frame (-16 %), -0.45 ms GPU, controls 0.04-0.10 ms; heaviest views -3 ms. Open: which
lights may bake (power-cut beat, Lux presets), and making it a pipeline job. Not yet a pipeline job. `docs/findings/light_bake/`.

**Shipped 2026-10-03:** light bake is a pipeline step: Level Factory 0.131.0
`export --bake-lights` (opt-in; editor window ~1 min, needs GPU) + Lux 0.66.0
(lightmap follows state: power cut takes it off; a foreign preset falls back to real
time by flipping static lights dynamic AND re-adding them). Priced as shipped: -0.56 ms
median (-12 %), -0.37 ms GPU, controls 0.00. Bake by default: DONE in LF 0.144.0 (walker's yes, 2026-10-05; `--no-bake-lights` skips; a failed bake ships unbaked). Still open:
quality above Low, leak/cap effects unmeasured. Next in the agreed order: the Empties.
