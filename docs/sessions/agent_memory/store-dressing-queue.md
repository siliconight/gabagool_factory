---
name: store-dressing-queue
description: "Walker's queued store/level requests at the 2026-09-29 pause, in order -- cooler lineup revision, cold run 9114, poster walls, snacks, ATMs, a VHS rental store."
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-09-30T12:48:06.129Z
---

State at the pause (2026-09-29): pushed and clean -- Lux 0.60.0 (counter accent 2x, the walker's call), Zoo 1.28.0 (cooler LINEUP + beer/water doors), Deli Counter 0.161.0 (8 m sales-floor cooler in the four stores lacking one; window sign clears the lit sign box). No cold run active. Cold run 9114's batch is written but untracked at `docs/cold_runs/cold_9114/` and NOT begun; its name still describes Zoo 1.28.0.

Queue, in the walker's order:
1. DONE 2026-09-30: Zoo 1.29.0 (soda, sports drinks, dairy, beer; no water), DC 0.162.0 (openings recorded where cut, sign box on its door), cold run 9114 at zero, priced at no cost. Original ask kept below. REVISE THE COOLER LINEUP before 9114. The walker: bottled water "wasn't really a thing in the 1990s in USA"; prioritise soda, sports drink (Gatorade-like: 20 oz bottle, orange cap, bright fruit colours), milk, beer. Drop BOTTLED WATER and `door_water`; add a sports-drink section; milk gains half-gallon gable-top cartons (white, red/blue print) beside jugs; beer gains green and amber bottles with cream labels (their Yuengling photo: reference only -- invented names, `club_names.WINDOW_NAMES`). Then update 9114's batch name and run it.
2. POSTER WALLS -- DONE except store WINDOW posters (2026-09-30): Zoo 1.30.0-1.33.0 (four families; club redrawn DN3D-style, three poses, monogram italic, blacklight), DC 0.163.0 (interior runs as fixtures in club/bar/selling rooms, off the glass), Lot 0.84.0 (alley runs on back-of-house walls + every other pole, as HUNG slots, never cover), cold run 9115 zero; 9116 is the first with blacklight + outdoor. OPEN: store window posters facing the street (the window-sign pattern); a real dive bar building (see [[first-dive-bar-the-wooder-hole]]); Lot has no true alleys (the LEVEL_RECIPE seam); DC style index is positional (declaring a material re-rolls unrelated modules -- measured harmless in 9115, fix = key by material id, walker's call). Original plan: a Zoo "poster wall" species -- a cluster of posters painted into one atlas, one mesh, one material, one draw -- plus the thumbnail/grayscale/blur tests, families, and DC placement for strip clubs, bars, alleys/poles, store windows. See [[posters-fill-four-wall-kinds]].
3. SNACKS -- DONE 2026-10-02: Zoo 1.40.0 (gondola's second face: YUMMYJAWNS cakes, fruit snacks, lunch kits, bagged candy; chips face unchanged), Zoo 1.42.0 (bag pinched at seals, from the walker's two Blender chip-bag tutorials -- shape only, no cloth sim), cold runs 9130/9131 at zero, draws unchanged. Open: boxes leave air on 0.37 m shelves; lunch kits stand on a dry shelf.
2b. STORE WINDOW POSTERS -- DONE 2026-10-02 (DC 0.170.0 `window_poster`, 9 stores; from inside the print shows reversed at full strength -- unfixed).
4. DONE: ATMs in convenience stores: free-standing late-90s units, lit ATM topper, green-on-black CRT screen, keypad.
4b. After ATMs: a PROPER WALK of the FLAPPHAS gas station / convenience store combo (walker, 2026-09-30). Note Zoo already has an `atm` species -- check it before building one.
5. DONE 2026-10-02: the VHS rental store -- MACDADE MOVIES (the walker's name), with the curtained back room ("suggestive only"). Zoo 1.43.0 `video_rack` (wall/island/adult, 36 invented titles), DC 0.171.0 `video_store` preset + `video_store_a01` (racks AUTHORED by the preset: the furnisher could only stand one or two), LF 0.126.0 alias, cold run 9132 zero on a new brief `video_block_001`. Open: its posters are the convenience store's copy (SCRATCH & WIN); sign bracket crosses the name; no TV, curtain or drop box; the selected candidate's Laser Tag route never completed (walktest ok) -- pick candidates on merit, not seed 9181 by habit.
The sign-box task was done (DC 0.162.0).

**Why:** requests arrived mid-turn faster than they could be built; this keeps their order and the walker's exact asks.
**How to apply:** start at item 1; never hand-author brands, see [[fake-delco-brands-funny-and-crass]]; price every look, see [[performance-beats-graphics]].
