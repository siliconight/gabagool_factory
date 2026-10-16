# Drop edges, roadmap 173: every unguarded edge on one package, sorted by what it stands beside

Roadmap 173 (2026-09-23) wants a rule with a real zero -- every drop edge is either GUARDED, or DECLARED as a
one-way reachability, or a defect -- and says why `tools/walkable_edge.gd` cannot be that gate yet: on cold run
9072 it found 5,897 unguarded edges, 1,024 of them the open sides of staircases, which the contract calls
ordinary architecture, and nothing tells those from a fall nobody meant. This folder is the first step the
item owed: the instrument run on a current package and every edge it found put in a named class.

## Instruments

- `tools/walkable_edge.gd` (the root tool), run on a copy of cold run 9317's package
  (`_runs/edge_probe_9317`, imported first, deleted after): `godot --headless --path . --script
  res://walkable_edge.gd -- edges_9317.json 0.5`. Its `MAX_ROWS` was 4,000 until this run, which kept the
  deepest 4,000 of 16,739 rows -- the plate's rim, not one indoor edge -- so it is 200,000 now; `edges_9317.log`
  is the run, `edges_9317.json` every row (1.8 MB).
- `sort_edges.py`: reads the rows (x, y, z in Godot metres, `drop_m`, `indoors`), the package's `site.tscn`
  (which library building stands where; this site is unrotated, and the sorter refuses one that is not) and
  Deli Counter's records for each building (`build/<id>.gameplay.json`: stair footprints, hatch and ladder
  markers, `floor_hole` / `hatch` vertical links; `specs/<id>.json`: footprint and storeys), and names each
  edge's first claimant. Output: `sort_9317.out.txt`.

