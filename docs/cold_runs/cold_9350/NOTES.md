# Cold run 9350 -- 0 interventions; restaurant_row_001, seed 9003: the office's computers are on

**What it was for.** Zoo 1.115.0 (the factory's roadmap 148) lights every monitor on a desk or a cubicle bank's work
surface: six invented 1997 office screens on a backlit `_Face` atlas. Level Factory 0.224.0 keeps each module's lit
screens a mesh of their own where they stood and merges the rest of the desk into its room cell. This is cold run
9349's level made cold through both, so the office can be seen, and priced, against 9349's.

**Tools:** Zoo 1.115.0 (9e8c9bc), Level Factory 0.224.0 (f754562), Deli Counter 0.238.0, Lot 0.125.0, Lux 0.78.0.
Staged from 9349; seed 9003 named.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0), read after `cold_run.py --end`; 8.5 min.
- **Shell:** 0 blockers of 79 findings, deli_a03, office and pharmacy_a01 with the terrace's twelve Empties, as 9349.
- **Art:** 0 blockers of 108 findings. **Findings 108 -> 108** against 9349.
- **Export:** the buildings merged as 0.224.0 merged 9349's copy -- 1,662 surfaces -> 808 meshes, 834 colliders kept
  -- with **24 lit surfaces in 24 meshes of their own where 9349's copy had 6**: the office 17 (2 before; its 9 desks
  and 6 cubicle banks), deli_a03 7 (4 before; its three desks with office stock, on the first floor). The light bake
  2,898 users, 18 more than the copy's 2,880: the screens.

## The office (`office_9349_vs_9350.jpg`; `office_stations.py`)

Six stations from where a person working there stands -- four desks with office stock and two cubicle banks, on the
ground floor and the top (storey 2) -- in a walk copy of each package, the level's own evening light; 9349 left, 9350
right. Every desk monitor 9349 shows as a dark box shows a screen in 9350: the blue word processor at two desks, the
starfield at a third, three lit screens along each cubicle row, and monitors lit in the background of the desk shots.

The stations were derived twice, and the first derivation is kept in `office_stations.py`'s docstring: turning a
slot's `rot_y` counter-clockwise put three of the four desk stations behind their monitors (the one turned 180 saw
its screen, where the two senses agree); a slot turns clockwise.

## The price (`_runs/perf_inner/run.py`, 53 station-headings; `price_a.out.txt`, `price_b.out.txt`)

The control is 9349's package re-merged by Level Factory 0.224.0 and re-baked by its own bake (`_runs/mb_lit_9349`,
`docs/findings/interior_merge_266/`), the same level without the screens; control and screens priced in turn, twice.

| | control A | control B | screens A | screens B |
|---|---|---|---|---|
| draws, all headings | 34,531 | 34,625 | 34,639 | 34,686 |
| p95, mean a heading | 3.881 ms | 3.836 ms | 3.785 ms | 3.797 ms |
| mesh instances | 2,953 | 2,953 | 2,971 | 2,971 |
| lightmap users | 2,880 | 2,880 | 2,898 | 2,898 |
| video memory | 134.5 MiB | 134.5 MiB | 134.7 MiB | 134.7 MiB |
| meshes over the 8-light cap, paired | 9 | 9 | 9 | 9 |

- **The draws:** at 18 headings both screen runs draw the same count, 1 to 14 over both controls, which agree there
  (camera_socket_0 yaw 270 +14, extraction_15 yaw 270 +12, camera_socket_1 yaw 270 +11); at the other 35 nothing
  moves. The controls agree at 51 of the 53 headings, and the 94 draws between their totals are all at the other two.
  Which of the 18 look into the office was not checked.
- **The frame time:** -0.074 and -0.062 ms a heading against the controls' mean, inside their 0.224 ms floor: no
  cost this machine can see.
- **The cost, then:** 18 meshes, one for each module with a monitor, and 0.2 MiB for the screen atlases.
