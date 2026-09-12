"""Roadmap batch 44, 2026-09-13: the paint and the kerb line in cold packages
-- 153 REPLACE (old kept), 17 REPLACE (old kept) for cold runs 9023 and
9024. Asserts every anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-13 -- STEP ZERO IS IN A COLD PACKAGE: THE
GENERATED SITE HAS A ROAD WITH SIDEWALKS, AND THE KERB IS CUT WHERE THE
CREW CROSSES AND A WALL EVERYWHERE ELSE.""",
"""*STATUS: NARROWED 2026-09-13 (evening) -- THE STREET IS A MODEL, THE PAINT
IS ON THE ROAD AND THE KERB LINE STANDS ON THE SIDEWALKS, ALL IN COLD
PACKAGES. Lot answered the walker's "does Lot need to evolve now" in
three releases the same day. 0.61.0: `site_streets`, the road as a model
-- kerbs, cuts, spans, the crossings of the centre line, a point at any
station and offset -- with the writer drawing what it says byte for byte
(792 road-family node lines identical before and after on the kerb
probe), and the paint from the same model: an edge line each side, a
dashed yellow centre line clear of the crossings and their stop bars, a
continental crosswalk at every crossing stationed on the CENTRE line (at
the kerbs it was fourteen crosswalks for eight crossings, two per
diagonal path), a stop bar per lane; flat quads one tier above the road,
no collision, and the same rectangles in `<site>.markings.json` for the
decal layer; `road` and `sidewalk` zones for the dressing planner. Cold
run 9023: 31 marking nodes in the package, the frame down the road a
street. 0.62.0: `site_furniture`, the kerb line -- a streetlight every 25
m and at every crossing a hydrant past the cut, a bin before it, a stop
post at its edge facing the road -- as the cover planner's own prop-slot
records with a `base` of `sidewalk`, so the site kit builds them and the
themed site stands them on the band's top; Zoo 0.67.x minted the hydrant,
the bin and the post beside the existing lamp. Cold run 9024: 23 pieces
placed (14 lamps, 3 each of the rest), 36 modules instanced, the corner
frame a sign, a bin and a hydrant at the crosswalk with the lamps down
the road. WHAT THE KIT INDEX SAYS THAT THE FRAME DOES NOT: two of the
seven site modules fail exact fit -- `streetlight` builds 6.18 m against
a 6.00 m slot, because its recipe floats the head above the lamp point it
puts at +h/2 on purpose, and `simple_car` 4.36 against 4.30, its bumpers
0.03 m proud at each end -- and Lot instanced them anyway, because it
resolves a module by file, not by the index's verdict. The car's bumpers
are brought within its length (Zoo 0.67.2); the lamp is a contract
question between its recipe and Lux's lamp point, recorded here rather
than moved in a hurry; and Lot reading the index's `status` before
standing a module is the next honest step. WHAT REMAINS: parking bays
and cars parked in them (the cover planner already stands cars in the
road: 9024 placed 13 pieces, four of them cars); the bus stop and the
tree; a marking texture in Pixelcoat so the paint is a decal and not a
quad; intersections, which the model was built to hold and the generated
spec does not ask for. Previously: STEP ZERO IS IN A COLD PACKAGE: THE
GENERATED SITE HAS A ROAD WITH SIDEWALKS, AND THE KERB IS CUT WHERE THE
CREW CROSSES AND A WALL EVERYWHERE ELSE."""))

R.append(("""*STATUS: NARROWED 2026-09-13 -- COLD RUN 9022 SCORED ZERO WITH A STREET
IN THE PACKAGE.""",
"""*STATUS: NARROWED 2026-09-13 (evening) -- COLD RUNS 9023 AND 9024 SCORED
ZERO: THE PAINT, THEN THE KERB LINE. Both the bank brief. 9023, on Lot
0.61.0: 0 interventions, 0 retries, 0 unattributed changes, every tool
repo clean at --begin, all stages succeeded, 0 blockers, export exit 0,
20 minutes (16:10 -> 16:30); 31 marking nodes (12 crosswalk bars, 11
dashes, 6 stop bars, 2 edge lines) over the road from 9022's shape; the
fifteenth zero. 9024, on Lot 0.62.0 / Zoo 0.67.1: the same zeros, 17
minutes (16:30 -> 16:47); 23 kerb-line pieces and 13 cover pieces
planned, 36 modules standing in the package, the site kit 5 of 7 modules
`pass` (the lamp and the car fail exact fit by 0.18 and 0.06 m, item
153), the walktest and Laser Tag routing across a street with 36 more
colliders on it; the sixteenth. Said plainly, because it was the wrong
way round: Zoo 0.67.0 was committed with three of its own material tests
red and fixed in 0.67.1 twelve minutes later; the run began on 0.67.1.
Logs and journals: `docs/cold_runs/cold_9023/`, `cold_9024/`; walk copy
`_runs/walk_export_bank_block_001` is 9024's. Previously: COLD RUN 9022
SCORED ZERO WITH A STREET
IN THE PACKAGE."""))


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    for old, new in R:
        if text.count(old) != 1:
            print(f"anchor matched {text.count(old)} times; refusing: {old[:60]!r}", file=sys.stderr)
            return 1
    for old, new in R:
        text = text.replace(old, new, 1)
    out = text.encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); 153, 17 updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
