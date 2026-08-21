#!/usr/bin/env python3
"""grammar_vocab.py -- what fields a MaterialGrammar actually accepts.

READS ONLY. Writing a grammar with an invented key either crashes the build or
is silently dropped, so this prints the dataclass fields, whether unknown keys
are rejected, and the generator names the code compares against.
"""
import ast
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PC = os.path.join(ROOT, "pixelcoat", "pixelcoat")
MATS = os.path.join(ROOT, "pixelcoat", "profiles", "materials")

target = os.path.join(PC, "core", "material_grammar.py")
if not os.path.isfile(target):
    print("REFUSING -- not found: %s" % target)
    sys.exit(2)


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


with open(target, "r", encoding="utf-8") as fh:
    src = fh.read()
tree = ast.parse(src, filename=target)

print("=" * 78)
print("DATACLASS FIELDS   %s" % rel(target))
print("=" * 78)
for node in ast.walk(tree):
    if not isinstance(node, ast.ClassDef):
        continue
    fields = []
    for stmt in node.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            ann = ast.unparse(stmt.annotation) if hasattr(ast, "unparse") else "?"
            dflt = ast.unparse(stmt.value) if (stmt.value is not None and
                                               hasattr(ast, "unparse")) else ""
            fields.append((stmt.target.id, ann, dflt))
    if fields:
        print("  class %s" % node.name)
        for name, ann, dflt in fields:
            print("      %-20s %-28s %s" % (name, ann, dflt))
        print("")

print("=" * 78)
print("UNKNOWN-KEY HANDLING   does a stray key raise, or vanish?")
print("=" * 78)
for m in re.finditer(r'^.*(unknown|unexpected|KeyError|ValueError|raise |\.pop\(|'
                     r'set\(data\)|data\.keys\(\)|__annotations__|fields\().*$',
                     src, re.M):
    line = src[: m.start()].count("\n") + 1
    print("  %4d  %s" % (line, m.group(0).strip()[:130]))
print("")

print("=" * 78)
print("GENERATOR / PATTERN VOCABULARY   string literals the code compares against")
print("=" * 78)
vocab = {}
for m in re.finditer(r'(generator|albedo_pattern|source_kind|processing_mode)'
                     r'\s*(?:==|!=|in)\s*([^\n:]{0,120})', src):
    vocab.setdefault(m.group(1), set()).add(m.group(2).strip()[:110])
for m in re.finditer(r'["\'](fbm|voronoi|worley|perlin|noise|stripes|checker|'
                     r'plain|flat|grain|weave|speckle|blotch|cells)["\']', src):
    vocab.setdefault("literals seen", set()).add(m.group(1))
if vocab:
    for k in sorted(vocab):
        print("  %s:" % k)
        for v in sorted(vocab[k]):
            print("      %s" % v)
else:
    print("  no comparisons found in this module -- check the renderer instead")
print("")

# where else generators are dispatched
for fn in ("core/render.py", "core/texture.py", "core/generate.py",
           "core/pattern.py", "core/noise.py"):
    p = os.path.join(PC, fn)
    if not os.path.isfile(p):
        continue
    with open(p, "r", encoding="utf-8") as fh:
        s = fh.read()
    hits = sorted(set(re.findall(
        r'(?:generator|pattern|kind)\s*==\s*["\']([a-z_]+)["\']', s)))
    if hits:
        print("  dispatch in %s: %s" % (rel(p), ", ".join(hits)))
print("")

print("=" * 78)
print("REFERENCE GRAMMARS -- the closest analogues for the six new kinds")
print("=" * 78)
for cand in ("plastic_neutral.json", "carpet_delco.json", "wood_delco.json",
             "canvas_delco.json", "leather_delco.json", "pebble_gravel.json",
             "dirt_delco.json"):
    p = os.path.join(MATS, cand)
    if not os.path.isfile(p):
        print("  (%s not present)" % cand)
        continue
    with open(p, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    print("-" * 78)
    print("  %s" % rel(p))
    print("-" * 78)
    for line in json.dumps(data, indent=2, ensure_ascii=False).splitlines():
        print("    " + line)
    print("")
