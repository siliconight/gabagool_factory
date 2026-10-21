"""Refurnish every spec of one Deli Counter checkout with ANOTHER checkout's code, in memory, and print per room kind
the rooms whose furniture moved and furnish's pieces in them before and after, and every room that lost pieces.
Writes nothing.

    python count_diff.py <code checkout> <specs checkout>

`count_diff_0245_0246.out.txt`: 0.246.0's code (the count fix) on 0.245.0's specs.
"""
import glob, json, os, sys, collections
clone, real = sys.argv[1], sys.argv[2]
sys.path.insert(0, clone)
import level_design as L
import migrate_furnish_recipes as M
by = collections.defaultdict(lambda: [0, 0, 0])
lost = []
specs = 0
for p in sorted(glob.glob(os.path.join(real, "specs", "*.json"))):
    name = os.path.basename(p)[:-5]
    if name.startswith("lf_"):
        continue
    d0 = json.load(open(p, encoding="utf-8"))
    if not d0.get("rooms"):
        continue
    d1 = json.loads(json.dumps(d0))
    M.migrate(d1)
    if json.dumps(d0, sort_keys=True) == json.dumps(d1, sort_keys=True):
        continue
    specs += 1
    b = L.club_building_id(d1)
    for room in d1["rooms"]:
        tag = "_%s_" % L._room_tag(room)
        v0 = sorted(json.dumps(v, sort_keys=True) for v in d0["volumes"] if tag in v.get("name", ""))
        v1 = sorted(json.dumps(v, sort_keys=True) for v in d1["volumes"] if tag in v.get("name", ""))
        if v0 == v1:
            continue
        k = L._room_kind(room, b)
        by[k][0] += 1; by[k][1] += len(v0); by[k][2] += len(v1)
        if len(v1) < len(v0):
            lost.append("%s/%s %s %d -> %d" % (name, room["id"], k, len(v0), len(v1)))
print("specs changed", specs)
print("%-13s %6s %8s %8s" % ("kind", "rooms", "before", "after"))
for k in sorted(by, key=lambda k: -by[k][0]):
    print("%-13s %6d %8d %8d" % (k, *by[k]))
print("all", sum(v[0] for v in by.values()), sum(v[1] for v in by.values()), sum(v[2] for v in by.values()))
print("rooms that lost pieces:", len(lost))
for l in lost[:40]:
    print("  ", l)
