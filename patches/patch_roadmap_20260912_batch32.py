"""Roadmap batch 32, 2026-09-12: item 44 step 3 shipped (REPLACE, old kept)
and item 150 filed (APPEND) -- the minting tools, from the walker's goal
statement. Asserts every anchor once.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

OLD_44 = """*STATUS: NARROWED 2026-09-12 -- STEPS 1 AND 2 SHIPPED AND NOW IN A COLD
PACKAGE:"""

NEW_44 = """*STATUS: NARROWED 2026-09-12 (later) -- STEP 3 SHIPPED: THE RUN SPECIES FILL
RUNS IN BAYS, THE RANGES MATCH WHAT THE SPECS AUTHOR, AND 541 OF 720 HINTED
PLACEMENTS NOW PLAN AS THEIR SPECIES (FROM 142); NOT YET IN A COLD PACKAGE.
Zoo 0.62.0: `recipes/_bays.bays` divides a width into equal bays of at
most the genome's `bay_max` -- counter 4.0, shelving 2.4, filing_cabinet
0.5, desk 2.2 -- and each recipe repeats its unit per bay (a counter run
is one body and top with a shelf and register per bay; a shelf run shares
an upright at every boundary; a cabinet bank is one body with a drawer
stack per bay; a desk row is one top over a leg set, pedestal and modesty
panel per bay); one bay is the unit each always built. Ranges opened by
measurement, not taste: counter depth 1.4 / height 1.2, shelving depth
1.2 / height 3.5, cabinet depth 0.9 / height 2.1, desk height 1.0,
hvac_unit 4.0 x 3.0 x 1.5, table 1.4 deep / 0.8 tall. Deli Counter
0.118.0: a hinted volume is recorded LONG SIDE FIRST (turned 90 when its
long side is y -- alone that took desks from 58 to 91 fits and counters
from 35 to 54), and `teller` routes to `counter`, because all 38
`teller_counter` volumes are 1.0 m counters and the `teller_line` barrier
starts at 2.0 m. REFUTED on the first build, kept: the cabinet bank came
out 0.840 deep against 0.800 (drawer fronts proud of the body) and the
counter 2.040 wide against 2.000 (the top's lip) -- both recipes now give
the body up under `fit_exact`. Built through Blender: an 8 m counter, a
6 x 1.0 shelf run turned, a 3 m locker bank, a 4.4 m desk row, a 4 x 3
rooftop unit, 5 of 5 pass; `test_bays` plans the measured shapes with no
fallback. THE NUMBER, re-measured over the specs with the turn: 720
hinted, 541 plan as their species, 179 fall back -- desk 58 (5 m x 1.6
"boss desks" too deep), shelving 35, table 30, chair 24 (5 m benches),
drop_safe 13 (vault-sized), water_tank 9, counter 9, cabinet 1 -- none
for want of a genome. Cold run 9010 is the package. Previously: STEPS 1
AND 2 SHIPPED AND NOW IN A COLD PACKAGE:"""

APPEND = """
*STATUS: NARROWED 2026-09-12 -- THE PROP HALF SHIPPED (ZOO 0.63.0) AND MINTED
ITS FIRST SPECIES; THE TEXTURE AND STYLE HALVES ARE NAMED AND UNBUILT*

**150. A new person cannot yet ask the factory for a prop, a texture or a
style that does not exist and get one.** The walker's goal, said
2026-09-12: "new people can walk up to this level factory and make a good
looking level and mint the necessary props, textures, styles to fulfil the
request." The gap protocol (USING_THE_FACTORY.md) says the owning tool
grows the capability; what it did not say is HOW, and for a prop that
meant reading five recipes, a genome schema and a test file. MEASURED over
Deli Counter's 129 built manifests (`zoo/tools/new_species.py report`):
511 prop slots carry no species hint, and the names say what they are --
`col_*` 96 (boxes by nature), `pump` 42, `canopy_col` 42, `pump_island`
21, `aisle` 19, `display_case` 11, `stall` 10, `lift` 8, `planter_box`,
`forecourt_pad`, `canopy_roof`; and a further 137 hinted slots name a
species that exists and did not fit (item 44's residue). SHIPPED, the prop
half: `new_species.py report` is that queue, most common first, split into
"mint this", "route this" and "widen this"; `new_species.py new <species>
--width --depth --height [--like prop] [--material] [--keywords]` writes a
genome from the template with the dims as defaults and a 0.5x..2.0x range,
a placeholder recipe (a solid box at the plan's exact dims, one named
part, collision, an attachment, and a docstring that says this is where
the drawing goes), a test, and a line in `genome/minted.json` that
`test_genome` unions into its known set; it prints the keyword line Deli
Counter needs and refuses to overwrite. `pump` (1.0 x 1.2 x 1.4, metal)
is the first minted species, routed by DC 0.118.0 -- a pump that is a box
is the honest state of a pump nobody has drawn, and it is now COUNTED as
a pump in every kit report, which is what makes it a request rather than
a silence. **WHAT WOULD CLOSE THIS:** the same tool for the other two
halves -- a Pixelcoat material profile minted from a kind and a base
colour (`profiles/materials/*.json` is a grammar, and `theme-library`
already builds every profile a theme names), and a Zoo style row minted
into a genome's `styles` for a new theme name -- each with its `report`
of what the briefs ask for that does not exist; then one worked example
of each reaching a cold package, and a page in USING_THE_FACTORY.md that
a new person can follow from "the brief wants a planter" to the planter.
"""


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    if text.count(OLD_44) != 1:
        print(f"44 anchor matched {text.count(OLD_44)} times; refusing", file=sys.stderr)
        return 1
    if "\n**150. " in text:
        print("item 150 already present", file=sys.stderr)
        return 1
    text = text.replace(OLD_44, NEW_44, 1)
    text = text.rstrip("\n") + "\n" + APPEND.rstrip("\n") + "\n"
    out = text.encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); 44 updated, 150 filed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
