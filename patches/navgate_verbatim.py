#!/usr/bin/env python3
"""navgate_verbatim.py -- read the verdict logic without filtering it.

READS ONLY. Regex-filtered reads fragmented the comments and produced three
different denominators (137, 103, 135). This prints the region verbatim, then
hunts every "of N shells" tally in the tree so the numbers can be reconciled
against their sources instead of guessed at.
"""
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKIP = re.compile(r'(^|[\\/])(\.git|__pycache__|_preview[^\\/]*|_probe|_runs'
                  r'|\.venv|venv|site-packages)([\\/]|$)')

def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")

targets = []
for dp, dns, fns in os.walk(ROOT):
    if SKIP.search(dp):
        dns[:] = []
        continue
    for fn in fns:
        if fn.startswith("nav_gate") and fn.endswith(".py"):
            targets.append(os.path.join(dp, fn))
targets.sort()
if not targets:
    print("REFUSING -- no nav_gate*.py")
    sys.exit(2)

main = targets[0]
with open(main, "r", encoding="utf-8", errors="replace") as fh:
    lines = fh.read().splitlines()
print("=" * 78)
print("%s -- %d lines, showing 195-330 VERBATIM" % (rel(main), len(lines)))
print("=" * 78)
for i in range(194, min(330, len(lines))):
    print("%5d  %s" % (i + 1, lines[i].rstrip()))

print("")
print("=" * 78)
print("EVERY \"of N shells\" / shell tally in the tree")
print("=" * 78)
rx = re.compile(r'(\d+)\s+of\s+(\d+)\s+shells?|(\d+)\s*/\s*(\d+)\s+shells?', re.I)
seen = Counter()
hits = []
for dp, dns, fns in os.walk(ROOT):
    if SKIP.search(dp):
        dns[:] = []
        continue
    for fn in fns:
        if os.path.splitext(fn)[1].lower() not in (".py", ".gd", ".md", ".txt"):
            continue
        p = os.path.join(dp, fn)
        try:
            if os.path.getsize(p) > 3_000_000:
                continue
            with open(p, "r", encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except Exception:
            continue
        for m in rx.finditer(text):
            line = text[: m.start()].count("\n") + 1
            frag = text[max(0, m.start() - 90): m.end() + 90].replace("\n", " ")
            hits.append((rel(p), line, m.group(0), frag.strip()[:170]))
            seen[m.group(0)] += 1
for f, l, g, frag in hits[:26]:
    print("  %s:%d   %r" % (f, l, g))
    print("        ...%s..." % frag)
print("")
print("distinct tallies: %s" % ", ".join("%s(x%d)" % (k, v) for k, v in seen.most_common()))
