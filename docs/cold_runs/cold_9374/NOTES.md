# Cold run 9374 -- 0 interventions; restaurant_row_001, seed 9003: Deli Counter 0.252.0, a piece that seats somebody stands with its chair

**What it was for.** The factory's roadmap 284. Deli Counter 0.252.0 (8eb3233f) seats a host the room left with no
chair last, when the room is furnished -- one chair from the host's own stream, tucked and then pushed in, off any
route the room reserves -- and takes away a host no chair fits beside. Of the three buildings restaurant_row_001 draws
at seed 9003 only `office` moved: its exec_suite, a room holding a marker on storey 2, lost its chairless desk
(`desk_r93ac9731_1`, which no chair spot cleared at all -- it goes with the route check off too,
`patches/dc_table_chairs/no_route_check.out.txt`). deli_a03 and pharmacy_a01 are unchanged. Cold run 9373's level
again, staged from it, Deli Counter the only tool that moved.

**Tools** (`before.json`, every repo clean at `--begin`): Deli Counter 0.252.0 (8eb3233f); the rest as 9373 -- Level
Factory 0.230.0, Zoo 1.120.1, Lot 0.126.0, Lux 0.79.0, Dispatch 0.5.3, Patina 0.32.0, Laser Tag 0.32.0, Pipeline
0.6.0, Pixelcoat 0.62.0.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0); 8.6 min (15:22:34 to 15:31:07). Shell 0
blockers of 79 findings; art 108; **findings 108 -> 108 against 9373, identical by code, candidate and message**
(`patches/dc_table_chairs/cold_compare.py` and its `.out.txt`, 9373's record read from a copy because its workspace
was retired at this run's end). The `--end` line's FAILING is the factory root's hygiene counting this block's own
records before they are committed, not the run.

**What moved** -- one desk, and everything it was built as. The export's bake: 153 models and 118 primitive meshes
lightmapped as 9373, **2,940 users against 2,948**. The walk copies (`_runs/walk_9373_restaurant_row_001` and
`_runs/walk_9374_restaurant_row_001`, each its run's export with a player in it) differ in eight files only one side
has, all office's: 2,948 -> 2,940 files. `lot/office/site.tscn` 912 -> 902 nodes: `MergedR_295` to `MergedR_301` and
`LitR_20` -- seven merged meshes and one lit one -- and one kit collision body with its shape, fewer; the rest of
office's merged resources renumbered, every other building's scene the same nodes. The eight meshes are the bake's
eight users: the desk's surfaces, merged by material within its room's cell, and a lit face on it, which the merge
keeps a mesh of its own (Level Factory's `assets/godot/merge_buildings.gd`: a room unit cut into cells, one mesh a
material; a lit face that is not a fixture's -- a screen, a sign, `M_*_Face` -- stays a mesh where its instance stood,
`LitR_<n>`). No other spec moved, so nothing else can have. No frame was shot; the room is drawn in plan, before and after, in
`patches/dc_table_chairs/plan_office_exec_suite.png` -- the desk stood by the door at the room's south-east corner,
off the room's reserved route, and its floor share goes 7.2 -> 5.4 %.

**The walk copy** is `_runs/walk_9374_restaurant_row_001` (the drive wrote it to `_runs/walk_export_restaurant_row_001`
and it was renamed after the run, as 9373's was).
