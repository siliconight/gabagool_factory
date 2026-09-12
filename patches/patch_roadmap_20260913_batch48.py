"""Roadmap batch 48, 2026-09-13: cold run 9028 zero with a corner on the
street, and the paint named but not worn (17 REPLACE, old kept; 153
REPLACE, old kept; Lot 0.65.1). Asserts every anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-13 (night) -- COLD RUN 9027 SCORED ZERO WITH
THE WAITING PLACES STANDING.""",
"""*STATUS: NARROWED 2026-09-13 (night) -- COLD RUN 9028 SCORED ZERO WITH A
CORNER ON THE STREET; THE PAINT WAS NAMED AND NOT WORN. The bank brief on
Lot 0.65.0 / Pixelcoat 0.31.0 / LF 0.79.0: 0 interventions, 0 retries, 0
unattributed changes, every tool repo clean at --begin, all stages
succeeded, 0 blockers, export exit 0, 19 minutes (18:20 -> 18:39). The
spec carried two roads -- the through road and a cross street at
x = -29.5 through the 31 m gap between b0 and b1 -- and Lot built the T:
the side street's slab from the through road's band edge, its kerbs cut
at t = 0, the through road's L kerb cut for the mouth (terminal), 29
crosswalk bars, 9 stop bars, 5 edge-line pieces, the centre lines out of
the box; 2 bus stops (one per road), 19 trees, 18 lamps, 28 parked cars.
The nineteenth zero. Frames: the mouth from the through road's far
sidewalk with a crosswalk each side of it, and the side street looking
back at the T with its centre line ending before the box
(`docs/cold_runs/cold_9028/frames/`). NOT IN THE PACKAGE: the paint
decal. The themed spec named the `road_paint_delco_1997` pack, Pixelcoat
built it (27 kinds), Lot's `ground_skins` resolved it, and the scene
shipped flat markings -- `write_godot_scene` declares only the families
its own table knows a body will reference, and `paint` was not in the
table, so the filter dropped it in silence. Lot 0.65.1 adds the family
(wherever there is a road) and tests the written scene end to end on a
stub pack. Cold run 9029 measures it. Previously: COLD RUN 9027 SCORED
ZERO WITH
THE WAITING PLACES STANDING."""))

R.append(("""*STATUS: NARROWED 2026-09-13 (night) -- THE WAITING PLACES ARE MEASURED
(9027); THE PAINT IS A DECAL AND THE STREET HAS A CORNER, IN THE TOOLS.""",
"""*STATUS: NARROWED 2026-09-13 (night) -- THE CORNER IS MEASURED (9028): A T
JUNCTION IN A COLD PACKAGE; THE PAINT DECAL WAITS ON 9029. Cold run 9028
built the cross street Level Factory 0.79.0 asked for and Lot 0.65.0
drew the junction the model describes -- slab from the band edge, the
mouth's dropped kerb, a crosswalk each side of the mouth and one across
the side street, the stop bar on the leg that ends. Two bus stops now,
one per road. The paint decal was named by the spec and dropped by the
scene writer's family table (item 17, Lot 0.65.1); 9029 is its
measurement. Residue unchanged: an X crossing's slabs overlap; the cover
planner's truck-in-the-road; the tree's crown as cards. Previously: THE
WAITING PLACES ARE MEASURED
(9027); THE PAINT IS A DECAL AND THE STREET HAS A CORNER, IN THE TOOLS."""))


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
