#!/usr/bin/env python3
"""kind_map_probe.py v4 -- measure which material kinds are reachable end to end.

READS ONLY. Writes patches/_probe/kind_map_report.json.

Genome location is no longer guessed: zoo/tests/test_material_options_closed.py
names it as zoo_keeper/genome/species/*.json, and the material fields are
genome["materials"]["options"] and ["default"]. v1 guessed a genomes/ dir, v2
required a top-level styles list, v3 looked inside the recipe modules -- all
three found nothing, and all three said so instead of printing a table.
"""
import ast
import json
import os
import re
import sys
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SKIP = re.compile(
    r'(^|[\\/])(\.git|__pycache__|node_modules|\.venv|venv|site-packages'
    r'|\.mypy_cache|\.pytest_cache|\.tox|\.idea|\.vs)([\\/]|$)'
)
AUTHORITATIVE_PACK = re.compile(r'^pixelcoat/build/')
SPECIES_TAIL = os.path.join("zoo_keeper", "genome", "species")


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh), None
    except Exception as exc:
        return None, "%s: %s" % (type(exc).__name__, exc)


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read(), None
    except Exception as exc:
        return None, "%s: %s" % (type(exc).__name__, exc)


material_profiles = []
theme_profiles = []
packs = []
species_files = []
skins_py = []
materials_py = []
recipe_py = []
errors = []

for dp, dns, fns in os.walk(ROOT):
    if SKIP.search(dp):
        dns[:] = []
        continue
    posix = dp.replace("\\", "/")
    in_species = dp.endswith(SPECIES_TAIL)
    for fn in fns:
        full = os.path.join(dp, fn)
        low = fn.lower()
        if fn == "skins.py" and "/core" in posix:
            skins_py.append(full)
        elif fn == "materials.py" and "/bpylayer" in posix:
            materials_py.append(full)
        elif low.endswith(".py") and "/recipes" in posix:
            recipe_py.append(full)
        elif in_species and low.endswith(".json"):
            species_files.append(full)
        elif low.endswith(".pack.json"):
            packs.append(full)
        elif low.endswith(".json") and "/profiles/materials" in posix:
            material_profiles.append(full)
        elif low.endswith(".json") and "/profiles/themes" in posix:
            theme_profiles.append(full)

for lst in (material_profiles, theme_profiles, packs, species_files,
            skins_py, materials_py, recipe_py):
    lst.sort()

print("SOURCES")
print("  species genomes    %4d   %s" % (
    len(species_files),
    rel(os.path.dirname(species_files[0])) if species_files else "DIR NOT FOUND"))
print("  material profiles  %4d" % len(material_profiles))
print("  theme profiles     %4d" % len(theme_profiles))
print("  pack manifests     %4d" % len(packs))
print("  recipe modules     %4d" % len(recipe_py))
print("")

# =========================================================== genomes
species_keys = Counter()
material_block_keys = Counter()
genome_kinds = defaultdict(list)      # kind -> species names (options)
genome_defaults = defaultdict(list)   # kind -> species names (default only)
genome_names = []
genomes_no_materials = []


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


for p in species_files:
    data, err = load_json(p)
    if err or not isinstance(data, dict):
        errors.append("species %s -- %s" % (rel(p), err or "not an object"))
        continue
    name = data.get("species") or os.path.basename(p)[:-5]
    genome_names.append(name)
    species_keys.update(data.keys())

    mats = data.get("materials")
    opts = set()
    default = None
    if isinstance(mats, dict):
        material_block_keys.update(mats.keys())
        raw = mats.get("options")
        if isinstance(raw, list):
            opts.update(x for x in raw if isinstance(x, str))
        if isinstance(mats.get("default"), str):
            default = mats["default"]
    elif isinstance(mats, list):
        opts.update(x for x in mats if isinstance(x, str))
    else:
        genomes_no_materials.append(name)

    deep = set()
    deep_materials(data, deep)
    opts |= deep

    if default:
        opts.add(default)
        genome_defaults[default].append(name)
    for k in opts:
        genome_kinds[k].append(name)

