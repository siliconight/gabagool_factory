# Cold run 9288 -- the urban near side, first try: nothing fit between the mission's buildings

**What it tested:** two releases on urban_row_001 (9287's brief unchanged). Level Factory 0.201.0 (27fc03d)
fills an urban street's near frontage with mid-rise Empties between the mission's own buildings, keeping a
4 m passage beside each. Lot 0.121.0 (bb6011d) keeps its fields, dumpsters, pads and cover clear of every
Empty. Staged from cold run 9287.

**Result: 0 interventions (journal 0, unattributed files 0) -- and no Empty stood on the near side.** Every
candidate's compose log says `8 Empties across the street (an urban wall), 0 on the near side between the
mission's buildings` (9 on one).

## Why none: measured, not guessed (`docs/findings/urban_street/near_room.py`)

The script rebuilds what the compose stage handed `infill`:
- each building's rect from the footprint its shell measures, with its passage;
- the block grammar's two side streets, each band 20 m wide with its sidewalks and frontage;
- the service lane, clear of the band at y 22.7 to 31.7.

The rooms left along the near line:

    seed 9003   12.67 m (b0 to b1), 11.35 m (b2 to the plate's end), and none else
    seed 9104    7.33 m (the plate's start to b0), 6.70 m (b1 to b2)
    seed 9205    7.33 m, 6.70 m

The narrowest mid-rise measures 15.3 m. On this mission the library buildings, their passages and the side
streets already hold nearly the whole near frontage, and what is left is two- and three-bay rooms.

**Answered by Deli Counter 0.217.0 (b3c2354b):** three narrow mid-rises, 12.30, 10.30 and 6.60 m wide as
built, each fitting one of those rooms. Proven by cold run 9289.

## The rest, against 9287

- The grader: seed_9104 picked at PASS 90, every summary row as 9287's (enemy stuck 0, blocked 1, crew 0).
- Findings 118 and bake users 3,037: the same.
- Lot 0.121.0 changed nothing it could. Its replay of the ten picked jobs from 9278 to 9287 had already
  shown 0 files moving, and with no near-side Empty there was nothing new in any planner's way.
- Three dumpsters on seed_9104 as in 9287.

## The time

    run    shell   art     export   walk   retire   the drive
    9287   102 s   160 s   182 s    7 s     3 s     7.7 min (460 s)
    9288   100 s   159 s   177 s    10 s    3 s     7.5 min (451 s)

## What is evidence of what

- The near side: `art.log` (`[site] ... 0 on the near side`).
- The rooms: `near_room.py` on `workspaces/cold-9288-ws/.level_factory/temp/urban_row_001/candidate_<seed>/site.json`.
- The grader and the count: as 9287's notes.
