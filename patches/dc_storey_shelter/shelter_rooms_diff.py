"""Room by room, what 0.249.0's library change moves: argv[1] is the real deli_counter (0.248.0's specs), argv[2] the
clone (0.249.0's). For every spec whose JSON differs, every room whose standing volumes differ -- a volume is a room's
when its centre is inside the room's plan and its foot on the room's storey (`stands_on_storey`), compared by
(stem, x, y, z, size) -- with its piece count before -> after, its floor share before -> after
(`room_floor_share`), and the stems added and removed. Prints every other spec touched with "no room moved" and the
count of specs identical. Writes nothing."""
import collections
import json
import os
import re
import sys

real, clone = sys.argv[1], sys.argv[2]
sys.path.insert(0, clone)
import level_design as L  # noqa: E402

STEM = re.compile(r"^(?P<stem>.+?)(_r[0-9a-f]{8}_\d+(_\d+)?)?$")


def stem(name):
    return STEM.match(name).group("stem")


def room_volumes(d, room):
    x0, y0, x1, y1 = room["bounds"]
    sh = L._story_height(d)
    floor = room.get("story", 0) * sh
    out = collections.Counter()
    for v in d.get("volumes") or []:
        if x0 <= v["x"] <= x1 and y0 <= v["y"] <= y1 and L.stands_on_storey(
                float(v.get("z", 0)), float(v.get("size_z", 0)), floor, sh):
            out[(stem(v["name"]), v["x"], v["y"], v.get("z"), v.get("size_x"), v.get("size_y"), v.get("size_z"))] += 1
    return out


same = 0
for fn in sorted(os.listdir(os.path.join(real, "specs"))):
    if not fn.endswith(".json") or fn.startswith("lf_"):
        continue
    a = json.load(open(os.path.join(real, "specs", fn), encoding="utf-8"))
    b = json.load(open(os.path.join(clone, "specs", fn), encoding="utf-8"))
    if json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True):
        same += 1
        continue
    moved = 0
    for ra in a.get("rooms") or []:
        rb = next(r for r in b["rooms"] if r["id"] == ra["id"])
        va, vb = room_volumes(a, ra), room_volumes(b, rb)
        if va == vb:
            continue
        moved += 1
        add = collections.Counter(k[0] for k in (vb - va).elements())
        rem = collections.Counter(k[0] for k in (va - vb).elements())
        print("%s / %s: %d -> %d pieces, floor %.1f -> %.1f %%; + %s; - %s" % (
            fn[:-5], ra["id"], sum(va.values()), sum(vb.values()),
            100 * L.room_floor_share(a, ra), 100 * L.room_floor_share(b, rb),
            dict(sorted(add.items())), dict(sorted(rem.items()))))
    if not moved:
        print("%s: the JSON differs and no room moved" % fn[:-5])
print("specs identical:", same)
