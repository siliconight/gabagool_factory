"""Deli Counter 0.189.0, the baseline's tests: the grid-fragile set is frozen
like the unjudged set. A shell newly fragile fails; a shell fixed must leave
the list; every result must carry the sweep, or "nothing fragile" would be
read off a gate run from before it existed.

Applied BEFORE the baseline entries (`patch_dc_grid_baseline.py`), so the new
tests are seen failing first.

    python patch_dc_grid_baseline_tests.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEST = ROOT / "deli_counter" / "test_navgate_population.py"

CONST_OLD = '''UNJUDGED = {e["shell"]: e for e in BASELINE["unjudged"]}
STAIR_FAILURES = {e["shell"]: e for e in BASELINE["stair_failures"]}
'''
CONST_NEW = '''UNJUDGED = {e["shell"]: e for e in BASELINE["unjudged"]}
STAIR_FAILURES = {e["shell"]: e for e in BASELINE["stair_failures"]}
# 0.189.0: shells whose connections the gate's grid sweep found on some voxel
# grids and not others. Frozen like UNJUDGED, for the same reason: the gate
# reports it and its exit code does not gate on it, so the set could grow
# without anything failing.
GRID_FRAGILE = {e["shell"]: e for e in BASELINE.get("grid_fragile", [])}
'''

HELPER_OLD = '''def _failed(live):
    return {n for n, d in live.items()
            if d.get("stairs_ok", d.get("ok")) is False}
'''
HELPER_NEW = '''def _failed(live):
    return {n for n, d in live.items()
            if d.get("stairs_ok", d.get("ok")) is False}


def _grid_fragile(live):
    """A stair, or an interior marker the base bake reached, that the grid
    sweep found connected at some origins and not all (nav_gate 0.189.0)."""
    out = set()
    for n, d in live.items():
        stairs = [s for s in d.get("stairs") or []
                  if isinstance(s.get("grid"), list) and any(s["grid"])
                  and not all(s["grid"])]
        markers = (d.get("markers") or {}).get("interior_grid_fragile") or []
        if stairs or markers:
            out.add(n)
    return out
'''

CONSIST_OLD = '''    for e in BASELINE["unjudged"] + BASELINE["stair_failures"]:
        assert e.get("reason"), "%s has no reason" % e["shell"]
        assert len(e["reason"]) > 30, "%s reason is too thin" % e["shell"]
'''
CONSIST_NEW = '''    for e in BASELINE["unjudged"] + BASELINE["stair_failures"]:
        assert e.get("reason"), "%s has no reason" % e["shell"]
        assert len(e["reason"]) > 30, "%s reason is too thin" % e["shell"]
    assert BASELINE["counts"]["grid_fragile"] == len(BASELINE["grid_fragile"])
    for e in BASELINE["grid_fragile"]:
        assert e.get("stairs") or e.get("markers"), (
            "%s names nothing fragile" % e["shell"])
        assert len(e.get("reason") or "") > 30, "%s reason is too thin" % e["shell"]
'''

SWEEP_OLD = '''def test_the_sweep_actually_read_shells():
'''
SWEEP_NEW = '''def test_no_new_grid_fragile_shell():
    live = _live()
    if live is None:
        pytest.skip("deli_counter/build is absent; nothing to compare against")
    added = sorted(_grid_fragile(live) - set(GRID_FRAGILE))
    assert not added, (
        "these shells connect on some voxel grids and not others, and are not "
        "in the baseline: %s. Widen the neck the gate's grid sweep found, or "
        "add the shell to navgate_baseline.json's grid_fragile with a reason."
        % ", ".join(added))


def test_grid_baseline_has_not_gone_stale():
    """A shell that got fixed must leave the list, or it hides the next one."""
    live = _live()
    if live is None:
        pytest.skip("deli_counter/build is absent")
    now = _grid_fragile(live)
    fixed = sorted(n for n in GRID_FRAGILE if n in live and n not in now)
    assert not fixed, (
        "these are in grid_fragile but now connect at every grid origin: %s. "
        "Remove them from navgate_baseline.json." % ", ".join(fixed))


def test_every_result_carries_the_grid_sweep():
    """A gate run from before 0.189.0 has no sweep, and would read as nothing
    fragile -- a check that cannot fail."""
    live = _live()
    if live is None:
        pytest.skip("deli_counter/build is absent")
    missing = sorted(n for n, d in live.items()
                     if "grid" not in d and not d.get("error"))
    assert not missing, (
        "%d shell result(s) carry no grid sweep: %s -- re-run nav_gate.py --all"
        % (len(missing), ", ".join(missing[:8])))


def test_the_sweep_actually_read_shells():
'''

EDITS = {TEST: [(CONST_OLD, CONST_NEW), (HELPER_OLD, HELPER_NEW),
                (CONSIST_OLD, CONSIST_NEW), (SWEEP_OLD, SWEEP_NEW)]}


def main():
    for path, pairs in EDITS.items():
        data = path.read_bytes()
        crlf = data.count(b"\r\n")
        assert crlf in (0, data.count(b"\n")), f"{path}: mixed line endings"
        eol = "\r\n" if crlf else "\n"
        text = data.decode("utf-8")
        for old, new in pairs:
            old, new = old.replace("\n", eol), new.replace("\n", eol)
            n = text.count(old)
            assert n == 1, f"{path.name}: anchor matched {n} times: {old[:70]!r}"
            text = text.replace(old, new)
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