print("GENOME SHAPE")
print("  top-level keys:      %s"
      % ", ".join("%s(%d)" % (k, n) for k, n in species_keys.most_common(14)))
print("  materials block:     %s"
      % (", ".join("%s(%d)" % (k, n) for k, n in material_block_keys.most_common(8))
         or "no dict-shaped materials block seen"))
print("  genomes parsed:      %d" % len(genome_names))
if genomes_no_materials:
    print("  genomes with NO materials block: %s"
          % ", ".join(sorted(genomes_no_materials)))
print("")

# ========================================================== profiles
theme_names = sorted(os.path.basename(p)[:-5] for p in theme_profiles)

profile_kinds = defaultdict(list)
profile_themes = defaultdict(set)
profile_no_kind = []
profile_rows = []
for p in material_profiles:
    stem = os.path.basename(p)[:-5]
    data, err = load_json(p)
    if err or not isinstance(data, dict):
        errors.append("profile %s -- %s" % (rel(p), err or "not an object"))
        continue
    kind = data.get("kind")
    if not isinstance(kind, str) or not kind:
        profile_no_kind.append(stem)
        continue
    theme = stem[len(kind) + 1:] if stem.startswith(kind + "_") else "?"
    profile_kinds[kind].append(rel(p))
    profile_themes[kind].add(theme)
    profile_rows.append({"file": rel(p), "id": data.get("id"), "kind": kind,
                         "theme": theme, "tintable": bool(data.get("tintable"))})

# ============================================================= packs
pack_kinds = defaultdict(list)
pack_themes = defaultdict(set)
pack_copies = defaultdict(list)
libraries = set()
for p in packs:
    r = rel(p)
    parent = os.path.basename(os.path.dirname(p))
    lib = os.path.basename(os.path.dirname(os.path.dirname(p)))
    data, err = load_json(p)
    if err:
        errors.append("pack %s -- %s" % (r, err))
        data = {}
    kind = None
    if isinstance(data, dict):
        for key in ("kind", "material", "material_kind"):
            if isinstance(data.get(key), str) and data[key]:
                kind = data[key]
                break
    if kind is None:
        kind = parent
        for th in sorted(theme_names, key=len, reverse=True):
            if parent.endswith("_" + th):
                kind = parent[: -(len(th) + 1)]
                break
    if AUTHORITATIVE_PACK.match(r):
        pack_kinds[kind].append(r)
        libraries.add(lib)
        theme = lib[len("skins_"):] if lib.startswith("skins_") else lib
        pack_themes[kind].add(theme)
    else:
        pack_copies[kind].append(r)

built_themes = sorted(l[len("skins_"):] if l.startswith("skins_") else l
                      for l in libraries)

# ================================================== module constants
def module_assigns(path, names):
    out = {}
    src, err = read_text(path)
    if err:
        errors.append("read %s -- %s" % (rel(path), err))
        return out
    try:
        tree = ast.parse(src, filename=path)
    except Exception as exc:
        errors.append("parse %s -- %s: %s" % (rel(path), type(exc).__name__, exc))
        return out
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id in names:
                val = node.value
                if (isinstance(val, ast.Call)
                        and isinstance(val.func, ast.Name)
                        and val.func.id in ("set", "frozenset", "tuple", "list")):
                    val = val.args[0] if val.args else None
                if val is None:
                    continue
                try:
                    out[t.id] = ast.literal_eval(val)
                except Exception:
                    pass
    return out


known_kinds = None
for p in skins_py:
    got = module_assigns(p, {"KNOWN_KINDS"})
    if "KNOWN_KINDS" in got:
        known_kinds = set(got["KNOWN_KINDS"])
        break

roughness = metallic = None
rough_default = metal_default = None
for p in materials_py:
    got = module_assigns(p, {"ROUGHNESS", "METALLIC"})
    if "ROUGHNESS" in got:
        roughness = dict(got["ROUGHNESS"])
    if "METALLIC" in got:
        metallic = dict(got["METALLIC"])
    src, _ = read_text(p)
    src = src or ""
    m = re.search(r'ROUGHNESS\.get\([^,]+,\s*([0-9.]+)\)', src)
    if m:
        rough_default = m.group(1)
    m = re.search(r'METALLIC\.get\([^,]+,\s*([0-9.]+)\)', src)
    if m:
        metal_default = m.group(1)

