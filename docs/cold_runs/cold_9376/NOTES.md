# Cold run 9376 -- 0 interventions; restaurant_row_001, seed 9003: Deli Counter 0.256.0, a host no chair fits beside is moved where one does

**What it was for.** The factory's roadmap 284. Deli Counter 0.256.0 (31eb0a59) moves a host no chair fits beside
where one does, instead of taking it away: after the room is furnished, to the nearest spot where it and its chair keep
off the room's routes and narrow no pair of its route endpoints (`room_necks`). In this level that is office's
exec_suite desk, which 0.252.0 took away (cold run 9374: the bake's users 2,948 -> 2,940). Cold run 9375's level
again, staged from it.

**Tools** (`_runs/cold/cold_9376/before.json`, every repo clean at `--begin`): Deli Counter 0.256.0; the rest as
9375 -- Level Factory 0.231.0, Lot 0.126.1, Zoo 1.120.1, Lux 0.79.0, Dispatch 0.5.3, Patina 0.32.0, Laser Tag 0.32.0,
Pipeline 0.6.0, Pixelcoat 0.62.0. Deli Counter moved 0.253.0 -> 0.256.0; 0.254.0 and 0.255.0 changed only the drawings
(`floorplan.py`, `axonometric.py`), which `build_freshness` files as not baked and nothing in a run reads.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0); 8.8 min (20:07:58 to 20:16:43). The
validation record 108 findings, none blocking. The `--end` line's FAILING is the factory root's hygiene counting this
block's own records before they are committed, not the run.

**What it shows** (`patches/dc_desk_move/cold_compare.py` and `walk_diff.py`, each with its `.out.txt`; 9375's staged
scenarios and record read from copies taken before this run):

- **The scenario the run writes is the one it wrote.** Each of the three Laser Tag candidates' `mission_scenario.tres`
  is byte for byte 9375's, 1,326 bytes.
- **The findings are 9375's**, 108 by code, candidate and message.
- **What moved is the desk and its chair, and nothing else.** The export's bake: 153 models and 118 primitive meshes
  lightmapped as 9375, **2,947 users against 2,940**. The walk copies (`_runs/walk_9375_restaurant_row_001` and
  `_runs/walk_9376_restaurant_row_001`) differ in seven files only 9376 has, all office's merged resources
  (`lot/office/merged/r295.res` to `r300.res` and `l20.res`); `lot/office/site.tscn` 899 -> 910 nodes -- six merged
  meshes and one lit face more, the bake's seven users, and two kit collision bodies with their shapes, the desk's and
  its chair's. Every other building's scene is the same but for node `unique_id`s, which Godot gives afresh at every
  save -- and pharmacy_a01's for the engine's own `@StaticBody3D@<n>` names too, numbered from a counter the merge
  run shares, which office's two bodies more renumber by two. When 0.252.0 took the desk away (cold run 9374) it went
  as seven merged meshes and one lit face; it comes back beside its chair, at the room's east wall, as six and one.
- **No frame was shot**; the room is drawn in plan, before and after, in `patches/dc_desk_move/plan_office_exec_suite.png`.

**The walk copy** is `_runs/walk_9376_restaurant_row_001` (the drive wrote it to `_runs/walk_export_restaurant_row_001`
and it was renamed after the run, as 9375's was).
