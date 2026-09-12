"""Roadmap batch 28, 2026-09-12: item 44 narrowed -- steps (1) and (2) of
its measured plan shipped (DC 0.117.0, Zoo 0.61.0) and built. REPLACE the
status block; the old one is kept verbatim. Asserts once.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

OLD = """*STATUS: OPEN 2026-09-11 -- RE-RAISED BY THE WALKER, FROM THE INSIDE, AND
MEASURED:"""

NEW = """*STATUS: NARROWED 2026-09-12 -- THE WIRE AND THE EXACT FIT SHIPPED (STEPS 1
AND 2 OF THE MEASURED PLAN), BUILT THROUGH BLENDER, NOT YET IN A PACKAGE.
Deli Counter 0.117.0: `prop_species.species_for_name` stamps a `species`
hint on every volume slot from its name (teller -> teller_line; counter /
reception / station / island / cage -> counter; desk / cubicle -> desk;
cabinet / locker -> filing_cabinet; shelf / rack / stock -> shelving;
vending, atm, hvac, tank, seat / bench, table, safe; crates, columns,
pallets, pumps, carts, planters and the vault stay None), and
`themed_tscn.module_stem` carries it between type and theme. Zoo 0.61.0:
`plan_kit` checks the hint against the species' genome ranges in the
slot's own orientation, plans that species at the slot's exact dims when
it fits and the `prop` box otherwise, and reports every fallback with its
reason in `species_fallbacks` (indexed, printed: "width 8.00 outside
1.00..5.00", "would fit turned 90 degrees", "no genome"). DC's
`resolve_slot_ref` asks for the species module first and the box second
before the style-01 degrade, so a hinted slot never falls to greybox for
not fitting. BUILT on a three-slot probe with the 9006 run's packs: the
desk (1.6 x 0.8 x 0.75) is a desk -- top, legs, pedestal, two drawers with
handles; the counter (2.0 x 0.65 x 0.95) a counter with its register
attachment; the 8 m teller run the box, said out loud. The counter FAILED
`fit_width` on the first build at 2.040 m -- the recipe's 2 cm top lip on
a free-standing prop -- and now takes the lip out of the body under
`fit_exact`; 3 of 3 pass. Unhinted slots plan byte for byte as before
(`test_species_hint`, 27 kit tests; DC 684). RESIDUE, as measured on
2026-09-11: 142 of 721 hinted placements fit today; the hospital's own
are all runs (an 8 m reception, a 4.0 x 1.4 nurse station, a 5 m bench)
and still ship as boxes -- step (3), the bays mode for counter, shelving,
teller_line, locker and bench, is where 579 of them live. No package has
been built by these versions yet; a bank brief is the first that would
show a desk. EARLIER STATUS, KEPT VERBATIM: OPEN 2026-09-11 -- RE-RAISED
BY THE WALKER, FROM THE INSIDE, AND MEASURED:"""


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    n = text.count(OLD)
    if n != 1:
        print(f"anchor matched {n} times; refusing", file=sys.stderr)
        return 1
    out = text.replace(OLD, NEW, 1).encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); item 44 narrowed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
