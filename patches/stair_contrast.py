#!/usr/bin/env python3
"""stair_contrast.py -- the fields that actually exist, pass vs fail.

READS ONLY. Compares on the real schema (from_story/to_story/width/run/
step_rise/style/cut_slabs/role) and prints cbp_town_finale's four stairs side
by side -- same building, same bake, two pass and two fail.
"""
import json, math, os, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DC = os.path.join(ROOT, "deli_counter")
BUILD, SPECS = os.path.join(DC, "build"), os.path.join(DC, "specs")
CLIMB, RADIUS, SLOPE = 0.15, 0.40, 55.0

verdict = {}
for fn in sorted(os.listdir(BUILD)):
    if not fn.endswith(".navgate.json"):
        continue
    with open(os.path.join(BUILD, fn), "r", encoding="utf-8") as fh:
        d = json.load(fh)
    for s in (d.get("stairs") or []):
        verdict[(fn[: -len(".navgate.json")], str(s.get("id")))] = str(s.get("status"))

rows = []
for (shell, sid), st in verdict.items():
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
        rise = (span * sh) if span is not None and isinstance(sh, (int, float)) else None
        run = sd.get("run")
        sr = sd.get("step_rise")
        slope = math.degrees(math.atan2(rise, run)) if rise and run else None
        steps = (rise / sr) if rise and sr else None
        tread = (run / steps) if steps else None
        rows.append({"shell": shell, "id": sid, "ok": st == "ok",
                     "span": span, "width": sd.get("width"), "run": run,
                     "step_rise": sr, "style": sd.get("style"),
                     "cut_slabs": sd.get("cut_slabs"), "role": sd.get("role"),
                     "story_height": sh, "rise": rise, "slope": slope,
                     "steps": steps, "tread": tread})

print("stairs matched to a spec: %d  (%d failing)"
      % (len(rows), sum(1 for r in rows if not r["ok"])))
if len(rows) < 20:
    print("REFUSING -- too few for a distribution"); sys.exit(1)

def dist(field):
    p = [r[field] for r in rows if r["ok"] and isinstance(r[field], (int, float))]
    f = [(r[field], r["id"]) for r in rows if not r["ok"] and isinstance(r[field], (int, float))]
    return sorted(p), sorted(f)

print("")
print("%-12s %-30s %s" % ("field", "passing min/med/max (n)", "failing"))
print("-" * 90)
for k in ("span", "width", "run", "step_rise", "slope", "steps", "tread",
          "story_height", "rise"):
    p, f = dist(k)
    if not p and not f:
        continue
    ps = "%g / %g / %g (n=%d)" % (p[0], p[len(p)//2], p[-1], len(p)) if p else "(none)"
    fs = ", ".join("%.3g" % v for v, _ in f) if f else "(none)"
    out = [v for v, _ in f if p and (v < p[0] or v > p[-1])]
    print("%-12s %-30s %s%s" % (k, ps, fs, "   <== OUTSIDE" if out else ""))

print("")
print("CATEGORICAL / MISSING-FIELD RATES")
for k in ("style", "cut_slabs", "role"):
    pc = Counter(str(r[k]) for r in rows if r["ok"])
    fc = Counter(str(r[k]) for r in rows if not r["ok"])
    print("  %-10s failing: %-30s passing top: %s"
          % (k, dict(fc), ", ".join("%s x%d" % t for t in pc.most_common(3))))
for k in ("width", "step_rise"):
    pm = sum(1 for r in rows if r["ok"] and r[k] is None)
    fm = sum(1 for r in rows if not r["ok"] and r[k] is None)
    print("  %-10s MISSING on %d/%d passing, %d/%d failing"
          % (k, pm, sum(1 for r in rows if r["ok"]),
             fm, sum(1 for r in rows if not r["ok"])))

print("")
print("SPAN: how many stairs cross more than one story?")
sp = Counter((r["span"], r["ok"]) for r in rows if r["span"] is not None)
for span in sorted({s for s, _ in sp}):
    print("  span %-4s  passing %-4d  failing %d"
          % (span, sp.get((span, True), 0), sp.get((span, False), 0)))

print("")
print("BAKE LIMIT VIOLATIONS across every stair")
for r in rows:
    bad = []
    if isinstance(r["step_rise"], (int, float)) and r["step_rise"] > CLIMB:
        bad.append("step_rise %.2f > climb %.2f" % (r["step_rise"], CLIMB))
    if isinstance(r["width"], (int, float)) and r["width"] <= 2 * RADIUS:
        bad.append("width %.2f <= 2*radius %.2f" % (r["width"], 2 * RADIUS))
    if isinstance(r["slope"], (int, float)) and r["slope"] > SLOPE:
        bad.append("slope %.1f > %.0f" % (r["slope"], SLOPE))
    if bad:
        print("  %-46s %-5s %s" % (r["id"], "PASS" if r["ok"] else "FAIL", "; ".join(bad)))

print("")
print("=" * 78)
print("cbp_town_finale -- ALL FOUR STAIRS, same building, same bake")
print("=" * 78)
for r in sorted((x for x in rows if x["shell"].startswith("cbp_town_finale")),
                key=lambda x: x["id"]):
    print("  %-46s %s" % (r["id"], "ok" if r["ok"] else "NO_PATH"))
    print("      span=%s width=%s run=%s step_rise=%s style=%s role=%s"
          % (r["span"], r["width"], r["run"], r["step_rise"], r["style"], r["role"]))
    print("      rise=%s slope=%s steps=%s tread=%s"
          % (r["rise"],
             "%.1f" % r["slope"] if r["slope"] else None,
             "%.0f" % r["steps"] if r["steps"] else None,
             "%.3f" % r["tread"] if r["tread"] else None))
