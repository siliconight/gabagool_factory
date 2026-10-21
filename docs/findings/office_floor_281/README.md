# An office building's open floor is an office (roadmap 281)

**What it was for.** Roadmap 148's frames of cold run 9369 (`docs/findings/denser_rooms_148/`): the office's `floor_1`,
816 m2 over the bullpen, filled to its furnish target by Deli Counter 0.246.0's count fix, showed litter bins standing
mid-floor among carton stacks. `floor` is a shop-floor word in `level_design._ROOM_KINDS`, so the room had always been
furnished by the shop floor's recipe.

**Measured first.** Fifteen library rooms are shop floors by the word `floor` alone: the two offices' `floor_1`, and an
arena's event floors, a brewery's, a depot's, a foundry's two, a freight terminal's, three warehouses' floors, a setback
demo's and a supermarket's mezzanine. Only the offices' were plainly wrong; the rest keep their kind, each a question
of its own.

**What changed.** Deli Counter 0.248.0 (88422d0b; `patches/patch_dc_office_floor.py`, `patches/dc_office_floor/`):
`level_design.is_office_floor`, read in `_room_kind` after the strip club's, the card shop's and the video store's
rules -- a building whose id says `office`, and a room the word table would make a shop floor by `floor` alone. The
refurnish moves the two offices' floor_1 and nothing else:

| spec | floor_1 before | floor_1 after | floor share |
|---|---|---|---|
| office | a service counter, 3 vending machines, 2 filing cabinets, 4 shelf runs, 4 cartons, 4 litter bins | 4 desks and their chairs, 3 shelf runs, 6 filing cabinets, 5 cartons | 13.9 -> 13.9 % |
| office_stepped | 5 litter bins, 9 cartons | 6 desks and their chairs, 10 cartons | 12.5 -> 13.6 % |

Inside the walker's band (`rooms-not-crowded-not-barren`, about 12-25 %): the swap changes what the room is, not how
full it is.

**In a package.** Cold run 9370, cold run 9369's level with Deli Counter the only tool moved: 0 interventions, findings
108 -> 108. `floor_1_9369_9370_lit.jpg` and `_inspect.jpg` (`compose_pair.py`; stations from `tools/room_stations.py`,
the same in both): the desks stand where the bins stood, their screens lit (Zoo 1.115.0); the bullpen, the frames'
control, does not move. `frame_change_9369_9370.out.txt`: floor_1 7.2 % of its pixels moved in the level's light and
9.1 % in the inspection light; every other station within 1.1 %.

**What it costs.** `merged_counts_9369_9370.out.txt`: the office's merged meshes 290 -> 302, every other building's the
same -- up to twelve more submissions where floor_1 is in view. Not priced on its own: the 148 price measured the same
office's +52 merged meshes at +0.058 ms mean frame time where draws moved, inside the control's -0.242 to +0.113 ms,
and twelve is a quarter of that.

## Files

- `compose_pair.py`, `floor_1_9369_9370_lit.jpg`, `floor_1_9369_9370_inspect.jpg`: the frames (shot with
  `docs/findings/denser_rooms_148/shots.sh`).
- `frame_change.py`, `frame_change_9369_9370.out.txt`: how much of each frame moved.
- `merged_counts.py`, `merged_counts_9369_9370.out.txt`: the submissions.
