#!/usr/bin/env python3
"""patch_kinds10.py -- make ten material kinds reachable end to end.

Creates five Pixelcoat grammars, retags pebble_gravel from kind "dirt" to its
actual subject "gravel", and lists ten kinds in all nine theme profiles so the
build emits packs for them.

  --check     preconditions only, writes nothing
  (no flag)   apply, all or nothing
  --revert    restore from .pre_kinds10 sidecars and delete created files
  --selftest  verify the applied state AND falsify the verifier

No pre_sha is embedded: this payload was authored without read access to the
target files. Every target instead carries a semantic precondition and a
byte-exact format round-trip check, so drift refuses instead of reformatting.
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MATS = os.path.join(ROOT, "pixelcoat", "profiles", "materials")
THEMES = os.path.join(ROOT, "pixelcoat", "profiles", "themes")
SIDE = ".pre_kinds10"

MODE = "apply"
for a in sys.argv[1:]:
    if a in ("--check", "--revert", "--selftest"):
        MODE = a[2:]
    else:
        print("unknown argument %r" % a)
        sys.exit(2)

# ------------------------------------------------------------ payloads
NEW_PROFILES = {
    "laminate_neutral.json": {
        "id": "laminate_neutral",
        "kind": "laminate",
        "base_colors": ["#d8d8d4", "#cfcfca", "#e0e0dc"],
        "meters_per_tile": 1.2,
        "bands": {"macro": 0.12, "meso": 0.18, "micro": 0.3},
        "macro": {"generator": "fbm", "cells": 3, "octaves": 2},
        "meso": {"generator": "fbm", "cells": 46, "octaves": 2},
        "micro": {"generator": "fbm", "cells": 170, "octaves": 2},
        "albedo_pattern": 0.45,
        "detail_strength": 0.07,
        "posterize": 16,
        "roughness": {"base": 0.34, "variation": 0.05},
        "height_strength": 0.12,
        "emit": {"roughness": True, "normal": False},
        "tintable": True,
    },
    "paper_neutral.json": {
        "id": "paper_neutral",
        "kind": "paper",
        "base_colors": ["#eceae4", "#e4e1d9", "#f2f0ea"],
        "meters_per_tile": 0.6,
        "bands": {"macro": 0.1, "meso": 0.16, "micro": 0.34},
        "macro": {"generator": "fbm", "cells": 4, "octaves": 2},
        "meso": {"generator": "fbm", "cells": 60, "octaves": 2},
        "micro": {"generator": "fbm", "cells": 210, "octaves": 2},
        "albedo_pattern": 0.35,
        "detail_strength": 0.06,
        "posterize": 14,
        "roughness": {"base": 0.86, "variation": 0.04},
        "height_strength": 0.08,
        "emit": {"roughness": True, "normal": False},
        "tintable": True,
    },
    "carbon_neutral.json": {
        "id": "carbon_neutral",
        "kind": "carbon",
        "base_colors": ["#2b2d31", "#232529", "#34373c"],
        "meters_per_tile": 0.5,
        "bands": {"macro": 0.1, "meso": 0.3, "micro": 0.28},
        "macro": {"generator": "fbm", "cells": 4, "octaves": 2},
        "meso": {"generator": "worley_f1", "cells": 44},
        "micro": {"generator": "fbm", "cells": 190, "octaves": 2},
        "albedo_pattern": 0.6,
        "detail_strength": 0.1,
        "posterize": 12,
        "roughness": {"base": 0.32, "variation": 0.06},
        "height_strength": 0.18,
        "emit": {"roughness": True, "normal": False},
        "tintable": False,
    },
    "tar_neutral.json": {
        "id": "tar_neutral",
        "kind": "tar",
        "base_colors": ["#2e2c2a", "#26241f", "#38352f"],
        "undercoat": "#1c1a17",
        "meters_per_tile": 2.0,
        "bands": {"macro": 0.3, "meso": 0.28, "micro": 0.3},
        "macro": {"generator": "fbm", "cells": 3, "octaves": 3},
        "meso": {"generator": "worley_f1", "cells": 22},
        "micro": {"generator": "fbm", "cells": 200, "octaves": 2},
        "chips": {"cells": 30, "amount": 0.08},
        "albedo_pattern": 0.7,
        "detail_strength": 0.18,
        "posterize": 12,
        "roughness": {"base": 0.72, "variation": 0.1},
        "height_strength": 0.3,
        "emit": {"roughness": True, "normal": False},
        "tintable": False,
    },
    "vegetation_neutral.json": {
        "id": "vegetation_neutral",
        "kind": "vegetation",
        "base_colors": ["#4d6b33", "#3f5a2b", "#5d7d3d", "#6b8a45"],
        "undercoat": "#33421f",
        "meters_per_tile": 1.0,
        "bands": {"macro": 0.3, "meso": 0.34, "micro": 0.24},
        "macro": {"generator": "fbm", "cells": 4, "octaves": 3},
        "meso": {"generator": "worley_f1", "cells": 30},
        "micro": {"generator": "fbm", "cells": 160, "octaves": 2},
        "albedo_pattern": 0.85,
        "detail_strength": 0.2,
        "posterize": 14,
        "roughness": {"base": 0.8, "variation": 0.08},
        "height_strength": 0.35,
        "emit": {"roughness": True, "normal": False},
        "tintable": False,
    },
}

THEME_ADDITIONS = {
    "canvas": "canvas_delco",
    "carbon": "carbon_neutral",
    "dirt": "dirt_delco",
    "gravel": "pebble_gravel",
    "laminate": "laminate_neutral",
    "leather": "leather_delco",
    "paper": "paper_neutral",
    "rubber": "rubber_delco",
    "tar": "tar_neutral",
    "vegetation": "vegetation_neutral",
}

RETAG_FILE = "pebble_gravel.json"
RETAG_FROM, RETAG_TO = "dirt", "gravel"

FORMATS = [(2, False), (2, True), (4, False), (4, True), (1, False), (1, True)]


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def read_file(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    eol = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8").replace("\r\n", "\n")
    return raw, text, eol


def detect_format(text, data):
    for indent, ea in FORMATS:
        body = json.dumps(data, indent=indent, ensure_ascii=ea)
        for suffix in ("\n", ""):
            if body + suffix == text:
                return (indent, ea, suffix)
    return None


def render(data, fmt, eol):
    indent, ea, suffix = fmt
    body = json.dumps(data, indent=indent, ensure_ascii=ea) + suffix
    return body.replace("\n", eol).encode("utf-8")


def purge_bytecode():
    n = 0
    for base in (os.path.join(ROOT, "pixelcoat"), os.path.join(ROOT, "zoo")):
        for dp, dns, fns in os.walk(base):
            if os.path.basename(dp) == "__pycache__":
                shutil.rmtree(dp, ignore_errors=True)
                dns[:] = []
                n += 1
    return n


# ------------------------------------------------------------- revert
if MODE == "revert":
    restored = removed = 0
    for d in (MATS, THEMES):
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(SIDE):
                continue
            side = os.path.join(d, fn)
            target = side[: -len(SIDE)]
            with open(side, "rb") as fh:
                raw = fh.read()
            with open(target, "wb") as fh:
                fh.write(raw)
            os.remove(side)
            print("  restored %s" % rel(target))
            restored += 1
    for fn in NEW_PROFILES:
        p = os.path.join(MATS, fn)
        if os.path.isfile(p):
            os.remove(p)
            print("  removed  %s" % rel(p))
            removed += 1
    print("REVERTED -- %d restored, %d created files removed" % (restored, removed))
    purge_bytecode()
    sys.exit(0)


# ----------------------------------------------------------- validate
def validate(theme_data_by_name, profile_ids):
    """Return a list of problems. Empty list means the wiring is complete."""
    problems = []
    for kind, profile in sorted(THEME_ADDITIONS.items()):
        if profile not in profile_ids:
            problems.append("profile %r referenced for kind %r does not exist"
                            % (profile, kind))
    for name in sorted(theme_data_by_name):
        mats = theme_data_by_name[name].get("materials")
        if not isinstance(mats, dict):
            problems.append("theme %s has no materials dict" % name)
            continue
        for kind, profile in sorted(THEME_ADDITIONS.items()):
            if kind not in mats:
                problems.append("theme %s does not list kind %r" % (name, kind))
            elif mats[kind] != profile:
                problems.append("theme %s maps %r to %r, expected %r"
                                % (name, kind, mats[kind], profile))
    return problems


def load_themes():
    out = {}
    for fn in sorted(os.listdir(THEMES)):
        if fn.endswith(".json"):
            with open(os.path.join(THEMES, fn), "r", encoding="utf-8") as fh:
                out[fn[:-5]] = json.load(fh)
    return out


def profile_ids_on_disk():
    ids = set()
    for fn in os.listdir(MATS):
        if fn.endswith(".json"):
            ids.add(fn[:-5])
    return ids


# ----------------------------------------------------------- selftest
if MODE == "selftest":
    themes = load_themes()
    ids = profile_ids_on_disk()
    problems = validate(themes, ids)
    if problems:
        print("SELFTEST FAILED -- the wiring is not complete:")
        for p in problems[:30]:
            print("      %s" % p)
        sys.exit(1)

    # the five new grammars must parse and declare the kind their name claims
    for fn, payload in sorted(NEW_PROFILES.items()):
        p = os.path.join(MATS, fn)
        if not os.path.isfile(p):
            print("SELFTEST FAILED -- missing %s" % rel(p))
            sys.exit(1)
        with open(p, "r", encoding="utf-8") as fh:
            got = json.load(fh)
        if got.get("kind") != payload["kind"]:
            print("SELFTEST FAILED -- %s declares kind %r, expected %r"
                  % (fn, got.get("kind"), payload["kind"]))
            sys.exit(1)

    # the retag must have landed
    with open(os.path.join(MATS, RETAG_FILE), "r", encoding="utf-8") as fh:
        pg = json.load(fh)
    if pg.get("kind") != RETAG_TO:
        print("SELFTEST FAILED -- %s declares kind %r, expected %r"
              % (RETAG_FILE, pg.get("kind"), RETAG_TO))
        sys.exit(1)

    # FALSIFICATION: the verifier must FAIL when the fix is removed.
    import copy
    broken = copy.deepcopy(themes)
    victim = sorted(broken)[0]
    del broken[victim]["materials"]["laminate"]
    if not validate(broken, ids):
        print("SELFTEST FAILED -- the verifier passed a deliberately broken input,")
        print("                   so a green result from it would mean nothing")
        sys.exit(1)
    broken2 = copy.deepcopy(themes)
    broken2[victim]["materials"]["paper"] = "no_such_profile"
    if not validate(broken2, ids):
        print("SELFTEST FAILED -- the verifier accepted a dangling profile reference")
        sys.exit(1)

    print("SELFTEST OK -- %d themes each list all %d kinds, every referenced profile"
          % (len(themes), len(THEME_ADDITIONS)))
    print("               exists on disk, the five new grammars declare their own")
    print("               kinds, pebble_gravel is now %r, and the verifier was" % RETAG_TO)
    print("               shown to FAIL on both a removed entry and a dangling ref")
    sys.exit(0)


# ---------------------------------------------------------- preflight
failures = []
plan = []          # (path, new_bytes, is_new)
already = []

for fn, payload in sorted(NEW_PROFILES.items()):
    p = os.path.join(MATS, fn)
    want = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if os.path.isfile(p):
        _, text, _ = read_file(p)
        if text == want:
            already.append("%s already present and identical" % rel(p))
        else:
            failures.append("%s already exists with different content -- refusing"
                            % rel(p))
    else:
        plan.append((p, want.encode("utf-8"), True))

pg_path = os.path.join(MATS, RETAG_FILE)
if not os.path.isfile(pg_path):
    failures.append("%s not found" % rel(pg_path))
else:
    raw, text, eol = read_file(pg_path)
    try:
        data = json.loads(text)
    except Exception as exc:
        failures.append("%s does not parse: %s" % (rel(pg_path), exc))
        data = None
    if data is not None:
        fmt = detect_format(text, data)
        if fmt is None:
            failures.append("%s does not round-trip through json.dumps in any "
                            "known format -- refusing to reformat it" % rel(pg_path))
        elif data.get("kind") == RETAG_TO:
            already.append("%s already declares kind %r" % (rel(pg_path), RETAG_TO))
        elif data.get("kind") != RETAG_FROM:
            failures.append("%s declares kind %r, expected %r -- refusing"
                            % (rel(pg_path), data.get("kind"), RETAG_FROM))
        else:
            new = dict(data)
            new["kind"] = RETAG_TO
            plan.append((pg_path, render(new, fmt, eol), False))

theme_files = sorted(f for f in os.listdir(THEMES) if f.endswith(".json"))
if not theme_files:
    failures.append("no theme profiles found in %s" % rel(THEMES))

for fn in theme_files:
    p = os.path.join(THEMES, fn)
    raw, text, eol = read_file(p)
    try:
        data = json.loads(text)
    except Exception as exc:
        failures.append("%s does not parse: %s" % (rel(p), exc))
        continue
    fmt = detect_format(text, data)
    if fmt is None:
        failures.append("%s does not round-trip in any known format -- refusing"
                        % rel(p))
        continue
    mats = data.get("materials")
    if not isinstance(mats, dict):
        failures.append("%s has no materials dict" % rel(p))
        continue
    conflict = False
    missing = []
    for kind, profile in sorted(THEME_ADDITIONS.items()):
        if kind in mats and mats[kind] != profile:
            failures.append("%s already maps %r to %r, expected %r -- refusing"
                            % (rel(p), kind, mats[kind], profile))
            conflict = True
        elif kind not in mats:
            missing.append(kind)
    if conflict:
        continue
    if not missing:
        already.append("%s already lists all %d kinds" % (rel(p), len(THEME_ADDITIONS)))
        continue
    merged = dict(mats)
    for kind in missing:
        merged[kind] = THEME_ADDITIONS[kind]
    # preserve the file's existing ordering convention
    if list(mats.keys()) == sorted(mats.keys()):
        ordered = {k: merged[k] for k in sorted(merged)}
    else:
        ordered = {k: merged[k] for k in list(mats.keys())}
        for k in sorted(missing):
            ordered[k] = merged[k]
    new = dict(data)
    new["materials"] = ordered
    plan.append((p, render(new, fmt, eol), False))

print("PRE-FLIGHT")
for a in already:
    print("  already  %s" % a)
for path, _, is_new in plan:
    print("  %-7s %s" % ("create" if is_new else "rewrite", rel(path)))
if failures:
    print("")
    print("REFUSING -- %d precondition(s) failed, nothing was written:" % len(failures))
    for f in failures:
        print("      %s" % f)
    sys.exit(1)
if not plan:
    print("")
    print("NOTHING TO DO -- already applied")
    sys.exit(0)
print("")
print("  %d file(s) would change, %d already correct" % (len(plan), len(already)))

if MODE == "check":
    print("CHECK OK -- run without --check to apply")
    sys.exit(0)

# -------------------------------------------------------------- apply
for path, new_bytes, is_new in plan:
    if not is_new:
        side = path + SIDE
        if not os.path.exists(side):
            shutil.copyfile(path, side)
    with open(path, "wb") as fh:
        fh.write(new_bytes)
    print("  wrote %s" % rel(path))

n = purge_bytecode()
print("")
print("APPLIED -- %d file(s) written, %d __pycache__ dir(s) purged" % (len(plan), n))
print("           sidecars written with suffix %s; --revert undoes this" % SIDE)
print("           run --selftest next, then rebuild the theme libraries")
