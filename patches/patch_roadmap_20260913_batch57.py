"""Roadmap batch 57, 2026-09-13: cold runs 9038-9040 (17 REPLACE, old kept);
the shop signs, the typeface, the 1997 prices and the ground retune (153
REPLACE, old kept; 45 REPLACE, old kept). Asserts every anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-13 (morning) -- COLD RUN 9037 COUNTED SEVEN
INTERVENTIONS AND EVERY ONE WAS MINE.""",
"""*STATUS: NARROWED 2026-09-13 (midday) -- 9038 AND 9040 SCORED ZERO; 9039
WAS REFUSED BY THE CLOSURE GATE, CORRECTLY. 9038 (Lot 0.68.1, clean tree):
0 interventions, export exit 0, and the question 9037 could not answer
honestly -- 8 stop signs at the driveway cuts. The twenty-seventh zero.
9039 (the first run with shop signs) built the street and the export
refused the package: `EXPORT_CLOSURE_BROKEN`, six unresolved references,
the scene naming `signs/sign_*.png` that no exported directory held --
because `signs` was not in the list of siblings the export copies beside
`skins` and `cover`. The gate caught it one stage after the mistake, which
is where a closure gate catches things. LF 0.80.1 adds the directory and
folds each sign pack into the Lot job's fingerprint. 9040: 0 interventions,
export exit 0, the signs in the package -- CHECK CASH NOW, A-1 AUTO, BEER
WORLD over three shops. The twenty-eighth zero. WHAT ITS FRAMES SAID: the
band is on the right facade at the right size and its face was blown to
white, unreadable, at an emission multiplier of 1.6 on top of the Lux spot
that already lights a facade sign (Lot 0.69.1: 0.65). Previously: COLD RUN
9037 COUNTED SEVEN
INTERVENTIONS AND EVERY ONE WAS MINE."""))

R.append(("""*STATUS: NARROWED 2026-09-13 (morning) -- THE SIGNS ARE RENDERED AND THE
WALKER'S FRAMES NAME WHAT THE FORECOURT STILL LACKS.""",
"""*STATUS: NARROWED 2026-09-13 (midday) -- EVERY SHOP ON THE STREET HAS ITS
NAME OVER THE DOOR, IN A TYPEFACE THE FACTORY OWNS. The chain, end to end:
Pixelcoat's theme profile names the businesses of a 1997 Delaware County
strip (22 of them, every name invented, asserted by a test); `theme-signs`
builds one pack per shop with an index of slug, text and the families it
suits; the pixelcoat job builds them beside the skins; Level Factory reads
an archetype's id for the kind of place it is (`sign_family`) and gives
each building a shop of that family, no two alike while the family has
another to give; Lot hangs a lit band on the facade the nearest road lies
off, sized to that facade; the export carries `signs/` and Lux lights it.
Measured in a package on cold run 9040.

THE TYPEFACE (Pixelcoat 0.35.0). The walker: "the fonts are lazy for now"
-- so Pixel Operator, by Jayvee Enaguas, CC0 1.0, vendored with its
dedication. CC0 rather than merely free, because a licence asking for
attribution puts a condition on every level this factory ships; a PIXEL
face, because every pack here is read under a nearest filter; VENDORED,
because a font resolved from the host renders differently on two machines.
Sizes snap to its 16 px grid and the raster is thresholded: at 21 px one
word came back with 18 distinct ink values, which is a grey fringe on
every letter.

THE 1997 PRICES, derived rather than chosen (the walker asked for the year
specifically). EIA's Pennsylvania regular retail series excludes tax and
averages 0.770 $/gal across 1997; the state took 0.259 and the federal
excise 0.184, so a Delco pump reads 1.21 and nine tenths, a dime a grade.
The national pump average of 1.234 is the same number from the other end.
The board renders with the fraction raised, as a board does.

WHAT REMAINS: the pylon sign at the kerb, the projecting blade sign, the
awnings, the numbers on things, the overhead wires and the trolley tracks
-- all named in `docs/SET_DRESSING_REFERENCES.md` from the walker's Call
of Duty and Delco frames, none built. And the biggest: those photographs
are of ATTACHED storefronts meeting the sidewalk, where this pipeline lays
freestanding shells with a plate between them and the road. Previously:
THE SIGNS ARE RENDERED AND THE
WALKER'S FRAMES NAME WHAT THE FORECOURT STILL LACKS."""))

R.append(("""*STATUS: NARROWED 2026-09-12 (late night) -- THE FIRST CONCRETE STEP IS
IN A COLD PACKAGE: THE GROUND PLATE WEARS THE THEME'S SKIN.""",
"""*STATUS: NARROWED 2026-09-13 (midday) -- THE GROUND STOPPED READING AS
PAVING, AND THE DIAGNOSIS THAT GOT THERE WAS WRONG TWICE BEFORE IT WAS
RIGHT. Every frame set since cold run 9017 showed the asphalt as a mosaic
of cells and the sidewalk as a white one, and both were read as the MESO
band -- a 22-cell Worley on a 3 m tile, 13 cm blobs. Retuning meso from 22
cells to 150 changed nothing a before/after render could see, WHICH IS THE
REFUTATION: the cells are the `edges` layer, a 5-to-6-cell Worley crack
network at a quarter strength, which on a 3 m tile is 50 cm cracks in a
grid -- crazy paving, and nothing to do with the aggregate. Pixelcoat
0.36.0: asphalt carries aggregate at 150 cells (2 cm of stone, which is
what asphalt is), a few long cracks at 3 cells and 0.965, patchiness in
the macro band; the sidewalk is SLABS, a 2 x 2 scored grid on a 2.5 m tile
(1.25 m squares), fine sand in the face, hairlines at 0.07 -- at 0.16 the
web still read over the joints and the walk wore both. AND A DIRECTIONAL
WARP, from the walker's Substance frames: a noise field displaces the
composed surface along one angle, wrapped so the tile still tiles, applied
to albedo, height, meso and micro together. Blending a noise over a grid
changes its colour and leaves the grid; warping MOVES it. Measured on
tiled renders at 3x3; a cold run puts it in a package next.
Previously: THE FIRST CONCRETE STEP IS
IN A COLD PACKAGE: THE GROUND PLATE WEARS THE THEME'S SKIN."""))


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