## What 9317's package reads (urban_row_001, seed_9104: deli_a01, pharmacy_a01, office and twelve Empties)

    grid 1521 x 1521 cells of 0.5 m over x, z +-380 m (the backdrop's extent)
    standable cells 133,992    drop edges 22,445    unguarded 16,739    unguarded indoors 6,004

    class         edges   indoors   what it is
    site_edge     3,753       137   nothing below: the plate's rim and the backdrop's
    wall_line     2,703       939   a cell on a footprint's own line -- the INSTRUMENT'S, see below
    stair           278       268   inside a stair footprint (+0.6 m): the open side of a flight
    hatch            48        34   within 1.6 m of a hatch or ladder marker: the ladder's own hole
    floor_hole       16        16   within 1.6 m of a `floor_hole` link at its storey: a drop the spec declared
    roof_rim         34         0   at roof level within 1 m of the footprint's edge: a parapet's job
    storey_rim    1,053       651   at a storey level inside a footprint, no stair, no hole: the item's class
    prop_top      8,757     3,862   above a kerb, outside footprints or between storeys: a thing a body stood on
    ground           97        97   at ground level inside a footprint, between the classes above
    other             0         0

**The instrument's blind spot, found by the sort.** 2,703 edges sit on a footprint's own line (|distance to
the rect's edge| <= 0.3 m). The headroom ray `_columns` casts from a surface starts inside the exterior wall
there, Godot's `intersect_ray` reports nothing for a ray that starts inside a solid, and a floor slab's edge
under a wall reads as a standable surface with a bottomless drop beyond it -- 939 of them "indoors", at the
basements' and storeys' wall lines (e.g. x -70.0 along deli_a01's west face at y -3.30). The same
mechanism is in CLAUDE.md's rule: a ray answers "what is the floor here"; "does a body fit" wants a shape. The
fix is the instrument's (a shape test at the standing point, or `hit_from_inside`), not the level's.

**Furniture is standable.** 8,757 edges are the tops of things -- desks, counters, shelves, cars, dumpsters,
benches, stoops -- 3,862 of them indoors: a body on a desk can walk off a 0.75 m drop, and the instrument
reports it. They are not level defects, and a gate has to exclude them by what the surface IS (a floor, a
slab, a roof) rather than by its height; the sorter's class is a height band and a footprint test, which is
not that.

**What is declared, in the item's sense,** today: a stair's footprint (278), a hatch or ladder hole (48), a
`floor_hole` link (16), the plate's rim (3,753: the fence's business, roadmap 188). None of these is a defect.

**What is left for a gate to judge: 1,053 storey rims, 651 of them indoors, and 34 roof rims.** A storey rim
is an edge at a floor's level inside a building with a full-storey drop and nothing above step-over height
between -- e.g. a run along x -41.75 at y 3.30 inside deli_a01 (local x 9.25, y -3 .. -8), and one at
y 6.90 inside the office. Which of those are a cut slab's collar (roadmap 168), a stair's discharge void, a
mezzanine lip somebody meant, or an unrailed hole is the attribution the next step owes, row by row, with the
same records the sorter reads plus the slab holes (`SlabHole`) `_stairs` and `_vertical_links` cut.

## What would make the gate

1. The instrument stops reporting its own blind spot (a shape test at the standing point).
2. Standable means a floor-like surface, not any top: the test reads what the hit collider belongs to (a slab,
   a stair tread, the ground, a roof) and skips props.
3. The declared set is read from the package's own records -- stair footprints, hatch and floor-hole links,
   the plate's rim -- and a `walk_off_ledge` link is emitted for each (Dispatch's `navigation_hints` `links[]`
   is where the item puts it), so the gate's set and the AI's set are one list.
4. The residue is attributed on one package until it reads zero, and then it is frozen (the baseline pattern
   178 names) and fails on a new entrant.

Steps 1 and 2 were then taken the same night, and measured; what follows supersedes the table above.

## The instrument repaired, twice, on the same package

**Second run** (`edges_9317_probe.json`, `sort_9317_probe.out.txt`): `_columns` keeps a surface only if a
shin-high sphere over it (`PROBE_R` 0.20 m at `PROBE_H` 0.60 m, `intersect_shape`) overlaps nothing -- the
"does a body fit" question asked with a shape. The wall-line class fell from 2,703 to 1,387 and its indoor part
from 939 to 32; standable cells 133,992 -> 122,161. But the bottomless-neighbour class rose from 3,753 to 8,803,
2,058 of them indoors: once the cells inside a wall are rejected, every floor cell beside a wall sees a column
with no surface and reads a bottomless drop toward it -- 2,090 of them, at the foot of the Empties' walls and
the office's, as `_nearest_below` returns -INF there. The repair had moved the artefact, not removed it.

**Third run** (`edges_9317_probe2.json`, `sort_9317_probe2.out.txt`): in pass 2, a neighbour column with no
surface is tested with the same sphere at its own standing point before it counts as a drop; inside something,
it is a wall the body walks into, not an edge it walks off. Bottomless indoors 2,090 -> 191. The sort then
gained a `slab_cut` class -- every hole the builder cut, read off the built slots' floor and roof `fit.voids`
(relative to the slot's translation; checked against deli_a01's stair at (-15, 9), its ladder at (8, -12), its
hatch at (-12, 8) and its floor hole at (8, -4), all four landing on a void) -- and it claimed 58 edges, so the
storey rims were NOT at the builder's cuts. Their heights said why: 236 at 6.3 m under the sky on deli_a01, whose
roof top is 6.6; 206 at 3.0 and 222 at -0.3 indoors, each 0.3 m under a floor's top. The downward ray meets a
slab's underside (a ceiling skin, a slab's bottom face) and the headroom ray from there starts inside the slab
and sees nothing; the shin-high sphere, 0.6 m up, stands clear above the slab's top. A surface inside a slab.

