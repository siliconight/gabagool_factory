"""Simulate the rule before writing it: a store's video poker cabinet with no free wall takes a filler's
(cabinet_file, then vending) in its own room. On in-memory copies of every library spec; writes nothing.
A probe: prints and stops.

Run for patch_dc_store_cabinets.py on Deli Counter 0.227.0's library (709fee88), where it gave +15 cabinets, 9
vending and 5 file cabinets displaced. That is the TARGETED placement -- cabinets alone, after everything else --
which the patch refutes as a migration: a fresh furnish places them before the poster boards, so the library's
strip and refurnish (`migrate_furnish_recipes.py`) gives +18, 9 file cabinets and 6 vending. Kept with the
refutation, not as the patch's figure.

    python simulate.py <deli_counter dir>
"""
import collections
import glob
import json
import os
import sys

dc = os.path.abspath(sys.argv[1])
sys.path.insert(0, dc)
os.chdir(dc)
import level_design as L  # noqa: E402

KEY = "video_poker_store"
DISPLACES = ("cabinet_file", "vending")
CAP = 2


def place(spec):
    building = L.club_building_id(spec)
    placed, displaced, still = 0, collections.Counter(), []
    only = L._PIECES[KEY]["rooms"]
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
        rtag = L._room_tag(room)
        for k in range(L.fixture_limit(KEY, area)):
            have = sum(1 for stem, _s, _v in L._room_names(spec, rtag) if stem == KEY)
            if have > k:
                continue
            in_building = sum(1 for v in spec.get("volumes") or [] if str(v.get("name", "")).startswith(KEY + "_r"))
            if in_building >= CAP:
                break
            got = L._place_fixture(spec, room, KEY, k, building)
            if got is None:
                for stem in DISPLACES:
                    cands = sorted((t for t in L._room_names(spec, rtag) if t[0] == stem), key=lambda t: -t[1])
                    for _s, _seq, vol in cands:
                        i = spec["volumes"].index(vol)
                        spec["volumes"].pop(i)
                        got = L._place_fixture(spec, room, KEY, k, building)
                        if got is not None:
                            displaced[stem] += 1
                            break
                        spec["volumes"].insert(i, vol)
                    if got is not None:
                        break
            if got is None:
                still.append(room["id"])
                break
            placed += 1
    return placed, displaced, still


tot_p, tot_d = 0, collections.Counter()
for path in sorted(glob.glob("specs/*.json")):
    name = os.path.basename(path)[:-5]
    if name.startswith("lf_"):
        continue
    spec = json.load(open(path, encoding="utf-8"))
    if not spec.get("rooms"):
        continue
    before = sum(1 for v in spec.get("volumes") or [] if str(v.get("name", "")).startswith(KEY + "_r"))
    p, d, still = place(spec)
    after = before + p
    if p or still:
        tot_p += p
        tot_d.update(d)
        print("%-34s %d -> %d%s%s" % (name, before, after, ("; displaced " + ", ".join("%d %s" % (n, s) for s, n in d.items())) if d else "",
                                          ("; still none in " + ", ".join(still)) if still else ""))
print("total: +%d cabinets, displaced %s" % (tot_p, dict(tot_d)))
