#!/usr/bin/env python3
"""finish_head.py -- _finish_stairs from its def, verbatim, in one chunk.

READS ONLY. All three failing stairs carry meta.generated_by = "presets", not
"stair_core", and one has no width at all -- so the defaulting and the run
derivation both live here.
"""
import ast, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
P = os.path.join(os.path.dirname(HERE), "deli_counter", "presets.py")
P = os.path.join(ROOT, "deli_counter", "presets.py")
START = int(os.environ.get("CHUNK", "0"))

with open(P, "r", encoding="utf-8", errors="replace") as fh:
    src = fh.read()
lines = src.splitlines()
tree = ast.parse(src, filename=P)

fn = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_finish_stairs":
        fn = node
        break
if fn is None:
    print("REFUSING -- _finish_stairs not found"); sys.exit(2)

lo, hi = fn.lineno, (fn.end_lineno or fn.lineno)
print("_finish_stairs  lines %d-%d  (%d lines total)" % (lo, hi, hi - lo + 1))
print("showing from offset %d" % START)
print("=" * 78)
a = lo - 1 + START
b = min(hi, a + 125)
for i in range(a, b):
    print("%5d  %s" % (i + 1, lines[i].rstrip()))
if b < hi:
    print("")
    print("... %d more line(s). For the next chunk run:" % (hi - b))
    print("    $env:CHUNK='%d'; python patches\\finish_head.py" % (b - lo + 1))

print("")
print("=" * 78)
print("ANY LINE IN presets.py THAT COULD PRODUCE width 2.2 OR run 6.5")
print("=" * 78)
for i, l in enumerate(lines, 1):
    if re.search(r'(width|run)\s*=\s*[^=]', l) and \
       re.search(r'stair|st\[|sd\[|landing|flight', l, re.I):
        print("%5d  %s" % (i, l.strip()[:130]))
