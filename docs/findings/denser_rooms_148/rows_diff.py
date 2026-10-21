"""Refurnish every spec of one Deli Counter checkout with ANOTHER checkout's code, in memory -- the store-gondola
rename first, then furnish -- and print every room whose furniture moved: its kind, the gondolas the rows laid, its
floor share before and after, its other pieces, and whether it is a corner store's floor; then every room that moved
and is not one. Writes nothing.

    python rows_diff.py <code checkout> <specs checkout>

`rows_diff_0246_0247.out.txt`: 0.247.0's code on 0.246.0's specs.
"""
import glob, json, os, sys, collections
clone, real = sys.argv[1], sys.argv[2]
sys.path.insert(0, clone)
import level_design as L
import migrate_furnish_recipes as M
changed_specs = 0
rows_total = 0
other_changed = []
for p in sorted(glob.glob(os.path.join(real, "specs", "*.json"))):
    name = os.path.basename(p)[:-5]
    if name.startswith("lf_"):
        continue
    d0 = json.load(open(p, encoding="utf-8"))
    if not d0.get("rooms"):
        continue
    d1 = json.loads(json.dumps(d0))
    import migrate_store_gondolas as G
    for a, b in G.renames(d1):
        [v.update(name=b) for v in d1["volumes"] if v.get("name") == a]
    M.migrate(d1)
    if json.dumps(d0, sort_keys=True) == json.dumps(d1, sort_keys=True):
        continue
    changed_specs += 1
    b = L.club_building_id(d1)
    for room in d1["rooms"]:
        tag = "_%s_" % L._room_tag(room)
        v0 = sorted(json.dumps(v, sort_keys=True) for v in d0["volumes"] if tag in v.get("name", ""))
        v1 = sorted(json.dumps(v, sort_keys=True) for v in d1["volumes"] if tag in v.get("name", ""))
        if v0 == v1:
            continue
        g = [v for v in d1["volumes"] if v["name"].startswith("gondola_aisle" + tag)]
        rows_total += len(g)
        n0 = sum(1 for v in d0["volumes"] if tag in v.get("name", ""))
        n1 = sum(1 for v in d1["volumes"] if tag in v.get("name", "")) - len(g)
        r0 = [r for r in d0["rooms"] if r["id"] == room["id"]][0]
        line = "%-24s %-18s %-11s rows %2d  share %4.1f%% -> %4.1f%%  other pieces %2d -> %2d  corner_store=%s" % (
            name, room["id"], L._room_kind(room, b), len(g), 100 * L.room_floor_share(d0, r0),
            100 * L.room_floor_share(d1, room), n0, n1, L.is_corner_store_floor(room, b))
        print(line)
        if not L.is_corner_store_floor(room, b):
            other_changed.append(line)
    # anything else that moved: markers, non-room volumes
    m0 = json.dumps(d0.get("markers"), sort_keys=True); m1 = json.dumps(d1.get("markers"), sort_keys=True)
    if m0 != m1:
        print("   markers changed in", name)
print("specs changed", changed_specs, "gondolas laid", rows_total)
print("rooms changed that are not a corner store's floor:", len(other_changed))
for l in other_changed:
    print("  ", l)
