#!/usr/bin/env python3
"""navgate_tally.py -- the CURRENT per-shell state, measured not quoted.

READS ONLY. Every number in the comments (135, 137, 103, 123) was written at a
different time. This reads the per-shell .navgate.json files and computes the
tally now, reporting the schema split first because nav_gate.py:309 says some
files predate the stairs_ok/ok split and carry `ok` alone.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKIP = re.compile(r'(^|[\\/])(\.git|__pycache__|_preview[^\\/]*|_probe|_runs)([\\/]|$)')

def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")

files = []
for dp, dns, fns in os.walk(ROOT):
    if SKIP.search(dp):
        dns[:] = []
        continue
    for fn in fns:
        if fn.endswith(".navgate.json"):
            files.append(os.path.join(dp, fn))
files.sort()

dirs = Counter(rel(os.path.dirname(p)) for p in files)
print("*.navgate.json found: %d across %d dir(s)" % (len(files), len(dirs)))
for d, n in dirs.most_common(8):
    print("    %5d  %s" % (n, d))
print("")
if not files:
    print("REFUSING TO CONCLUDE -- no .navgate.json anywhere; the gate's per-shell")
    print("results are not on disk, so any tally here would be invented")
    sys.exit(2)

# take the largest directory as the live population
live_dir = dirs.most_common(1)[0][0]
live = [p for p in files if rel(os.path.dirname(p)) == live_dir]
print("using %s as the live population: %d shell(s)" % (live_dir, len(live)))
print("")

schema = Counter()
stairs = Counter()
navigable = Counter()
markers_state = Counter()
fail_names, unjudged_names, err_names = [], [], []
scoped = 0
rows = []

for p in live:
    name = os.path.basename(p)[: -len(".navgate.json")]
    try:
        with open(p, "r", encoding="utf-8") as fh:
            d = json.load(fh)
    except Exception as exc:
        err_names.append((name, "%s: %s" % (type(exc).__name__, exc)))
        continue
    if not isinstance(d, dict):
        err_names.append((name, "not an object"))
        continue

    has_new = "stairs_ok" in d
    schema["stairs_ok present" if has_new else "only legacy ok"] += 1
    ok = d.get("stairs_ok", d.get("ok"))
    stairs[repr(ok)] += 1
    if ok is False:
        fail_names.append(name)
    if d.get("error"):
        err_names.append((name, str(d["error"])[:80]))

    nav = d.get("navigable", "ABSENT")
    navigable[repr(nav)] += 1

    mk = d.get("markers") or {}
    checked = mk.get("checked", 0) or 0
    if "interior_checked" in mk:
        scoped += 1
    if checked == 0:
        markers_state["0 checked (UNJUDGED)"] += 1
        unjudged_names.append(name)
    elif mk.get("reachable", 0) == checked:
        markers_state["all reachable"] += 1
    else:
        markers_state["some unreachable"] += 1

    rows.append((name, ok, nav, checked, mk.get("reachable", 0),
                 mk.get("interior_checked"), mk.get("scope_note")))

def show(title, counter):
    print("%s" % title)
    for k, v in counter.most_common():
        print("    %-26s %d" % (k, v))
    print("")

show("SCHEMA", schema)
show("STAIR VERDICT  (stairs_ok, falling back to legacy ok)", stairs)
show("NAVIGABLE  (tri-state; the promotion the gate refuses to enforce)", navigable)
show("MARKERS", markers_state)
print("shells carrying SCOPED marker counts (interior_checked): %d of %d"
      % (scoped, len(live)))
print("")

print("=" * 74)
print("STAIR FAILURES -- %d" % len(fail_names))
print("=" * 74)
for n in fail_names:
    print("    %s" % n)

print("")
print("=" * 74)
print("NO SPAWN MARKER / nothing checked -- %d" % len(unjudged_names))
print("=" * 74)
for n in unjudged_names:
    print("    %s" % n)

if err_names:
    print("")
    print("ERRORS -- %d" % len(err_names))
    for n, e in err_names[:20]:
        print("    %-40s %s" % (n, e))

out = os.path.join(HERE, "_probe")
os.makedirs(out, exist_ok=True)
with open(os.path.join(out, "navgate_tally.json"), "w", encoding="utf-8") as fh:
    json.dump({"live_dir": live_dir, "count": len(live),
               "schema": dict(schema), "stairs": dict(stairs),
               "navigable": dict(navigable), "markers": dict(markers_state),
               "stair_failures": fail_names, "unjudged": unjudged_names,
               "rows": [{"shell": r[0], "stairs_ok": r[1], "navigable": r[2],
                         "checked": r[3], "reachable": r[4],
                         "interior_checked": r[5], "scope_note": r[6]}
                        for r in rows]}, fh, indent=2)
print("")
print("wrote %s" % rel(os.path.join(out, "navgate_tally.json")))
