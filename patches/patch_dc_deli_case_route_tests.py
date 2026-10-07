"""Deli Counter 0.200.0 test: a deli's case is Zoo's `deli_case`.

    python patch_dc_deli_case_route_tests.py

Appends one test to `deli_counter/test_prop_species.py`, anchored on its last
test as read 2026-10-06 (13,592 bytes, LF). Run BEFORE
`patch_dc_deli_case_route.py`: it must fail there, where `deli_case_cover`
routes to no species.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEST = ROOT / "deli_counter" / "test_prop_species.py"

OLD_TAIL = '''def test_a_cooler_run_is_the_cooler_species_and_the_backstock_is_not():
    """0.148.0."""
    from prop_species import species_for_name as f
    assert f("cooler_run") == "cooler_run"
    assert f("cooler_backstock_rack") == "shelving"
    assert f("cooler_backstock") == "shelving"
'''

NEW_TAIL = OLD_TAIL + '''

def test_a_deli_case_is_the_deli_case_species():
    """0.200.0 (Zoo 1.81.0): `deli_case_cover` routed nowhere and built as a
    plain box wearing glass -- cold run 9189's composed deli_a01 stood
    `prop_delco_1997_03_w700_d110_h130_mglass` where its case is. The six
    delis' cases are the only library volumes the keyword reaches; a deli's
    own counter is a counter still."""
    from prop_species import species_for_name as f
    assert f("deli_case_cover") == "deli_case"
    assert f("the_deli_counter") == "counter"
    assert f("front_register_counter") == "counter"
    assert f("cooler_run") == "cooler_run"
'''


def main():
    data = TEST.read_bytes()
    assert len(data) == 13592, "test_prop_species.py is %d bytes, not the 13,592 read" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.endswith(OLD_TAIL), "test_prop_species.py no longer ends as read; refusing"
    TEST.write_bytes((text[:-len(OLD_TAIL)] + NEW_TAIL).encode("utf-8"))
    print("test_prop_species.py: 1 test appended")


if __name__ == "__main__":
    main()
