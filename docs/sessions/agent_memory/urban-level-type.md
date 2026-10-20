---
name: urban-level-type
description: "walker 2026-10-11 chose a NEW urban level type (roadmap 241); far side, near side, residues, heights by cause, street trees SHIPPED (cold 9287-9294); next: corner shop, frontage, variants, haze"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-14T19:12:36.700Z
---

From three screenshots of another studio's game ("more around potential lot
layout city building height"; docs/reference/URBAN_MIDRISE_COMPS.md, not
stored, layout/scale only): mid-rise brick blocks 5-12 storeys at the sidewalk
line and touching, skyline stepping up with distance, corner buildings with a
lit shop at grade and homes above, 4-lane streets, tree pits, signals at every
corner, dusk haze. Asked, the walker chose **a new urban level type picked by
the brief**; the Delco strip levels stay byte for byte.

**Why:** every level so far is a 1-3 storey Delco strip with set-back lots;
the walker wants a denser, taller city as a second kind of level, not a
replacement.

**How to apply:** roadmap 241's order -- (1) DC mid-rise Empty family
(non-enterable, merged covers, dark inside, lit-window paint; corner variant
with a lit shop; bay-window variant; heights by cause, never jitter), (2) Lot
urban layout (zero setback, continuous rows, enterable buildings among the
Empties, tree pits, signals), (3) LF brief field (absent = today's strip),
(4) Lux dusk haze, (5) price (lightmap area, shadows, texture memory 238) and
frames vs the comps. Roadmap 240's parts serve both types. Queued after 240's
first builds unless the walker reorders. Related: [[philly-street-comps]],
[[edge-menu-walker-picked-e]].

**2026-10-13, step 1 first cut SHIPPED** (DC 84ef4439, root 208dbb6): `presets.empty_midrise` + `EMPTY_MIDRISES` (gs_midrise_a..f: 5,6,7,8,10,12 storeys, 15-24 m wide, regular 3.2 m bays CHOSEN not read, lobby door, parapet). Prefix `gs_midrise_` on purpose: LF's `building_library.empty_rows` hands every `gs_empty_*` to any terrace brief; facades are already outside the enterable draw. A presets.py change makes DC's pre-commit gate demand `build.py --all` (152 shells, ~6.5 min) and nav-baseline entries for new UNJUDGED shells. Cold 9277: lots byte-identical to 9276. Greybox frames (tint by NODE name: `_pane`, `_leaf`; by material fails) in docs/findings/urban_midrise/, sent to the walker. Not built: penthouse, corner shop, bay windows (each a missing DC capability).

**2026-10-13, the walker's verdict on the frames:** "general scale looks fine for that specific building type" (heights and widths stand). They saw "very simple boxes with black boxes for windows" -- greybox frames judge scale only. Still open: window rhythm, the themed look, detail (cornice, storefronts, fire escapes, bays). Recorded in docs/findings/urban_midrise/README.md (root 7ebc9a4).

**2026-10-13 ~21:30, steps 2-3 first cut SHIPPED:** LF 0.200.0 (65cf5e7), root 397a581.
- **The field:** a brief's `streetscape: "urban"` stands the far side as a continuous mid-rise wall. It
  takes effect only where a terrace stands; a strip brief is byte for byte unchanged.
- **Cold run 9287** (urban_row_001 = restaurant_row_001 + the field): 0 interventions, 8-9 mid-rises
  across the street.
- **Priced vs 9285:** draws -72 a heading, p95 -0.15 ms, video memory +19 MiB (all buffers).
- **For the walker:** `docs/findings/urban_street/ab_9287/ab_sheet.png`.

**2026-10-13 ~23:00, the near side SHIPPED** (root 5a834bc): Lot 0.121.0 keeps every planner clear of
Empties; LF 0.201.0 `empties.infill` fills the near frontage (4 m passage beside each mission building);
cold 9288 stood none (rooms 6.7-12.7 m vs a 15.3 m narrowest block), so DC 0.217.0 added three narrow
mid-rises (12.3/10.3/6.6 m); cold 9289 0 interventions, priced vs 9285 over 52 matched headings
(`price_matched.py`: draws -38.5, p95 -0.26 ms, video +38 MiB). Frames: `ab_9289/ab_sheet.png`.
- **RESIDUES FIXED (root 05fc22d):** Lot 0.122.0 lets enemies stand where the fences leave a row open
  (a near block's band had starved seed_9205; cold 9290, all three PASS 90); LF 0.203.0 deals afresh
  where a design fits the room and the bag's remainder does not (cold 9291: every near room holds a block).
- **HEIGHTS BY CAUSE SHIPPED (LF 0.204.0, root 3e634fa):** the wall lowest across from the action's centre,
  rising to the plate's farther end; cold 9292 rho +0.91..+0.93 (was +0.40/-0.05/+0.03), priced at nothing.
  The standard A/B sheet's elevations CROP a tall wall: shoot given stations (skyline_N from behind the
  near side 25 m up; street_up_W/E) -- see `ab_9292/skyline_sheet.png`, sent to the walker.
- **STREET TREES SHIPPED (Lot 0.123.0 + LF 0.205.0, root 424b5bc):** every 30 ft, 30 ft clear of a corner
  (PHS siting guidelines, docs/reference/STREET_TREES.md); cold 9294 trees 19 -> 46, every fight moved
  with the furniture and no spawn did; priced +28.6 draws, p95 inside the floor; `ab_9294/ab_sheet.png`.
- **CORNER SHOP, steps 1-3 SHIPPED 2026-10-14** (docs/proposals/CORNER_SHOP.md "As built"):
  - Zoo 1.107.0 (fbbe818): `shop_panes`, M_Shop_pane_Face.
  - DC 0.218.0 (173c91b5): `gs_cornershop_a..d` (deli/bar/laundry/grocery), Opening.pane, schema `pane`.
  - LF 0.206.0 (e8bd89b): each run of the wall opens and closes on a corner; the plate's ends count.
  - Prefix NOT gs_corner_ (gs_corner_station is an enterable gas station).
  - The shop door is the front door; the homes' door is at the back.
  - No Lux light: the comps' table names Lux for "the shop's light" -- a spill is the expensive version.
  - LF 0.206.1 (c189baf): the fill deals afresh on a spent bag. 9295's seed_9003 had stopped 12.70 m short;
    over 600 walls the worst went 14.20 -> 4.10 m.
  - Cold runs 9295 and 9296 proved it (root 39a1069). Frames: `ab_9295/corner_sheet.png`
    (docs/findings/urban_street/corner_stations.py).
  - Priced: -4.0 draws, p95 inside the floor, +4.2 MiB video.
  - Taste calls: the cool shops glow nearly white at EMISSION 2.2; the corners step the skyline down at the ends.
  - AWNING SHIPPED: Zoo 1.108.0 b028d3d (`shop_awning`, a canvas shed, 4 colours as the form) and DC 0.219.0
    42fe102a (hung over each corner's storefront); cold 9297 0 interventions, no fight field moved, +0.7 draws.
    Root 43af821.
  - At night the awning BARELY READS (unlit dark canvas; the glow is paint). The walker's call: brighter canvas
    or a light under it.
  - Its frame time is UNPRICED: StarCraft II was running and the controls disagreed by 0.48 and 1.22 ms.
  - Next: the sign band. Scoped 2026-10-14: four repos. LF's `sign_family("gs_cornershop_*")` reads RETAIL for
    every corner (the id never names the shop); Pixelcoat has no laundromat family; Lot's `building_signs` takes
    building ids only; Lot hangs a band at a fixed SIGN_Z 3.6 m, where the awning meets the wall. My own addition
    -- the comps ask for "lit, awning" only.
- **PACKAGE TRIM (LF 0.207.0 dff4b8c, root 655aabc, cold 9298):** a package carries only the `lot/<id>/` its
  assembly stands; 9298 16 -> 13 packages, 11.4 MB and 95 baked imports fewer, nothing the graders read moved.
- **FIRE ESCAPE SHIPPED (roadmap 156, root e9f60eb):** Zoo 1.110.0 c173a8a + DC 0.220.0 827038a4 on the walk-ups
  (gs_midrise_a/b/g/h/i); cold 9303, 6 stand on seed_9104; `docs/findings/fire_escape/walkups_9303_sheet.png`.
  Not merged yet (LF 0.209.0). Found 248: Patina moves front dressing onto any prop proud of the wall.
- **Dusk haze already ships:** `blue_hour.tres` fog on, density 0.005, colour (0.42, 0.48, 0.62); 241's step 4 is
  verify + price, not build.
- **LEFT:** frontage; penthouse / bay variants;
  haze; window rhythm and detail; the walker's eye on `ab_9287/`, `ab_9289/`, `ab_9292/skyline_sheet.png`
  and `ab_9294/`.
- **PICKS FOLLOW THE GRADE (LF 0.202.0):** 9290 picked seed_9003 (a three-way tie at 90), 9291 seed_9104
  (PASS 100), and grades move with any change near a fight. An A/B against an earlier run passes the seed
  to cold_drive.sh, not `auto`. See [[pick-moved-name-the-seed]].
