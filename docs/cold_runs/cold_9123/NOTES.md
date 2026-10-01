# Cold run 9123 -- the room face, and what it costs

Zoo 1.38.0 (a wall module with a room face; also 1.37.1, the door sign's
matte face) and Deli Counter 0.166.0 (exterior brick/stone/wood/siding walls
carry their building's interior finish). Same brief, same seed, same lot as
9122. Zero interventions, one observation (the measurement and the shots).

The art leg before export: 0 blockers, 63 findings -- identical to 9122's by
code. Export closure clean. The package places 28 room-face wall instances
(`wall_delco_1997_0{1,2}_w200_mstone_idrywall`) plus the gas station's door,
breach panel and two windows.

## The look (`stone_inside_before_after.png`; 9122 left, 9123 right)

Stations aimed at the stone walls from INSIDE, positions taken from
gas_station_a02's slot manifest (`material_in` segments, Godot = (78 - y, z,
10 - x)): the manager's office (north wall), the stockroom (north), the sales
floor (west), the walk-in cooler (east). The flagstone is gone from all four;
the wall is the drywall the partitions are. From the street the same wall is
still flagstone (`04_outside_north.png`): the room face is not inside out.

A FIRST PAIR OF FRAMES PROVED NOTHING and is not kept as evidence: two
stations chosen by eye ("inside, facing north") came out identical before and
after, because both faced interior partitions that were drywall all along.
Only stations aimed at slots the manifest says carry `material_in` can show
the change.

NOT COVERED, AND IT READS: the remainders (`wallEnd`, a unit box scaled per
slot) keep the wall's finish -- a stone strip at the stockroom frame's left
edge, beside the sales floor's window, at the cooler's corner. gas_station_a02
has 9, the widest 1.65 m. Next.

## The price (`perf_9122_a.json`, `perf_9122_b_control.json`, `perf_9123.json`)

level_factory's fixed-station harness, fresh package copies (import cache
removed, imported headless), 14 stations x their headings = 53 measurements:

    control (9122 twice)        draw difference 0 over 53 headings
    9122 -> 9123, all headings  61,006 -> 61,202 draws  (+196, +0.3%)
    headings that changed       11 of 53
    largest single change       +37  (highest_vantage, yaw 270: 1,143 -> 1,180)
    worst heading on the map    2,626 -> 2,626  (objective_4, yaw 90)

Draws are deterministic and are the instrument; FRAME TIME IS NOT RESOLVED by
this run. The control moved by up to 2.5 ms p95 at one station on identical
bytes (player_start_26: 9.02 vs 11.55), so a change of the size above cannot
be seen in it and no frame-time claim is made. +37 at one heading is slightly
more than the 33 room-face instances on the site; a shadowed light drawing the
extra surface again would explain it, and is not confirmed.

Library-wide, the change applies to 1,630 modules in 15 buildings; this site
has one of them.

Four stations were over the provisional 2,000-draw budget before this change
and are after it (crew_spawn_2 2,367 -> 2,397); the room face is not what put
them there.
