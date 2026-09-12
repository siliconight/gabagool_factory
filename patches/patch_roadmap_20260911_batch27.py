"""Roadmap batch 27, 2026-09-11: item 44 gets the fit measurement that
scopes its fix. INSERT a paragraph directly under the heading. Asserts once.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

ANCHOR = """**44. The green boxes could be cars, and the collision would not change.**
"""

INSERT = """**44. The green boxes could be cars, and the collision would not change.**

**MEASURED 2026-09-11, AND THE WIRE IS NOT THE WHOLE GAP.** Every placement
name in the 176 specs keyed to the species its name asks for, against that
species' genome size range (`zoo_keeper/genome/species/*.json`), over 1,443
placements: 721 name a species Zoo has, and the species FITS only 142 of them
-- `counter` 54 of 146, `desk` 82 of 144, `shelving` 6 of 126; `teller_line`
0 of 29, `filing_cabinet` 0 of 112, `chair` 0 of 27, `table` 0 of 36,
`hvac_unit` 0 of 32, `drop_safe` 0 of 60, `water_tank` 0 of 9. What does
not fit is a RUN: `teller_counter` 8.0 x 0.8, `bar_counter` 10.0 x 0.9,
`aisle_shelf` 7.0 x 0.7 and 1.0 x 6.0, `ARMORY_LOCKER` 3.0 x 0.8 x 2.0,
`bench` 5.0 x 1.4, `VAULT` 5.0 x 5.0 x 3.0 -- lengths a single desk or
counter cannot be, and which the `prop` recipe alone builds today because
it is the one species that takes the slot's dims verbatim (`_arch`,
`fit_exact`). The other 722: 394 are boxes by nature (`crate_stack`,
`col_*`, pallets) and lose nothing as skinned boxes; 328 name things no
species exists for (`pump` 42, `canopy_col` 42, `supply_cart` 18,
`planter_box` 44, `kiosk`, `cage`). SO THE SCOPE, in order of placements
recovered per species: (1) Deli Counter stamps a `species` hint on each
prop slot from the placement's name (the keyword table this measurement
used, kept next to `_SEED_ARCHETYPES` where the names are minted), and the
stem carries it (`prop_<species>_...`) on both sides -- Zoo's
`module_stem` and DC's `resolve_themed_stem` -- so a desk and a crate of
one size cannot share a filename; (2) Zoo builds a hinted species at the
slot's exact dims when they fall in its range, else the `prop` box, and
SAYS which; (3) the run species -- `counter`, `shelving`, `teller_line`,
`locker` (new), `bench` (new) -- gain a bays mode that repeats their unit
along the long axis to any length, the way `prop` already fills any box;
that is where 579 of the 721 live. (1)+(2) is a day; (3) is a recipe each.
The walker's line stands over all of it: the box is the placeholder, and
the pipeline ships the placeholder.

"""


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    n = text.count(ANCHOR)
    if n != 1:
        print(f"anchor matched {n} times; refusing", file=sys.stderr)
        return 1
    out = text.replace(ANCHOR, INSERT, 1).encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); 44 measured")
    return 0


if __name__ == "__main__":
    sys.exit(main())
