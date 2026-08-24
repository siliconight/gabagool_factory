#!/usr/bin/env python3
"""stair_core_read.py -- the archetypes that replace authored stairs.

READS ONLY. presets.make() with stairs_first=True discards the recipe's stair
and calls stair_core.core_first(spec, archetype). So the failing dimensions come
from an archetype, not from presets.py. This prints every archetype, the default
mapping, and which one each failing shell used.
"""
import ast, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DC = os.path.join(ROOT, "deli_counter")
SC = os.path.join(DC, "stair_core.py")
SPECS = os.path.join(DC, "specs")
FAILING = ("cbp_town_finale_midbalanced_schemafixed", "night_pawn", "primos_pizza")

def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")

if not os.path.isfile(SC):
    print("REFUSING -- %s not found" % rel(SC)); sys.exit(2)
with open(SC, "r", encoding="utf-8", errors="replace") as fh:
    src = fh.read()
lines = src.splitlines()
tree = ast.parse(src, filename=SC)
print("%s -- %d lines" % (rel(SC), len(lines)))
print("")

print("=" * 78)
print("MODULE-LEVEL CONSTANTS (archetypes live here)")
print("=" * 78)
for node in tree.body:
    if not isinstance(node, ast.Assign):
        continue
    for t in node.targets:
        if not isinstance(t, ast.Name) or not t.id.isupper():
            continue
        try:
            val = ast.literal_eval(node.value)
            txt = json.dumps(val, indent=2, default=str)
            print("  %s = %s" % (t.id, txt[:1400].replace("\n", "\n  ")))
        except Exception:
            print("  %s = <computed>   line %d" % (t.id, node.lineno))
        print("")

print("=" * 78)
print("ARCHETYPE-SHAPED DICTS anywhere in the module")
print("=" * 78)
seen = 0
for node in ast.walk(tree):
    if not isinstance(node, ast.Dict):
        continue
    keys = {k.value for k in node.keys
            if isinstance(k, ast.Constant) and isinstance(k.value, str)}
    if not ({"width", "run", "style"} & keys):
        continue
    seg = ast.get_source_segment(src, node) or ""
    print("  line %d: %s" % (node.lineno, " ".join(seg.split())[:240]))
    seen += 1
    if seen >= 25:
        print("  ... truncated")
        break
if seen == 0:
    print("  none -- widths/runs are computed, not tabled")

print("")
print("=" * 78)
print("core_first() and any width/run derivation")
print("=" * 78)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in (
            "core_first", "_place_core", "place_core", "_stair_dict", "_core"):
        lo, hi = node.lineno, (node.end_lineno or node.lineno)
        print("-- %s()  lines %d-%d" % (node.name, lo, hi))
        for i in range(lo - 1, min(hi, lo - 1 + 70)):
            print("%5d  %s" % (i + 1, lines[i].rstrip()[:130]))
        if hi - lo + 1 > 70:
            print("      ... %d more" % (hi - lo + 1 - 70))
        print("")

print("=" * 78)
print("LINES SETTING width / run")
print("=" * 78)
for i, l in enumerate(lines, 1):
    if re.search(r'["\'](width|run)["\']\s*[:=]|\bwidth\s*=|\brun\s*=', l):
        print("%5d  %s" % (i, l.strip()[:130]))

print("")
print("=" * 78)
print("WHAT THE FAILING SPECS RECORD ABOUT THEIR CORE")
print("=" * 78)
for name in FAILING:
    p = os.path.join(SPECS, name + ".json")
    if not os.path.isfile(p):
        print("  %s: not found" % name); continue
    with open(p, "r", encoding="utf-8") as fh:
        d = json.load(fh)
    hits = {k: v for k, v in d.items()
            if re.search(r'arch|core|preset|stairs_first|n_stories|facade', k, re.I)
            and not isinstance(v, (list, dict))}
    st = (d.get("stairs") or [{}])[0]
    print("  %-42s n_stories=%s facade=%s" % (name, d.get("n_stories"), d.get("facade")))
    if hits:
        print("      %s" % json.dumps(hits)[:160])
    print("      stair[0] meta: %s   role=%s width=%s run=%s"
          % (json.dumps(st.get("meta")), st.get("role"), st.get("width"), st.get("run")))