# =================================================== recipe literals
class MakeMaterialVisitor(ast.NodeVisitor):
    def __init__(self):
        self.hits = []

    def visit_Call(self, node):
        fn = node.func
        name = getattr(fn, "id", None) or getattr(fn, "attr", None)
        if name == "make_material":
            for a in list(node.args) + [kw.value for kw in node.keywords]:
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    self.hits.append((node.lineno, a.value))
        self.generic_visit(node)


recipe_literals = []
for p in recipe_py:
    src, err = read_text(p)
    if err:
        continue
    try:
        tree = ast.parse(src, filename=p)
    except Exception:
        continue
    v = MakeMaterialVisitor()
    v.visit(tree)
    for lineno, val in v.hits:
        recipe_literals.append((rel(p), lineno, val))

# ============================================================ vacuity
print("SOURCE HEALTH")
print("  themes with a profile   %s" % ", ".join(theme_names))
print("  themes actually BUILT   %s" % ", ".join(built_themes))
missing_libs = [t for t in theme_names if t not in built_themes]
if missing_libs:
    print("  themes NEVER BUILT      %s" % ", ".join(missing_libs))
print("  profiles with a kind    %d of %d, %d distinct kinds"
      % (len(profile_rows), len(material_profiles), len(profile_kinds)))
if profile_no_kind:
    print("  profiles with NO kind   %s" % ", ".join(profile_no_kind))
print("  packs in pixelcoat/build %d   elsewhere (job outputs) %d"
      % (sum(len(v) for v in pack_kinds.values()),
         sum(len(v) for v in pack_copies.values())))
print("  KNOWN_KINDS  %s" % ("%d" % len(known_kinds) if known_kinds is not None else "NOT FOUND"))
print("  ROUGHNESS    %s" % ("%d entries, default %s" % (len(roughness), rough_default)
                             if roughness is not None else "NOT FOUND"))
print("  METALLIC     %s" % ("%d entries, default %s" % (len(metallic), metal_default)
                             if metallic is not None else "NOT FOUND"))
print("")

fatal = []
if len(genome_names) < 50:
    fatal.append("only %d genomes read -- the test asserts at least 50"
                 % len(genome_names))
if not profile_rows:
    fatal.append("ZERO material profiles carried a usable kind field")
if fatal:
    print("REFUSING TO CONCLUDE")
    for f in fatal:
        print("  %s" % f)
    print("  root was %s" % ROOT)
    sys.exit(2)

# ============================================================= matrix
universe = set(genome_kinds) | set(profile_kinds) | set(pack_kinds) | set(pack_copies)
if known_kinds is not None:
    universe |= known_kinds
if roughness is not None:
    universe |= set(roughness)
if metallic is not None:
    universe |= set(metallic)


def mark(flag, disabled=False):
    return " ? " if disabled else (" x " if flag else " . ")


rows = []
for kind in sorted(universe):
    g = len(set(genome_kinds.get(kind, [])))
    p = len(profile_kinds.get(kind, []))
    b = len(pack_kinds.get(kind, []))
    k = known_kinds is not None and kind in known_kinds
    r = roughness is not None and kind in roughness
    m = metallic is not None and kind in metallic

    if g and p == 0:
        verdict = "NO PROFILE"
    elif g and p and b == 0:
        verdict = "PROFILE NEVER BUILT"
    elif g and known_kinds is not None and not k:
        verdict = "NOT IN KNOWN_KINDS"
    elif g == 0 and (p or b):
        verdict = "DEAD -- profile exists, no genome refers to it"
    elif g == 0:
        verdict = "DEAD -- lookup entry only"
    elif not r or not m:
        verdict = "REACHABLE (default r/m)"
    else:
        verdict = "REACHABLE"

    rows.append({
        "kind": kind, "genomes": g, "profiles": p, "packs": b,
        "known": bool(k),
        "roughness": roughness.get(kind) if roughness else None,
        "metallic": metallic.get(kind) if metallic else None,
        "verdict": verdict,
        "genome_names": sorted(set(genome_kinds.get(kind, []))),
        "default_for": sorted(set(genome_defaults.get(kind, []))),
        "profile_themes": sorted(profile_themes.get(kind, [])),
        "pack_themes": sorted(pack_themes.get(kind, [])),
    })

