"""Roadmap batch 42, 2026-09-13: item 153 filed (APPEND) -- the street's order
vocabulary, from the walker's question. Asserts the item is not present.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

APPEND = """
*STATUS: OPEN 2026-09-13 -- FILED FROM THE WALKER'S QUESTION AFTER THE SPECIES
COVER LANDED; THE VOCABULARY AND ITS OWNERS ARE IN THE ITEM, NOTHING BUILT*

**153. A street reads as ordered when its furniture says where cars and
people go, and the lot has none of that furniture yet.** The walker,
2026-09-13, after item 22 put a truck and a container on the lot: "what
other species should decorate a street where cars and people transport
themselves with order." Order on a street is not the buildings and not the
vehicles; it is the small vocabulary that assigns every metre of ground to
a use -- a painted line, a kerb-line post, a place to wait. Three layers,
each with an owner that already holds what it needs. THE MARKINGS (Lot says
where, Pixelcoat/Patina say what; height zero, so the honesty rule never
enters): crosswalk stripes at every kerb cut `_kerb_crossings` already
computes, stop bars where a path meets a road, a centre line and lane edges
along every road, parking-bay lines along the kerb, arrows at the lane
ends, the yellow kerb face where nothing may stand. This is the cheapest
order there is and the most legible from eye height; it is item 152's
decal layer with Lot's road geometry as the anchor set. THE KERB LINE (Lot
places, along the kerb between the crossings, at spacings it derives; Zoo
builds; every piece above 0.117 m carries collision): streetlight (exists,
0.7 x 0.3 x 6.0) at a lamp spacing; traffic signal -- a pole with a mast
arm and a three-lamp head -- at each crossing corner; stop and regulatory
sign posts (0.1 x 0.1 x 2.4, a plate on top) at the corners a signal does
not take; fire hydrant (0.3 x 0.3 x 0.75); parking meter (0.15 x 0.15 x
1.4) one per bay; bollards (0.2 dia x 0.9) in rows at crossings and
storefronts, gaps never under the contract's door width; litter bin (0.6 x
0.6 x 1.0); newspaper boxes in a cluster (0.5 x 0.4 x 1.2); mailbox (0.5 x
0.6 x 1.2); utility cabinet (0.9 x 0.5 x 1.4); bike rack (0.9 x 0.1 x
0.8); utility pole (0.3 dia x 9.0) with a crossarm, and the wire between
two of them. THE WAITING PLACES (Lot places by role; Zoo builds; these are
cover too, and the cover planner counts them): a bus stop as a set --
shelter (3.0 x 1.5 x 2.5, the walker's transparency: glass panels on a
frame), bench (1.8 x 0.5 x 0.45), sign post; benches and planters (2.0 x
1.0 x 0.9, a shrub in it) along storefronts; a tree in a kerb grate (the
contract's alpha-cutout foliage, the first species that needs it). AND
THE CARS THEMSELVES, IN ORDER: `simple_car` parallel-parked in the bays
the markings draw, at a seeded occupancy, each a collision slot like the
cover pieces -- which unifies with item 22: a parked car IS cover, and
the sightline planner's pieces become the cars that were going to be
there anyway, with a truck or a container only where a lane still needs
breaking. MEASURED FIRST, BECAUSE IT CHANGES THE ORDER: every cold package's site
spec carries `paths` and no `roads` -- `_write_site_spec` writes the
connections between doors as walkways (the comment calls them roads; the
key is `paths`), so Lot's road, sidewalk, kerb and `_kerb_crossings`
machinery, all of which exists for hand-authored specs, has never run on a
cold package. The street the walker is standing in is a plate with paths
across it. Step zero is therefore the road itself: the spec names roads
with sidewalks where today it names paths, and the kerbs, crossings and
kerb cuts that already exist appear on their own. WHAT DECIDES THE ORDER
OF WORK AFTER THAT: markings first (zero geometry,
maximum legibility, the anchors exist), then the kerb line (the species
are boxes and posts that a placeholder recipe already serves), then
parked cars in bays (the recipe exists), then the bus stop and the tree
(the first alpha-cutout species and the first transparent one). WHAT THIS
IS NOT: item 148's interiors, and not item 152's clutter -- this is the
layer between them, the one that makes a street a street. **WHAT WOULD
CLOSE THIS:** a cold package whose street carries markings at Lot's
crossings, a lit kerb line with signals at the corners, and cars parked in
bays, judged from eye height by the walker as a street one could drive
and cross.
"""


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    if "\n**153. " in text:
        print("item 153 already present", file=sys.stderr)
        return 1
    text = text.rstrip("\n") + "\n" + APPEND.rstrip("\n") + "\n"
    out = text.encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); 153 filed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
