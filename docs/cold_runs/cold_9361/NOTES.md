# Cold run 9361 -- 0 interventions; club_block_014, seed 9014: arena_a02's box office queue

**What it was for.** Roadmap 267, the walker's re-scope of arena_a02's crowd barricades: "queue lanes to the box
office", in "retractable belt stanchion[s]" -- "metal barriers are for outdoor concerts or riot protection from
police". Zoo 1.119.0 draws one straight run of retractable-belt stanchions, `stanchion_run`; Deli Counter 0.243.0's
`ticket_queue` gives a box office a sealed ticket window and a switchback of runs in front of it, and takes arena_a02's
four barricades off its event floor. This run made 9360's level -- the same brief and batch, seed 9014 named -- on
those two.

**Tools:** Zoo 1.119.0 (3f54314) and Deli Counter 0.243.0 (067df43d); the rest as 9360 -- Level Factory 0.227.0, Lot
0.126.0, Lux 0.79.0, Dispatch 0.5.3, Patina 0.32.0, Laser Tag 0.32.0, Pipeline 0.6.0, Pixelcoat 0.62.0.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0), read after `cold_run.py --end`; 7.5 min
(23:47:19 to 23:54:51). Shell 0 blockers of 73 findings; art 0 of 101; findings 101 -> 101 against 9360, this level.

**The export, line by line against 9360's** (the workspace's name and the bake's seconds set aside): 18 of 27 lines
the same; the nine that moved, each attributed --
- occluders: porous modules 238 -> 239, the ticket window's module (`bake_occluders.gd` leaves `window_`, `doorway_`
  and `breach_` modules open); the scene tree 24,868 -> 24,876 nodes, the window's module and what Godot's import makes
  of its three nodes, not counted node by node;
- buildings merged: the same 618 slots and 1,372 surfaces, 825 -> 821 merged meshes. arena_a02's own report
  (`merge_buildings.json`): 202 slots, 323 meshes, 320 surfaces and 205 colliders before and after, 168 -> 164 merged.
  The four barricades each made a merge group of their own in 9360 (`lot/arena_a02/merged/r164.res` to `r167.res`,
  gone); which groups the runs' four surfaces joined is not traced -- the merge names its meshes `MergedR_<n>`;
- modules kept by name 40 -> 41: the window's module, `window_delco_1997_04_w120_mmetal_o8e667a.glb`, which the merge
  does not take apart. The runs' own module is merged and, like the barricades', not in the package;
- light bake: models 133 -> 134 (the window's module), steady rigs 94 -> 95 (Deli Counter derives a light anchor at
  the window, `int_0_0_window_1`), users 2,375 -> 2,373;
- GLB references: 119 -> 120 GLBs and 430 -> 435 references, every one resolving: the window's module;
- drop edges: 45,123 -> 45,164 cells reached of 60,708 -> 60,718 standable -- the barricades' floor given back, less
  what the runs stand on -- and still 8 unguarded edges, 0 undeclared indoors;
- the package: 2,879 -> 2,878 files, 2,885 -> 2,884 in the manifest: the barricades' four merge resources out, the
  window's GLB, its `.import` and its `.unwrap_cache` in.

**Collision, read from the package** (`lot/arena_a02/site.tscn`): four `KitCollision` bodies at the four runs, x
-12.5 / -13.7 alternately and y 4.572, 3.016, 1.46 and -0.096 in building metres, sharing one concave shape -- the
posts and the belt line Zoo's module carries; no greybox box over any run.

**The frames** (`docs/findings/ticket_queue_267/queue_9360_vs_9361_inspect.jpg` and `_lit.jpg`, `shots.sh`): six
stations, both lights, 9360 the before. In the inspection light the queue reads from every station that faces it:
four lines of black posts and belts beside the box office's secure door, switching back, the ticket window in the wall
to the door's right, the box office's cabinets and cartons seen through it; from inside a lane, the lane. Where the
barricades stood, the refurnished cartons and litter bins. A litter bin furnish placed stands with its centre 1.5 m
past the lanes' east end. In the level's own night light the event floor is all but black, before and after (roadmap
267's question for the walker).
