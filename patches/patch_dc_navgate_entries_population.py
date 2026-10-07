"""Deli Counter 0.196.0: freeze the library's stairs no entrance reaches.

    python patch_dc_navgate_entries_population.py

Anchored on test_navgate_population.py and navgate_baseline.json as read
2026-10-06; refuses on any miss. navgate_baseline.json must round-trip
through `json.dumps(indent=2)`, its own form, so the diff is the new set.

MEASURED FIRST (`nav_gate.py --all` with the gate's entrance check, after
0.195.0): 98 shells have judged stairs, 149 stairs in all, and 148 are
reached from a storey-0 entrance. The one that is not is primos_pizza's,
roadmap 189's discharge neck. No shell with stairs went unjudged; 14 have no
storey-0 exterior door at all (the 12 Empties, shut by design, and the two
facade shells, which have no stairs).
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"
TEST = DC / "test_navgate_population.py"
BASE = DC / "navgate_baseline.json"

OLD_CONST = 'GRID_FRAGILE = {e["shell"]: e for e in BASELINE.get("grid_fragile", [])}\n'
NEW_CONST = OLD_CONST + '''# 0.196.0: shells with a stair no storey-0 entrance reaches. Frozen like the
# rest, for the same reason: the gate reports it and its exit code does not
# gate on it, so the set could grow without anything failing.
ENTRY_UNREACHED = {e["shell"]: e for e in BASELINE.get("entry_unreached", [])}
'''

OLD_TAIL = '''def test_the_sweep_actually_read_shells():
    live = _live()
    if live is None:
        pytest.skip("deli_counter/build is absent")
    assert len(live) >= 100, "only %d shell result(s) read" % len(live)
'''
NEW_TAIL = OLD_TAIL + '''

# ------------------------------------------------------ entrances (0.196.0)
def _entry_unreached(live):
    """{shell: [stair ids]} with a stair no storey-0 entrance reaches."""
    out = {}
    for n, d in live.items():
        ent = d.get("entries")
        if isinstance(ent, dict) and ent.get("stairs_unreached"):
            out[n] = sorted(ent["stairs_unreached"])
    return out


def _pairs(by_shell):
    return {(n, s) for n, ss in by_shell.items() for s in ss}


def test_entry_baseline_is_internally_consistent():
    rows = BASELINE["entry_unreached"]
    assert BASELINE["counts"]["entry_unreached"] == len(rows)
    names = [e["shell"] for e in rows]
    assert len(names) == len(set(names)), "duplicate shell in entry_unreached"
    for e in rows:
        assert e.get("stairs"), "%s names no stair" % e["shell"]
        assert len(e.get("reason") or "") > 30, "%s reason is too thin" % e["shell"]


def test_no_new_stair_no_entrance_reaches():
    live = _live()
    if live is None:
        pytest.skip("deli_counter/build is absent; nothing to compare against")
    frozen = _pairs({n: e["stairs"] for n, e in ENTRY_UNREACHED.items()})
    added = sorted(_pairs(_entry_unreached(live)) - frozen)
    assert not added, (
        "no storey-0 entrance reaches these stairs, and they are not in the "
        "baseline: %s. Clear the way to them, or add them to "
        "navgate_baseline.json's entry_unreached with a reason." % added)


def test_entry_baseline_has_not_gone_stale():
    """A stair an entrance now reaches must leave the list, or it hides the next one."""
    live = _live()
    if live is None:
        pytest.skip("deli_counter/build is absent")
    now = _pairs(_entry_unreached(live))
    gone = sorted((n, s) for n, e in ENTRY_UNREACHED.items() if n in live
                  for s in e["stairs"] if (n, s) not in now)
    assert not gone, (
        "an entrance now reaches these: %s. Remove them from entry_unreached."
        % gone)


def test_every_result_carries_the_entrance_check():
    """A gate result from before 0.196.0 has no entrances, and would read as
    every stair reached -- a check that cannot fail."""
    live = _live()
    if live is None:
        pytest.skip("deli_counter/build is absent")
    missing = sorted(n for n, d in live.items()
                     if "entries" not in d and not d.get("error"))
    assert not missing, (
        "%d shell result(s) carry no entrance check: %s -- re-run "
        "nav_gate.py --all" % (len(missing), ", ".join(missing[:8])))
'''

ENTRY = {
    "shell": "primos_pizza",
    "stairs": ["primos_pizza_stair_0"],
    "reason": ("All 3 storey-0 entrances snap onto one island, and the stair -- basement to "
               "storey 1, through the ground floor -- joins its two ends, but neither end is on "
               "the entrances' island at the gate's own origin: the ground floor it passes "
               "through cannot reach it (nav_gate 0.196.0, 2026-10-06). Roadmap 189 located the "
               "neck at its discharge plate against the north wall beside its breach panel "
               "(docs/findings/stairwell_on_one_grid_in_four/ at the factory root, necks.txt); "
               "'primos_pizza's discharge' is on that item's list. Not fixed here."),
}


def main():
    t = TEST.read_bytes()
    assert b"\r\n" not in t
    ttext = t.decode("utf-8")
    assert ttext.count(OLD_CONST) == 1, "GRID_FRAGILE line not found once"
    assert ttext.endswith(OLD_TAIL), "test_navgate_population.py no longer ends as read"
    assert "ENTRY_UNREACHED" not in ttext
    b = BASE.read_bytes()
    assert b"\r\n" not in b
    btext = b.decode("utf-8")
    d = json.loads(btext)
    assert json.dumps(d, indent=2) + "\n" == btext, "navgate_baseline.json does not round-trip"
    assert "entry_unreached" not in d
    d["entry_unreached"] = [ENTRY]
    d["counts"]["entry_unreached"] = 1
    new = ttext.replace(OLD_CONST, NEW_CONST)       # near the top; the tail is untouched
    TEST.write_bytes((new[:-len(OLD_TAIL)] + NEW_TAIL).encode("utf-8"))
    BASE.write_bytes((json.dumps(d, indent=2) + "\n").encode("utf-8"))
    print("test_navgate_population.py: 4 tests; navgate_baseline.json: entry_unreached, 1 shell")


if __name__ == "__main__":
    main()
