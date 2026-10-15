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

**The number this leaves: 643 storey rims, 592 of them indoors, and they are three places.** deli_a01 at its
ground floor (220 edges at 0.0 m, a full storey down) and at its first floor (183 at 3.3 m, 6.6 m down -- a run
along world x -59.0 .. -59.25, z -6 .. -14, in the building's frame x -8, y 3.5 .. 11.5, where the next column
has no floor at 3.3 or at 0 and its nearest surface is the basement at -3.3); office at its second floor (115
at 7.2 m); and about 75 smaller ones (pharmacy_a01's roof rim at 3.4, office mezzanine lips at 3.6 and 7.2). None
is at a hole the builder recorded, so each is either a void the builder cut without recording it as one, a wall
with no collider (the barrier ray at step-over height passes where a wall should stand), or a lip somebody
meant. Reading those three places in the scene is the next step, and it is now a morning's work rather than a
census. Then the furniture (1,151 prop tops indoors) by what a surface IS, the declared set emitted as links,
and the freeze.
