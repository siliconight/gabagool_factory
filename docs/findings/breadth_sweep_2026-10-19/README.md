# The breadth sweep, 2026-10-19: six missions after the store cabinets and the transform fixes

**Why.** Every cold run of 2026-10-19 before this sweep (9319 to 9327) built urban_row_001. Since each other mission
last ran cold, the factory had shipped, among much else:

- the drop-edge gate (Level Factory 0.216.0, roadmap 173) and the strict greybox census (0.218.0);
- the store cabinets (Deli Counter 0.228.0), the cabinet on its partition (0.231.0) and two machines a room
  (0.231.1), each a strip and refurnish of the library;
- the build freshness gate's sources (Deli Counter 0.229.0);
- the z-fight gate and the ground-contact pre-flight reading a scene's transforms as Godot does (Deli Counter
  0.230.0, Level Factory 0.218.2) -- the second matters only where a site turns a building, which a courtyard or a
  campus does.

None of it had been through a cold run on another mission. The zeros on one level are one level's zeros.

**Refuted, kept: the sweep exercised the transform fix.** It did not. precinct_yard_001 turns 21 of its 25
buildings, every one a half turn. A half turn's basis is its own transpose, so rows and columns read it alike.
county_hospital_001 places one building, unturned. That was read off the two packages' `site.tscn` after the sweep.
No level in it turns a building a quarter turn, so Level Factory 0.218.2's fix, which reads a building's turn in the
site, is still unexercised by any cold run. Deli Counter 0.230.0's fix reads modules turned inside a building, which
every building has, and cold run 9325 exercised it.

**How.** `tools/cold_drive/sweep_one.sh`, one cold run a mission in one script
(`sweep_2026_10_19.sh` in the session's scratchpad, its six lines quoted below), each mission staged from its own
last cold run, the seed picked by the driver. The six: the two that turn buildings (precinct_yard_001, a
courtyard; county_hospital_001, a campus) and the four whose stores the cabinets moved (deli_001, convenience_001,
gas_block_001, restaurant_row_001). Runs 9328 to 9333 used Level Factory 0.218.2 and Deli Counter 0.231.1. Run 9334
used Deli Counter 0.232.0, the fix to 9329's stop. The versions are each run's own record
(`_runs/cold/cold_N/after.json`). The table is `docs/findings/breadth_sweep_2026-10-13/sweep_table.py` on cold runs
9328 to 9334 (`sweep_table.out.txt`).

    run 9328 9316 precinct_yard_001
    run 9329 9230 county_hospital_001
    run 9330 9286 deli_001
    run 9331 9280 convenience_001
    run 9332 9309 gas_block_001
    run 9333 9311 restaurant_row_001

## The result

Every run recorded 0 interventions. Four shipped; two stopped at the export on the drop-edge gate, and both stops
are attributed below. 9334 is county_hospital_001 again, staged from 9329 after the fix to its stop.

| run | mission | staged from | outcome | interventions | pick | grade | stuck: enemy, blocked, crew | findings: shell / art | bake users | drive |
|---|---|---|---|---|---|---|---|---|---|---|
| 9328 | precinct_yard_001 | 9316 | DONE | 0 | seed 9203 | PASS 100 | 0, 0, 0 | 77 / 108 | 3,002 | 8.0 min |
| 9329 | county_hospital_001 | 9230 | STOPPED at the export | 0 | seed 9208 | not graded | not graded | 62 / 83 | 1,434 | no clock |
| 9330 | deli_001 | 9286 | DONE | 0 | seed 9292 | PASS 90 | 0, 0, 0 | 69 / 93 | 1,643 | 4.9 min |
| 9331 | convenience_001 | 9280 | DONE | 0 | seed 9282 | PASS 100 | 3, 24, 0 | 54 / 77 | 565 | 3.7 min |
| 9332 | gas_block_001 | 9309 | DONE | 0 | seed 9080 | PASS 100 | 1, 3, 0 | 70 / 105 | 3,197 | 7.9 min |
| 9333 | restaurant_row_001 | 9311 | STOPPED at the export | 0 | seed 9003 | not graded | not graded | 81 / 110 | 3,503 | no clock |
| 9334 | county_hospital_001 | 9329 | DONE | 0 | seed 9208 | PASS 100 | 1, 22, 0 | 62 / 83 | 1,434 | 4.1 min |

The table is `sweep_table.out.txt`, written by `docs/findings/breadth_sweep_2026-10-13/sweep_table.py 9328 9329 9330
9331 9332 9333 9334`. A stopped run has no Laser Tag report and no drive clock, and the tool says so rather than
printing a zero. Both county hospital runs picked seed 9208 and read the same findings and the same bake
users.

## The stop, attributed: county_hospital_001's elevator shaft

Cold run 9329 stopped at the export with 0 interventions, on Level Factory 0.216.0's drop-edge gate:
`UNDECLARED_DROP_INDOORS: 20 unguarded edge(s) a body reaches, indoors, on a floor, that nothing declares`. The
gate's report (`drop_edges_scan.json` in the run's export) puts all 20 on one rim: the storey-2 slab
(`GreyboxBase/slab_col_2`, y 7.2) round a 2.6 m hole at x -7 to -5, z -13.25 to -10.75, falling 7.2 m to the
ground floor. The building is the mission's own generated shell, `lf_county_hospital_001_9208`, unturned, at
(-6, 0).

