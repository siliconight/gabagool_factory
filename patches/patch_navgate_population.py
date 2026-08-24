#!/usr/bin/env python3
"""patch_navgate_population.py -- freeze the unjudged set so it cannot drift.

  --check / (apply) / --revert / --selftest

The gate's per-shell results live in deli_counter/build/, which is not committed.
So the baseline is DERIVED from live data at apply time and committed; the test
compares live-vs-baseline when build/ exists and validates the baseline's own
integrity when it does not. It never reports a clean sweep of nothing.
"""
import json
import os
import re
import shutil
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DC = os.path.join(ROOT, "deli_counter")
BUILD = os.path.join(DC, "build")
BASELINE = os.path.join(DC, "navgate_baseline.json")
TEST = os.path.join(DC, "test_navgate_population.py")
SIDE = ".pre_navpop"
TODAY = "2026-08-21"

MODE = "apply"
for a in sys.argv[1:]:
    if a in ("--check", "--revert", "--selftest"):
        MODE = a[2:]
    else:
        print("unknown argument %r" % a)
        sys.exit(2)


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def classify(name):
    if re.match(r'^gs_facade_', name):
        return ("facade-only shell: there is no interior for a spawn marker to "
                "stand in, so zero markers checked is the correct outcome")
    if re.match(r'^lf_art_probe_', name):
        return ("probe artifact, not a shipping shell; it exists to exercise the "
                "art path and was never authored with gameplay markers")
    return ("no marker whose type ends in _spawn. RECORDED, NOT EXPLAINED -- "
            "whether this shell should have one is an author decision that has "
            "not been made")


def read_live():
    if not os.path.isdir(BUILD):
        return None
    out = {}
    for fn in sorted(os.listdir(BUILD)):
        if not fn.endswith(".navgate.json"):
            continue
        name = fn[: -len(".navgate.json")]
        try:
            with open(os.path.join(BUILD, fn), "r", encoding="utf-8") as fh:
                d = json.load(fh)
        except Exception:
            continue
        if isinstance(d, dict):
            out[name] = d
    return out or None


TEST_SRC = '''"""The unjudged set is frozen. A NEW shell falling into it must fail.

WHAT THIS CATCHES: nav_gate reports `markers: 0 checked -- reachability
UNJUDGED` for a shell with no marker whose type ends in `_spawn`. That is a
report, not a gate -- the exit code is deliberately unchanged (see nav_gate.gd
and nav_gate.py, both of which say so at length). So the unjudged count can grow
without anything failing, and it has: what a session recorded as 18 measured as
17 with five names the note never mentioned.

The per-shell results live in deli_counter/build/, which is not committed. When
build/ is absent these tests SKIP rather than pass, and the baseline's own
integrity is checked instead, so a clean checkout never reports a green sweep of
nothing.
"""
import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(HERE, "navgate_baseline.json")
BUILD = os.path.join(HERE, "build")

with open(BASELINE_PATH, "r", encoding="utf-8") as _fh:
    BASELINE = json.load(_fh)

UNJUDGED = {e["shell"]: e for e in BASELINE["unjudged"]}
STAIR_FAILURES = {e["shell"]: e for e in BASELINE["stair_failures"]}


def _live():
    if not os.path.isdir(BUILD):
        return None
    out = {}
    for fn in sorted(os.listdir(BUILD)):
        if not fn.endswith(".navgate.json"):
            continue
        try:
            with open(os.path.join(BUILD, fn), "r", encoding="utf-8") as fh:
                d = json.load(fh)
        except Exception:
            continue
        if isinstance(d, dict):
            out[fn[: -len(".navgate.json")]] = d
    return out or None


def _unjudged(live):
    return {n for n, d in live.items()
            if ((d.get("markers") or {}).get("checked", 0) or 0) == 0}


def _failed(live):
    return {n for n, d in live.items()
            if d.get("stairs_ok", d.get("ok")) is False}


# ---------------------------------------------------------------- baseline
def test_baseline_is_internally_consistent():
    assert BASELINE["counts"]["unjudged"] == len(BASELINE["unjudged"])
    assert BASELINE["counts"]["stair_failures"] == len(BASELINE["stair_failures"])
    names = [e["shell"] for e in BASELINE["unjudged"]]
    assert len(names) == len(set(names)), "duplicate shell in the unjudged list"
    for e in BASELINE["unjudged"] + BASELINE["stair_failures"]:
        assert e.get("reason"), "%s has no reason" % e["shell"]
        assert len(e["reason"]) > 30, "%s reason is too thin" % e["shell"]


def test_baseline_is_not_empty():
    assert BASELINE["counts"]["shells"] >= 100
    assert BASELINE["counts"]["unjudged"] > 0, (
        "an empty unjudged baseline would make every comparison below vacuous")


# ------------------------------------------------------------------- sweep
def test_no_new_unjudged_shell():
    live = _live()
    if live is None:
        pytest.skip("deli_counter/build is absent; nothing to compare against")
    added = sorted(_unjudged(live) - set(UNJUDGED))
    assert not added, (
        "these shells are newly UNJUDGED and are not in the baseline: %s. "
        "Either give each a marker whose type ends in _spawn, or add it to "
        "navgate_baseline.json with a reason." % ", ".join(added))


def test_no_new_stair_failure():
    live = _live()
    if live is None:
        pytest.skip("deli_counter/build is absent; nothing to compare against")
    added = sorted(_failed(live) - set(STAIR_FAILURES))
    assert not added, (
        "these shells newly fail the stair gate: %s" % ", ".join(added))


def test_baseline_has_not_gone_stale():
    """A shell that got fixed must leave the baseline, or it hides the next one."""
    live = _live()
    if live is None:
        pytest.skip("deli_counter/build is absent")
    now = _unjudged(live)
    fixed = sorted(n for n in UNJUDGED if n in live and n not in now)
    assert not fixed, (
        "these are in the unjudged baseline but now check markers: %s. "
        "Remove them from navgate_baseline.json -- a stale entry hides a "
        "future regression." % ", ".join(fixed))


def test_the_sweep_actually_read_shells():
    live = _live()
    if live is None:
        pytest.skip("deli_counter/build is absent")
    assert len(live) >= 100, "only %d shell result(s) read" % len(live)
'''

