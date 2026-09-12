"""Roadmap batch 50, 2026-09-13: cold run 9030 not a zero -- two seed
defects, a tuft narrower than its genome and a lamp on an enemy spawn (17
REPLACE, old kept); the four residues of 153 in the tools (153 REPLACE, old
kept). Asserts every anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-13 (night) -- COLD RUN 9029 SCORED ZERO WITH THE
PAINT DECAL IN THE PACKAGE.""",
"""*STATUS: NARROWED 2026-09-13 (night) -- COLD RUN 9030 WAS NOT A ZERO: TWO
SEED DEFECTS, ONE IN ZOO AND ONE IN LOT, AND THE EXPORT GATE HELD. The bank
brief on Lot 0.66.0 / Zoo 0.69.0 / Pixelcoat 0.32.0: 0 interventions, 0
retries, 0 unattributed changes, but `zoo_clutter_build` exited 2 and the
export was refused. (1) `weed_tuft` at seed 9030 built 0.028 m wide
against its genome's 0.050 m floor -- the blades' bases and leans are
drawn, and this draw leaned them all one way from a tight root; the
habitat FAILED on `dim_width`. Zoo 0.69.1 spreads the clump in plan until
it fills nine tenths of the plan's width (never shrunk); rebuilt at seed
9030, PASS. (2) The third seed's Laser Tag preflight refused its candidate
for Enemy_4 inside solid geometry: a streetlight stood ON the spawn --
the kerb line had never looked at the markers, where the cover planner
and the cars always had. Lot 0.66.1 keeps every kerb-line piece
`MARKER_CLEARANCE` from every marker (a lamp or a tree steps along its
band, a corner piece is skipped). Neither defect was new: both were
latent and seed-dependent, and the run's seed found them. WHAT THE RUN
DID MEASURE: with the cars parked before the cover planner ran, 3 cover
pieces were stood against 6 on 9028 for the same brief; the site kit
built every species `pass` including the tree with its foliage material
exported as alphaMode MASK. Cold run 9031 (Lot 0.66.1, Zoo 0.69.1) is
running; no frames of 9030 exist because it shipped no package. Previously:
COLD RUN 9029 SCORED ZERO WITH THE
PAINT DECAL IN THE PACKAGE."""))

R.append(("""*STATUS: NARROWED 2026-09-13 (night) -- THE STREET'S VOCABULARY IS IN COLD
PACKAGES: ROAD, KERB LINE, PARKED CARS, THE WAITING PLACES, A CORNER, AND
THE PAINT AS A DECAL (9023-9029).""",
"""*STATUS: NARROWED 2026-09-13 (night) -- THE FOUR RESIDUES ARE IN THE TOOLS,
MEASURED BY 9031. (1) THE CARS FIRST: Lot 0.66.0 plans the kerb line and
parks the cars before the cover planner runs and hands both to
`plan_cover(standing=...)`, where they occlude a sightline like a placed
piece and a piece keeps its daylight from them -- a truck in the road is
now the exception (9030: 3 pieces against 9028's 6). (2) AN X CROSSING:
the lower-index road owns the junction's surface; the higher road carries
`gaps` and `drawn_spans` splits its slab and band pieces around the box
(tested on a two-road X; the spec still makes a T). (3) THE CROWN AS
CARDS: Zoo 0.69.0 builds `street_tree`'s crown as four crossed vertical
cards and two horizontal ones wearing a new `foliage` kind; Pixelcoat
0.32.0 mints `foliage_delco`, the vegetation greens under an inverted
worley cutout (leaf clusters with sky between) with a scissor hint; Zoo's
`_textured` feeds a scissor pack's alpha through Math > Greater Than 0.5
into the Principled Alpha, which Blender 5.1's glTF exporter reads as
alphaMode MASK (measured: MASK, double-sided) and Godot imports as alpha
scissor. (4) THE PAINT IN PATCHES: the cutout is a low-frequency fbm
field (3 cells, 4 octaves, threshold 0.40) rather than 7-cell holes, and
a test pins that the largest hole is a patch, not a speck. 9030 built all
of it and shipped none of it (item 17); 9031 measures it. Previously: THE
STREET'S VOCABULARY IS IN COLD
PACKAGES: ROAD, KERB LINE, PARKED CARS, THE WAITING PLACES, A CORNER, AND
THE PAINT AS A DECAL (9023-9029)."""))


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
