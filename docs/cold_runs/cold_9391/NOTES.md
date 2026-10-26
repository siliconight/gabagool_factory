# Cold run 9391 -- 0 interventions; restaurant_row_001, seed 9003: the walker's walk of 9386, five fixes in a package

**What it was for.** The tool releases since 9390, each from the walker's walk of cold run 9386
(`docs/findings/walk_2026-10-23_9386/`): one sign a building (Zoo 1.123.0, Lot 0.129.0, Level Factory 0.241.0;
finding 1), door panels and a knob (Zoo 1.124.0; finding 13), a painted drop safe (Zoo 1.125.0 and Deli Counter
0.267.0; finding 3), the loading dock's pile as pallet stacks (Deli Counter 0.267.0; finding 9), and casings at
doorways and breach panels (Zoo 1.126.0; finding 2).

**Every leg ran, `INTERVENTIONS: 0`.** The light check: FAIL 3, PASS 33, REPORT 1, as before. The walk copy
`_runs/walk_9391_restaurant_row_001`; the workspace `workspaces/cold-9391-ws` (an earlier line here said the run had
retired it -- it had been looked for under `_runs/`; the run's retire leg removed something else, 1.1 GB).

## Each fix, in the package (against 9389, the control)

- **One sign.** The fixtures GLBs' sign-box nodes (`SignBox_*`, `LuxEmit_sign`): in 9389 on all three buildings; in
  9391 on the office only -- pharmacy_a01 and deli_a03, the two dealt a band, build no box. Frame `sign`: the blue
  PHARMACY box gone, the band alone. And the lamp: `themed_site_assemble`'s `site.site.lights.json`, the lights that
  ship, records `door_signs_dropped` ['b0/ext_0_S_sign', 'b1/ext_0_S_sign'] and keeps the office's sign anchor alone.
  A false alarm on the way, kept: the greybox candidate's `lot_assemble` lights still carry all three sign anchors
  and an empty `door_signs_dropped` -- correctly, the bands being dealt to the THEMED spec only -- and were read first,
  before naming which job wrote them.
- **Pallets.** deli_a03's stockroom stands `loading_pallet_stack_1` .. `_6` about (-39.0, -12.5), and the import cache
  builds `prop_pallet_stack_..._w140_d115` at 1.0 to 1.3 m -- the species, not a box. Frame `pallets`: six wrapped
  loads on pallets where one brown block stood.
- **The drop safe.** Built as `prop_drop_safe_...` with no material tag, `metal_painted` being its default now. Frame
  `safe` under the inspection light: grey steel with its dial and handle; in the level's own light the room is dark,
  as before.
- **Door hardware.** Frame `door_close` (inspection light): rowhome j's door carries its knob on the latch side.
- **Casings.** Frames `breach_close` and `east_door` (inspection light): strips at the breach panel's edges and both
  sides of the east wall's doorway, where 9389 shows the bake's step.

Sheets: `fixes_9389_vs_9391.webp` (six stations, 9389 / 9391 / 9391 under the inspection light) and
`close_9389_vs_9391_inspect.webp`. Stations from `find_nodes.gd` (`find_nodes.out.txt`).

## The price (`price.py`, `price_compare.py` -> `price_compare.out.txt`)

Four arms of walk copies in one session, 53 headings in each: 9389 twice as the control, 9391, and 9389 with roadmap
305's prototype horizon ring. The control's spread: +0 draws, +0.249 ms median mean.
- **The fixes: +582 draws** over the 53 headings (-1 to +45 a heading), frame time +0.015 ms -- inside the spread.
  ATTRIBUTED (`count_by_site_child.gd`, both packages): every one of the 26 Empties gained exactly 2 meshes, the door
  hardware's brass, one more colour of `metal_painted` and so one more mesh on each side with a door (`blocker_0`'s
  mesh lists side by side: `metal_painted_..._b58c3d` on N and on S); deli_a03 +7 (the pile); the pharmacy -1 (its
  sign box). The casings, as Zoo 1.126.0 measured in its GLBs, added none. Answered by Zoo 1.127.0: the hardware in
  the stoop railing's black iron, so it merges with the railing on every front. To be proven in the next run.
- **The ring: +1 draw at every heading**, +0.017 ms -- inside the spread.
- An instrument that read nothing and is kept: `count_materials.gd` counted 0 drop safes in a level that has three;
  material names do not survive the import, so it counts by place instead.

## Walk it

```powershell
& "C:\Godot\4.7\Godot_v4.7-stable_win64.exe" --path "C:\Projects\gabagool_studios\gabagool_factory\_runs\walk_9391_restaurant_row_001"
```
