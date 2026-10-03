## 0.88.0 - a path meets a door, not the middle of a wall

The walker, 2026-10-03, on cold run 9139's lot: "sidewalks don't
consistently lead up to doors which seems random", and after the first look,
"lot still not drawing walkways to open doorways". Read off the spec: the
door spur Level Factory authors for each building runs at the building's
centre x (`road_grammar._spurs`: ``{"a": [x, face - 1.0], ...}``), and the
bank's two south doors sit metres from its centre, so the spur met a blank
wall between them; the 8 m paths between buildings ran centre to centre and
met each facade wherever the centre line crossed it. Seven readers in this
repo resolved ``from``/``to`` to the centres, each in its own line.

`site_paths.snap_to_doors(site_spec, merged)`, run once in `assemble` after
the gameplay merge and before anything reads a path: for every path end that
belongs to a building, the storey-0 exterior entries that face the way the
path leaves (`site_enterability._approach_points`, the gate's own reading,
dot with the leaving direction at least `FACING_DOT` 0.7) are the doors on
the facade the path meets, and the nearest to the path's line wins. A spur
slides sideways along the facade to run at that door, its authored standoff
kept; a building path's end becomes the point `DOOR_STANDOFF` (1.0 m, the
spur's own figure) in front of the door. The resolved ``a``/``b`` are
written into the spec's path record beside its ids, with ``snapped`` naming
the wall, so the connectivity graph and the surface labels do not move. A
facade with no door is said (`LOT_PATH_END_OFF_DOOR`) and the end stays:
inventing a door is not this module's to do.

`site_paths.endpoints(p, bld)` is now the one reader -- ``a``/``b`` when a
record carries both, else the centres -- and `path_slabs`,
`site_enterability._near_route`, `site_surfaces._path_segments`,
`site_steps.routes`, `site_streets._endpoints` (which `site_furniture` and
`kerb_crossings` use) and `site_extent` call it. A hand-authored spec with
no resolved points reads exactly as before.

MEASURED (`patches/lot_door_paths/snap_census.py`, which snaps a copy of
every site spec on disk that has its merged gameplay beside it and writes
nothing). The walker's lot, gas_block_001 seed 9080: all 8 building-owned
ends snap -- the bank's spur slides 9.0 m, from x 62 to its south door at
x 53 (the walker stood at x 54.2 looking at the blank wall the old spur
met); the gas station's 3.5 m; the terminal's none (its door is on its
centre line); the two 8 m building paths end a metre in front of the
facing east and west doors instead of under the buildings.

Every site on disk -- 204 specs, 36 distinct lots:

    building-path ends          468    left at the centre    36
    door spurs                  920    left at a blank wall  312  (177 sites)

THE 312 ARE NOT THIS MODULE'S TO FIX, AND THEY ARE THE BIGGER FINDING. A
third of all door spurs run to a facade with no ground door on it at all:
Level Factory's road grammar authors a spur from a building to every road
it faces, and rotates buildings, without reading where the doors are (a
credit union turned 90 has doors east, north and south and a spur to the
west; strip clubs, funeral homes and gas stations lead the list). Before
this release that was silent; now each prints `[lot] LOT_PATH_END_OFF_DOOR:
...` and rides the tactical report as a minor finding. Closing them is a
Level Factory change -- face a door to the street, or do not draw a walk to
a wall -- and is recorded as open in
`docs/findings/entry_paths/NOTES.md`.

`tests/test_site_paths.py`: the spur slides and keeps its standoff; a
building path ends in front of both facing doors; a rotated building's door
is found in world space; a blank facade is said and the end stays;
`endpoints` prefers the resolved points; the slab and the enterability route
check read the snapped ends (0.83.0 had left "whether a route drawn centre
to centre is the right model" as a separate question -- this is the answer,
and the route check's warning now means what it says). All six fail against
0.87.0.

