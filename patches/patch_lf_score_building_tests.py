"""Level Factory 0.152.0's tests, written first: the score is the building the
brief asked for.

    python patch_lf_score_building_tests.py

Writes `level_factory/tests/unit/test_score_building.py` (new; refuses if it
exists). On 0.151.0 it must FAIL: `site_placements` takes no `objective` and
`building_library` has no `score_building`.

THE DEFECT (roadmap 201). `site_variation.site_placements` draws the spawn and
the objective building independently from the seed, so the score is not the
archetype's building and can be the spawn building itself. Measured on the
current code, seeds 9000-9011: spawn == objective on 3 of 12 three-building
sites and 2 of 12 four-building sites.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEST = ROOT / "level_factory" / "tests" / "unit" / "test_score_building.py"

SRC = '''"""The score is the building the brief asked for (0.152.0, roadmap 201).

`site_variation.site_placements` drew the spawn and the objective building
independently from the seed: the score was not the archetype's building, and on
3 of 12 three-building sites (seeds 9000-9011) the crew spawned inside it.
`pick_lot` already places the archetype's family first, so when a family
answers to the archetype the score is b0. With no such family, the archetype
is not on the site at all, and the seeded pick stands.
"""
from __future__ import annotations

import pytest

from packages.pipeline import building_library
from packages.pipeline.site_variation import site_placements

SEEDS = range(9000, 9100)


@pytest.mark.parametrize("count", [2, 3, 4, 5])
def test_a_fixed_score_is_the_objective_and_never_the_spawn(count):
    for s in SEEDS:
        p = site_placements(s, count, objective="b0")
        assert p["objective"] == "b0", (s, p)
        assert p["spawn"] != "b0", ("the crew spawned in the score", s, p)
        assert p["extraction"] != p["spawn"], ("the route should cross the site", s, p)


def test_a_one_building_site_is_all_three_whatever_is_asked():
    p = site_placements(9003, 1, objective="b0")
    assert p["spawn"] == p["objective"] == p["extraction"] == "b0"


def test_an_unknown_score_building_is_refused():
    with pytest.raises(ValueError):
        site_placements(9003, 3, objective="b7")


def test_no_score_given_is_the_draw_that_always_was():
    """Pinned on 0.151.0's own output, so a site with no anchored score -- and
    every candidate already graded -- keeps its roles."""
    expect = {9000: ("b0", "b0", "b1"), 9001: ("b2", "b1", "b0"),
              9002: ("b2", "b2", "b0"), 9003: ("b1", "b0", "b0")}
    for s, roles in expect.items():
        p = site_placements(s, 3)
        assert (p["spawn"], p["objective"], p["extraction"]) == roles, (s, p)


@pytest.mark.parametrize("count", [3, 4])
def test_fixing_the_score_moves_no_building(count):
    for s in range(9000, 9020):
        a, b = site_placements(s, count), site_placements(s, count, objective="b0")
        assert a["buildings"] == b["buildings"], s


def test_the_score_building_is_b0_when_a_family_answers_to_the_archetype():
    entries = [{"id": "bank_branch_a02", "family": "bank_branch"},
               {"id": "pharmacy_a01", "family": "pharmacy"},
               {"id": "deli_a01", "family": "deli"}]
    assert building_library.score_building(entries, "bank") == "b0"
    assert building_library.score_building(entries, "corner_deli") == "b0"


def test_no_family_answers_and_the_seed_keeps_the_pick():
    entries = [{"id": "pharmacy_a01", "family": "pharmacy"},
               {"id": "deli_a01", "family": "deli"}]
    assert building_library.score_building(entries, "hospital") is None
    assert building_library.score_building(entries, "") is None
'''


def main():
    assert not TEST.exists(), "%s exists; this patch writes it new" % TEST
    TEST.write_bytes(SRC.encode("utf-8"))
    print("wrote %s (%d bytes)" % (TEST.relative_to(ROOT), len(SRC.encode("utf-8"))))


if __name__ == "__main__":
    main()
