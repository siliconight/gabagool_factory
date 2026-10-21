# A bank's teller line gets a queue (Deli Counter 0.244.0)

**What was asked.** The walker, 2026-10-20, correcting the steel barricades of roadmap 267: "stanchion or stanchions are
likley more common for banks and indoor common areas". Deli Counter 0.243.0 laid a box office's queue of Zoo 1.119.0's
`stanchion_run` (`docs/findings/ticket_queue_267/`); roadmap 275 asked for a bank teller line's the same way, as
generator logic.

## The rule (`deli_counter/ticket_queue.py`)

One fitting, `_fit`, now serves any frontage. What differs between a box office and a bank:

| | box office | teller line |
|---|---|---|
| the frontage | the shared wall's face | the counter's public face (`level_design._teller_lines`) |
| the public side | the public room's | `level_design._public_side`, the side the room's street doors are on |
| where the queue lets out | at the ticket window, on the builder's grid | anywhere along the counter, a 0.5 m grid |
| the floor in front | `door_approach()` | `teller_service_depth()`: a door's approach and a corridor behind it |
| the runs | `stanchion_run_<q>_<k>` | `stanchion_run_t<q>_<k>` |

The box office's queue is unchanged: re-planned from 0.242.0's arena_a02 through the new fitting, the same runs and
window to the millimetre. `level_design.enrich` lays both (`lay_queues`), after the teller line's enclosure and before
cover and furniture; `migrate_ticket_queue.py` gives the library the same answer, fitting a spec's queues with its
furniture set aside and refurnishing after -- on 0.242.0's arena_a02 that writes 0.243.0's to the byte
(`patches/dc_teller_queue/arena_either_way.out.txt` at the factory root).

## A queue is not furniture: the first cut, refuted and kept

The first cut refurnished the banks with furnish counting the four runs, like any volume, against each lobby's target,
and every lobby lost four pieces -- among them bank_job's payphone and sofa and bank_branch_a03's and
credit_union_a01's ATMs, the pieces a bank lobby is known by. Measured on a scratch copy with the runs left out of the
count: three of the four lobbies kept every piece they had. Shipped: `_room_volume_count` leaves stanchion runs out
(the queue keeps its floor anyway -- furnish holds a piece 0.9 m off each run, and a lane is narrower than two of
those), and a room holding a queue drops the lobby recipe's cluster of lone stanchion posts, which stood for a queue.

## Found on the way, recorded, not changed

- **Furnish's storey filter is decided by float rounding.** bank_branch_a03's upstairs offices re-drew five pieces
  when the lobby below lost its lone posts. `_room_volume_count`'s `abs(z - (story * sh + h / 2)) < sh` is exactly
  the storey height, in exact arithmetic, for every piece standing on the floor below; printed, seven of the eleven
  ground-floor pieces under the offices read 3.5999999999999996 and count against them -- the teller counter, a
  vending machine, a waiting chair, the three lone posts, cartons -- and four read 3.6 and do not -- the service
  counter, the payphone, the ATM, a low table (`patches/dc_teller_queue/storey_filter_floats.py` and
  `storey_filter_floats_0243.out.txt`). Roadmap 277.
- **bank_branch_a04's counter stands against a wall.** Its public face is 0.1 m into the concrete partition between
  the grand lobby and the teller room, so no queue stands in front of it and the rule says so ("partition 0 inside
  the queue"). Roadmap 279.
- **Level Factory accepts an unbuilt candidate.** Cold run 9362 named a seed its batch did not build; `approve
  candidate_selected` took it, and the lock gate refused it as protecting nothing (`docs/cold_runs/cold_9362/`).
  `tools/cold_drive/cold_drive.sh` now refuses such a seed up front. Roadmap 278.

## The library

| spec | queue | lobby, against 0.243.0 |
|---|---|---|
| bank_branch_a02 | 3 lanes, 5.2 m | lone post -> litter bin |
| bank_branch_a03 | 3 lanes, 5.6 m | 3 lone posts and a waiting chair -> 2 litter bins, 2 low tables; offices above re-drawn (277) |
| bank_job | 3 lanes, 5.2 m | 3 lone posts -> 2 litter bins, a low table |
| credit_union_a01 | 3 lanes, 5.6 m | 3 lone posts -> 2 litter bins, a low table |
| bank_branch_a04 | none: its counter's face is in a wall (279) | unchanged |

arena_a02 was refurnished too, its runs no longer counted: four more cartons and a file cabinet on its event floor, a
litter bin fewer. Zoo plans all twenty runs as the species, no fallback
(`patches/dc_teller_queue/zoo_plan_check.out.txt`).

## The level that shows it

Cold run 9363 (`docs/cold_runs/cold_9363/NOTES.md`) made bank_block_001 at seed 9281, which draws bank_branch_a02, on
Zoo 1.119.0 and Deli Counter 0.244.0: 0 interventions. The package carries the queue as Zoo draws it -- four bodies at
the four runs sharing one concave shape, the posts and the belt line, no greybox box -- and the runs' module merged
with the building's. No earlier run made this level, so there is no before; the frames are the after
(`shots.sh`, with `stations.py` turning stations in the building's frame into the package's):

- `bank_queue_9363_inspect.jpg`, six stations in the inspection light: four lines of black posts and belts
  switching back in front of the wood-and-glass teller counter, letting out at its west end, the basement stair's
  railed opening clear behind the queue.
- `bank_queue_9363_lit.jpg`, four in the level's own night light: the lobby dim and readable, the teller windows lit,
  the posts standing out against the floor.

Cold run 9362 tried first and is void: it named seed 9281 against a batch whose candidates were 9054, 9155 and 9256
(`docs/cold_runs/cold_9362/NOTES.md`).
