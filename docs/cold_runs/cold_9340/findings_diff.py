"""The findings one cold run's validation carries and another's does not, by source, code and location.

A probe: prints what it measured and stops. Reads `.level_factory/validation/<mission>.json` from two workspaces.

    python docs/cold_runs/cold_9340/findings_diff.py <workspace A> <workspace B> [<mission>]
"""
import collections
import json
import os
import sys

a_ws, b_ws = sys.argv[1], sys.argv[2]
mission = sys.argv[3] if len(sys.argv) > 3 else "restaurant_row_001"


def load(ws):
    d = json.load(open(os.path.join(ws, ".level_factory", "validation", mission + ".json"), encoding="utf-8"))
    issues = d.get("issues") or d.get("findings") or []
    if not isinstance(issues, list):
        raise SystemExit("%s: no issues list in its validation (keys %s)" % (ws, sorted(d)))
    return d, issues


def key(i):
    return (i.get("source_tool"), i.get("code"), i.get("candidate_id"), i.get("location") or i.get("message", "")[:80])


da, ia = load(a_ws)
db, ib = load(b_ws)
print("A %s: %d findings | B %s: %d findings" % (a_ws, len(ia), b_ws, len(ib)))
ca, cb = collections.Counter(key(i) for i in ia), collections.Counter(key(i) for i in ib)
by_code_a = collections.Counter((i.get("source_tool"), i.get("code")) for i in ia)
by_code_b = collections.Counter((i.get("source_tool"), i.get("code")) for i in ib)
print("by source and code, where the counts differ:")
for k in sorted(set(by_code_a) | set(by_code_b), key=str):
    if by_code_a[k] != by_code_b[k]:
        print("  %-60s A %3d  B %3d" % ("%s %s" % k, by_code_a[k], by_code_b[k]))
print("in B, not in A:")
for i in ib:
    if ca[key(i)] < cb[key(i)]:
        cb[key(i)] -= 1
        print("  +", i.get("severity"), i.get("source_tool"), i.get("code"), i.get("candidate_id"), "|",
              (i.get("location") or ""), "|", (i.get("message") or "")[:220])
print("in A, not in B:")
cb = collections.Counter(key(i) for i in ib)
for i in ia:
    if cb[key(i)] < ca[key(i)]:
        ca[key(i)] -= 1
        print("  -", i.get("severity"), i.get("source_tool"), i.get("code"), i.get("candidate_id"), "|",
              (i.get("location") or ""), "|", (i.get("message") or "")[:220])
