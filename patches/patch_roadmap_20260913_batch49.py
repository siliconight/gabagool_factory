"""Roadmap batch 49, 2026-09-13: cold run 9029 zero with the paint decal in
the package (17 REPLACE, old kept; 153 REPLACE, old kept; 152 REPLACE, old
kept). Asserts every anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-13 (night) -- COLD RUN 9028 SCORED ZERO WITH A
CORNER ON THE STREET; THE PAINT WAS NAMED AND NOT WORN.""",
"""*STATUS: NARROWED 2026-09-13 (night) -- COLD RUN 9029 SCORED ZERO WITH THE
PAINT DECAL IN THE PACKAGE. The bank brief on Lot 0.65.1: 0 interventions,
0 retries, 0 unattributed changes, every tool repo clean at --begin, all
stages succeeded, 0 blockers, export exit 0, 15 minutes (18:42 -> 18:57);
110 marking materials in the themed scene carry `transparency = 2` and
the road-paint albedo and roughness, and the package's `skins/` ships
both maps with their imports. The twentieth zero. Frames in
`docs/cold_runs/cold_9029/frames/`. Previously: COLD RUN 9028 SCORED ZERO
WITH A
CORNER ON THE STREET; THE PAINT WAS NAMED AND NOT WORN."""))

R.append(("""*STATUS: NARROWED 2026-09-13 (night) -- THE CORNER IS MEASURED (9028): A T
JUNCTION IN A COLD PACKAGE; THE PAINT DECAL WAITS ON 9029.""",
"""*STATUS: NARROWED 2026-09-13 (night) -- THE STREET'S VOCABULARY IS IN COLD
PACKAGES: ROAD, KERB LINE, PARKED CARS, THE WAITING PLACES, A CORNER, AND
THE PAINT AS A DECAL (9023-9029). Cold run 9029 shipped the road-paint
decal on every marking: 110 scissor materials tinted white or yellow,
the maps beside the scene and in the package. What the item asked for on
2026-09-13 morning is built and measured, each layer by a cold run. WHAT
REMAINS, as residue rather than build order: an X crossing's slabs
overlap (the spec makes a T); the cover planner's truck-in-the-road
should become the exception now that cars park; the tree's crown as
cutout cards rather than a faceted volume; and the paint's own look --
the cutout at 0.5 m per tile reads as wear only up close. Previously:
THE CORNER IS MEASURED (9028): A T
JUNCTION IN A COLD PACKAGE; THE PAINT DECAL WAITS ON 9029."""))

R.append(("""*STATUS: NARROWED 2026-09-13 (night) -- STEP 2 HAS ITS FIRST DECAL IN THE
TOOLS: THE ROAD PAINT.""",
"""*STATUS: NARROWED 2026-09-13 (night) -- STEP 2 HAS ITS FIRST DECAL IN A
COLD PACKAGE (9029): THE ROAD PAINT. A Pixelcoat pack with a cutout
alpha, placed geometry that carries it, the consumer told to test rather
than blend -- the decal layer's shape, shipped end to end after one
dropped filter (item 17, Lot 0.65.1). Steps 3 and 4 and item 45's
grammars remain as before. Previously: STEP 2 HAS ITS FIRST DECAL IN THE
TOOLS: THE ROAD PAINT."""))


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
