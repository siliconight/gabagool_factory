"""Deli Counter 0.200.0: `deli_case_cover` asks for Zoo's `deli_case`.

    python patch_dc_deli_case_route.py

One row in `prop_species.PROP_SPECIES`, after the cooler wall's, anchored on
that row as read 2026-10-06 (`prop_species.py`, 18,329 bytes, LF).

MEASURED FIRST: across the 146 non-LF specs, the keyword `deli_case` reaches
six volumes, one `deli_case_cover` in each of corner_deli_heist_01, cr_deli,
deli_a01, deli_a02, deli_a03 and night_deli; `the_deli_counter`
(primos_pizza, strip_retail_a01) does not contain it and stays a counter.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PS = ROOT / "deli_counter" / "prop_species.py"

OLD = '''    (("cooler_run",), "cooler_run"),
'''
NEW = '''    (("cooler_run",), "cooler_run"),
    # THE DELI CASE (Zoo 1.81.0). `deli_case_cover` routed nowhere and built
    # as a plain box wearing glass: cold run 9189's composed deli_a01 stood a
    # 7 m `prop_delco_1997_03_w700_d110_h130_mglass` where its case is. Only
    # the six delis' cases carry `deli_case`; `the_deli_counter` (primos_pizza,
    # strip_retail_a01) is a counter and stays one.
    (("deli_case",), "deli_case"),
'''


def main():
    data = PS.read_bytes()
    assert len(data) == 18329, "prop_species.py is %d bytes, not the 18,329 read" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.count(OLD) == 1, "the cooler wall's row found %d times" % text.count(OLD)
    PS.write_bytes(text.replace(OLD, NEW).encode("utf-8"))
    print("prop_species.py: the deli case's row")


if __name__ == "__main__":
    main()
