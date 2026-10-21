"""Every library room's kind, area, furnish target and what it holds (`_room_volume_count`), summarised by kind, and
the seven rooms the look review of 2026-10-19 framed. Pure; reads the specs of the Deli Counter checkout it is run
from. `furnish_census_0245.out.txt` is 0.245.0's.
"""
import collections, glob, json, os, sys
sys.path.insert(0, os.getcwd())
import level_design as LD
rows = []
for path in sorted(glob.glob("specs/*.json")):
    if os.path.basename(path).startswith("lf_"):
        continue
    spec = json.load(open(path, encoding="utf-8"))
    building = LD.club_building_id(spec)
    for room in spec.get("rooms") or []:
        x0, y0, x1, y1 = room["bounds"]
        area = max(0.0, x1 - x0) * max(0.0, y1 - y0)
        if area < LD._FURNISH_MIN_AREA:
            continue
        kind = LD._room_kind(room, building)
        recipe = LD._RECIPES[kind]
        target = LD._furnish_target(area, recipe.get("per_area"))
        if recipe.get("cap") is not None:
            target = min(target, recipe["cap"])
        have = LD._room_volume_count(spec, room)
        rows.append((os.path.basename(path)[:-5], room["id"], kind, area, target, have))
by = collections.defaultdict(list)
for r in rows:
    by[r[2]].append(r)
print("%-14s %5s %9s %8s %8s %10s" % ("kind", "rooms", "area_med", "tgt_med", "have_med", "m2/piece"))
import statistics as st
for k in sorted(by, key=lambda k: -len(by[k])):
    rs = by[k]
    a = [r[3] for r in rs]; t = [r[4] for r in rs]; h = [r[5] for r in rs]
    dens = sum(a) / max(1, sum(h))
    print("%-14s %5d %9.0f %8.1f %8.1f %10.1f" % (k, len(rs), st.median(a), st.median(t), st.median(h), dens))
print("rooms", len(rows), "short of target", sum(1 for r in rows if r[5] < r[4]))
for name in ("restaurant_row", "deli_a03", "pharmacy_a01", "office"):
    for r in rows:
        if r[0] == name:
            print("  ", r[0], r[1], r[2], "%.0f m2" % r[3], "target", r[4], "holds", r[5])
