#!/usr/bin/env python3
"""stair_geometry.py v2 -- the key is "stairs" in deli_counter/specs/*.json."""
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DC = os.path.join(ROOT, "deli_counter")
BUILD = os.path.join(DC, "build")
SPECS = os.path.join(DC, "specs")
BAKE = {"radius": 0.40, "climb": 0.15, "slope_deg": 55.0}

def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")

verdict = {}
for fn in sorted(os.listdir(BUILD)) if os.path.isdir(BUILD) else []:
    if not fn.endswith(".navgate.json"):
        continue
    try:
        with open(os.path.join(BUILD, fn), "r", encoding="utf-8") as fh:
            d = json.load(fh)
    except Exception:
        continue
    shell = fn[: -len(".navgate.json")]
    for s in (d.get("stairs") or []):
        verdict[(shell, str(s.get("id")))] = (str(s.get("status")),
                                              str(s.get("detail") or ""))
print("stair verdicts: %d" % len(verdict))
bad = {k: v for k, v in verdict.items() if v[0] != "ok"}
print("failing: %d -- %s" % (len(bad), ", ".join(sorted(k[1] for k in bad))))
if not verdict:
    print("REFUSING -- no verdicts"); sys.exit(2)

if not os.path.isdir(SPECS):
    print("REFUSING -- %s not found" % rel(SPECS)); sys.exit(2)
specs = {}
for fn in sorted(os.listdir(SPECS)):
    if not fn.endswith(".json"):
        continue
    try:
        with open(os.path.join(SPECS, fn), "r", encoding="utf-8") as fh:
            specs[fn[:-5]] = json.load(fh)
    except Exception:
        pass
print("specs: %d" % len(specs))

matched = {}
for shell, sid in verdict:
    spec = specs.get(shell)
    if not isinstance(spec, dict):
        continue
    stairs = spec.get("stairs") or []
    hit = None
    for i, sd in enumerate(stairs):
        if not isinstance(sd, dict):
            continue
        cands = {str(sd.get("id")), "%s_stair_%d" % (shell, i),
                 "%s_%s" % (shell, sd.get("id"))}
        if sid in cands:
            hit = sd
            break
    if hit is None and re.search(r'_stair_(\d+)$', sid):
        i = int(re.search(r'_stair_(\d+)$', sid).group(1))
        if i < len(stairs) and isinstance(stairs[i], dict):
            hit = stairs[i]
    if hit is not None:
        matched[(shell, sid)] = hit

print("matched %d of %d verdicts to a spec stair" % (len(matched), len(verdict)))
missing = [k for k in bad if k not in matched]
if missing:
    print("  UNMATCHED failing stairs: %s" % ", ".join("%s/%s" % k for k in missing))
if len(matched) < 20:
    print("REFUSING -- too few matches for a distribution")
    ex = [str(sd.get("id")) for s in list(specs.values())[:6]
          for sd in (s.get("stairs") or []) if isinstance(sd, dict)]
    print("  spec stair ids look like: %s" % ", ".join(ex[:8]))
    print("  verdict ids look like:    %s" % ", ".join(k[1] for k in list(verdict)[:6]))
    sys.exit(1)

numeric = defaultdict(lambda: {"pass": [], "fail": []})
textual = defaultdict(lambda: {"pass": Counter(), "fail": Counter()})
for key, sd in matched.items():
    bucket = "fail" if verdict[key][0] != "ok" else "pass"
    for k, v in sd.items():
        if isinstance(v, bool):
            textual[k][bucket][str(v)] += 1
        elif isinstance(v, (int, float)):
            numeric[k][bucket].append((float(v), key[1]))
        elif isinstance(v, str):
            textual[k][bucket][v] += 1

print("")
print("=" * 78)
print("NUMERIC STAIR FIELDS -- failing values vs the passing distribution")
print("=" * 78)
print("  %-18s %-24s %s" % ("field", "passing min/med/max", "failing"))
print("  " + "-" * 72)
suspects = []
for k in sorted(numeric):
    p, f = numeric[k]["pass"], numeric[k]["fail"]
    if not p or not f:
        continue
    xs = sorted(v for v, _ in p)
    lo, mid, hi = xs[0], xs[len(xs) // 2], xs[-1]
    out = [(v, s) for v, s in f if v < lo or v > hi]
    print("  %-18s %-24s %s%s" % (k, "%g / %g / %g" % (lo, mid, hi),
          ", ".join("%g" % v for v, _ in sorted(f)),
          "   <== OUTSIDE" if out else ""))
    if out:
        suspects.append((k, out, lo, hi))

print("")
print("=" * 78)
print("TEXT / FLAG FIELDS -- values seen on failing vs passing stairs")
print("=" * 78)
for k in sorted(textual):
    p, f = textual[k]["pass"], textual[k]["fail"]
    if not f:
        continue
    onlyf = set(f) - set(p)
    print("  %-18s failing: %-34s %s"
          % (k, ", ".join("%s x%d" % (a, b) for a, b in f.most_common(4)),
             ("ONLY ON FAILING: %s" % ", ".join(sorted(onlyf))) if onlyf else ""))

print("")
if suspects:
    print("FIELDS PUTTING A FAILING STAIR OUTSIDE EVERY PASSING ONE")
    for k, out, lo, hi in suspects:
        print("  %s (passing %g..%g)" % (k, lo, hi))
        for v, s in out:
            print("      %-44s %g" % (s, v))
else:
    print("NO numeric field separates them. The four are dimensionally ordinary;")
    print("the cause is placement or what the stair abuts, not its own geometry.")

print("")
print("=" * 78)
print("THE FOUR, VERBATIM   (bake: radius %.2f climb %.2f slope %.0f)"
      % (BAKE["radius"], BAKE["climb"], BAKE["slope_deg"]))
print("=" * 78)
for key in sorted(bad):
    shell, sid = key
    sd = matched.get(key)
    print("")
    print("-- %s   [%s]" % (sid, shell))
    print("   %s" % verdict[key][1][:100])
    if sd is None:
        print("   NO SPEC MATCH"); continue
    print("   " + json.dumps(sd, indent=2)[:800].replace("\n", "\n   "))
    spec = specs.get(shell) or {}
    ctx = {k: v for k, v in spec.items()
           if k in ("stories", "story_height", "floor_height", "floors",
                    "height", "name") and not isinstance(v, (list, dict))}
    if ctx:
        print("   building: %s" % json.dumps(ctx))
    rise = sd.get("rise") or sd.get("height")
    run = sd.get("run") or sd.get("length")
    steps = sd.get("steps") or sd.get("step_count")
    width = sd.get("width")
    try:
        if rise and steps:
            r = float(rise) / float(steps)
            print("   riser %.3f m%s" % (r, "   EXCEEDS climb" if r > BAKE["climb"] else ""))
        if rise and run:
            a = math.degrees(math.atan2(float(rise), float(run)))
            print("   slope %.1f deg%s" % (a, "   EXCEEDS" if a > BAKE["slope_deg"] else ""))
        if width:
            print("   width %.2f m%s" % (float(width),
                  "   TOO NARROW" if float(width) <= 2 * BAKE["radius"] else ""))
    except Exception:
        pass
