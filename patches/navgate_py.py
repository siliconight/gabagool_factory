#!/usr/bin/env python3
"""navgate_py.py -- find the Python half and the 3-of-135 verdict.

READS ONLY. Output is capped per section; every section prints what it read.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKIP = re.compile(r'(^|[\\/])(\.git|__pycache__|_preview[^\\/]*|_probe|_runs'
                  r'|\.venv|venv|site-packages)([\\/]|$)')

def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")

# ---- locate nav_gate*.py
found = []
for dp, dns, fns in os.walk(ROOT):
    if SKIP.search(dp):
        dns[:] = []
        continue
    for fn in fns:
        if fn.startswith("nav_gate") and fn.endswith(".py"):
            found.append(os.path.join(dp, fn))
found.sort()
print("nav_gate*.py found: %d" % len(found))
for p in found:
    print("    %s  (%d bytes)" % (rel(p), os.path.getsize(p)))
print("")

if not found:
    print("REFUSING TO CONCLUDE -- the .gd names nav_gate.py but no such file exists")
    sys.exit(2)

for p in found[:2]:
    with open(p, "r", encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()
    print("=" * 76)
    print("%s -- %d lines" % (rel(p), len(lines)))
    print("=" * 76)
    rx = re.compile(r'^\s*(def |class |[A-Z_]{3,}\s*=)|footprint|scope|verdict|'
                    r'spawn|markers|detail|PASS|FAIL|exit\(|return ', re.I)
    shown = 0
    for i, l in enumerate(lines, 1):
        if rx.search(l):
            print("%5d  %s" % (i, l.rstrip()[:140]))
            shown += 1
            if shown >= 110:
                print("      ... truncated at 110")
                break
    print("")

# ---- the tally in the report
TXT = os.path.join(ROOT, "deli_counter", "nav_gate.txt")
if os.path.isfile(TXT):
    with open(TXT, "r", encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()
    print("=" * 76)
    print("nav_gate.txt -- %d lines; verdict/tally only" % len(lines))
    print("=" * 76)
    rx = re.compile(r'(\bof\s+\d+\b|\d+\s*/\s*\d+|verdict|PASS|FAIL|UNSCOPED|'
                    r'UNRESOLVED|no spawn|spawn|navigable)', re.I)
    shown = 0
    for i, l in enumerate(lines, 1):
        s = l.strip()
        if s and rx.search(s) and len(s) < 170:
            print("%5d  %s" % (i, s[:150]))
            shown += 1
            if shown >= 60:
                print("      ... truncated at 60")
                break
    if shown == 0:
        print("      no tally lines matched")
