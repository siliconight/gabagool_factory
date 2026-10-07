"""Deli Counter 0.200.0: VERSION and CHANGELOG for the deli case's routing.

    python patch_dc_0200_release.py <suite line>

Anchored on VERSION and the CHANGELOG head as read 2026-10-06.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"

ENTRY = '''## [0.200.0] - a deli's case asks for Zoo's deli case

**What it was.** `deli_case_cover`, the case every corner deli stands in
front of its deli counter, routed to no species. So it built as a plain box
wearing glass. Cold run 9189's composed deli_a01 stood a 7 m
`prop_delco_1997_03_w700_d110_h130_mglass` there.

**What it asks for now.** Zoo 1.81.0 grows the species: curved glass, a lit
deck of salads, cards and parsley, and whole logs cut to the glass. One row
in `prop_species.PROP_SPECIES` (`deli_case`) routes the name to it.
- **What the keyword reaches** in the 146 non-LF specs: six volumes, one
  `deli_case_cover` in each of corner_deli_heist_01, cr_deli, deli_a01,
  deli_a02, deli_a03 and night_deli.
- `the_deli_counter` (primos_pizza, strip_retail_a01) does not contain it
  and stays a counter.

**The six shells are rebuilt.** Each one's case slot asks for `deli_case` at
5.815 x 1.1 x 1.3. That is the case as 0.199.0 trims it off its wall, inside
the species' range (1.2-8.0 x 0.8-1.4 x 1.1-1.5).

**Tests:** `test_prop_species.py` +1. The test fails before the row: the
name routed to nothing. Every other test in the file passes either side.

**Unproven until a cold run draws a deli.**

**Suite:** SUITE_LINE.

'''


def main():
    suite = " ".join(sys.argv[1:]).strip()
    assert suite, "pass the suite line as run"
    v = DC / "VERSION"
    assert v.read_bytes() == b"Deli Counter 0.199.0", v.read_bytes()
    cl = DC / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## [0.199.0] - no piece passes through a wall"), text[:60]
    cl.write_bytes((ENTRY.replace("SUITE_LINE", suite) + text).encode("utf-8"))
    v.write_bytes(b"Deli Counter 0.200.0")
    print("Deli Counter 0.200.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
