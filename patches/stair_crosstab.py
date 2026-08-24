#!/usr/bin/env python3
"""stair_crosstab.py -- style x span, and what separates passing switchbacks.

READS ONLY. step_rise is a project-wide constant (0.19) and slope>55 passes
routinely, so both are dead as explanations. This cross-tabs the two fields that
still differ and prints every switchback that spans 2+ stories, passing and
failing, so the survivors can be compared against the casualties.
"""
import json, math, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DC = os.path.join(ROOT, "deli_counter")
BUILD, SPECS = os.path.join(DC, "build"), os.path.join(DC, "specs")

verdict = {}
for fn in sorted(os.listdir(BUILD)):
    if fn.endswith(".navgate.json"):
        with open(os.path.join(BUILD, fn), "r", encoding="utf-8") as fh:
            d = json.load(fh)
        for s in (d.get("stairs") or []):
            verdict[(fn[:-len(".navgate.json")], str(s.get("id")))] = (
                str(s.get("status")), str(s.get("detail") or ""))

rows = []
for (shell, sid), (st, detail) in verdict.items():
    p = os.path.join(SPECS, shell + ".json")
    if not os.path.isfile(p):
        continue
    with open(p, "r", encoding="utf-8") as fh:
        spec = json.load(fh)
    sh = spec.get("story_height")
    for sd in (spec.get("stairs") or []):
        if not isinstance(sd, dict) or str(sd.get("id")) != sid:
            continue
        fs, ts = sd.get("from_story"), sd.get("to_story")
        span = (ts - fs) if isinstance(fs, (int, float)) and isinstance(ts, (int, float)) else None
        rows.append({"shell": shell, "id": sid, "ok": st == "ok", "detail": detail,
                     "span": span, "style": sd.get("style"), "run": sd.get("run"),
                     "width": sd.get("width"), "role": sd.get("role"),
                     "from": fs, "to": ts, "story_height": sh,
                     "rise": (span * sh) if span is not None and isinstance(sh, (int, float)) else None})

print("stairs: %d  (%d failing)" % (len(rows), sum(1 for r in rows if not r["ok"])))
if len(rows) < 20:
    print("REFUSING -- too few"); sys.exit(1)

print("")
print("STYLE x SPAN")
print("  %-12s %-6s %8s %8s %8s" % ("style", "span", "passing", "failing", "fail %"))
print("  " + "-" * 48)
cells = Counter((str(r["style"]), r["span"], r["ok"]) for r in rows)
for style in sorted({str(r["style"]) for r in rows}):
    for span in sorted({r["span"] for r in rows if r["span"] is not None}):
        p = cells.get((style, span, True), 0)
        f = cells.get((style, span, False), 0)
        if p or f:
            print("  %-12s %-6s %8d %8d %8s"
                  % (style, span, p, f,
                     "%.0f%%" % (100.0 * f / (p + f)) if (p + f) else "-"))

multi = [r for r in rows if r["span"] is not None and r["span"] >= 2
         and str(r["style"]) == "switchback"]
print("")
print("=" * 78)
print("EVERY SWITCHBACK SPANNING 2+ STORIES  (%d total, %d failing)"
      % (len(multi), sum(1 for r in multi if not r["ok"])))
print("=" * 78)
print("  %-42s %-5s %-5s %-5s %-6s %-6s %s"
      % ("id", "verd", "span", "run", "width", "rise", "role"))
print("  " + "-" * 88)
for r in sorted(multi, key=lambda x: (x["ok"], x["id"])):
    print("  %-42s %-5s %-5s %-5s %-6s %-6s %s"
          % (r["id"][:42], "FAIL" if not r["ok"] else "ok", r["span"],
             r["run"], r["width"], r["rise"], r["role"]))

print("")
print("SWITCHBACK span>=2: passing vs failing on each numeric field")
for k in ("run", "width", "rise", "story_height"):
    p = sorted(r[k] for r in multi if r["ok"] and isinstance(r[k], (int, float)))
    f = sorted(r[k] for r in multi if not r["ok"] and isinstance(r[k], (int, float)))
    print("  %-12s passing %-28s failing %s"
          % (k, ("%g..%g (n=%d)" % (p[0], p[-1], len(p))) if p else "(none)",
             (", ".join("%g" % v for v in f)) if f else "(none)"))

print("")
print("THE ONE SPAN-1 FAILURE, for contrast")
for r in rows:
    if not r["ok"] and r["span"] == 1:
        print("  %s  style=%s run=%s width=%s rise=%s"
              % (r["id"], r["style"], r["run"], r["width"], r["rise"]))
        print("      %s" % r["detail"][:90])
        same = [x for x in rows if x["ok"] and str(x["style"]) == str(r["style"])
                and x["span"] == 1 and isinstance(x["width"], (int, float))]
        if same:
            ws = sorted(x["width"] for x in same)
            print("      passing span-1 %s widths: %g..%g (n=%d); this one is %s"
                  % (r["style"], ws[0], ws[-1], len(ws), r["width"]))
