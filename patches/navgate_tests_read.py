#!/usr/bin/env python3
"""navgate_tests_read.py -- what the existing gate tests already assert.

READS ONLY. Prints each test's functions, its assertions, and any hardcoded
shell-name list, so a new test cannot silently duplicate or contradict one.
"""
import ast
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DC = os.path.join(ROOT, "deli_counter")

names = []
for dp, dns, fns in os.walk(DC):
    if "__pycache__" in dp or "\\build" in dp or "/build" in dp:
        dns[:] = []
        continue
    for fn in fns:
        if fn.endswith(".py") and re.search(r'nav|marker|traversal|gate', fn, re.I):
            names.append(os.path.join(dp, fn))
names.sort()

def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")

print("gate-related test/py modules under deli_counter: %d" % len(names))
for p in names:
    print("    %s  (%d bytes)" % (rel(p), os.path.getsize(p)))
print("")
if not names:
    print("REFUSING TO CONCLUDE -- found none")
    sys.exit(2)

for p in names:
    with open(p, "r", encoding="utf-8", errors="replace") as fh:
        src = fh.read()
    lines = src.splitlines()
    print("=" * 76)
    print("%s -- %d lines" % (rel(p), len(lines)))
    print("=" * 76)
    try:
        tree = ast.parse(src, filename=p)
    except Exception as exc:
        print("  parse error: %s" % exc)
        continue
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            doc = (ast.get_docstring(node) or "").splitlines()
            print("  def %s()   # line %d" % (node.name, node.lineno))
            if doc:
                print("        \"%s\"" % doc[0][:120])
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id.isupper():
                    try:
                        val = ast.literal_eval(node.value)
                        s = repr(val)
                        print("  %s = %s" % (t.id, s[:200]))
                    except Exception:
                        print("  %s = <non-literal>  # line %d" % (t.id, node.lineno))
    print("  --- assertions ---")
    shown = 0
    for i, l in enumerate(lines, 1):
        if re.search(r'^\s*assert\b', l):
            print("  %5d  %s" % (i, l.strip()[:140]))
            shown += 1
            if shown >= 30:
                print("        ... truncated")
                break
    if shown == 0:
        print("        none")
    print("")
