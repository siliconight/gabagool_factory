#!/usr/bin/env python3
"""genome_shadow_probe.py -- which hardcoded material literals make a genome inert.

READS ONLY. Writes patches/_probe/genome_shadow_report.json.

A literal in a recipe is only a defect when it names the kind the GENOME is
supposed to control. simple_car passing 'rubber' for a tire is correct; a recipe
passing its own genome's material as a literal means editing the genome changes
nothing -- the flat_top_grill defect. This probe separates the two by asking, per
literal, whether that kind appears in that species' own genome.
"""
import ast
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPECIES_DIR = os.path.join(ROOT, "zoo", "zoo_keeper", "genome", "species")
RECIPE_DIR = os.path.join(ROOT, "zoo", "zoo_keeper", "recipes")


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def read_text(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


errors = []

if not os.path.isdir(SPECIES_DIR):
    print("REFUSING TO CONCLUDE -- species dir not found: %s" % SPECIES_DIR)
    sys.exit(2)
if not os.path.isdir(RECIPE_DIR):
    print("REFUSING TO CONCLUDE -- recipes dir not found: %s" % RECIPE_DIR)
    sys.exit(2)

# ------------------------------------------------------------- genomes
def deep_materials(node, out):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("material", "materials"):
                if isinstance(v, str):
                    out.add(v)
                elif isinstance(v, list):
                    for it in v:
                        if isinstance(it, str):
                            out.add(it)
            deep_materials(v, out)
    elif isinstance(node, list):
        for it in node:
            deep_materials(it, out)


genomes = {}
for fn in sorted(os.listdir(SPECIES_DIR)):
    if not fn.lower().endswith(".json"):
        continue
    p = os.path.join(SPECIES_DIR, fn)
    try:
        data = load_json(p)
    except Exception as exc:
        errors.append("species %s -- %s: %s" % (fn, type(exc).__name__, exc))
        continue
    name = data.get("species") or fn[:-5]
    mats = data.get("materials")
    options, default = set(), None
    if isinstance(mats, dict):
        raw = mats.get("options")
        if isinstance(raw, list):
            options.update(x for x in raw if isinstance(x, str))
        if isinstance(mats.get("default"), str):
            default = mats["default"]
            options.add(default)
    elif isinstance(mats, list):
        options.update(x for x in mats if isinstance(x, str))
    deep = set()
    deep_materials(data, deep)
    genomes[name] = {
        "file": rel(p),
        "options": sorted(options),
        "default": default,
        "all_referenced": sorted(options | deep),
    }

print("GENOMES  %d read from %s" % (len(genomes), rel(SPECIES_DIR)))
if len(genomes) < 50:
    print("REFUSING TO CONCLUDE -- the sweeping test asserts at least 50")
    sys.exit(2)

# ------------------------------------------------------------- recipes
class Scan(ast.NodeVisitor):
    def __init__(self):
        self.literals = []      # (lineno, value)
        self.material_reads = []  # (lineno, rendered)
        self.make_calls = 0

    def visit_Call(self, node):
        fn = node.func
        name = getattr(fn, "id", None) or getattr(fn, "attr", None)
        if name == "make_material":
            self.make_calls += 1
            for a in list(node.args) + [kw.value for kw in node.keywords]:
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    self.literals.append((node.lineno, a.value))
        self.generic_visit(node)

    def visit_Subscript(self, node):
        sl = node.slice
        if isinstance(sl, ast.Constant) and sl.value == "material":
            base = node.value
            base_name = getattr(base, "id", None) or getattr(base, "attr", None) or "?"
            self.material_reads.append((node.lineno, "%s[\"material\"]" % base_name))
        self.generic_visit(node)


recipes = {}
for fn in sorted(os.listdir(RECIPE_DIR)):
    if not fn.lower().endswith(".py") or fn == "__init__.py":
        continue
    p = os.path.join(RECIPE_DIR, fn)
    try:
        src = read_text(p)
        tree = ast.parse(src, filename=p)
    except Exception as exc:
        errors.append("recipe %s -- %s: %s" % (fn, type(exc).__name__, exc))
        continue
    s = Scan()
    s.visit(tree)
    # also catch plan.get("material") which is not a Subscript
    for m in re.finditer(r'(\w+)\.get\(\s*["\']material["\']', src):
        line = src[: m.start()].count("\n") + 1
        s.material_reads.append((line, "%s.get(\"material\")" % m.group(1)))
    recipes[fn[:-3]] = {
        "file": rel(p),
        "lines": src.splitlines(),
        "literals": s.literals,
        "material_reads": sorted(set(s.material_reads)),
        "make_calls": s.make_calls,
    }

print("RECIPES  %d modules in %s" % (len(recipes), rel(RECIPE_DIR)))
print("")

only_recipe = sorted(set(recipes) - set(genomes))
only_genome = sorted(set(genomes) - set(recipes))
if only_recipe or only_genome:
    print("NAME MISMATCH between recipe modules and species files")
    if only_recipe:
        print("  recipe with no species json: %s" % ", ".join(only_recipe))
    if only_genome:
        print("  species with no recipe module: %s" % ", ".join(only_genome))
    print("")

# --------------------------------------------------------- classify
inert = []
shadow = []
secondary = []

for name in sorted(set(recipes) & set(genomes)):
    r = recipes[name]
    g = genomes[name]
    own = set(g["all_referenced"])

    if r["make_calls"] and not r["material_reads"]:
        inert.append({
            "species": name, "file": r["file"],
            "options": g["options"], "default": g["default"],
            "make_calls": r["make_calls"],
        })

    for lineno, val in r["literals"]:
        src_line = r["lines"][lineno - 1].strip() if lineno - 1 < len(r["lines"]) else ""
        rec = {"species": name, "file": r["file"], "line": lineno,
               "literal": val, "source": src_line[:120],
               "options": g["options"], "default": g["default"],
               "reads_material": bool(r["material_reads"])}
        if val in own:
            shadow.append(rec)
        else:
            secondary.append(rec)

print("=" * 78)
print("A. GENOME INERT -- recipe calls make_material but never reads a material key")
print("   (this is the flat_top_grill defect: editing the genome changes nothing)")
print("=" * 78)
if inert:
    for rec in inert:
        print("  %-20s %s" % (rec["species"], rec["file"]))
        print("      %d make_material call(s), 0 reads of [\"material\"]"
              % rec["make_calls"])
        print("      genome offers: %s   default: %s"
              % (", ".join(rec["options"]) or "(none)", rec["default"]))
else:
    print("  none -- every recipe that builds a material reads one from its plan")

print("")
print("=" * 78)
print("B. SHADOW LITERALS -- literal names a kind THIS species' genome also names")
print("   (suspect: the genome and the literal are both trying to set this)")
print("=" * 78)
if shadow:
    for rec in shadow:
        flag = "" if rec["reads_material"] else "   <-- and never reads material"
        print("  %s:%d  %r%s" % (rec["file"], rec["line"], rec["literal"], flag))
        print("      %s" % rec["source"])
        print("      genome offers: %s   default: %s"
              % (", ".join(rec["options"]) or "(none)", rec["default"]))
else:
    print("  none")

print("")
print("=" * 78)
print("C. SECONDARY-PART LITERALS -- literal names a kind NOT in this genome")
print("   (expected and correct: a glass screen, a rubber tire, a paper wrapper)")
print("=" * 78)
by_species = defaultdict(list)
for rec in secondary:
    by_species[rec["species"]].append(rec)
for name in sorted(by_species):
    vals = ", ".join(sorted(set(r["literal"] for r in by_species[name])))
    print("  %-20s %s" % (name, vals))
print("  (%d literal(s) across %d species)" % (len(secondary), len(by_species)))

print("")
print("SUMMARY   inert recipes %d   shadow literals %d   secondary literals %d"
      % (len(inert), len(shadow), len(secondary)))

if errors:
    print("")
    print("READ ERRORS -- %d" % len(errors))
    for e in errors[:20]:
        print("      %s" % e)

outdir = os.path.join(HERE, "_probe")
os.makedirs(outdir, exist_ok=True)
outpath = os.path.join(outdir, "genome_shadow_report.json")
with open(outpath, "w", encoding="utf-8") as fh:
    json.dump({"genomes": len(genomes), "recipes": len(recipes),
               "only_recipe": only_recipe, "only_genome": only_genome,
               "inert": inert, "shadow": shadow, "secondary": secondary,
               "errors": errors}, fh, indent=2)
print("")
print("wrote %s" % rel(outpath))
