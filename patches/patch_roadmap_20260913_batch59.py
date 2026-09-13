"""Roadmap batch 59, 2026-09-13 (evening): cold run 9042, the thirtieth zero,
and the second sign defect its frames caught (17 REPLACE, old kept); the sign
face is a quad (153 REPLACE, old kept); and the art direction's first four
tool changes land (154 REPLACE, old kept). Asserts every anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-13 (afternoon) -- 9041 IS THE TWENTY-NINTH ZERO
AND ITS FRAMES CAUGHT A DEFECT NO GATE CAN SEE.""",
"""*STATUS: NARROWED 2026-09-13 (evening) -- 9042 IS THE THIRTIETH ZERO AND
ITS FRAMES CAUGHT THE SECOND DEFECT IN THE SAME THIRTY LINES. 0
interventions, 0 unattributed, 0 retries, export exit 0, with Lot 0.69.2's
`sign_facing` and Pixelcoat 0.37.0's grammar work in the package. The signs
FACE THE ROAD now -- all three verified against the scene's own bases, one
per road the planner chose -- and the name on them was CROPPED. A BoxMesh
does not map a texture 1:1 onto any of its sides: its unwrap's extents are
proportional to the box's dimensions, so a 9 x 1.5 x 0.22 cabinet showed
about u in [0, 0.90] and v in [0, 0.62] of a centred 512 x 128 pack and cut
KEYSTONE SAVINGS off below the letter tops. Measured off the frame, not
recalled from the engine's docs. Lot 0.69.3 makes the face a QuadMesh, which
spans the full 0..1 by construction.

TWO RUNS, TWO ZEROS, TWO DEFECTS IN ONE THIRTY-LINE FUNCTION, AND NO GATE
SAW EITHER. 9041 pointed every sign at the wrong wall; 9042 showed two
thirds of its name. Both were found by a person looking at a picture, which
is item 18 stated as a measurement rather than as a worry: thirty zeros in,
the cheapest defect-finder in this repo is still the walker's eye. Previously:
9041 IS THE TWENTY-NINTH ZERO
AND ITS FRAMES CAUGHT A DEFECT NO GATE CAN SEE."""))

R.append(("""*STATUS: NARROWED 2026-09-13 (afternoon) -- AND EVERY ONE OF THEM WAS
FACING THE WRONG WAY.""",
"""*STATUS: NARROWED 2026-09-13 (evening) -- THEY FACE THE ROAD, AND NOW THE
WHOLE NAME IS ON THEM. Cold run 9042 fixed the facing and exposed the next
layer: the band read as a field of colour with the letters cut off at its
bottom edge. The cabinet was ONE BoxMesh wearing the pack, and a BoxMesh's
unwrap has extents proportional to the box rather than normalised per face,
so the visible sub-rectangle changes with the sign's size and no fixed
`uv1_scale` corrects it. Lot 0.69.3 splits the cabinet into what a cabinet
is: the box keeps the silhouette and the 22 cm of depth in a plain dark
colour, and a QuadMesh of exactly the band's width and height stands 2 mm
proud carrying the pack, the emissive and the nearest filter.

WHAT REMAINS ON THIS ITEM is unchanged and is now the bigger half: the pylon
sign at the kerb, the projecting blade sign, the awnings, the numbers on
things, the overhead wires and the trolley tracks. Previously: AND EVERY ONE
OF THEM WAS
FACING THE WRONG WAY."""))

