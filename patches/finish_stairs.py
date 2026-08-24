#!/usr/bin/env python3
"""finish_stairs.py -- read the actual stair logic, verbatim.

READS ONLY. _finish_stairs is called by migrate_stairs, stair_regression and
the preset tests; it is where a stair dict becomes final. Also grabs
deli_counter.py's build CLI, which scrolled past last run.
"""
import ast, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DC = os.path.join(ROOT, "deli_counter")
P = os.path.join(DC, "presets.py")

def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")

with open(P, "r", encoding="utf-8", errors="replace") as fh:
    src = fh.read()
lines = src.splitlines()
tree = ast.parse(src, filename=P)

WANT = ("_finish_stairs", "_finish_ladders", "make")
for node in ast.walk(tree):
    if not isinstance(node, ast.FunctionDef) or node.name not in WANT:
        continue
    lo, hi = node.lineno, (node.end_lineno or node.lineno)
    n = hi - lo + 1
    print("=" * 78)
    print("%s()  %s:%d-%d  (%d lines)" % (node.name, rel(P), lo, hi, n))
    print("=" * 78)
    cap = 150 if node.name.startswith("_finish") else 40
    for i in range(lo - 1, min(hi, lo - 1 + cap)):
        print("%5d  %s" % (i + 1, lines[i].rstrip()))
    if n > cap:
        print("      ... %d more line(s)" % (n - cap))
    print("")

print("=" * 78)
print("STAIR-RELATED CONSTANTS in presets.py")
print("=" * 78)
for node in tree.body:
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id.isupper() and \
               re.search(r'STAIR|RUN|WIDTH|RISE|STEP|LAND|TREAD|CLIMB', t.id):
                try:
                    print("  %-24s = %r" % (t.id, ast.literal_eval(node.value)))
                except Exception:
                    print("  %-24s = <computed>  line %d" % (t.id, node.lineno))

print("")
print("=" * 78)
print("deli_counter.py build CLI")
print("=" * 78)
d = os.path.join(DC, "deli_counter.py")
if os.path.isfile(d):
    with open(d, "r", encoding="utf-8", errors="replace") as fh:
        s = fh.read()
    shown = 0
    for m in re.finditer(r'add_(argument|parser)\(\s*([^)]{0,130})', s):
        print("  %-8s %5d  %s" % (m.group(1), s[: m.start()].count("\n") + 1,
                                  m.group(2).strip()[:110]))
        shown += 1
        if shown >= 30:
            break
    if shown == 0:
        print("  no argparse in deli_counter.py -- check check.py / catalog.py")
        for alt in ("check.py", "catalog.py", "new_level.py"):
            ap = os.path.join(DC, alt)
            if not os.path.isfile(ap):
                continue
            with open(ap, "r", encoding="utf-8", errors="replace") as fh:
                t = fh.read()
            hits = re.findall(r'add_argument\(\s*([^)]{0,90})', t)
            if hits:
                print("  -- %s" % alt)
                for h in hits[:12]:
                    print("       %s" % h.strip()[:100])
