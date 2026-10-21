"""Why each room 0.252.0 moved, moved (argv: the 0.251.0 checkout, the 0.252.0 clone, and `rooms_moved.py`'s two
dumps): by the rescue alone -- every piece added a chair and every piece gone a host, in a room that stood a chairless
host at 0.251.0 -- or re-drawn, other pieces moved too. Prints the counts, and the re-drawn rooms. Read-only.

The one re-drawn room, landmark_hall_a01's artifact_room, was first put down to a room furnished before it:
`_seed_clear` keeps a piece 0.9 m off every standing volume on its storey, through a partition too, so a desk taken
away next door could free a candidate on this side of the wall. REFUTED (`artifact_steps.py`): curator_band's desk
stands 4.14 m off and is furnished after it; the room furnishes as 0.251.0 less its own chairless dining table, and
re-draws in the shelter pass, which stands a crate where the table stood and refurnishes the spec around it."""
import collections
import glob
import json
import os
import re
import sys

base, clone, dump_a, dump_b = sys.argv[1:5]
sys.path.insert(0, base)
import level_design as L  # noqa: E402

SEATED = {k: v["seats"] for k, v in L._PIECES.items() if v.get("seats")}
HOST = re.compile(r"^(?P<key>%s)_(?P<tag>r[0-9a-f]{8})_(?P<seq>\d+)$" % "|".join(sorted(SEATED, key=len, reverse=True)))
CHAIR = re.compile(r"^[a-z_]+?_(?P<tag>r[0-9a-f]{8})_(?P<seq>\d+)_\d+$")
MUST = {k for k, v in SEATED.items() if v[1] >= 1} | {"table_dining"}
own = set()
for p in sorted(glob.glob(os.path.join(base, "specs", "*.json"))):
    name = os.path.basename(p)[:-5]
    if name.startswith("lf_"):
        continue
    d = json.load(open(p, encoding="utf-8"))
    hosts, chairs = {}, set()
    for v in d.get("volumes") or []:
        m = HOST.match(str(v.get("name") or ""))
        if m and m.group("key") in MUST:
            hosts[(m.group("tag"), m.group("seq"))] = m.group("tag")
        m = CHAIR.match(str(v.get("name") or ""))
        if m:
            chairs.add((m.group("tag"), m.group("seq")))
    own |= {(name, tag) for k, tag in hosts.items() if k not in chairs}
a, b = json.load(open(dump_a, encoding="utf-8")), json.load(open(dump_b, encoding="utf-8"))
why = collections.Counter()
redrawn = []
for spec in sorted(b):
    for rid, r in b[spec].items():
        if rid == "__all__" or r["pieces"] == a[spec][rid]["pieces"]:
            continue
        before, after = set(a[spec][rid]["pieces"]), set(r["pieces"])
        # a piece is "name@x,y": the rescue only ADDS a chair to a host that had none and TAKES AWAY such a host
        added = {x.split("@")[0] for x in after - before}
        gone = {x.split("@")[0] for x in before - after}
        rescue_only = (all(CHAIR.match(n) and (spec, CHAIR.match(n).group("tag")) in own for n in added)
                       and all(HOST.match(n) and (spec, HOST.match(n).group("tag")) in own for n in gone))
        if rescue_only:
            why["the rescue only: chairs seated, hosts taken away"] += 1
        else:
            why["re-drawn: other pieces moved too"] += 1
            redrawn.append("%s / %s (%s): %d pieces moved or changed" % (
                spec, rid, r["kind"], len((before - after) | (after - before))))
print("rooms moved:", sum(why.values()), dict(why))
print("re-drawn rooms:")
for x in redrawn:
    print("  " + x)
