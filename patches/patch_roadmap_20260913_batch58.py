"""Roadmap batch 58, 2026-09-13 (afternoon): cold run 9041 and the defect
its frames caught (17 REPLACE, old kept); the three refutations in the
material grammar and the stone the county is built of (45 REPLACE, old
kept); the signs that faced the wrong way (153 REPLACE, old kept); and item
154, the walker's art direction, appended. Asserts every anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-13 (midday) -- 9038 AND 9040 SCORED ZERO; 9039
WAS REFUSED BY THE CLOSURE GATE, CORRECTLY.""",
"""*STATUS: NARROWED 2026-09-13 (afternoon) -- 9041 IS THE TWENTY-NINTH ZERO
AND ITS FRAMES CAUGHT A DEFECT NO GATE CAN SEE. 0 interventions, 0
unattributed, 0 retries, export exit 0, with Pixelcoat 0.36.0's warp and
retuned ground and Lot 0.69.1's dimmed sign band in the package. Then the
frames, shot through `look_shots.py` at stations read from the scene's own
sign transforms rather than guessed: every one of the three shop signs was
a blue sliver a few pixels wide, standing EDGE-ON to the road it was hung
for. `sign_placement` had picked the right facade -- its test proves that
and the test was right -- and the scene writer took the plan-space angle it
returns and used it as a Godot rotation with only the handedness flipped, a
quarter turn off on all four sides (Lot 0.69.2, `sign_facing`, derivation
in the docstring, and a test that asserts the EMITTED BASIS for all four
sides rather than the intermediate number). THE POINT FOR THIS ITEM: a run
can score a clean zero on every instrument the pipeline owns and still ship
a level whose signs cannot be read, because nothing in the pipeline looks at
a picture. That is item 18, and 9041 is the sharpest instance of it so far
-- 29 zeros in, the cheapest defect-finder in this repo is still a person
looking at a frame. Previously: 9038 AND 9040 SCORED ZERO; 9039
WAS REFUSED BY THE CLOSURE GATE, CORRECTLY."""))

R.append(("""*STATUS: NARROWED 2026-09-13 (midday) -- THE GROUND STOPPED READING AS
PAVING, AND THE DIAGNOSIS THAT GOT THERE WAS WRONG TWICE BEFORE IT WAS
RIGHT.""",
"""*STATUS: NARROWED 2026-09-13 (afternoon) -- THE GROUND IS RIGHT, THE WALLS
WERE PEBBLEDASH, AND THREE THINGS THIS ITEM BELIEVED TURNED OUT TO BE
FALSE. Cold run 9041's ground frames are the first that read as asphalt and
concrete. The same frames showed every FACADE as pale cells on a dark
matrix, and `shell.slots.json` says why that mattered more than it looked:
187 of that shell's 236 slots ask for `concrete`, so one grammar dresses
79% of every wall surface the walker sees.

REFUTATION 1, and it retracts this item's own midday claim. The 0.36.0
retune said 3 cells at a 0.965 threshold gave asphalt "a few long cracks".
It does not. `worley_edges` is F2-F1, which spikes at EVERY cell wall, so
the field is a CLOSED TESSELLATION at every threshold: `thr` controls how
thin a crack is and never how many. Three grammars shipped crazy paving
while their notes claimed cracks -- asphalt (a 1 m honeycomb),
`concrete_delco` (a 22 cm pebbledash) and `sidewalk_delco` (crazing over
the slabs). Pixelcoat 0.37.0 adds `edges.sparsity`, the fraction of the net
that draws, masked by a low-frequency field thresholded at its own quantile
so runs go uncracked and the survivors begin and end. 1.0 is the old
behaviour and is the default, because grout and panel seams want the net.

REFUTATION 2. `cells` is PER AXIS -- `cells x cells` feature points, a cell
`meters_per_tile / cells` across, `cells**2` per tile. The first
`fieldstone_delco` draft read it as cells per tile, asked for 40 on a 2.5 m
tile expecting a 40 cm stone, and rendered 6 cm chips.

REFUTATION 3, the invisible one. `posterize` steps each channel
INDEPENDENTLY, so a palette whose channels differ by less than one step
(255/n) has its hue decided by the quantiser rather than by its author. At
n = 12, step 21.2: the warm grey `#6e685d` lands on (116, 93, 93), a pink;
`#7a7266` on (116, 116, 93), an olive. Five warm greys rendered as a
harlequin of olive and mauve. A NEAR-NEUTRAL PALETTE IS THE FRAGILE CASE,
which is the opposite of the intuition.
`pixelcoat/tests/test_posterize_palette.py` asserts the rule exactly where
it bites -- a palette poured FLAT into a region (`aggregate`, `masonry`),
where no noise band dithers across the levels to hide it. Three grammars
were failing: `fieldstone_delco`, `cobblestone`, `terrazzo`. Thirty-five
have palettes finer than their own step and look correct because their
noise dithers; the test does not touch them and says so.

AND ONE THING LEARNED RATHER THAN REFUTED: a sparse feature in a TILING
texture advertises the tile. At sparsity 0.12 on a 2 m tile the surviving
cracks were one recognisable clump, and a 2 m tile crossing a 30 m wall
repeats it fifteen times in a lattice. `concrete_delco` therefore carries
no cracks at all -- cracks on a wall belong in an insert layer, which is
what this repo's own Bloodborne reference called tileables plus inserts.
Sparsity stays on the asphalt at 0.30, where dozens of fragments per tile
make no motif. Previously: THE GROUND STOPPED READING AS
PAVING, AND THE DIAGNOSIS THAT GOT THERE WAS WRONG TWICE BEFORE IT WAS
RIGHT."""))