`presets.hospital` cuts the shaft as "an elevator shaft as a vertical horde-spawn channel (floor holes stacked)": a
slab hole on every storey from 1 to the top. It declares one of them, a `floor_hole` on storey 1. The package
carried that one link; the gate classified its rim's 20 edges as declared and the 20 on storey 2 as not, because a
declared rim is keyed on its storey as well as its rect. The gate was right.

The census of every spec on disk: 46 slab holes in 37 specs; undeclared, the generated hospitals' upper shaft holes
and, in the library, three atriums -- bank, cbp_town_finale_midbalanced_schemafixed, final_stand -- large voids of
another kind, which no mission in this sweep places.

Fixed in Deli Counter 0.232.0 (`patches/patch_dc_hospital_shaft.py`): the preset declares every hole it stacks,
and a declared drop lands on the first floor below that is not cut under it -- the storey-2 link had ended in
mid-air over storey 1's cut.

## The stop, attributed: restaurant_row_001's seam, which was the instrument's

Cold run 9333 stopped at the export with 0 interventions, on the same gate: `UNDECLARED_DROP_INDOORS: 3 unguarded
edge(s)`, a 3.3 m drop from deli_a03's storey-1 floor at site x -64.25 to -64.0, z -9.5 to -8.75. That is the west
edge of the up-stair's discharge plate, where the slab's cut and the plate are authored flush at deli_a03's local
x -13.0. The building stands at x -51, so that is site x -64.0, a line of the gate's 0.5 m lattice.

**What the rays meet** (`seam_rays.gd`, `seam_rays.out.txt`, on a copy of the package). Rays at x -64.02 and -64.01
meet the slab at 3.3, and rays at -63.99 and -63.98 meet the plate at 3.3. A ray at exactly -64.00 meets neither and
falls to the ground.

**Refuted, kept: "a ray exactly on a line where two flush colliders meet reports neither."** They were never flush in
the engine. The floats settle it:

- `seam_floats.py` (`seam_floats.out.txt`) reads the package's GLB. The slab's cut vertices are stored at local x
  -13.000000953674316, one float32 step west of -13. The plate's body sits at -11.800000190734863, with a hull
  1.2000000476837158 across each way.
- `seam_ulps.gd` (`seam_ulps.out.txt`) reads the engine. Composed with the building's -51, the plate's body lands at
  site x -62.799999237, because a float32 near 63 steps 3.8 um. Its west face is then at -63.999999285 and the
  slab's cut at -64.000000954.
- That leaves a 1.7 um gap straddling x -64.0. A ray at exactly -64.0 falls through it. Rays one float32 step either
  side, at -64.000007629 and -63.999996185, meet the slab and the plate.

The instrument cast one ray down each lattice point, and the gate's lattice is snapped to round coordinates, so it
landed exactly where pieces meet. A body is 0.4 m across and cannot fall through 1.7 um.

**The fix is Level Factory 0.219.0** (`patches/patch_lf_edge_seam.py`). The lattice is laid 3.1 mm and 2.3 mm off the
round coordinates, so every query the instrument makes asks the moved points. Neither offset is a multiple of 0.5 mm,
and each is more than 35 float32 steps anywhere within 1 km of the origin. `tests/unit/test_edge_seam.py` rebuilds
the seam from deli_a03's own floats. On 0.218.2 it reads 19 drops along the seam's interior
(`patches/lf_edge_seam/prove_before.out.txt`), and on 0.219.0 none, with the plate's far rim still found.

