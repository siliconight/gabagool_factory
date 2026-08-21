#!/usr/bin/env python3
"""zoo_pack_probe.py v2 -- can zoo actually resolve the ten new kinds?

READS ONLY. v1 called load_pack on find_pack's return value; find_pack already
returns the loaded dict, so all 50 lookups succeeded and v1 discarded them.
"""
import inspect
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "zoo"))

from zoo_keeper.core import skins  # noqa: E402

BUILD = os.path.join(ROOT, "pixelcoat", "build")
THEMES = ["rockay", "rockay_civic", "rockay_retail", "rockay_service", "street"]
NEW = ["canvas", "carbon", "dirt", "gravel", "laminate",
       "leather", "paper", "rubber", "tar", "vegetation"]
TINT_EXPECTED = {"laminate": True, "paper": True,
                 "carbon": False, "tar": False, "vegetation": False,
                 "canvas": False, "dirt": False, "gravel": False,
                 "leather": False, "rubber": False}

print("skins.find_pack%s" % inspect.signature(skins.find_pack))
kk = sorted(getattr(skins, "KNOWN_KINDS", []))
print("KNOWN_KINDS (%d)" % len(kk))
print("  not in KNOWN_KINDS: %s"
      % (", ".join(k for k in NEW if k not in kk) or "none"))
print("")

lookups = 0
failures = []
tint = {}
keys_seen = set()

print("%-12s%s" % ("kind", "".join("%-24s" % t for t in THEMES)))
print("-" * (12 + 24 * len(THEMES)))
for kind in NEW:
    cells = ""
    for theme in THEMES:
        lib = os.path.join(BUILD, "skins_" + theme)
        if not os.path.isdir(lib):
            cells += "%-24s" % "NO LIBRARY"
            failures.append("%s/%s: library dir missing" % (kind, theme))
            continue
        lookups += 1
        try:
            pack = skins.find_pack(lib, kind, theme)
        except Exception as exc:
            cells += "%-24s" % ("ERR %s" % type(exc).__name__)
            failures.append("%s/%s: find_pack raised %s: %s"
                            % (kind, theme, type(exc).__name__, exc))
            continue
        if not pack:
            cells += "%-24s" % "NOT FOUND"
            failures.append("%s/%s: find_pack returned %r" % (kind, theme, pack))
            continue
        if not isinstance(pack, dict):
            cells += "%-24s" % ("NOT A DICT: %s" % type(pack).__name__)
            failures.append("%s/%s: find_pack returned %s"
                            % (kind, theme, type(pack).__name__))
            continue
        keys_seen.update(pack.keys())
        label = (pack.get("material_profile") or pack.get("asset_id")
                 or pack.get("name") or "?")
        cells += "%-24s" % str(label)[:23]
        tint.setdefault(kind, set()).add(bool(pack.get("tintable")))
    print("%-12s%s" % (kind, cells))

print("")
print("keys zoo sees on a pack: %s" % ", ".join(sorted(keys_seen)))
print("")
print("TINTABLE as loaded by zoo")
for kind in NEW:
    want = TINT_EXPECTED[kind]
    got = tint.get(kind)
    if got is None:
        print("  %-12s never loaded" % kind)
        failures.append("%s: never loaded" % kind)
    elif got == {want}:
        print("  %-12s %-5s ok" % (kind, want))
    else:
        print("  %-12s expected %s, got %s   <-- MISMATCH"
              % (kind, want, sorted(got)))
        failures.append("%s: tintable expected %s, got %s"
                        % (kind, want, sorted(got)))

print("")
if lookups == 0:
    print("REFUSING TO CONCLUDE -- zero lookups performed")
    sys.exit(2)
print("%d lookup(s) performed" % lookups)
if failures:
    print("FAILURES -- %d" % len(failures))
    for f in failures[:30]:
        print("      %s" % f)
    sys.exit(1)
print("ALL TEN KINDS RESOLVE IN ALL FIVE THEMES, tintable flags as authored")
