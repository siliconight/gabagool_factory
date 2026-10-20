---
name: philly-street-comps
description: "walker's 3 Philly comps (2026-10-11), roadmap 240: pole line + wires SHIPPED (Lot 0.119.1, cold 9263); the line's cost is the street lights' shadow maps (+170 draws vs lamps), a 30 m shadow fade measured not applied; next rowhouse stoops, silver roofs"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-12T18:28:41.049Z
---

The walker sent three Philly photographs 2026-10-11 ("some really good comps
that you need to learn from"): an avenue corner (wooden utility pole carrying
cobra-head, street-name sign, low side-street signal, wires everywhere; fenced
vacant lot; litter along the lot edge; brick housing towers behind), an aerial
over rowhouse blocks (flat SILVER/white coated roofs, some tar, rear ells; a
mixed-use corridor with a colour + sign band + awning per front; ballfield,
stacks, water tower), a rowhouse block party (stoops with iron railings,
satellite dishes on the FRONTS at 2nd floor, parged fronts, canopy tents,
lawn chairs, chalk, kids). Filed: docs/reference/PHILLY_STREET_COMPS.md,
roadmap 240 (photos not stored).

**Pole line decided by the walker, 2026-10-12** (all four recommended; in
docs/proposals/POLE_LINE_DESIGN.md): one side, every street; the full wire
set, NO house drops; a transformer can every 3rd-4th pole by cause; a
cobra-head on EVERY pole, the far kerb loses its lamps.

**Shipped 2026-10-12, all three builds:** Zoo 1.104.0 `utility_pole`; Lot
0.118.0/0.118.1 the line (cold 9262); Lot 0.119.0 the wires (themed site
only, unshaded, no shadow, one mesh a 32 m cell) + LF 0.194.0 (site_wires_*
OBJs under the bake's `unlit`), cold 9263 0 interventions, +2.2 draws and
noise-level ms; Lot 0.119.1 holds a far wire to a pixel (UV.x = radius,
vertex shader widens + fades by coverage; faces now wound outward, cull back).
0.119.1 PROVEN in cold 9264 (far dashes -> faint lines, +2.2 draws, noise ms);
Lot 0.119.2 writes min_px as a float (Godot reads `= 1` for a float uniform
as null). The 30 m shadow fade was REFUTED on GL Compat (far shadows freeze).

**The line's price (found 2026-10-12, docs/findings/pole_line/):** 9262 vs
9261 +170 draws a heading, p95 +0.39 ms -- ALL the street lights' shadow
maps (Lux's 12 casters both runs; cobra-head lamp at 7.50 m vs steel 5.92):
300 vs 133 draws. Levers on 9262, none applied: rig distance_fade_shadow 30 m
-154 (+16 over lamps), budget 8 -118, budget 4 -241. Lux's shadow knobs are
set AT RUNTIME (policy sets shadow_enabled; the street rig's _rebuild() frees
and rebuilds its lamps) -- scene edits to lights measure nothing; use
LuxRoot.shadow_caster_budget or edit the vendored rig. Roadmap 243: packages
run Lux's High tier (quality_tier never set) -- the walker's call.

**Why:** these are what "reads as Philly" and the factory had none of them.

**How to apply:** next for 240: the walker's call on the street lights'
shadow cost (levers in docs/findings/pole_line/); the walker's eye on
9264's against_9263.png and the pole look; then (2) DC rowhome raised floor + stoop, Zoo
stoop + railing, Patina facade dish anchors; (3) Pixelcoat silver + tar roof
packs. Generator rules only; frames beside the comps. Related:
[[edge-menu-walker-picked-e]], [[texture-accents-guide-filed]],
[[performance-beats-graphics]].
