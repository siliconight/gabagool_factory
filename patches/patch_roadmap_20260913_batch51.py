"""Roadmap batch 51, 2026-09-13: cold run 9031 zero with the four residues
in the package (17 REPLACE, old kept; 153 REPLACE, old kept). Asserts every
anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-13 (night) -- COLD RUN 9030 WAS NOT A ZERO: TWO
SEED DEFECTS, ONE IN ZOO AND ONE IN LOT, AND THE EXPORT GATE HELD.""",
"""*STATUS: NARROWED 2026-09-13 (night) -- COLD RUN 9031 SCORED ZERO WITH THE
CROWN AS CARDS, THE PAINT IN PATCHES AND THE CARS BEFORE THE COVER. The
bank brief on Lot 0.66.1 / Zoo 0.69.1 / Pixelcoat 0.32.0: 0 interventions,
0 retries, 0 unattributed changes, every tool repo clean at --begin, all
stages succeeded, 0 blockers, export exit 0, 11 minutes (19:29 -> 19:40);
every site-kit module `pass` (10 of 10), 16 trees, 15 lamps, 2 bus stops,
21 cars, 6 cover pieces on this seed's layout. The twenty-first zero.
Frames (`docs/cold_runs/cold_9031/frames/`): the tree's crossed cards
wearing the foliage cutout -- leaf clusters with sky between, alpha
tested in Godot; the worn patches on the crosswalk bars and the edge
line; the T with a crosswalk each side of the mouth. Previously: COLD RUN
9030 WAS NOT A ZERO: TWO
SEED DEFECTS, ONE IN ZOO AND ONE IN LOT, AND THE EXPORT GATE HELD."""))

R.append(("""*STATUS: NARROWED 2026-09-13 (night) -- THE FOUR RESIDUES ARE IN THE TOOLS,
MEASURED BY 9031.""",
"""*STATUS: NARROWED 2026-09-13 (night) -- THE FOUR RESIDUES ARE IN A COLD
PACKAGE (9031). Measured on its frames: the cards carry the cutout and
read as leaf mass with sky between; the paint's wear is patches; the
cars stand before the cover planner and the corner is drawn once. WHAT
THE FRAMES SAY NEXT: the crown's silhouette is the cards' -- a square
with straight edges, and the two horizontal cards read as shelves --
because the foliage tile repeats 2.7 times across a 4 m card and the
card's border is a hard line. The fix is in the pack and the recipe
together: one tile per card (`meters_per_tile` = the card's width) with
the cutout faded to nothing inside an ellipse, so the card's edge is the
canopy's, and no horizontal cards. Previously: THE FOUR RESIDUES ARE IN
THE TOOLS,
MEASURED BY 9031."""))


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
    print(f"wrote {len(out)} bytes ({len(raw)} before); 17, 153 updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
