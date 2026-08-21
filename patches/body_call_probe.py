#!/usr/bin/env python3
"""body_call_probe.py -- which recipes never pass plan["material"] to a material?

READS ONLY.

The rule: a make_material call is a BODY call if plan["material"] appears in an
argument OTHER than the first. The first argument is the material's NAME, and
f"M_Bottle_{plan['material']}" interpolates the kind into a name without the
material ever depending on it -- which is exactly how the earlier, weaker rule
produced six false positives.

A recipe with make_material calls and no body call cannot respond to its genome.
"""
import ast
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RECIPES = os.path.join(ROOT, "zoo", "zoo_keeper", "recipes")
SPECIES = os.path.join(ROOT, "zoo", "zoo_keeper", "genome", "species")

import json  # noqa: E402


def has_material_ref(node):
    for sub in ast.walk(node):
        if isinstance(sub, ast.Subscript) and isinstance(sub.slice, ast.Constant) \
                and sub.slice.value == "material":
            return True
        if isinstance(sub, ast.Call):
            fn = sub.func
            if getattr(fn, "attr", None) == "get" and sub.args \
                    and isinstance(sub.args[0], ast.Constant) \
                    and sub.args[0].value == "material":
                return True
    return False


genomes = {}
for fn in sorted(os.listdir(SPECIES)):
    if not fn.endswith(".json"):
        continue
    with open(os.path.join(SPECIES, fn), "r", encoding="utf-8") as fh:
        d = json.load(fh)
    mats = d.get("materials") or {}
    opts = mats.get("options") if isinstance(mats, dict) else None
    genomes[d.get("species") or fn[:-5]] = {
        "options": sorted(opts) if isinstance(opts, list) else [],
        "default": mats.get("default") if isinstance(mats, dict) else None,
    }

rows = []
for fn in sorted(os.listdir(RECIPES)):
    if not fn.endswith(".py") or fn.startswith("_"):
        continue
    name = fn[:-3]
    path = os.path.join(RECIPES, fn)
    with open(path, "r", encoding="utf-8") as fh:
        src = fh.read()
    try:
        tree = ast.parse(src, filename=path)
    except Exception as exc:
        print("parse error %s: %s" % (fn, exc))
        continue
    body = subpart = 0
    subpart_kinds = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        if (getattr(f, "id", None) or getattr(f, "attr", None)) != "make_material":
            continue
        rest = list(node.args[1:]) + [k.value for k in node.keywords]
        if any(has_material_ref(a) for a in rest):
            body += 1
        else:
            subpart += 1
            for a in rest:
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    subpart_kinds.append(a.value)
    g = genomes.get(name)
    rows.append({"recipe": name, "body": body, "subpart": subpart,
                 "options": g["options"] if g else None,
                 "default": g["default"] if g else None,
                 "subpart_kinds": sorted(set(subpart_kinds))})

total_calls = sum(r["body"] + r["subpart"] for r in rows)
print("%d recipe modules, %d make_material calls, %d genomes"
      % (len(rows), total_calls, len(genomes)))
if total_calls == 0:
    print("REFUSING TO CONCLUDE -- zero make_material calls found")
    sys.exit(2)
print("")

inert = [r for r in rows if (r["body"] + r["subpart"]) > 0 and r["body"] == 0]
print("=" * 74)
print("INERT -- builds materials, never passes plan[\"material\"] to any of them")
print("=" * 74)
if inert:
    for r in inert:
        print("  %-20s %d sub-part call(s), genome offers %s, default %s"
              % (r["recipe"], r["subpart"],
                 ", ".join(r["options"]) if r["options"] else "(none)",
                 r["default"]))
        print("      sub-part kinds: %s" % ", ".join(r["subpart_kinds"]))
else:
    print("  none")

multi = [r for r in inert if r["options"] and len(r["options"]) > 1]
print("")
print("  of those, genomes offering MORE THAN ONE option (a live wrong answer): %d"
      % len(multi))
for r in multi:
    print("      %s -- %s" % (r["recipe"], ", ".join(r["options"])))

print("")
print("=" * 74)
print("HEALTHY -- body honours the genome; sub-parts correctly fixed")
print("=" * 74)
healthy = [r for r in rows if r["body"] > 0]
print("  %d recipe(s); %d also carry fixed sub-parts"
      % (len(healthy), sum(1 for r in healthy if r["subpart"])))
for r in healthy:
    if r["subpart"]:
        print("      %-20s body=%d sub=%d   %s"
              % (r["recipe"], r["body"], r["subpart"],
                 ", ".join(r["subpart_kinds"])[:52]))

nocalls = [r for r in rows if r["body"] + r["subpart"] == 0]
print("")
print("NO make_material AT ALL: %d  (%s)"
      % (len(nocalls), ", ".join(r["recipe"] for r in nocalls[:12]) or "none"))
