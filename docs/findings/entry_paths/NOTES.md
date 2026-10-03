# Entry walkways that end at a blank wall

The walker, 2026-10-03, walking the gas station lot: "sidewalks don't
consistently lead up to doors which seems random", with a frame of a paved
spur running from the sidewalk to the bank's facade and stopping a few
metres right of the door it should serve.

## The cause, read off Lot

`lot/lot.py::path_slabs` draws one slab per declared path, from
`bld[p["from"]]["at"]` to `bld[p["to"]]["at"]`: the CENTRES of the two
buildings. The slab runs through both footprints, and the part a player
sees is whatever is left between the facades -- it meets each facade where
the centre line happens to cross it, which is the door only by luck. The
spur in the frame is that: aimed at the bank's centre, not its door.

Lot already knows where the doors are. `site_enterability._approach_points`
reads each building's `gameplay.json` for its entries and computes an
approach point outside each, and the enterability gate judges every
building by them.

## The fix (Lot, not built)

End a path at the nearest ENTRY APPROACH of each building it joins rather
than at the centre, and stop the slab at the facade. One place to change
(`path_slabs`), one existing source of truth to read (the approach points),
and a test that every path's end lies within a stride of an entry approach
and outside the footprint. Where a building has no usable entry the path
keeps its old behaviour and the gate already says so.

## Who declares paths

The site spec's `paths` list, written upstream by the brief's layout; this
note is about where Lot draws them, not whether they should exist.

## Built: Lot 0.88.0 (2026-10-03), and a correction to the cause above

Kept above as written. One thing in it was imprecise: the spur in the
walker's frame is not a `from`/`to` path. It is the DOOR SPUR Level Factory
authors for each building (`road_grammar._spurs`), a raw-point path at the
building's centre x from a metre off its face to the sidewalk. The bank's
centre is x 62; its south door is at x 53; the walker stood at x 54.2. The
centre-to-centre reading is true of the two 8 m paths between buildings,
and the same resolver fixes both.

`lot/site_paths.py` (`patches/patch_lot_door_paths.py`): `snap_to_doors`
runs once in `assemble`, after the gameplay merge. For every path end that
belongs to a building it takes the storey-0 exterior entries that face the
way the path leaves (the enterability gate's own reading), picks the
nearest to the path's line, and slides a spur sideways to that door or ends
a building path a metre in front of it. The resolved points are written
into the spec's path record, and one `endpoints` reader replaces the seven
places that each resolved a path to building centres, so the slab, the
surface zones, the step and kerb gates, the plate extent and the
enterability route check all read the same geometry. Six tests, all
failing on 0.87.0; suite 611.

## What it does, measured (`patches/lot_door_paths/snap_census.py`)

The walker's lot (gas_block_001, seed 9080), all 8 building-owned ends:

    path             end a before -> after           snapped to
    b0 -> b1  (8 m)  (-59.0, 10.0) -> (-47.0, 15.0)  station's east door
                     ( -1.0,  5.0) -> (-29.0, -4.5)  terminal's west door
    b1 -> b2  (8 m)  ( -1.0,  5.0) -> ( 27.0,  5.0)  terminal's east door
                     ( 62.0, 10.0) -> ( 43.0, 10.0)  bank's west door
    spur b0 south    x -59.0 -> -62.5                 station's south door
    spur b1 south    x  -1.0 ->  -1.0                 already on it
    spur b2 south    x  62.0 ->  53.0                 bank's south door
    spur b0 west     unchanged                        already on it

Every site spec on disk with its merged gameplay beside it -- 204 specs,
36 distinct lots:

    building-path ends   468    left at the centre     36
    door spurs           920    left at a blank wall  312   (177 sites)

## Open, and bigger than what was fixed: a third of door spurs lead to a wall with no door

The 312 are not a snapping problem. The facade the spur meets has no
ground door on it at all, so there is nothing to slide to. They come from
upstream: Level Factory's road grammar draws a spur from a building to
every road it faces, and rotates buildings, without reading where the doors
are. By building and rotation on the distinct lots: gas_station_a02 at 90
(3 of its 4 spurs), strip_club_a01/a02/a03 (3 each), funeral_home_a02,
mansion_a02 at 180, credit_union_a02 at 90 (doors east, north and south; a
spur to the west), video_store_a01 at three rotations. Before 0.88.0 this
was silent. Now each prints `LOT_PATH_END_OFF_DOOR` and rides the tactical
report as a minor finding, so a cold run shows them.

Three ways to close it, in Level Factory, not built:

1. **Face a door to the street.** Choose each building's rotation from its
   own ground doors so one faces the front road. Fixes the front spurs at
   their source and is what a real lot does. It changes every seed's
   layout, so baselines move.
2. **Do not draw a walk to a wall.** Keep the path record (the street graph
   reads it to know the building meets that road) and mark it undrawn when
   the facing facade has no door. Cheap, changes no layout, removes the
   walkway the walker would call wrong; leaves the building without a
   paved way in from that street.
3. **Route round the corner.** From the nearest door on an adjacent face,
   out a metre, along the facade and down to the sidewalk: an L. Needs
   paths to be polylines, which every reader in Lot would have to learn.

Recommended: 2 first (small, no layout change, stops the visible defect on
177 sites), then 1 as its own piece with a before-and-after census, since
it reshuffles lots. 3 only if 1 leaves side streets badly served.
