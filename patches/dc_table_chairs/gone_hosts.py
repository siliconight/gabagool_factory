"""Every host 0.252.0 took away, attributed (argv: the 0.251.0 checkout, the 0.252.0 clone): a piece that must seat
somebody -- its seats ask one or more, or it is a dining table -- standing in 0.251.0's library and not in the clone's,
with its spec, its room -- by the room tag in its name, as `rooms_moved.py` assigns pieces; a first draft took the
first room whose plan held the piece, and rooms on two storeys share a plan -- the room's storey, kind and area, what
the room reserves (`reserves_routes`: "all" on a corner store's floor, "dressing" where a marker is, "" elsewhere) and
whether it stood with a chair at 0.251.0. Prints measurements only."""
import collections
import glob
import json
import os
import re
import sys

base, clone = sys.argv[1], sys.argv[2]
sys.path.insert(0, clone)
import level_design as L  # noqa: E402

assert os.path.samefile(L.__file__, os.path.join(clone, "level_design.py"))
MUST = sorted(k for k, p in L._PIECES.items() if p.get("seats") and (p.get("must_seat") or p["seats"][1] >= 1))
HOST = re.compile(r"^(?P<key>%s)_(?P<tag>r[0-9a-f]{8})_(?P<seq>\d+)$" % "|".join(sorted(MUST, key=len, reverse=True)))
CHAIR = re.compile(r"^[a-z_]+?_(?P<tag>r[0-9a-f]{8})_(?P<seq>\d+)_\d+$")


gone = []
for p in sorted(glob.glob(os.path.join(base, "specs", "*.json"))):
    name = os.path.basename(p)[:-5]
    if name.startswith("lf_"):
        continue
    a = json.load(open(p, encoding="utf-8"))
    b = json.load(open(os.path.join(clone, "specs", name + ".json"), encoding="utf-8"))
    after = {v["name"] for v in b.get("volumes") or []}
    chairs = {(m.group("tag"), m.group("seq")) for v in a.get("volumes") or []
              for m in [CHAIR.match(str(v.get("name") or ""))] if m}
    bid = L.club_building_id(a)
    by_tag = {L._room_tag(r): r for r in a.get("rooms") or []}
    for v in a.get("volumes") or []:
        m = HOST.match(str(v.get("name") or ""))
        if not m or v["name"] in after:
            continue
        r = by_tag.get(m.group("tag"))
        x0, y0, x1, y1 = r["bounds"] if r else (0, 0, 0, 0)
        gone.append((name, "%s (storey %s)" % (r["id"], r.get("story", 0)) if r else "?",
                     L._room_kind(r, bid) if r else "?", (x1 - x0) * (y1 - y0),
                     L.reserves_routes(a, r, bid) if r else "?", m.group("key"),
                     (m.group("tag"), m.group("seq")) in chairs, v["name"]))
print("hosts taken away:", len(gone), dict(collections.Counter(g[5] for g in gone)))
print("  by what the room reserves:", dict(collections.Counter(g[4] or "nothing" for g in gone)))
print("  stood with a chair at 0.251.0:", sum(1 for g in gone if g[6]))
for g in gone:
    print("  %-40s %-30s %-10s %5.0f m2  reserves %-9s %-14s %s" % (g[0], g[1], g[2], g[3], repr(g[4]), g[5], g[7]))
