#!/usr/bin/env python3
"""schema_dump.py -- print the three schemas thread 3 needs, verbatim.

READS ONLY. Prints nothing it did not read from a file, and names every file.

1. a full theme profile        -- so a new material can be listed correctly
2. a full material grammar     -- the template for the six missing kinds
3. a pack manifest             -- what the build actually emits
4. theme materials vs pack dirs, per library, compared by NAME not by a
   "kind" key, because the pack manifests do not carry one
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PC = os.path.join(ROOT, "pixelcoat")
THEMES = os.path.join(PC, "profiles", "themes")
MATS = os.path.join(PC, "profiles", "materials")
BUILD = os.path.join(PC, "build")


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def load(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def dump(label, path, data, limit=90):
    print("=" * 78)
    print("%s   %s" % (label, rel(path)))
    print("=" * 78)
    text = json.dumps(data, indent=2, ensure_ascii=False)
    lines = text.splitlines()
    for line in lines[:limit]:
        print("  " + line)
    if len(lines) > limit:
        print("  ... %d more line(s)" % (len(lines) - limit))
    print("")


# 1. a theme profile -- street is the smallest at 13
for cand in ("street.json", "rockay.json"):
    p = os.path.join(THEMES, cand)
    if os.path.isfile(p):
        dump("THEME PROFILE", p, load(p))
        break
else:
    print("no theme profile found in %s" % rel(THEMES))
    sys.exit(2)

# 2. a material grammar -- plastic_neutral is one of the tintable ones we added
tmpl = None
for cand in ("plastic_neutral.json", "metal_painted_neutral.json"):
    p = os.path.join(MATS, cand)
    if os.path.isfile(p):
        tmpl = p
        break
if tmpl is None:
    names = sorted(f for f in os.listdir(MATS) if f.endswith(".json"))
    tmpl = os.path.join(MATS, names[0])
dump("MATERIAL GRAMMAR (template for the six missing kinds)", tmpl, load(tmpl))

# 2b. a non-tintable one for contrast
for cand in ("concrete_street.json", "brick_buff_civic.json", "wood_delco.json"):
    p = os.path.join(MATS, cand)
    if os.path.isfile(p):
        dump("MATERIAL GRAMMAR (second example)", p, load(p))
        break

# 3. a pack manifest
found = None
if os.path.isdir(BUILD):
    for lib in sorted(os.listdir(BUILD)):
        d = os.path.join(BUILD, lib)
        if not os.path.isdir(d):
            continue
        for sub in sorted(os.listdir(d)):
            sd = os.path.join(d, sub)
            if not os.path.isdir(sd):
                continue
            man = sorted(f for f in os.listdir(sd) if f.endswith(".pack.json"))
            if man:
                found = os.path.join(sd, man[0])
                break
        if found:
            break
if found:
    dump("PACK MANIFEST (what the build emits)", found, load(found), limit=40)
    print("  sibling files in that pack dir: %s"
          % ", ".join(sorted(os.listdir(os.path.dirname(found)))))
    print("")
else:
    print("no pack manifest found under %s" % rel(BUILD))
    print("")

# 4. the gate, compared by name
print("=" * 78)
print("THEME MATERIALS vs PACK DIRECTORIES, per library")
print("=" * 78)
themes = {}
for fn in sorted(os.listdir(THEMES)):
    if fn.endswith(".json"):
        themes[fn[:-5]] = load(os.path.join(THEMES, fn))

for lib in sorted(os.listdir(BUILD)) if os.path.isdir(BUILD) else []:
    d = os.path.join(BUILD, lib)
    if not os.path.isdir(d):
        continue
    theme = lib[len("skins_"):] if lib.startswith("skins_") else lib
    t = themes.get(theme)
    packdirs = sorted(s for s in os.listdir(d)
                      if os.path.isdir(os.path.join(d, s)))
    print("  %s   theme=%s" % (lib, theme))
    print("      pack dirs (%d): %s" % (len(packdirs), ", ".join(packdirs)))
    if t is None:
        print("      NO THEME PROFILE OF THAT NAME")
        print("")
        continue
    mats = t.get("materials")
    if isinstance(mats, dict):
        entries = sorted("%s=%s" % (k, v) for k, v in mats.items())
    elif isinstance(mats, list):
        entries = [str(x) for x in mats]
    else:
        entries = []
    print("      theme materials (%d): %s" % (len(entries), ", ".join(entries)))
    print("")

print("MATERIAL PROFILES ON DISK, grouped by kind")
by_kind = {}
for fn in sorted(os.listdir(MATS)):
    if not fn.endswith(".json"):
        continue
    data = load(os.path.join(MATS, fn))
    by_kind.setdefault(data.get("kind") or "(no kind)", []).append(fn[:-5])
for kind in sorted(by_kind):
    print("  %-14s %s" % (kind, ", ".join(by_kind[kind])))