**Why the whole lattice.** The first build moved the column rays and the sky ray alone. The gate's own measure,
classify and assert ran on copies of all six packages (`gate_ab.py`). The control held: the old instrument reproduced
every export's own scan exactly. Across the six packages, 38 edge rows changed. `edge_cells.gd` asks the
instrument's questions of named cell pairs in both arms, and it put every changed row down to one of four things a
query on a round coordinate does:

| what the query did | where | rows |
|---|---|---|
| a rounding gap between colliders authored flush | 9333's seam: 3 undeclared, 2 a flight's own side | 5 |
| a ray in a face's plane, which reads the collider or misses it as rounding falls | ramp sides read a cell east or west (9333: 6, 9332: 3); rail and guard tops stood on (9333: 3, 9330: 1); a slab edge read as floor (9333: 1) | 14 |
| a capsule exactly its radius from a face on a lattice line, which Godot calls an overlap | 9328: two flight sides hidden, and a guard's top occupied, so its six rows were never asked | 8 |
| a hit a few millimetres along a slope | the same edge a centimetre apart once rounded, counted once in each arm (9333: 2, 9332: 6, 9334: 2); one drop of 0.501 against a 0.500 limit (9330: 1) | 11 |

`edge_cells_*.out.txt` hold the pairs asked. Two of 9332's three same-edge pairs and 9334's one were not asked one
by one; they carry the same signature, a ramp's height a centimetre apart in the two arms. One of 9332's three
ramp-side rows met the ramp on the lattice as well. The flood did not reach that cell there, and the probe does not
replicate the flood.

The capsule kind applies as much to the block capsule, and the face-plane kind as much to the barrier ray, and the
first build left both on the lattice. So 0.219.0 moves the grid's origin instead, and every query leaves the lattice
at once. On these six packages that changed nothing more, as the next table shows. The first build's record is
`gate_ab_columns_only/`.

A fifth artefact changed no row. On 9333's package, 684 of 685 "steep surfaces" were rays starting inside a
quarter-turned sidewalk box, exactly on its side (`steep_hits.gd`). Godot's strict point test calls such a start
outside, so the box reports a hit at the ray's start with a zero normal. The other packages' steep counts fell the
same way and were not probed one by one.

**Through the gate, before and after** (`ab_table.py`, `ab_table.out.txt`; every arm's scan and rows in `gate_ab/`).
The first build of 0.219.0 matches the final one on every count and every row of all six packages, so this table
shows 0.218.2 against the final.

| run | mission | gate on 0.218.2 | gate on 0.219.0 | unguarded | undeclared | rows moved |
|---|---|---|---|---|---|---|
| 9328 | precinct_yard_001 | passes | passes | 5 to 13 | 0 to 0 | 8 |
| 9330 | deli_001 | passes | passes | 66 to 64 | 0 to 0 | 2 |
| 9331 | convenience_001 | passes | passes | 0 to 0 | 0 to 0 | 0 |
| 9332 | gas_block_001 | passes | passes | 16 to 19 | 0 to 0 | 9 |
| 9333 | restaurant_row_001 | REFUSES | passes | 59 to 52 | 3 to 0 | 17 |
| 9334 | county_hospital_001 | passes | passes | 49 to 49 | 0 to 0 | 2 |

Not attributed: deli_001's guarded drops rose from 19 to 111, while the times a body walked into something fell
from 3,796 to 3,727. No guarded edge is a row, and none was asked cell by cell. The shape is the capsule kind seen
at a rail, with fewer neighbours occupied and more drops each guarded, but that is not proven here.

## After

**The shaft fix, proven.** Cold run 9334 is county_hospital_001 staged from 9329, on Deli Counter 0.232.0. It
finished DONE with 0 interventions, and seed 9208 graded PASS 100. The gate counted 49 unguarded edges: 40 at
declared drops, 6 on things' tops and 3 on flights' own sides. None was undeclared.

**The seam fix, proven.** Cold run 9335 is restaurant_row_001 staged from 9333, on Level Factory 0.219.0. It
finished DONE with 0 interventions, and seed 9003 graded PASS 90 with nothing stuck, as every candidate did on 9311.
The gate counted 52 unguarded edges and none undeclared. Those are the very 52 rows the A/B predicted off 9333's
package, every count with them.

So every mission in the sweep now ships on the gate, and no run of it needed a hand. Of its two stops, one was a
generator's defect the gate exists to catch. The other was the gate's own instrument, which is why every changed
row above was attributed before the fix shipped.

