#!/usr/bin/env python3
"""stair_where.py -- where is stair geometry actually defined?

READS ONLY. stair_system appears in no deli_counter spec, so this looks across
the whole tree: every JSON key matching /stair/, every Python reference to
stair_systems, and the spec files for the three failing shells by name.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKIP = re.compile(r'(^|[\\/])(\.git|__pycache__|_preview[^\\/]*|_probe|_runs'
                  r'|\.venv|venv|site-packages|node_modules)([\\/]|$)')
SHELLS = ("cbp_town_finale", "night_pawn", "primos_pizza")

def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")

def walk_keys(node, out, depth=0):
    if depth > 8:
        return
    if isinstance(node, dict):
        for k, v in node.items():
            if re.search(r'stair', str(k), re.I):
                out[str(k)] += 1
            walk_keys(v, out, depth + 1)
    elif isinstance(node, list):
        for it in node[:200]:
            walk_keys(it, out, depth + 1)

json_keys = Counter()
key_files = defaultdict(set)
sample = {}
scanned = 0
named = defaultdict(list)

for dp, dns, fns in os.walk(ROOT):
    if SKIP.search(dp):
        dns[:] = []
        continue
    for fn in fns:
        if not fn.endswith(".json"):
            continue
        p = os.path.join(dp, fn)
        low = fn.lower()
        for s in SHELLS:
            if low.startswith(s) and "/build/" not in rel(p):
                named[s].append(rel(p))
        try:
            if os.path.getsize(p) > 3_000_000:
                continue
            with open(p, "r", encoding="utf-8") as fh:
                txt = fh.read()
        except Exception:
            continue
        if "stair" not in txt.lower():
            continue
        scanned += 1
        try:
            d = json.loads(txt)
        except Exception:
            continue
        got = Counter()
        walk_keys(d, got)
        for k, n in got.items():
            json_keys[k] += n
            key_files[k].add(rel(p))
            if k not in sample:
                sample[k] = rel(p)

print("JSON files mentioning 'stair': %d" % scanned)
if scanned == 0:
    print("REFUSING TO CONCLUDE -- no JSON anywhere mentions stair")
    sys.exit(2)
print("")
print("JSON KEYS matching /stair/  (occurrences, distinct files)")
for k, n in json_keys.most_common(20):
    print("    %-26s %6d in %3d file(s)   e.g. %s"
          % (k, n, len(key_files[k]), sample[k]))
print("")

print("PYTHON/GD references to stair_systems or a stair list")
hits = 0
for dp, dns, fns in os.walk(ROOT):
    if SKIP.search(dp):
        dns[:] = []
        continue
    for fn in fns:
        if not fn.endswith((".py", ".gd")):
            continue
        p = os.path.join(dp, fn)
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as fh:
                lines = fh.read().splitlines()
        except Exception:
            continue
        for i, l in enumerate(lines, 1):
            if re.search(r'stair_systems|\["stairs"\]|get\(\s*["\']stairs?["\']', l):
                print("    %s:%d  %s" % (rel(p), i, l.strip()[:110]))
                hits += 1
                if hits >= 30:
                    break
        if hits >= 30:
            break
    if hits >= 30:
        break
if hits == 0:
    print("    none")
print("")

print("SPEC FILES for the three failing shells (outside build/)")
for s in SHELLS:
    ps = sorted(set(named[s]))
    print("  %-20s %d file(s)" % (s, len(ps)))
    for p in ps[:8]:
        print("        %s" % p)
