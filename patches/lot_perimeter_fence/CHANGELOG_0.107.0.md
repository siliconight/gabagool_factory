## 0.107.0 - the fence at the plate's edge

**Roadmap 228, step B.** The walker picked the edge of the plate from the
six-option menu in `docs/findings/edge_menu/` at the factory root: E, a
chain-link fence with rowhomes and a water tower behind it under a sky-glow.
The glow shipped first (Lux 0.73.0). This is the fence: the plate's edge is
now the fence the walker already liked at the Empties, with the backdrop to
come behind it, and no longer the pale wall the menu called "the brightest
thing in the frame".

**What it does.** `site_fences.plan_perimeter` lays one chain-link run a
side, `PERIM_INSET` (0.25 m) inside the wall's centre line, as the mockup
stood it:
- a side longer than `MAX_RUN` (120 m, Zoo's widest `chain_link_fence`) is
  split into equal runs that meet end to end, so cold run 9223's 196 x 100 m
  plate takes six runs, twelve draws;
- the short sides butt the long runs without overlapping them;
- a run that would stand on a mission marker is left out and said
  (`LOT_FENCE_SKIPPED`), as every fence is;
- the runs are cover slots like the row fences (`source`
  `site_fences.perimeter`), so the same kit build makes them and the same
  census counts them; `LOT_PERIMETER_FENCED` says how many and how long.

**The wall behind it keeps its collision and shows nothing.** `_box_node`
takes `visual`; with runs standing, the perimeter bodies are written with
their shape alone (`_wall_seen`), so nothing changes for a body and 78
lightmapped tiles stop being drawn. A plate with no run standing keeps its
wall as it was. The roads that leave the plate end at the fence, as they
ended at the wall: a gate module is a later refinement.

**Not this release:** `perimeter.fence` is read (`false` keeps the wall) and
nothing writes it yet; step D's `surroundings` recipe will.

**Priced** with the glow standing, in the first cold run that carries both,
against the run before it; the number lives in that run's notes and in
roadmap 228.

**Tests:** 6, `tests/test_site_perimeter_fence.py`, all failing on 0.106.0.
**Suite:** 745 passed, exit 0 (739 as 0.106.0 and the 6 new). One existing test moved with the change: the example compound's slot manifest now carries the perimeter's six runs beside its cover, and `test_assemble_writes_the_manifest_beside_the_scene` asserts exactly that instead of 'every slot is cover'.