print("KIND MATRIX   G=genomes referencing  P=profiles  B=packs in pixelcoat/build")
print("              K=in KNOWN_KINDS  R=ROUGHNESS entry  M=METALLIC entry")
print("")
print("  %-20s %4s %4s %4s  %s %s %s   %s"
      % ("kind", "G", "P", "B", "K", "R", "M", "verdict"))
print("  " + "-" * 98)
for row in rows:
    print("  %-20s %4d %4d %4d  %s%s%s   %s" % (
        row["kind"], row["genomes"], row["profiles"], row["packs"],
        mark(row["known"], known_kinds is None),
        mark(row["roughness"] is not None, roughness is None),
        mark(row["metallic"] is not None, metallic is None),
        row["verdict"]))

print("")
print("BY VERDICT")
buckets = defaultdict(list)
for row in rows:
    buckets[row["verdict"]].append(row)
for verdict in sorted(buckets):
    group = buckets[verdict]
    print("  %s -- %d kind(s)" % (verdict, len(group)))
    for row in group:
        names = ", ".join(row["genome_names"][:6])
        if len(row["genome_names"]) > 6:
            names += ", +%d more" % (len(row["genome_names"]) - 6)
        print("      %-20s %s" % (row["kind"], names or "(no genome)"))

print("")
print("THEME COVERAGE   P=profile exists   B=pack built   *=both   .=neither")
print("")
hdr = "".join("%-6s" % t[:5] for t in theme_names)
print("  %-20s %s" % ("kind", hdr))
print("  " + "-" * (20 + len(hdr)))
for row in rows:
    if not (row["profiles"] or row["packs"]):
        continue
    cells = ""
    for t in theme_names:
        has_p = t in row["profile_themes"]
        has_b = t in row["pack_themes"]
        cells += "%-6s" % ("*" if (has_p and has_b) else
                           "P" if has_p else "B" if has_b else ".")
    print("  %-20s %s" % (row["kind"], cells))

interesting = [t for t in recipe_literals if t[2] in universe]
print("")
print("RECIPE LITERALS passed to make_material that name a known kind")
print("  (the flat_top_grill defect shape -- a literal here outranks the genome)")
if interesting:
    for path, lineno, val in interesting:
        print("      %s:%d  %r" % (path, lineno, val))
else:
    print("      none")

if errors:
    print("")
    print("READ ERRORS -- %d" % len(errors))
    for e in errors[:40]:
        print("      %s" % e)

outdir = os.path.join(HERE, "_probe")
os.makedirs(outdir, exist_ok=True)
outpath = os.path.join(outdir, "kind_map_report.json")
with open(outpath, "w", encoding="utf-8") as fh:
    json.dump({
        "root": ROOT,
        "counts": {
            "genomes": len(genome_names),
            "material_profiles": len(material_profiles),
            "profiles_with_kind": len(profile_rows),
            "theme_profiles": len(theme_profiles),
            "packs_authoritative": sum(len(v) for v in pack_kinds.values()),
            "packs_elsewhere": sum(len(v) for v in pack_copies.values()),
        },
        "themes_with_profile": theme_names,
        "themes_built": built_themes,
        "themes_never_built": missing_libs,
        "species_keys": dict(species_keys),
        "materials_block_keys": dict(material_block_keys),
        "profiles": profile_rows,
        "genome_names": sorted(set(genome_names)),
        "rows": rows,
        "recipe_literals": [
            {"file": f, "line": l, "value": v} for f, l, v in recipe_literals
        ],
        "errors": errors,
    }, fh, indent=2)
print("")
print("wrote %s" % rel(outpath))