R.append(("""*STATUS: OPEN 2026-09-13 (afternoon) -- THE DIRECTION IS WRITTEN DOWN AND
ROUTED; ONE OF ITS FIVE POINTS HAS A TOOL CHANGE BEHIND IT.""",
"""*STATUS: NARROWED 2026-09-13 (evening) -- FOUR OF THE FIVE POINTS HAVE A
TOOL CHANGE BEHIND THEM, EACH MEASURED BEFORE IT WAS MADE. Five repos moved
in one pass and every number below was taken from an artefact rather than
assumed.

POINT 3, THE FIELDSTONE, IS WHOLE. `fieldstone_delco` in Pixelcoat 0.37.0,
`stone` mapped in both Delco themes, and -- the half that was missing --
`stone` in Zoo 0.75.0's `KNOWN_KINDS`, without which the pack is built into
every library and reaches no wall. That gap existed for exactly one commit
and is the reason `siding` and `shingle` were added to the vocabulary in the
same breath as their grammars.

POINT 1, THE INHERITED BUILDING, HAS ITS FIRST TWO MECHANISMS. Deli Counter
0.121.0's `material_kind.py`: the library names 25 distinct materials across
6,716 surface references and 16 of them are outside the skin resolver's
vocabulary -- 326 references, of which the 131 saying `brick_ext` are
exactly the surfaces that never got brick, because an unknown kind falls
back to a FLAT colour. The spec keeps the builder's name (the acoustic table
and the style index key on it) and only the emitted slot moves. And
`roof_material`: `roof_slots` took the roof from `default_material` and
always had, so the 232 of 281 specs defaulting to `concrete` had concrete
roofs, mansions and houses included.

POINT 2, THE TWIN, EXISTS. Of 133 built archetypes, 7 were housing of any
kind, 1 was a rowhouse and 0 were twins. `twin_a01` is two 8 m halves either
side of a SOLID PARTY WALL -- a partition on the centre line, both storeys,
no openings, which nothing in the archetype set could say before -- with two
front doors, two back doors, two stairs, `stone_ext` on storey 0 under
`siding` on storey 1, and a `shingle` roof. 178 slots: 89 stone, 40 siding,
3 shingle. The first spec in this library whose walls are made of two
things from two dates. Its halves diverge the way a real pair does: a
full-width open porch one side, a stoop and a door hood the other. It passes
the nav gate, after two gates moved it and both were right --
`test_cover_breaks_sightlines` named all four back rooms as having nothing
to fight from (a 0.9 m counter is furniture; `cover_break_height` is 1.30),
and the offline nav proxy refused 1.0 m interior doors for a 0.4 m-radius
agent, which is what made the upstairs objective unreachable.

POINT 4, THE CORRIDOR, IS A ONE-LINE ORDERING FIX AND IT IS IN. Level
Factory 0.81.0: `y_road` came from the PLATE's own south edge, and the plate
is sized by the building row plus whatever the shape asked for, so the
distance from a front door to the kerb was a residue nobody chose --
measured on cold run 9041, 21.5 m of empty ground between a bank's south
face and its sidewalk. The road is derived from the FACE now and the plate
from the road; `FRONTAGE` is `ROAD_MARGIN`, the 2 m the module already keeps
between a sidewalk and anything else. On 9041's own row: 21.5 m -> 2.0 m.
Shallower buildings still stand back by the difference, which is what a real
corridor does.

POINT 5 IS HALF DONE AND THE HALF IS DELIBERATE. `siding_delco` and
`shingle_delco` (Pixelcoat 0.38.0) are minted because something asks for
them. Glass block, EIFS, faux shutters and storm doors are NOT, because
nothing does, and an unused pack is built into every library and reaches no
surface.

WHAT REMAINS. The two halves of a twin cannot wear different materials on
the SAME wall: `Builder._exterior` indexes `ext_walls` into a dict keyed by
(wall, storey), so a second entry for one wall silently replaces the first,
and "one keeps stone, the other sides it" lands as a stone base under a
sided upper instead of a split down the party wall. That needs a run range
on an exterior wall entry. The ACCRETION -- a later addition at a different
height with a roofline that does not continue -- is still unexpressed.
Patina's per-instance differentiation is untouched. And the twin is in the
library but no brief asks for housing, so it will appear on a lot only when
`pick_lot` happens to draw its family. Cold run 9043 is running to measure
all of it. Previously: THE DIRECTION IS WRITTEN DOWN AND
ROUTED; ONE OF ITS FIVE POINTS HAS A TOOL CHANGE BEHIND IT."""))


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    for old, _new in R:
        if text.count(old) != 1:
            print(f"anchor matched {text.count(old)} times; refusing: "
                  f"{old[:60]!r}", file=sys.stderr)
            return 1
    for old, new in R:
        text = text.replace(old, new, 1)
    out = text.encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); 17, 153, 154 updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