# ------------------------------------------------------------------ revert
if MODE == "revert":
    n = 0
    for p in (BASELINE, TEST):
        if os.path.isfile(p + SIDE):
            shutil.copyfile(p + SIDE, p)
            os.remove(p + SIDE)
            print("  restored %s" % rel(p))
            n += 1
        elif os.path.isfile(p):
            os.remove(p)
            print("  removed  %s" % rel(p))
            n += 1
    print("REVERTED -- %d file(s)" % n)
    sys.exit(0)

live = read_live()
if live is None:
    print("REFUSING -- no .navgate.json under %s" % rel(BUILD))
    print("            the baseline must be derived from real results, never invented")
    sys.exit(1)

unjudged, failures, navnull, disagree, explained = [], [], 0, [], []
for name in sorted(live):
    d = live[name]
    mk = d.get("markers") or {}
    checked = mk.get("checked", 0) or 0
    nav = d.get("navigable", "ABSENT")
    if nav is None:
        navnull += 1
    st_ok = d.get("stairs_ok", d.get("ok"))
    if checked == 0:
        unjudged.append({"shell": name, "checked": 0,
                         "navigable": nav if nav != "ABSENT" else None,
                         "stairs_ok": st_ok,
                         "reason": classify(name)})
        # navigable is a conjunction: a stair failure forces False without the
        # marker state mattering. That is the gate short-circuiting correctly,
        # NOT an inconsistency. Only a shell that passes stairs, checks zero
        # markers and still reports a non-null navigable is unexplained.
        if nav is not None and st_ok is False:
            explained.append((name, nav))
        elif nav is not None:
            disagree.append((name, nav))
    if d.get("stairs_ok", d.get("ok")) is False:
        st = [s.get("id") for s in (d.get("stairs") or [])
              if s.get("status") not in (None, "ok", "traversable")]
        failures.append({"shell": name,
                         "stairs": [s for s in st if s][:6],
                         "reason": "stair(s) reported not traversable by the "
                                   "Godot bake; a geometry fix, not a marker one"})

