---
name: store-at-night-work-queue
description: "Open work on the convenience store at night after cold run 9105 (2026-09-29): the spill's per-mesh cost, the grade, the pylon brand at night, the shell-walled stores"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-09-29T01:27:09.338Z
---

Shipped at zero in cold run 9102 (2026-09-28): see-through storefront (Zoo 1.18.0 / DC 0.153.0), sales floor fluorescent row (DC 0.154.0), FLAPPHAS price pylon at the road frontage (Zoo 1.19.0 / Lot 0.80.0). +7 to +27 draws at 6 of 53 headings.

Still open:
1. THE STORE GLOWS ONTO ITS PAVEMENT (cold run 9105, 2026-09-29). Shipped in order: Lux 0.55.0 night fluorescents (9103), Zoo 1.20.0 clear glass + storefront `reach` (9104), outward spill (DC 0.156.0 / Zoo 1.22.0 / Lux 0.57.0, 9105). Spill level is FRAME-MATCHED (Lux SPILL_FRAME_MATCH 8.4, measured at Delco Night on delco_1997's pad) -- the physical level read as nothing. The spill pushed b2's room-sized floor/ceiling meshes to 20 claimants and dimmed the room; the walker chose to split them: Zoo 1.23.0 (Floor/Ceiling parts not merged), cold run 9106 restored the room (carpet 16.9 -> 20.5) but cost draws +7.4% summed (+4..+230 at 51/53 headings, median p95 +0.4 ms, over-budget stations 7 -> 10-11) because the split is library-wide. The walker chose NARROW: DC 0.157.0 tags storefront-lit rooms' plates `light_budget_tiles`, Zoo 1.24.0 splits only those (`_lbt`); cold run 9107: carpet held 20.2, draws +0.09% vs 9105, over-budget stations 7. Non-storefront rooms (b2 stockroom/back hall) stay merged and over budget, unseen in frames. All four levers pulled: night grade = Lux 0.58.0 (Delco Night contrast 1.08 -> 1.0, cold run 9111; street 30 m 6.2 -> 10.2, black 51% -> 36%). Open: the canopy, not the store, is still the brightest thing on the street; other night presets carry contrast > 1 (reported, not changed). TRAPS: hiding every CanvasLayer hides Lux's post stack (use tools/look_shots.py); `storefront_square` camera stands behind a pump island; a fresh export's project.godot says max_renderable_lights=157, not 150.
2. PYLON (cold run 9108, Zoo 1.25.0): measured, the green field DID read at night; the lettering read at no time. Name now stretched to half its face (a bold word at 12 m); digits still unresolved; a 2.4 m face reads as colour past ~14 m. Transmitted-glow idea measured and rejected (washes the name, brightens noon). Pylon made 3.4 x 0.7 x 9.0 (Zoo 1.26.0, Lot 0.81.0/0.82.0; cold run 9109 FAILED on a 4.5 m cover test point, fixed; 9110 zero): name reads at 20 m. REOPENED AND KEPT: at full scale (the 9113 look_shots fix) FLAPPHAS reads at 30 m, so 3.4 m was judged from 10% frames; the walker kept it anyway (2026-09-29). TRAP: swapping a GLB into a walk copy needs its cover/_tex PNGs AND the shipped .import settings, or new PNGs import without mipmaps and alias to dots.
3. DONE (DC 0.158.0): fuel_stop_heist/stop_n_go built non-modular (modular unset, not pvp_heist); migrate_modular_storefront makes every storefront spec modular. 13 other non-modular specs remain (none with storefronts).

**Why:** the walker asked for the store to glow at night through see-through glass and for the pylon.
**How to apply:** check the walker's answer on item 1 before touching Lux energy; see [[never-edit-tool-repos-during-a-cold-run]].

TRAP (9109): never chain export/--observe/--end after the art leg without reading its blocker count first -- a blocked run was once recorded as 'export ok'.