R.append(("""*STATUS: NARROWED 2026-09-13 (midday) -- EVERY SHOP ON THE STREET HAS ITS
NAME OVER THE DOOR, IN A TYPEFACE THE FACTORY OWNS.""",
"""*STATUS: NARROWED 2026-09-13 (afternoon) -- AND EVERY ONE OF THEM WAS
FACING THE WRONG WAY. Cold run 9041 put three lit bands on three facades
and its frames showed all three edge-on to the road: blue slivers a few
pixels wide. `sign_placement` chooses the facade by which of the
footprint's four sides the nearest road lies off and returns the PLAN-SPACE
angle of that side's outward normal; `_outdoor_nodes` handed that number to
`_sign_node` as a Godot rotation about Y with only the handedness flipped.
Lot 0.69.2 derives the conversion instead of nudging it: the cabinet's face
is its local +Z, pointing at `(-sin r, 0, cos r)`; plan maps to Godot as
`(x, -y)`; an outward normal `(cos t, sin t)` therefore needs
`r = -(t + 90)`, the only angle in the circle satisfying both components.
The new test asserts the EMITTED BASIS for all four sides, because the
intermediate number was already correct and already tested -- a test on the
quantity that was right is what let a quarter turn ship. Previously: EVERY
SHOP ON THE STREET HAS ITS
NAME OVER THE DOOR, IN A TYPEFACE THE FACTORY OWNS."""))


