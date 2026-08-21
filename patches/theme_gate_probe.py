#!/usr/bin/env python3
"""theme_gate_probe.py -- does a theme profile decide which materials get built?

READS ONLY. Writes patches/_probe/theme_gate_report.json.

canvas, dirt, leather and rubber have Pixelcoat profiles and zero built packs.
Either the theme profiles gate the build, or the build gates itself. This tells
which, and prints the theme schema so a new material can be wired correctly the
first time instead of landing in the same never-built bucket.
"""
import json
import os
import re
import sys
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PC = os.path.join(ROOT, "pixelcoat")
THEMES = os.path.join(PC, "profiles", "themes")
MATS = os.path.join(PC, "profiles", "materials")
BUILD = os.path.join(PC, "build")

MISSING_KINDS = ["laminate", "paper", "gravel", "carbon", "tar", "vegetation"]
UNBUILT_KINDS = ["canvas", "dirt", "leather", "rubber"]


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


for d in (THEMES, MATS):
    if not os.path.isdir(d):
        print("REFUSING TO CONCLUDE -- missing dir %s" % d)
        sys.exit(2)

# ------------------------------------------------ material profiles by id
profiles = {}          # id or stem -> {kind, stem}
kind_of_id = {}
by_kind = defaultdict(list)
for fn in sorted(os.listdir(MATS)):
    if not fn.lower().endswith(".json"):
        continue
    stem = fn[:-5]
    try:
        data = load(os.path.join(MATS, fn))
    except Exception as exc:
        print("  ! unreadable %s: %s" % (fn, exc))
        continue
    ident = data.get("id") or stem
    kind = data.get("kind")
    profiles[stem] = {"id": ident, "kind": kind}
    kind_of_id[ident] = kind
    kind_of_id[stem] = kind
    if kind:
        by_kind[kind].append(stem)

print("MATERIAL PROFILES  %d files, %d kinds" % (len(profiles), len(by_kind)))
print("")

# ------------------------------------------------------- theme profiles
theme_keys = Counter()
themes = {}
for fn in sorted(os.listdir(THEMES)):
    if not fn.lower().endswith(".json"):
        continue
    name = fn[:-5]
    try:
        data = load(os.path.join(THEMES, fn))
    except Exception as exc:
        print("  ! unreadable theme %s: %s" % (fn, exc))
        continue
    theme_keys.update(data.keys())
    # find every profile reference anywhere in the theme, whatever the shape
    refs = set()

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(v, str) and (v in profiles or v in kind_of_id):
                    refs.add(v)
                walk(v)
        elif isinstance(node, list):
            for it in node:
                if isinstance(it, str) and (it in profiles or it in kind_of_id):
                    refs.add(it)
                walk(it)

    walk(data)
    themes[name] = {"file": rel(os.path.join(THEMES, fn)),
                    "keys": sorted(data.keys()), "refs": sorted(refs),
                    "kinds": sorted(set(filter(None,
                                               (kind_of_id.get(r) for r in refs))))}

print("THEME PROFILE SHAPE")
print("  keys seen across %d themes: %s"
      % (len(themes), ", ".join("%s(%d)" % (k, n) for k, n in theme_keys.most_common(14))))
print("")
print("  %-16s %6s %6s   kinds referenced" % ("theme", "refs", "kinds"))
print("  " + "-" * 92)
for name in sorted(themes):
    t = themes[name]
    print("  %-16s %6d %6d   %s"
          % (name, len(t["refs"]), len(t["kinds"]), ", ".join(t["kinds"])[:60]))
print("")

# ------------------------------------------------------ built libraries
libs = {}
if os.path.isdir(BUILD):
    for lib in sorted(os.listdir(BUILD)):
        d = os.path.join(BUILD, lib)
        if not os.path.isdir(d):
            continue
        kinds = set()
        packdirs = []
        for sub in sorted(os.listdir(d)):
            sd = os.path.join(d, sub)
            if not os.path.isdir(sd):
                continue
            manifests = [f for f in os.listdir(sd) if f.endswith(".pack.json")]
            if not manifests:
                continue
            packdirs.append(sub)
            try:
                pdata = load(os.path.join(sd, sorted(manifests)[0]))
            except Exception:
                pdata = {}
            k = pdata.get("kind")
            if k:
                kinds.add(k)
        libs[lib] = {"packdirs": packdirs, "kinds": sorted(kinds)}

print("BUILT LIBRARIES  under %s" % rel(BUILD))
print("  %-24s %6s   kinds built" % ("library", "packs"))
print("  " + "-" * 92)
for lib in sorted(libs):
    print("  %-24s %6d   %s"
          % (lib, len(libs[lib]["packdirs"]), ", ".join(libs[lib]["kinds"])[:56]))
print("")

# ------------------------------------------------------------ the gate
print("=" * 78)
print("IS THE THEME THE GATE?  listed-by-theme vs actually-built, per library")
print("=" * 78)
gate_evidence = []
for lib in sorted(libs):
    theme = lib[len("skins_"):] if lib.startswith("skins_") else lib
    t = themes.get(theme)
    if t is None:
        print("  %-24s no theme profile named %r" % (lib, theme))
        continue
    listed = set(t["kinds"])
    built = set(libs[lib]["kinds"])
    only_listed = sorted(listed - built)
    only_built = sorted(built - listed)
    verdict = ("EXACT MATCH -- the theme decides the build" if not only_listed
               and not only_built else "MISMATCH")
    print("  %-24s %s" % (lib, verdict))
    if only_listed:
        print("      listed by theme but NOT built: %s" % ", ".join(only_listed))
    if only_built:
        print("      built but NOT listed by theme: %s" % ", ".join(only_built))
    gate_evidence.append({"library": lib, "theme": theme,
                          "only_listed": only_listed, "only_built": only_built})
print("")

# -------------------------------------------------- the two open buckets
all_listed = set()
for t in themes.values():
    all_listed |= set(t["kinds"])

print("THE FOUR NEVER-BUILT KINDS -- is a theme listing them?")
for k in UNBUILT_KINDS:
    where = sorted(n for n, t in themes.items() if k in t["kinds"])
    print("  %-12s profiles: %-28s listed by theme(s): %s"
          % (k, ", ".join(by_kind.get(k, [])) or "(none)",
             ", ".join(where) or "NONE"))
print("")

print("THE SIX MISSING KINDS -- confirming no profile and no listing")
for k in MISSING_KINDS:
    where = sorted(n for n, t in themes.items() if k in t["kinds"])
    print("  %-12s profiles: %-28s listed by theme(s): %s"
          % (k, ", ".join(by_kind.get(k, [])) or "(none)",
             ", ".join(where) or "NONE"))
print("")

never_listed = sorted(k for k in by_kind if k not in all_listed)
print("KINDS WITH A PROFILE THAT NO THEME LISTS: %s"
      % (", ".join(never_listed) or "none"))

outdir = os.path.join(HERE, "_probe")
os.makedirs(outdir, exist_ok=True)
outpath = os.path.join(outdir, "theme_gate_report.json")
with open(outpath, "w", encoding="utf-8") as fh:
    json.dump({"profiles": profiles, "themes": themes, "libraries": libs,
               "gate_evidence": gate_evidence, "never_listed": never_listed},
              fh, indent=2)
print("")
print("wrote %s" % rel(outpath))