**Fourth run** (`edges_9317_probe3.json`, `sort_9317_probe3.out.txt`): the headroom ray and the sphere are one
test now, the body's own column -- a capsule `PROBE_R` 0.20 wide and `STAND_M` 1.80 tall standing on the hit,
overlapping nothing (CLAUDE.md's rule: "does a body fit" is a shape question). A hit inside a slab is inside the
capsule. The neighbour-solid test uses the same capsule.

    run                       drop edges   unguarded   indoors   wall_line (in)   bottomless (in)   storey_rim (in)
    1  rays only                  22,445      16,739     6,004     2,703 (939)      3,753 (137)       1,053 (651)
    2  + shin probe               24,121      16,493     4,897     1,387 (32)       8,803 (2,058)     1,622 (1,152)
    3  + neighbour-solid test     13,618      11,798     2,998     1,357 (12)       4,138 (179)       1,622 (1,152)
    4  capsule for the body        8,722       7,330     1,958       545 (0)        1,855 (61)          643 (592)

    fourth run, the classes:  site_edge 1,855 (61 in)   wall_line 545 (0 in)   stair 45 (32 in)   hatch 52 (26 in)
                              floor_hole 16 (16 in)   slab_cut 38 (38 in)   roof_rim 236   storey_rim 643 (592 in)
                              prop_top 3,858 (1,151 in)   ground 42 (42 in)   other 0

The instrument's tests are in `tools/walkable_edge.gd` with the counts above beside them. The 545 wall-line
edges left are all outdoors (parapet tops, the sidewalk beside a face), and the 61 bottomless indoors are small
enough to read one by one.

**The number this left: 643 storey rims, 592 of them indoors, and they were three places** -- deli_a01's ground
floor (220 edges at 0.0 m) and first floor (183 at 3.3 m, 6.6 m down), office's second floor (115 at 7.2 m) --
and the reading written here before they were probed was wrong in all three of its guesses (a void cut and not
recorded, a wall with no collider at step-over height, a lip somebody meant). Kept, with what replaced it.

## Five more repairs, each attributed in the scene before it was made

`probe_at.gd` (beside this README; launched like the instrument, with a points file) reads what stands at a
reported edge: every surface in the two columns 0.25 m either side of it, by node path, what the body's capsule
overlaps standing on each, and what a ray at step-over height between them meets. `residue_points.json` /
`residue_probe.json` are 16 points from the three places; `roof_points.json` / `roof_probe.json` one roof rim per
face of the deli; `residue_points_run6.json` / `residue_probe_run6.json` the eight storey rims of the sixth run;
`ramp_points.json` / `ramp_probe.json` eight points up each building's stair. Every run's rows and sort are kept
(`edges_9317_probeN.*`, `sort_9317_probeN.out.txt`, `*_classed.json` from `--dump`).

**The three places were furniture and walls, read as drops a storey down.** At all 16 points both columns stand
on the same slab, no barrier meets the ray between them, and the "drop" side is a cell where a prop or a wall
occupies the body's volume: carton stacks and the front counter on the deli's ground floor, planter boxes and the
counter island in its upper hall, desks, a shelf run, cubicle banks and an interior wall segment in the office.
The standing capsule rejected the floor under each (it overlaps the thing), so the next surface the body fitted on
in that column was a storey down; the 6.6 m run at deli x -8 is the upper hall's furniture standing over the
ground floor's interior wall line, whose column has no free surface at 3.3 OR at 0. A blocked neighbour is an
obstruction, not a drop.

- **Fifth run** (`edges_9317_probe4.*`): every drop candidate's neighbour tested with the whole capsule at the
  cell's level. Storey rims 643 -> 0 -- but it swallowed the guards (7,629 drops, 7,628 unguarded, ONE guarded: a
  rail within the capsule's reach reads as a wall) and would read a kerb the body steps over as a wall; and the
  plate's rim came back, 1,855 -> 3,237, wall-line 545 -> 686: the old bottomless test's capsule was centred
  0.6 m up and reached 0.3 m BELOW the cell, meeting the cell's own slab at a true rim. Both spellings are kept
  in the file beside the one that replaced them.
- **Sixth run** (`edges_9317_probe5.*`): the transition surface in the next column is the highest within
  step-UP range (a planter the body steps onto is a step, not a 6.6 m fall past it); the barrier ray is asked
  first, so a guard stays a guard; the blocking shape is only the body ABOVE what it steps over, from `FALL_M`,
  the one number the step test shares. Drops 19,864: guarded 7,411, blocked 4,966, unguarded 7,487 (1,538
  indoors); storey rims 8. Rows carry `on` / `to` from here: the owners of the surface the cell stands on and
  of the one it drops to.
- **The 236 roof rims of the fourth run were the parapet.** On all four faces of the deli the cell beside the
  rim overlaps `GreyboxBase/parapet_*_col` with its standing capsule, and the parapet's inner face sits between
  the neighbour's centre, where the barrier ray ENDS, and the capsule's reach. The block test holds them.
- **The eight storey rims of the sixth run:** six first-floor cells beside two carton stacks
  (`cartons_rb2746d70_7/_8`) and two roof cells beside `RoofProps/ExhaustFan2`, each a thing under 0.52 m tall
  within 0.2 m of the cell's centre, so neither a surface in that column nor met by the block shape -- and the
  "drop" was THROUGH the slab to the storey below. Rejecting an occupied surface let the column see through it.
- **Seventh run** (`edges_9317_probe6.*`): an occupied surface stays in the column as occupied, and a body
  whose transition surface is occupied walks into the thing (`occupied_next` 13,911). Drops 5,953: guarded 868,
  blocked 0 (the block shape found nothing the occupied rule had not), unguarded 5,085 (910 indoors). Standable
  114,890 in runs 4 through 7: the column pass's control. Sorted by owner first: perimeter-fence tops 2,464,
  parapet tops 987, prop tops 1,315 (877 indoors: cars 185, cubicle banks 330, a honey locust 88, parking meters
  61, desks, filing cabinets, cartons), the roof strip outside the parapet 278, hatches 21, floor holes 16,
  cuts 4; storey rim, stair, site edge, roof rim, ground: 0.

**What a surface IS, by owner, is in `sort_edges.py` now** (`_floor_like`): Deli Counter's slabs
(`GreyboxBase/slab_col_<n>`), roofs (`roof_footprint/Roof`, an Empty's `KitCollision/Roof`), stair ramps, landings
and discharges (`GreyboxBase/stair<n>...`), ladder planes, and Lot's own surfaces, which are the site node's
direct children (`Site/Ground_13`, `Site/road_0`, `Site/sidewalk_1L_1`, `Site/frontage_0L_1`,
`Site/kerbcut_0L_1`, `Site/path_1`, `Site/yard_1`); `Site/perim_*` is the fence. One collider is not identified:
`GreyboxBase/@StaticBody3D@19803` (`@19802` in the office), a surface 1.05 m above the ground floor in both
mission buildings, 22 rows -- a sill, a counter, or an interactive's state collider. Its owner is the next thing
to name.

**Then reachability, which answers the same question without names (eighth run, `edges_9317_probe7.*`).**
Every top the body fits on is standable -- the fence, a parapet, a car's roof -- and none is anywhere a body
walks. The instrument takes a seed now, the package's `player_start` anchor (the getaway van's crew spawn, here
(44.85, 0, 15.47)), and floods from it across the transitions the edge pass itself uses: a step up to `FALL_M`, a
step down, a fall onto a free surface; only reached cells are asked, and the report tallies standable and reached
cells by owner. 75,155 of 114,890 standable cells reached; 863 drops, 857 guarded, 6 unguarded, all six the deli's
own ladder hole to its basement (declared). But the flood reached NO upper floor and NO roof in any building
while it reached both basements: it descends a stair (a fall) and never climbs one. `ramp_probe.json`: at every
point up deli_a01's flight the standing capsule overlaps `stair1ramp_0`, the ramp it stands on, and the rise is
0.41-0.42 m per 0.5 m cell -- 39-40 degrees, Deli Counter's own cap (`stair_pitch.py`,
`MAX_WALKABLE_PITCH_DEG` 40). With 2 cm of clearance a capsule 0.2 m wide overlaps a 40-degree ramp 8 cm from its
contact. (The office's eight points were taken at x 48.0, the seam between its two side-by-side flights, and
overlap both flights; they show the seam, not a headroom problem.)

