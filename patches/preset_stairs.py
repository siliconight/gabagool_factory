#!/usr/bin/env python3
"""preset_stairs.py -- where do width 2.2 / run 6.5 / width 1.0 come from?

READS ONLY. Every failing stair carries meta.generated_by = "presets", so the
values were chosen by presets.py, not by an author. This finds every stair dict
the generator builds, with its enclosing function, and reports which literal
width/run combinations exist -- so the four outliers can be traced to a branch.
"""
import ast
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DC = os.path.join(ROOT, "deli_counter")
SPECS = os.path.join(DC, "specs")
TARGETS = ("cbp_town_finale_midbalanced_schemafixed", "night_pawn", "primos_pizza")

def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")

# ---- 1. which preset made the three failing shells?
print("=" * 78)
print("THE THREE SPECS -- top-level keys and any preset/provenance field")
print("=" * 78)
for name in TARGETS:
    p = os.path.join(SPECS, name + ".json")
    if not os.path.isfile(p):
        print("  %s: NOT FOUND" % name)
        continue
    with open(p, "r", encoding="utf-8") as fh:
        d = json.load(fh)
    print("  %s" % name)
    print("      keys: %s" % ", ".join(sorted(d.keys()))[:150])
    for k in sorted(d):
        if re.search(r'preset|template|archetype|kind|type|generated|meta|source', k, re.I):
            v = d[k]
            print("      %-14s %s" % (k, json.dumps(v)[:120]))
print("")

# ---- 2. every stair dict literal the generator builds
files = []
for dp, dns, fns in os.walk(DC):
    if re.search(r'[\\/](build|__pycache__|_probe|specs)$', dp):
        dns[:] = []
        continue
    for fn in fns:
        if fn.endswith(".py") and re.search(r'preset|level_design|new_level|migrate_stairs',
                                            fn, re.I):
            files.append(os.path.join(dp, fn))
files.sort()
print("generator modules: %s" % ", ".join(rel(p) for p in files))
if not files:
    print("REFUSING TO CONCLUDE -- no generator module found")
    sys.exit(2)
print("")

combos = Counter()
sites = 0
for p in files:
    with open(p, "r", encoding="utf-8", errors="replace") as fh:
        src = fh.read()
    try:
        tree = ast.parse(src, filename=p)
    except Exception as exc:
        print("  parse error %s: %s" % (rel(p), exc))
        continue

    # map line -> enclosing function
    owner = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for ln in range(node.lineno, (node.end_lineno or node.lineno) + 1):
                owner[ln] = node.name

    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        keys = {k.value for k in node.keys
                if isinstance(k, ast.Constant) and isinstance(k.value, str)}
        if not ({"style", "step_rise", "to_story"} & keys):
            continue
        sites += 1
        seg = ast.get_source_segment(src, node) or ""
        vals = {}
        for k, v in zip(node.keys, node.values):
            if isinstance(k, ast.Constant) and isinstance(v, ast.Constant):
                vals[k.value] = v.value
        combos[(str(vals.get("style")), vals.get("width"), vals.get("run"))] += 1
        print("-- %s:%d   in %s()" % (rel(p), node.lineno,
                                      owner.get(node.lineno, "<module>")))
        body = " ".join(seg.split())
        print("     %s" % body[:220])

print("")
print("LITERAL (style, width, run) COMBINATIONS IN THE GENERATOR")
print("  %-14s %-8s %-8s %s" % ("style", "width", "run", "sites"))
print("  " + "-" * 44)
for (st, w, r), n in sorted(combos.items(), key=lambda t: str(t[0])):
    flag = ""
    if w in (2.2, 1.0) or r in (6.5, 5.2):
        flag = "   <== matches a FAILING stair"
    print("  %-14s %-8s %-8s %d%s" % (st, w, r, n, flag))
if sites == 0:
    print("  none -- the generator does not build stair dicts as literals;")
    print("  the values are computed, so look at the computation instead")

# ---- 3. any literal 2.2 / 6.5 / 1.0 / 5.2 near stair code
print("")
print("=" * 78)
print("LITERALS 2.2 / 6.5 / 1.0 / 5.2 ON LINES MENTIONING width/run/stair")
print("=" * 78)
hits = 0
for p in files:
    with open(p, "r", encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()
    for i, l in enumerate(lines, 1):
        if re.search(r'\b(2\.2|6\.5|5\.2|1\.0)\b', l) and \
           re.search(r'width|run|stair', l, re.I):
            print("  %s:%d  %s" % (rel(p), i, l.strip()[:120]))
            hits += 1
            if hits >= 40:
                break
    if hits >= 40:
        break
if hits == 0:
    print("  none -- these values are computed, not written down")
