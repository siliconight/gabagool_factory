#!/usr/bin/env python3
"""agent_reconcile.py -- do the stair contract and the navmesh bake agree?

READS ONLY. stairwell.py imports agent_contract and holds _AGENT_PASS_WIDTH=0.7
while nav_gate bakes at radius 0.40 (a 0.80 m agent). If those disagree, a stair
can satisfy the contract and still be unbakeable by construction.
"""
import ast, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DC = os.path.join(ROOT, "deli_counter")

def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")

def consts(path, pat):
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        src = fh.read()
    out = []
    try:
        tree = ast.parse(src, filename=path)
    except Exception:
        return out
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and re.search(pat, t.id, re.I):
                    try:
                        out.append((t.id, ast.literal_eval(node.value), node.lineno))
                    except Exception:
                        out.append((t.id, "<computed>", node.lineno))
    return out

AC = os.path.join(DC, "agent_contract.py")
print("=" * 78)
print("agent_contract.py -- the ratified body")
print("=" * 78)
got = consts(AC, r'.')
if got is None:
    print("  NOT FOUND at %s" % rel(AC))
    for dp, dns, fns in os.walk(ROOT):
        if "__pycache__" in dp or "\\.git" in dp:
            continue
        if "agent_contract.py" in fns:
            print("  found instead at %s" % rel(os.path.join(dp, "agent_contract.py")))
            got = consts(os.path.join(dp, "agent_contract.py"), r'.')
            break
for name, val, ln in (got or []):
    print("  %-28s = %-12r  line %d" % (name, val, ln))

print("")
print("=" * 78)
print("stairwell.py -- dimensional constants")
print("=" * 78)
for name, val, ln in (consts(os.path.join(DC, "stairwell.py"),
                             r'WIDTH|DEPTH|MARGIN|BAND|STEP|HEAD|AGENT|ENFORC|CONTRACT') or []):
    print("  %-28s = %-12r  line %d" % (name, val, ln))

print("")
print("=" * 78)
print("THE BAKE PARAMETERS the gate actually uses")
print("=" * 78)
GD = os.path.join(DC, "godot", "addon", "deli_counter", "nav_gate.gd")
if os.path.isfile(GD):
    with open(GD, "r", encoding="utf-8", errors="replace") as fh:
        for i, l in enumerate(fh.read().splitlines(), 1):
            if re.search(r'agent_radius|agent_height|cell_size|max_climb|max_slope|'
                         r'radius|climb|slope|cell', l) and not l.strip().startswith("#"):
                print("%5d  %s" % (i, l.strip()[:120]))
else:
    print("  nav_gate.gd not found")

print("")
print("=" * 78)
print("RECONCILIATION")
print("=" * 78)
print("  stair contract minimum passage : _AGENT_PASS_WIDTH  (above)")
print("  navmesh needs                  : 2 x agent_radius")
print("  If the first is smaller than the second, a stair can satisfy the")
print("  contract and still be unwalkable by construction -- and nothing")
print("  downstream of the contract would ever say so.")
