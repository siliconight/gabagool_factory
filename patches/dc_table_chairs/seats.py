"""The chairs every seated piece of a Deli Counter checkout's library stands (argv[1]; the checkout's modules loaded):
per piece that brings seats (`_PIECES[...]["seats"]`), how many stand in the library and how many chairs each has --
a chair is grouped with its host by the host's sequence number, `<seat>_<room tag>_<host seq>_<j>` -- and, for every
table, how far each chair's near edge stands from the table's (the tuck), counted as within a seat's depth or not.
Prints measurements only.

    python seats.py <checkout>
"""
import collections
import glob
import json
import os
import re
import sys

dc = sys.argv[1]
sys.path.insert(0, dc)
import level_design as L  # noqa: E402

assert os.path.samefile(L.__file__, os.path.join(dc, "level_design.py"))
SEATED = {k: p["seats"] for k, p in L._PIECES.items() if p.get("seats")}
HOST = re.compile(r"^(?P<key>%s)_(?P<tag>r[0-9a-f]{8})_(?P<seq>\d+)$" % "|".join(sorted(SEATED, key=len,
                                                                                        reverse=True)))
SEAT = re.compile(r"^(?P<stem>[a-z_]+?)_(?P<tag>r[0-9a-f]{8})_(?P<seq>\d+)_(?P<j>\d+)$")
dist = collections.defaultdict(collections.Counter)
chairless = collections.defaultdict(list)
tuck = collections.Counter()
specs = 0
for p in sorted(glob.glob(os.path.join(dc, "specs", "*.json"))):
    name = os.path.basename(p)[:-5]
    if name.startswith("lf_"):
        continue
    d = json.load(open(p, encoding="utf-8"))
    if not d.get("rooms"):
        continue
    specs += 1
    hosts, chairs = {}, collections.defaultdict(list)
    for v in d.get("volumes") or []:
        m = HOST.match(str(v.get("name") or ""))
        if m:
            hosts[(m.group("tag"), m.group("seq"))] = (m.group("key"), v)
            continue
        m = SEAT.match(str(v.get("name") or ""))
        if m:
            chairs[(m.group("tag"), m.group("seq"))].append(v)
    for k, (key, v) in hosts.items():
        mine = chairs.get(k, [])
        dist[key][len(mine)] += 1
        if not mine:
            chairless[key].append(name)
        if SEATED[key][0] == "table":
            for c in mine:
                gx = abs(c["x"] - v["x"]) - (v["size_x"] + c["size_x"]) / 2.0
                gy = abs(c["y"] - v["y"]) - (v["size_y"] + c["size_y"]) / 2.0
                gap = max(gx, gy)
                tuck["tucked (gap <= 0.30 m)" if gap <= 0.30 + 1e-6 else "pulled out (gap > 0.30 m)"] += 1
print("# seats.py over %s: %d specs" % (dc, specs))
for key in sorted(SEATED):
    c = dist[key]
    n = sum(c.values())
    if not n:
        continue
    print("%-18s seats %-22s hosts %4d  chairs per host %s  chairless %d%s"
          % (key, SEATED[key], n, dict(sorted(c.items())), c[0],
             ("  (%s)" % ", ".join(sorted(set(chairless[key]))[:8])) if c[0] else ""))
print("table chairs:", dict(tuck))
