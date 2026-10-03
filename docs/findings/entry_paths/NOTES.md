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
