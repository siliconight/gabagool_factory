"""Roadmap batch 33, 2026-09-12: cold run 9010 (17 REPLACE, old kept), the
runs in a package (44 REPLACE, old kept), the texture half of the minting
tools (150 REPLACE, old kept). Asserts every anchor once.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-12 -- COLD RUN 9009 SCORED ZERO ON THE BANK BRIEF,
THIRD TRY, WITH A BANK IN EVERY CANDIDATE'S LOT AND THE FIRST DIEGETIC PROP
IN A SHIPPED PACKAGE.""",
"""*STATUS: NARROWED 2026-09-12 (later) -- COLD RUN 9010 SCORED ZERO ON THE
BANK BRIEF WITH THE RUNS IN THE PACKAGE: A 10 M TELLER COUNTER BUILT AS A
COUNTER RUN, A TURNED PARTS RACK, A WORKBENCH THAT IS A COUNTER, NO
FALLBACKS. Same brief, on DC 0.118.0 / Zoo 0.63.0 / LF 0.73.1: 0
interventions, 0 retries, 0 unattributed changes, every tool repo clean at
--begin, all stages succeeded, export exit 0, 13 minutes (08:04 -> 08:17).
Lot `bank_branch_a04` / `auto_shop_a02` / `market_hall_a01`. Kit indexes:
the bank's `teller_counter` (10.0 x 0.9 x 1.1) is `prop_counter_..._w1000
_d90_h110`, PASS; the shop's `parts_rack` (authored 1.0 x 5.0, recorded
5.0 x 1.0 turned 90) is a `prop_shelving` run, PASS; its `tool_bench`
(3.0 x 1.0 x 1.0) a `prop_counter`, PASS; its `office_desk` a desk;
`species_fallbacks` empty on all three buildings. A `look_shots --station`
in the walk copy shows the teller counter as one wooden run along the
banking hall's wall. The seventh zero, and the first package in which
every hinted volume the lot carried was built as what its name says. Log
and journal: `docs/cold_runs/cold_9010/`; walk copy
`_runs/walk_export_bank_block_001` (overwrites 9009's). EARLIER STATUS,
KEPT VERBATIM: NARROWED 2026-09-12 -- COLD RUN 9009 SCORED ZERO ON THE
BANK BRIEF,
THIRD TRY, WITH A BANK IN EVERY CANDIDATE'S LOT AND THE FIRST DIEGETIC PROP
IN A SHIPPED PACKAGE."""))

R.append(("""*STATUS: NARROWED 2026-09-12 (later) -- STEP 3 SHIPPED: THE RUN SPECIES FILL
RUNS IN BAYS, THE RANGES MATCH WHAT THE SPECS AUTHOR, AND 541 OF 720 HINTED
PLACEMENTS NOW PLAN AS THEIR SPECIES (FROM 142); NOT YET IN A COLD PACKAGE.""",
"""*STATUS: NARROWED 2026-09-12 (evening) -- STEP 3 IN A COLD PACKAGE: cold
run 9010's bank carries its 10 m teller counter as a counter run and its
auto shop a turned 5 m parts rack, a workbench counter and a desk, zero
fallbacks across the lot (item 17). What remains is the 179 of 720 that
still fall back (boss desks too deep, benches, vault-sized safes, tanks),
the 511 unhinted slots item 150's queue lists, and the eye: whether a
three-bay counter and a shared-upright rack read as furniture on the
re-walk. Previously: STEP 3 SHIPPED: THE RUN SPECIES FILL
RUNS IN BAYS, THE RANGES MATCH WHAT THE SPECS AUTHOR, AND 541 OF 720 HINTED
PLACEMENTS NOW PLAN AS THEIR SPECIES (FROM 142); NOT YET IN A COLD PACKAGE."""))

R.append(("""*STATUS: NARROWED 2026-09-12 -- THE PROP HALF SHIPPED (ZOO 0.63.0) AND MINTED
ITS FIRST SPECIES; THE TEXTURE AND STYLE HALVES ARE NAMED AND UNBUILT*""",
"""*STATUS: NARROWED 2026-09-12 (later) -- THE PROP HALF (ZOO 0.63.0) AND THE
TEXTURE HALF (PIXELCOAT 0.29.0) SHIPPED AND WIRED TO EACH OTHER; THE STYLE
HALF IS NAMED AND UNBUILT. The walker: "this should also support minting
new pixelcoats if that brings the prop or asset to life." A minted prop
wears a KIND, and a theme with no profile for the kind renders it flat --
Zoo's `find_pack` says so in `flat_fallback`. `pixelcoat/tools/
new_material.py report` lists, per theme, the kinds Zoo's species can wear
that the theme has no profile for; `new <profile> --kind --like --colors
[--theme]` writes a grammar from a template, synthesizes it at 64 px and
prints item 140's two numbers (albedo std, neighbour correlation, warned
under 0.3 -- a minted static is caught before anyone walks it), maps the
kind into the theme so `theme-library` builds it, refuses to overwrite,
and says when the kind is one Zoo does not know (three tables to touch,
named). Zoo 0.63.1: `new_species.py new` says whether the theme dresses
the species' material and prints the pixelcoat command when it does not,
so the two mints are one request. A grammar copied with new colours is the
template's surface in new colours, which is the honest state of a material
nobody has authored; the profile file is where the authoring goes.
Previously: THE PROP HALF SHIPPED (ZOO 0.63.0) AND MINTED ITS FIRST
SPECIES; THE TEXTURE AND STYLE HALVES ARE NAMED AND UNBUILT*"""))


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
    print(f"wrote {len(out)} bytes ({len(raw)} before); 17, 44, 150 updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
