#!/usr/bin/env python3
"""literal_sites.py -- show the seven shadow literals in context.

READS ONLY. Prints make_material's signature, then each target module's build
signature and every make_material call site with surrounding lines, so the
replacement can be written against the real code rather than guessed.
"""
import ast
import inspect
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "zoo"))

TARGETS = {
    "cash_stack": [36],
    "cheesesteak": [104, 105, 107, 109, 111],
    "condiment_bottle": [45],
    "drop_safe": [60],
    "french_fries": [44],
}
RECIPES = os.path.join(ROOT, "zoo", "zoo_keeper", "recipes")

try:
    from zoo_keeper.bpylayer import materials as M
    print("make_material%s" % inspect.signature(M.make_material))
except Exception as exc:
    print("could not import materials: %s: %s" % (type(exc).__name__, exc))
print("")

for name in sorted(TARGETS):
    path = os.path.join(RECIPES, name + ".py")
    if not os.path.isfile(path):
        print("MISSING %s" % path)
        continue
    with open(path, "r", encoding="utf-8") as fh:
        src = fh.read()
    lines = src.splitlines()
    tree = ast.parse(src, filename=path)

    print("=" * 78)
    print("%s.py   (%d lines)" % (name, len(lines)))
    print("=" * 78)

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            print("  def %s%s   # line %d"
                  % (node.name,
                     ast.unparse(node.args) and "(%s)" % ast.unparse(node.args),
                     node.lineno))
    print("")

    # every make_material call, with its full source segment
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            nm = getattr(fn, "id", None) or getattr(fn, "attr", None)
            if nm == "make_material":
                calls.append(node)
    calls.sort(key=lambda n: n.lineno)
    for node in calls:
        end = getattr(node, "end_lineno", node.lineno)
        lo = max(1, node.lineno - 3)
        hi = min(len(lines), end + 2)
        print("  --- call at line %d ---" % node.lineno)
        for i in range(lo, hi + 1):
            mark = ">>" if node.lineno <= i <= end else "  "
            print("  %s %4d  %s" % (mark, i, lines[i - 1]))
        print("")

    # does anything in this module mention a plan/material at all?
    hits = [(i + 1, l) for i, l in enumerate(lines)
            if "material" in l or "plan" in l]
    print("  lines mentioning 'plan' or 'material': %d" % len(hits))
    for i, l in hits[:14]:
        print("      %4d  %s" % (i, l.strip()[:110]))
    if len(hits) > 14:
        print("      ... %d more" % (len(hits) - 14))
    print("")