- **Ninth run** (`edges_9317_probe8.*`, seeded): the standing capsule is lifted by `PROBE_R * tan(slope)` from
  each hit's normal, and a surface steeper than `FLOOR_MAX_DEG` 45 (the controller's `floor_max_angle`) is
  neither a standing point nor a wall. Standable 114,992 (22,984 occupied, 4,184 steep); reached 84,367:
  deli_a01's first floor 3,600 of 3,600 and its basement, the office's first and second floors in full (2,814
  and 2,650), the pharmacy's ground floor; no roof (the deli's is reached by its ladder, which is a climb the
  flood does not make -- open) and no Empty's upper floor (their doors are shut by design). 936 drops: 874
  guarded, 3 blocked, 59 unguarded, all 59 indoors.

**Where this stands on 9317: 59 edges, three kinds.** 33 are declared by the package's own records: 13 at the
two ladder hatches (`hatch`), 16 at `floor_hole` links, 4 at recorded cuts (`slab_cut`). 3 are a guard rail's top
(`stair_guard_rail_1_col`, a cell the flood steps onto from the ramp beside it; excluded by owner). And 23 are on
the stairs (`stair_points.json` / `stair_probe.json`), probed: FIVE at the office's storey-2 discharge landing
(`stair0col_discharge_1`, x 48.5-49.75, z 1.5-1.75), whose edge over the well looks 6.65-6.67 m straight down onto
the lower flight's foot, with nothing at step-over height between the cells and nothing in the body's column
beyond; SEVEN along the office's upper flight (`stair0ramp_1`, x 48.25), whose inner side is open over the lower
flight 1.3-5.9 m below; and ELEVEN at the first metre of three flights' open sides (the office's lower flight at
x 49.75, the deli's up and down flights at x -63.75, -61.75 and -67.75), drops of 0.52-1.3 m, the "deliberately
open sides of staircases" the item named. The first two are what this instrument exists to find. Whether they
are guards without colliders or no guards at all is a question for the scene and for Deli Counter's
`stairwell.py` -- which sides of a switchback it guards, and whether it guards the top landing -- and it is the
next thing.