APPEND = """

*STATUS: OPEN 2026-09-13 (afternoon) -- THE DIRECTION IS WRITTEN DOWN AND
ROUTED; ONE OF ITS FIVE POINTS HAS A TOOL CHANGE BEHIND IT. The walker
handed over a statement of what late-1990s Delaware County actually looks
like, recorded in full with an owner per point in
`docs/DELCO_1997_ART_DIRECTION.md`. LANDED: point 3, the local fieldstone
the walker calls the county's visual ballast -- `fieldstone_delco` minted
in Pixelcoat 0.37.0 and a `stone` kind mapped into both Delco themes, which
had 29 kinds between them and no stone at all, so nothing downstream could
ask for it by name. MEASURED, AND IT IS THE HARDEST NUMBER IN THIS ITEM:
187 of a shell's 236 slots ask for `concrete` (cold run 9041,
`shell.slots.json`), so 79% of every wall in the level is one material --
which is the direction's first point failing at the root rather than a
dressing problem, and it is why no brick appears on a street the walker
describes as brick twins. NOT STARTED: the twin, the accretion, the
siding, the shingle, the glass block, the EIFS remodel, the overhead wires
that the walker says DOMINATE the view, and the corridor rule that
buildings MEET the sidewalk with parking beside or behind them. NOTHING
HERE IS COSTED.*

**154. The buildings are designed all at once, and Delco buildings are
not.** The walker, 2026-09-13: the place "did not look like architecture
from the late 1990s" but like "generations of southeastern Pennsylvania
buildings repeatedly expanded, repaired, enclosed, and commercialized."
The decade is a LAYER on older fabric, not a style anything was built in:
an early-1900s stone or brick shell, a 1950s rear addition, 1970s-80s
aluminium or vinyl siding, 1990s replacement windows and signage, a porch
enclosed later still -- and "the mismatches are the identity". A building
that reads as one coherent design decision is wrong here EVEN WHEN IT IS
WELL MADE, which is a statement about this pipeline's output rather than
about its bugs. The full text, the area table, and the routing of each of
the five points to the tool that owns it are in
`docs/DELCO_1997_ART_DIRECTION.md`; it is kept as a document rather than
inlined here because it is direction a person reads, not a task list.

WHAT IT ASKS OF EACH TOOL, in the order of how much it costs. PIXELCOAT
owns the surfaces and has taken its first bite: fieldstone exists, and the
palette the walker names for the 1990s layer -- beige, pale blue, cream,
faded yellow for siding; dark green, burgundy, navy for awnings; teal,
mauve, peach, hunter green for accents -- is specific enough to be a
constraint rather than a mood, with siding, asphalt shingle, glass block
and EIFS all still absent. ZOO owns the objects: 24 species minted covers
most of the street furniture, and the utility wires and poles the walker
says dominate the view are not among them, nor satellite dishes, window air
conditioners, security bars, roll-down gates or awnings. LOT owns the
corridor, and point 4 contradicts what it does today -- commercial Delco
grew out of ROADS, buildings close to the road with parking beside or
behind, where this pipeline lays freestanding shells with a plate between
them and the street. PATINA owns the differentiation, and it is the
cheapest ask here because it reuses geometry that exists: "similar
buildings become different through use" is a per-instance decision about
which of a small set of alterations a shell received, not a texture. DELI
COUNTER owns the buildings and carries the two structural asks -- the TWIN
(a pair sharing a party wall, built as one shell and then differentiated,
frequent rather than occasional, and nothing in the archetype set expresses
a shared wall) and the ACCRETION (a later addition at a different height,
in a different material, with a roofline that does not continue; the repo
has no vocabulary for "this part was added later").

WHY IT IS FILED AS ONE ITEM RATHER THAN FIVE. The measurement above is the
reason: 187 of 236 slots asking for `concrete` is not five separate gaps,
it is one shell vocabulary that has no way to say a building is made of
more than one thing at more than one date. Splitting it into a materials
task, a placement task and an archetype task would let each be closed
without the level changing. **WHAT WOULD CLOSE THIS:** a cold package whose
street carries twins that differ from each other, at least one building
wearing two materials from two dates, and buildings meeting the sidewalk --
judged from eye height by the walker as a place that was built over time
rather than generated at once."""


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    if "**154. " in text:
        print("refusing: item 154 already exists", file=sys.stderr)
        return 1
    for old, _new in R:
        if text.count(old) != 1:
            print(f"anchor matched {text.count(old)} times; refusing: "
                  f"{old[:60]!r}", file=sys.stderr)
            return 1
    for old, new in R:
        text = text.replace(old, new, 1)
    text = text.rstrip("\n") + "\n" + APPEND.rstrip("\n") + "\n"
    out = text.encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); 17, 45, 153 updated, "
          f"154 appended")
    return 0


if __name__ == "__main__":
    sys.exit(main())
