#!/usr/bin/env python3
"""stair_why.py -- why do these three stairs fail when 132 shells' stairs pass?

READS ONLY. Compares the failing stair records against the passing population
and prints the code paths that can produce each status, so the answer comes
from the gate's own vocabulary rather than a guess about geometry.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUILD = os.path.join(ROOT, "deli_counter", "build")
GD = os.path.join(ROOT, "deli_counter", "godot", "addon", "deli_counter", "nav_gate.gd")

def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")

shells = {}
for fn in sorted(os.listdir(BUILD)) if os.path.isdir(BUILD) else []:
    if not fn.endswith(".navgate.json"):
        continue
    try:
        with open(os.path.join(BUILD, fn), "r", encoding="utf-8") as fh:
            d = json.load(fh)
    except Exception:
        continue
    if isinstance(d, dict):
        shells[fn[: -len(".navgate.json")]] = d

print("shells read: %d" % len(shells))
if not shells:
    print("REFUSING TO CONCLUDE -- no results under %s" % rel(BUILD))
    sys.exit(2)

# ---- status vocabulary across every stair in every shell
status = Counter()
per_shell_stairs = Counter()
polys_by_verdict = defaultdict(list)
failing = {}
for name, d in shells.items():
    st = d.get("stairs") or []
    per_shell_stairs[len(st)] += 1
    ok = d.get("stairs_ok", d.get("ok"))
    polys_by_verdict[bool(ok)].append(d.get("navmesh_polys") or 0)
    for s in st:
        status[str(s.get("status"))] += 1
    if ok is False:
        failing[name] = d

print("")
print("STAIR STATUS VOCABULARY across all shells")
for k, v in status.most_common():
    print("    %-24s %d" % (k, v))
print("")
print("stairs per shell: %s" % ", ".join("%d stairs x%d" % (k, v)
                                          for k, v in sorted(per_shell_stairs.items())))
print("")
for verdict, vals in sorted(polys_by_verdict.items()):
    if vals:
        vals = sorted(vals)
        print("navmesh polys, stairs_ok=%s: n=%d  min=%d  median=%d  max=%d"
              % (verdict, len(vals), vals[0], vals[len(vals) // 2], vals[-1]))

print("")
print("=" * 78)
print("THE FAILING SHELLS, VERBATIM")
print("=" * 78)
for name in sorted(failing):
    d = failing[name]
    print("")
    print("-- %s --" % name)
    print("   navmesh_polys: %s   stairs_ok: %s   navigable: %s"
          % (d.get("navmesh_polys"), d.get("stairs_ok", d.get("ok")),
             d.get("navigable")))
    mk = d.get("markers") or {}
    print("   markers: checked=%s reachable=%s interior_checked=%s"
          % (mk.get("checked"), mk.get("reachable"), mk.get("interior_checked")))
    for s in d.get("stairs") or []:
        flag = "  <== FAILS" if str(s.get("status")) not in ("ok",) else ""
        print("   stair %-28s %-12s %s%s"
              % (s.get("id"), s.get("status"), str(s.get("detail"))[:70], flag))
    for k in sorted(d):
        if k not in ("stairs", "markers", "navmesh_polys", "stairs_ok", "ok",
                     "navigable", "exit_code"):
            v = d[k]
            if not isinstance(v, (dict, list)):
                print("   %-18s %s" % (k, str(v)[:80]))

# ---- a passing shell with the same stair count, for contrast
print("")
print("=" * 78)
print("CONTRAST -- passing shells with a similar stair count")
print("=" * 78)
want = max((len(failing[n].get("stairs") or []) for n in failing), default=1)
shown = 0
for name in sorted(shells):
    d = shells[name]
    if d.get("stairs_ok", d.get("ok")) is not True:
        continue
    st = d.get("stairs") or []
    if len(st) != want:
        continue
    print("-- %s   polys=%s" % (name, d.get("navmesh_polys")))
    for s in st:
        print("   stair %-28s %-12s %s"
              % (s.get("id"), s.get("status"), str(s.get("detail"))[:70]))
    shown += 1
    if shown >= 3:
        break
if shown == 0:
    print("   no passing shell has exactly %d stair(s)" % want)

# ---- what produces each status, from the gate itself
print("")
print("=" * 78)
print("WHAT SETS THESE STATUSES  (nav_gate.gd)")
print("=" * 78)
if os.path.isfile(GD):
    with open(GD, "r", encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()
    keys = set(k for k in status if k not in ("None",))
    for i, l in enumerate(lines, 1):
        if re.search(r'"(status|detail)"\s*[:=]|status\s*=|no_path|traversab|'
                     r'\bunreachable\b', l, re.I):
            print("%5d  %s" % (i, l.strip()[:130]))
else:
    print("nav_gate.gd not found at %s" % rel(GD))
