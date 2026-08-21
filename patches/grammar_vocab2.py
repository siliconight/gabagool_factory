#!/usr/bin/env python3
"""grammar_vocab2.py -- the authoring vocabulary, and only that.

READS ONLY. Prints the MaterialGrammar fields, whether an unknown key raises,
and an empirical inventory of every key actually used across the 55 profiles.
"""
import ast
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GRAM = os.path.join(ROOT, "pixelcoat", "pixelcoat", "core", "material_grammar.py")
MATS = os.path.join(ROOT, "pixelcoat", "profiles", "materials")

with open(GRAM, "r", encoding="utf-8") as fh:
    src = fh.read()
tree = ast.parse(src, filename=GRAM)

print("MaterialGrammar FIELDS")
for node in ast.walk(tree):
    if not isinstance(node, ast.ClassDef):
        continue
    rows = []
    for stmt in node.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            rows.append((stmt.target.id,
                         ast.unparse(stmt.annotation),
                         ast.unparse(stmt.value) if stmt.value is not None else ""))
    if rows:
        print("  class %s -- %d field(s)" % (node.name, len(rows)))
        for n, a, d in rows:
            print("      %-18s %-24s %s" % (n, a[:24], d[:40]))
print("")

print("UNKNOWN KEY -- raise or vanish?")
pat = re.compile(r'^.*(unknown|unexpected|raise |\.get\(|__annotations__|'
                 r'dataclasses\.fields|set\(raw|raw\.keys)\b.*$', re.M)
seen = 0
for m in pat.finditer(src):
    line = src[: m.start()].count("\n") + 1
    txt = m.group(0).strip()
    if len(txt) > 4:
        print("  %4d  %s" % (line, txt[:120]))
        seen += 1
    if seen >= 18:
        print("  ... truncated")
        break
print("")

print("GENERATOR NAMES the code dispatches on")
names = set()
for base in (os.path.join(ROOT, "pixelcoat", "pixelcoat"),):
    for dp, dns, fns in os.walk(base):
        if "__pycache__" in dp:
            continue
        for fn in fns:
            if not fn.endswith(".py"):
                continue
            with open(os.path.join(dp, fn), "r", encoding="utf-8") as fh:
                s = fh.read()
            names.update(re.findall(
                r'generator\s*==\s*["\']([a-z0-9_]+)["\']', s))
            names.update(re.findall(
                r'["\']([a-z]+_f[0-9])["\']', s))
print("  %s" % (", ".join(sorted(names)) or "none found by comparison"))
print("")

print("=" * 76)
print("EMPIRICAL KEY INVENTORY across the profiles on disk")
print("=" * 76)
top = Counter()
subs = defaultdict(Counter)
types = {}
gens = Counter()
kinds = defaultdict(list)
n = 0
for fn in sorted(os.listdir(MATS)):
    if not fn.endswith(".json"):
        continue
    with open(os.path.join(MATS, fn), "r", encoding="utf-8") as fh:
        data = json.load(fh)
    n += 1
    kinds[data.get("kind")].append(fn[:-5])
    for k, v in data.items():
        top[k] += 1
        types.setdefault(k, type(v).__name__)
        if isinstance(v, dict):
            for sk, sv in v.items():
                subs[k][sk] += 1
                if sk == "generator" and isinstance(sv, str):
                    gens[sv] += 1

print("  %d profiles read" % n)
print("")
print("  %-18s %5s  %-8s  sub-keys" % ("key", "used", "type"))
print("  " + "-" * 74)
for k, c in top.most_common():
    sk = ", ".join("%s(%d)" % (a, b) for a, b in subs[k].most_common()) if subs[k] else ""
    print("  %-18s %5d  %-8s  %s" % (k, c, types[k], sk[:44]))
print("")
print("  generator values in use: %s"
      % ", ".join("%s(%d)" % (g, c) for g, c in gens.most_common()))
print("")
print("  kinds with only one profile (the ones a theme cannot vary):")
for k in sorted(kinds):
    if k and len(kinds[k]) == 1:
        print("      %-14s %s" % (k, kinds[k][0]))
