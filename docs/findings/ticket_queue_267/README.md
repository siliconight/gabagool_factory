# A box office's queue in retractable-belt stanchions (Zoo 1.119.0, Deli Counter 0.243.0)

**What was asked.** Roadmap 267 put four steel crowd barricades on arena_a02's event floor
(`docs/findings/crowd_barrier_267/`). Shown them, the walker asked "what are these crowd barriers for....concerts?",
chose "queue lanes to the box office", and then corrected the kit: "stanchion or stanchions are likley more common for
banks and indoor common areas", "metal barriers are for outdoor concerts or riot protection from police", "retractable
belt stanchion", with a photo -- black posts on round weighted bases, a flat black belt taut between each pair at
waist height, lanes switching back in front of a registration desk.

So two things, both generator logic (the walker's rule: detail lives in the generators): Zoo draws the stanchions, and
Deli Counter lays a box office's queue of them wherever a box office is -- not by hand in arena_a02's spec.

## The species (Zoo 1.119.0, `patches/zoo_stanchion_run/`)

`stanchion_run` is one straight run: posts along the slot's width, one belt through them. A queue's switchback is
several runs, a run one slot. Its numbers are the common retractable-belt stanchion's -- a 38 in post 2-1/2 in across
on a 14 in base 2 in high, a cassette head, a 2 in belt and 7-1/2 ft of reach -- and `core/stanchion_run_forms.py`
argues each choice: as few posts as keep every belt within reach; the base 3 cm proud of Deli Counter's 2 cm floor skin
(the crowd barrier's buried feet, Zoo 1.118.1); one belt through every head, because a belt a span put two end faces
on one plane inside each middle head; one material, black `metal_painted`; collision the posts and the belt line.
Measured: 168 / 246 / 558 tris and 0 coincident pairs at the genome's corners in Blender's census (the bollard the
control, its known 2 / 2 / 1); four runs through `zoo_cli --build-kit`, each one mesh, one primitive, one material,
its bounds the slot's. `stanchion_run_preview.jpg`: the default run, 4.6 m and three posts, and the same from 2.4 m.

The single post Zoo already had, `queue_stanchion`, keeps its words: `test_stanchion_run.py` holds that every other
genome's keyword resolves as it did, because a new genome's `queue stanchions` would have taken that post's plural.

## The rule (Deli Counter 0.243.0, `deli_counter/ticket_queue.py`)

A room whose id names a box office (`box` with `office`, or `ticket`, `tickets`, `ticketing`, `boxoffice`) that shares
an interior wall with a public room gets a **ticket window** in that wall and a **queue** in front of it. The library
has one: arena_a02's `box_office`, beside its event floor.

- **The window**: 1.2 m wide over a 1.0 m sill, 1.1 m tall, sealed. Not `breakable`: a pane that shot out would be a
  firing line into the objective room behind it, and arena_a02's box office is that room. On the builder's 0.5 m grid,
  so it is cut where the queue was laid for it.
- **The queue**: lines of stanchion runs parallel to the wall, each a turn short at alternate ends, so the lanes
  switch back -- in at the end away from the window, out of the last lane onto the floor in front of the window.
- **Every clearance is the contract's**: a lane's clear floor and a turn are `stair_flight_width()` (a corridor and a
  bake cell); the floor in front of the window is `door_approach()`; nothing stands inside the queue, and each line
  keeps `min_corridor_width()` from every wall but its own, every standing volume in the public room, every walkable
  opening's approach, every stair, hole and vault swing.
- **Run by `enrich` before cover and furniture**, so a generated building furnishes round its queue; and by
  `migrate_ticket_queue.py` over the library.

**A refuted first draft, kept.** The clash test first held the whole queue -- wall face to last line -- a corridor off
everything, as if the lanes were solid. On arena_a02 nothing fitted between the event floor's west breach and the box
office's door ("door approach at (-17.50, 5.90) within 1.10 m"). The lanes and the floor in front of the window are
walked; only the lines stand. The shipped test asks two questions: nothing inside the queue, and a corridor round
every line. It also clips what the queue keeps clear of to the public room: the box office's own cabinet, 0.6 m
behind the shared wall, had been refusing every queue in front of it.

## arena_a02

- The four barricades and `metal_bare`, which they alone wore, are gone.
- The window at x -15.5 in the partition at y 5.9 (building metres), between the box office's secure door and its east
  wall; three lanes, 6.0 m along the event floor's north wall eastward from it, four lines of 4.8 m, style 10. Zoo
  plans all four `prop_stanchion_run_delco_1997_10_w480_d36_h97`, no fallback
  (`patches/dc_ticket_queue/zoo_plan_check.out.txt`).
- **Refurnished.** The library is a fixed point of furnish, and a piece taken away or added moves what furnish places
  round it: `refurnish_moves.py` (`refurnish_moves.out.txt`) -- ten of the event floor's cartons and litter bins
  stand elsewhere; on 0.242.0's spec, the control, the same pass moves nothing.
- **The fight** (`cover_and_audit.py`, `cover_and_audit.out.txt`): `combat_audit --rules auto`, as the build runs it,
  reads the same before and after -- 0 HIGH, 1 MED (the heist holdout it already had), 4 INFO, the box office's
  sightline 12.7 m, so the sealed window opens none. The event floor's cover-like pieces go 21 -> 17, the four
  barricades; its mid-floor pieces 1.0 m or taller 10 -> 6. All four barricades were 1.2 m, under the contract's
  1.3 m cover-break height, so no sightline they cut opens; what the floor loses is crouching cover in its middle.
  Whether it wants that back -- and as what, indoors -- is the walker's call.

## The level that shows it: cold run 9361

Cold run 9361 (`docs/cold_runs/cold_9361/NOTES.md`) made 9360's level -- club_block_014, seed 9014, which draws
arena_a02 -- on Zoo 1.119.0 and Deli Counter 0.243.0, at 0 interventions, findings 101 -> 101. Its export moved nine
lines against 9360's and each is attributed there: the window's module (one porous module, one model and one steady
rig more in the bake, one GLB and five references more), the barricades' four merge groups gone (825 -> 821 merged
meshes; which groups the runs' surfaces joined is not traced), the floor they stood on given back to the drop-edge
census. The package carries the runs' collision as Zoo draws it: four bodies sharing one concave shape, the posts and
the belt line, and no greybox box over a run.

## The frames

`shots.sh` frames the queue in one package, inspection light and the level's own, at six stations: in front of it,
from its entrance, at the window, inside a lane, from across the floor, and where the barricades stood.
`queue_9360_vs_9361_inspect.jpg` sets 9360 (the before) beside 9361 at all six; `queue_9360_vs_9361_lit.jpg` at the
three that face the queue, in the level's own night light.

- In the inspection light the queue reads from every station that faces it: four lines of black posts and belts
  switching back beside the box office's secure door, the ticket window in the wall to the door's right with the box
  office seen through it, and from inside a lane, the lane.
- Where the barricades stood, the refurnished cartons and litter bins; one bin stands with its centre 1.5 m past the
  lanes' east end.
- In the level's own night light the event floor is all but black, before and after: its troffers hang 5.5 m up and
  light the ceiling. A question for the walker, filed (roadmap 276), not this change's.
- The window is Deli Counter's plain sealed window, a frame and a pane, not a ticket window's counter, grille and tray.
  Whether it wants a species of its own is the walker's call (roadmap 267).
