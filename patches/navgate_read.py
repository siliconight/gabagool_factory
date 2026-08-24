#!/usr/bin/env python3
"""navgate_read.py -- read the gate's report and the rule it enforces.

READS ONLY. Reports the size of everything it opens so an empty or truncated
read is visible rather than producing a confident summary of nothing.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")

def read(p):
    with open(p, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()

TXT = os.path.join(ROOT, "deli_counter", "nav_gate.txt")
MD  = os.path.join(ROOT, "deli_counter", "godot", "NAVMESH_CHECK.md")
GD  = os.path.join(ROOT, "deli_counter", "godot", "addon", "deli_counter", "nav_gate.gd")

for p in (TXT, MD, GD):
    print("%-56s %s" % (rel(p), "%d bytes" % os.path.getsize(p)
                        if os.path.isfile(p) else "NOT FOUND"))
print("")
if not os.path.isfile(TXT):
    print("REFUSING TO CONCLUDE -- the report is not where the scan said it was")
    sys.exit(2)

txt = read(TXT)
lines = txt.splitlines()
print("=" * 76)
print("nav_gate.txt -- %d lines" % len(lines))
print("=" * 76)
print("--- first 30 ---")
for i, l in enumerate(lines[:30], 1):
    print("%5d  %s" % (i, l[:150]))
print("--- last 30 ---")
for i, l in enumerate(lines[-30:], len(lines) - 29):
    print("%5d  %s" % (i, l[:150]))

print("")
print("--- verdict / tally lines ---")
rx = re.compile(r'\b(\d+\s*/\s*\d+|\d+\s+of\s+\d+|PASS|FAIL|SKIP|OK|MISSING|'
                r'no spawn|spawn|marker|total|summary)\b', re.I)
shown = 0
for i, l in enumerate(lines, 1):
    if rx.search(l) and len(l.strip()) < 160:
        print("%5d  %s" % (i, l.strip()[:150]))
        shown += 1
        if shown >= 70:
            print("      ... truncated at 70")
            break
if shown == 0:
    print("      none matched -- the report does not use those words")

if os.path.isfile(MD):
    md = read(MD)
    print("")
    print("=" * 76)
    print("NAVMESH_CHECK.md -- %d lines" % len(md.splitlines()))
    print("=" * 76)
    for l in md.splitlines()[:80]:
        print("  " + l[:150])

if os.path.isfile(GD):
    gd = read(GD)
    gl = gd.splitlines()
    print("")
    print("=" * 76)
    print("nav_gate.gd -- %d lines; funcs and the marker/spawn rule" % len(gl))
    print("=" * 76)
    for i, l in enumerate(gl, 1):
        if re.match(r'^\s*(func |const |var |signal |class )', l) or \
           re.search(r'spawn|marker|gate_pass|verdict|fail', l, re.I):
            print("%5d  %s" % (i, l.rstrip()[:150]))
