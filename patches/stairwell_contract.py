#!/usr/bin/env python3
"""stairwell_contract.py -- the existing generated-stair contract.

READS ONLY. _finish_stairs opts a stair into "stairwell.py's hard generated-
stair contract". If that contract has no rule about what the navmesh baker can
walk, that gap is why four stairs shipped unbakeable -- and it is the right
place to add one.
"""
import ast, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SW = os.path.join(ROOT, "deli_counter", "stairwell.py")

def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")

if not os.path.isfile(SW):
    print("REFUSING -- %s not found" % rel(SW)); sys.exit(2)
with open(SW, "r", encoding="utf-8", errors="replace") as fh:
    src = fh.read()
lines = src.splitlines()
tree = ast.parse(src, filename=SW)
print("%s -- %d lines" % (rel(SW), len(lines)))
print("")

print("=" * 78)
print("MODULE CONSTANTS  (the dimensional contract, if there is one)")
print("=" * 78)
for node in tree.body:
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id.isupper():
                try:
                    print("  %-26s = %r" % (t.id, ast.literal_eval(node.value)))
                except Exception:
                    print("  %-26s = <computed>  line %d" % (t.id, node.lineno))
print("")

print("=" * 78)
print("FUNCTIONS")
print("=" * 78)
for node in tree.body:
    if isinstance(node, ast.FunctionDef):
        doc = (ast.get_docstring(node) or "").splitlines()
        print("  %-28s line %-5d %s" % (node.name + "()", node.lineno,
                                        doc[0][:90] if doc else ""))
print("")

print("=" * 78)
print("EVERY FINDING THE CONTRACT CAN RAISE  (code + severity + message)")
print("=" * 78)
shown = 0
for i, l in enumerate(lines, 1):
    if re.search(r'(append|add|yield)\s*\(.*(finding|Finding|\berror\b|\bwarn)', l) or \
       re.search(r'severity|SEVER|"error"|"warning"|"info"', l):
        print("%5d  %s" % (i, l.strip()[:135]))
        shown += 1
        if shown >= 45:
            print("      ... truncated")
            break
if shown == 0:
    print("  none matched")

print("")
print("=" * 78)
print("DOES THE CONTRACT MENTION width / run / navmesh / bake / agent AT ALL?")
print("=" * 78)
hits = 0
for i, l in enumerate(lines, 1):
    if re.search(r'\bwidth\b|\brun\b|navmesh|\bbake|agent|radius|climb|slope|'
                 r'tread|riser|step_rise', l, re.I):
        print("%5d  %s" % (i, l.strip()[:135]))
        hits += 1
        if hits >= 40:
            print("      ... truncated")
            break
if hits == 0:
    print("  NO. The contract says nothing about dimensions or bakeability --")
    print("  which is exactly the gap that let four unbakeable stairs through.")
