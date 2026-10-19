"""The store video poker cabinet census, per building, on two spec sources: a git revision of Deli Counter
(default 709fee88, 0.227.0, the library before patch_dc_store_cabinets.py) and its working tree.

A building is counted when one of its rooms asks for `video_poker_store` -- the recipe lists the fixture, the
room's id carries one of the piece's room tokens, and the room is at least `_FURNISH_MIN_AREA` -- the same
three tests `place_fixtures` applies. "May hold" is the sum of `fixture_limit` over those rooms; "held" counts
the cabinets standing in them. Room membership is read through the working tree's `level_design`; the patch
does not change which rooms ask. A probe: prints and stops.

    python census.py <deli_counter dir> [<rev>]
"""
import glob
import json
import os
import subprocess
import sys
from collections import Counter

dc = os.path.abspath(sys.argv[1])
rev = sys.argv[2] if len(sys.argv) > 2 else "709fee88"
sys.path.insert(0, dc)
os.chdir(dc)
import level_design as L  # noqa: E402

KEY = "video_poker_store"


def held(spec):
    building = L.club_building_id(spec)
    only = L._PIECES[KEY]["rooms"]
    want = have = 0
    for room in spec.get("rooms") or []:
        x0, y0, x1, y1 = room["bounds"]
        area = max(0.0, x1 - x0) * max(0.0, y1 - y0)
        if area < L._FURNISH_MIN_AREA:
            continue
        if KEY not in (L._RECIPES[L._room_kind(room, building)].get("fixtures") or ()):
            continue
        tokens = set(str(room.get("id", "")).lower().replace("-", "_").split("_"))
        if only and not tokens & only:
            continue
        want += L.fixture_limit(KEY, area)
        have += sum(1 for stem, _s, _v in L._room_names(spec, L._room_tag(room)) if stem == KEY)
    return want, have


rows = {}
for path in sorted(glob.glob("specs/*.json")):
    name = os.path.basename(path)[:-5]
    if name.startswith("lf_"):
        continue
    now = json.load(open(path, encoding="utf-8"))
    if not now.get("rooms"):
        continue
    out = subprocess.run(["git", "show", "%s:specs/%s.json" % (rev, name)], capture_output=True, text=True,
                         encoding="utf-8")
    if out.returncode != 0:
        print("not in %s: %s" % (rev, name))
        continue
    then = json.loads(out.stdout)
    w0, h0 = held(then)
    w1, h1 = held(now)
    if w0 or w1:
        rows[name] = (w0, h0, w1, h1)
print("Deli Counter %s against the working tree (%s)" % (rev, open("VERSION", encoding="utf-8").read().strip()))
print("buildings that ask:", len(rows))
print("%-8s by held:" % rev, dict(sorted(Counter(min(r[1], 2) for r in rows.values()).items())),
      " total held", sum(r[1] for r in rows.values()), " may hold", sum(r[0] for r in rows.values()))
print("tree     by held:", dict(sorted(Counter(min(r[3], 2) for r in rows.values()).items())),
      " total held", sum(r[3] for r in rows.values()), " may hold", sum(r[2] for r in rows.values()))
print("moves (%s -> tree):" % rev, dict(sorted(Counter((r[1], r[3]) for r in rows.values()).items())))
for name, r in sorted(rows.items()):
    if r[1] != r[3] or r[3] < 2:
        print("   %-28s %d -> %d   (may hold %d)" % (name, r[1], r[3], r[2]))
