"""Roadmap batch 47, 2026-09-13: cold run 9027 zero with the waiting places
standing (17 REPLACE, old kept); the paint as a decal and intersections in
the tools (153 REPLACE, old kept; 152 REPLACE, old kept). Asserts every
anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-13 (night) -- COLD RUN 9026 WAS NOT A ZERO: THE
LASER TAG PREFLIGHT REFUSED THE FIRST SEED ON THE WRONG STOREY, AND THE
EXPORT GATE HELD.""",
"""*STATUS: NARROWED 2026-09-13 (night) -- COLD RUN 9027 SCORED ZERO WITH
THE WAITING PLACES STANDING. The bank brief on Zoo 0.68.1 / Lot 0.64.0 /
LF 0.78.1: 0 interventions, 0 retries, 0 unattributed changes, every tool
repo clean at --begin, all stages succeeded, 0 blockers, export exit 0,
29 minutes (17:49 -> 18:18); 1 bus shelter with its bench, 17 street
trees, 16 lamps, 4 signs, 3 hydrants, 3 bins and 31 parked cars; every
species in the site kit `pass`, none boxed; the preflight's new
`LT_STOREY_UNSEEN` advisory filed once and blocked nothing. The
eighteenth zero. Frames: the shelter glazed with the bench inside and a
car at the kerb; the trees' faceted crowns over the parked row
(`docs/cold_runs/cold_9027/frames/`). Cold run 9028 (Lot 0.65.0,
Pixelcoat 0.31.0, LF 0.79.0: a cross street, the paint as a decal) is
running. Previously: COLD RUN 9026 WAS NOT A ZERO: THE
LASER TAG PREFLIGHT REFUSED THE FIRST SEED ON THE WRONG STOREY, AND THE
EXPORT GATE HELD."""))

R.append(("""*STATUS: NARROWED 2026-09-13 (night) -- THE WAITING PLACES ARE IN THE
TOOLS: A TREE BETWEEN THE LAMPS, A BUS STOP PER ROAD.""",
"""*STATUS: NARROWED 2026-09-13 (night) -- THE WAITING PLACES ARE MEASURED
(9027); THE PAINT IS A DECAL AND THE STREET HAS A CORNER, IN THE TOOLS.
Cold run 9027: 1 shelter, 1 bench, 17 trees, 16 lamps standing, every
species `pass`. THE PAINT: Pixelcoat 0.31.0 mints `road_paint` -- a kind
for Lot, near-white at 0.5 m per tile with a CUTOUT alpha (a new grammar
field thresholding a generator field into on/off alpha, the paint worn
through to the road in patches) and an `alpha_mode: scissor` hint; Lot
0.65.0 gives the markings a `paint` skin family, `transparency = 2` when
the pack asks for scissor, and tints the pack by the marking's own colour
(white lines, a yellow centre line); LF 0.79.0 names the pack. THE
CORNER: Lot 0.65.0's street model holds intersections -- a road crossing
is a BOX (the crosser's width plus its bands), crosswalks at each end of
the box in line with the crosser's sidewalks, the stop bar only on the
leg that ENDS there (`Cut.terminal`, judged at the centre line), the
centre and edge lines broken over the box (the edge line over a road's
mouth only), parking clear of it, and a road that ends on another begins
its slab at that road's band edge so no two slabs lie coplanar over the
mouth; LF 0.79.0's spec adds a cross street north from the through road
through the widest gap between two buildings that holds a band (9021's
row: 31 m, at x = -20.5), else past the west end with the plate widened.
Residue: two roads CROSSING (an X) still overlap their slabs -- the spec
makes a T. Cold run 9028 measures both. WHAT REMAINS after it: the cover
planner's truck-in-the-road as the exception now that cars park; the
tree's crown as cutout cards. Previously: THE WAITING PLACES ARE IN THE
TOOLS: A TREE BETWEEN THE LAMPS, A BUS STOP PER ROAD."""))

R.append(("""*STATUS: NARROWED 2026-09-12 (late night) -- STEP 1 OF THE BUILD ORDER IS
IN A COLD PACKAGE (9017): THE GROUND PLATE AND THE PATHS WEAR PIXELCOAT
SKINS, AND THE CLUTTER SITS ON A SURFACE.""",
"""*STATUS: NARROWED 2026-09-13 (night) -- STEP 2 HAS ITS FIRST DECAL IN THE
TOOLS: THE ROAD PAINT. Pixelcoat 0.31.0 `road_paint` (a cutout alpha, a
scissor hint), Lot 0.65.0 (the marking quads wear it, tinted), LF 0.79.0
(the spec names it) -- see item 153; cold run 9028 is the measurement.
It is the decal layer's shape: a Pixelcoat pack with alpha, placed
geometry that carries it, the consumer told to test rather than blend.
Steps 3 and 4 (clutter anchored and coloured by its surface with the
density table turned round; the low band) and the grammars (item 45: the
asphalt still reads as paving cells on the 9027 frames) remain.
Previously: STEP 1 OF THE BUILD ORDER IS
IN A COLD PACKAGE (9017): THE GROUND PLATE AND THE PATHS WEAR PIXELCOAT
SKINS, AND THE CLUTTER SITS ON A SURFACE."""))


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
    print(f"wrote {len(out)} bytes ({len(raw)} before); 17, 153, 152 updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
