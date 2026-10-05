"""`dressing_in_nav` reads merged dressing, and a run that matched no cover is
NOT MEASURED.

Zoo 1.68.0 merges a building's covers one side per material, so the nodes
are `Cover<side>_*` and none starts `Cover_`. With the old default prefix the
probe matched nothing, counted 0 covers and 0 offenders, and the report
called that clear: a check that could not fail.
"""
import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dressing_in_nav as D  # noqa: E402


def test_the_default_prefix_matches_merged_and_unmerged_covers():
    p = inspect.signature(D.probe).parameters["prefix"].default
    for name in ("CoverN_concrete_delco_1997", "CoverE_downspout", "Cover_edge_strip.003"):
        assert name.startswith(p), (p, name)


def test_a_run_that_matched_no_cover_is_not_measured(monkeypatch, capsys):
    monkeypatch.setattr(D, "probe", lambda *a, **k: {
        "covers": 0, "flagged": 0, "offenders": [], "scene": "s", "nav_samples": 12})
    assert D.main(["proj"]) == 2
    assert "NOT MEASURED" in capsys.readouterr().err