## What is left

1. ~~The office's two stair gaps attributed against Deli Counter's guard rules, and fixed there if they are
   real~~ -- DONE the same evening, Deli Counter 0.225.0 (`patches/patch_dc_switchback_top_run.py`): both gaps
   were rules. `rail` left the arrival end open across the whole reserved rectangle, two runs wide, while the
   arriving flight is one run wide; `side` stood only on the rectangle's outer edges, so nothing guarded the
   seam between a switchback's runs; and the top leg's cut spanned both runs when only its own run reaches that
   storey. Now the top leg cuts and reserves its own run (the slab covers the pit), a thin seam wall runs to
   the turn landing with its underside a body's height above the floor (the nav gate's measurement on one
   shell: `patches/dc_switchback_top_run/nav_gate_bisect.md`), and the rail rule puts a rail at the seam. The
   re-measure is cold run 9318 (staged) with the instrument seeded and linked (the session's `edge_9318.sh`):
   the 12 office rows should be gone and the 11 feet remain.
2. The declared set read off the package's records (stair footprints, hatch and `floor_hole` links, recorded
   cuts) and emitted as `walk_off_ledge` links in Dispatch's `navigation_hints`, so the gate's list and the AI's
   are one list.
3. The gate in Level Factory: the instrument seeded from the package's `player_start`, surfaces read by owner
   with the toolchain's names (`_floor_like` here), the residue frozen as a baseline that fails on a new entrant
   (178's pattern).
4. Ladders in the flood: a roof reached by its hatch is a place a body stands, and today no roof is reached.
5. `GreyboxBase/@StaticBody3D@19803` named.