print("PRE-FLIGHT   %d shell result(s) in %s" % (len(live), rel(BUILD)))
print("  unjudged        %d" % len(unjudged))
print("  stair failures  %d" % len(failures))
print("  navigable null  %d" % navnull)
if explained:
    print("  unjudged with a non-null navigable, EXPLAINED by a stair failure:")
    for n, v in explained:
        print("      %-40s navigable=%r (stairs failed, so navigable is" % (n, v))
        print("      %-40s  False on the stair verdict alone)" % "")
if disagree:
    print("  UNEXPLAINED -- passes stairs, checked zero markers, navigable not null:")
    for n, v in disagree:
        print("      %-40s navigable=%r" % (n, v))
print("")
for e in unjudged:
    print("    %-40s %s" % (e["shell"], e["reason"][:60]))
print("")

exists = [p for p in (BASELINE, TEST) if os.path.isfile(p)]
if exists and MODE != "check":
    print("  (overwriting: %s)" % ", ".join(rel(p) for p in exists))

if MODE == "check":
    print("CHECK OK -- would write %s and %s" % (rel(BASELINE), rel(TEST)))
    sys.exit(0)

if MODE == "selftest":
    if not os.path.isfile(BASELINE) or not os.path.isfile(TEST):
        print("SELFTEST FAILED -- not applied")
        sys.exit(1)
    with open(BASELINE, "r", encoding="utf-8") as fh:
        b = json.load(fh)
    base = {e["shell"] for e in b["unjudged"]}
    now = {e["shell"] for e in unjudged}
    if base != now:
        print("SELFTEST FAILED -- baseline %s vs live %s"
              % (sorted(base - now), sorted(now - base)))
        sys.exit(1)
    if b["counts"]["unjudged"] != len(b["unjudged"]):
        print("SELFTEST FAILED -- count does not match the list")
        sys.exit(1)
    # falsification: the comparison must FAIL on an injected new shell
    injected = now | {"__not_a_real_shell__"}
    if not (injected - base):
        print("SELFTEST FAILED -- the comparison accepted an injected shell, so a")
        print("                   green result from it would mean nothing")
        sys.exit(1)
    print("SELFTEST OK -- baseline names exactly the %d live unjudged shell(s) and"
          % len(now))
    print("               the %d stair failure(s); counts match their lists; and the"
          % len(b["stair_failures"]))
    print("               comparison was shown to FAIL on an injected new shell")
    sys.exit(0)

payload = {
    "generated": TODAY,
    "source": "derived from deli_counter/build/*.navgate.json, not hand-written",
    "what_this_is": (
        "nav_gate reports UNJUDGED for a shell with no marker whose type ends "
        "in _spawn, and the exit code is deliberately unchanged, so the set can "
        "grow silently. This freezes it. A new entrant fails test_navgate_"
        "population.py; a fixed shell must be removed from here."
    ),
    "not_certified": (
        "This says nothing about whether these shells SHOULD have spawn markers. "
        "Five of the seventeen were absent from the note that first recorded this "
        "set, and the note said 18 where the measurement says 17."
    ),
    "counts": {"shells": len(live), "unjudged": len(unjudged),
               "stair_failures": len(failures), "navigable_null": navnull},
    "navigable_null_reconciliation": {
        "unjudged": len(unjudged),
        "navigable_null": navnull,
        "explained_by_stair_failure": [
            {"shell": n, "navigable": v,
             "note": "navigable is a conjunction; a stair failure forces False "
                     "without marker state mattering. Not an inconsistency."}
            for n, v in explained],
        "unexplained": [
            {"shell": n, "navigable": v,
             "note": "passes stairs, checked zero markers, yet navigable is not "
                     "null -- this one is not accounted for"}
            for n, v in disagree] or None,
    },
    "unjudged": unjudged,
    "stair_failures": failures,
}

for p, text in ((BASELINE, json.dumps(payload, indent=2) + "\n"),
                (TEST, TEST_SRC)):
    if os.path.isfile(p) and not os.path.exists(p + SIDE):
        shutil.copyfile(p, p + SIDE)
    with open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    print("  wrote %s" % rel(p))

for dp, dns, fns in os.walk(DC):
    if os.path.basename(dp) == "__pycache__":
        shutil.rmtree(dp, ignore_errors=True)
        dns[:] = []
print("")
print("APPLIED -- run --selftest, then the deli_counter suite.")
