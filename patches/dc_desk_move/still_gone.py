"""Every host 0.256.0 still takes away, attributed (argv: the 0.256.0 clone, then spec names): a temporary copy of the
clone's level_design.py logs each spot `_move` asks and the check that refused it -- the clone is not touched -- and
each spec is furnished from bare. Per host: the spots asked, the count refused by each check (in a nested room; on a
route; `_seed_clear`; no chair fits; narrows a pair under two abreast), and the nearest few. Prints measurements only.

    python patches/dc_desk_move/still_gone.py <clone> airport_terminal_a01 bank_branch_a04 ...
"""
import collections
import copy
import json
import math
import os
import shutil
import sys
import tempfile

clone, names = sys.argv[1], sys.argv[2:]
text = open(os.path.join(clone, "level_design.py"), encoding="utf-8").read()
PAIRS = [
    ('''                if _over_rects(inner, qx, qy, half, half):
                    continue
                if on_protected_route(ways, qx, qy, sx, sy):
                    continue
                if not _seed_clear(spec, room, qx, qy, placed, half=half):
                    continue
''', '''                if _over_rects(inner, qx, qy, half, half):
                    _MOVE_LOG.append((host["name"], hx, hy, qx, qy, "in a nested room"))
                    continue
                if on_protected_route(ways, qx, qy, sx, sy):
                    _MOVE_LOG.append((host["name"], hx, hy, qx, qy, "on a route"))
                    continue
                if not _seed_clear(spec, room, qx, qy, placed, half=half):
                    _MOVE_LOG.append((host["name"], hx, hy, qx, qy, "seed_clear"))
                    continue
'''),
    ('''                if got and not _narrows(before, room_necks(spec, room)):
''', '''                _ok = bool(got) and not _narrows(before, room_necks(spec, room))
                _MOVE_LOG.append((host["name"], hx, hy, qx, qy,
                                  "stood" if _ok else ("narrows a pair" if got else "no chair fits")))
                if _ok:
'''),
]
for old, new in PAIRS:
    assert text.count(old) == 1, old[:60]
    text = text.replace(old, new)
text = "_MOVE_LOG = []\n" + text
tmp = tempfile.mkdtemp(prefix="still_gone_")
open(os.path.join(tmp, "level_design.py"), "w", encoding="utf-8", newline="\n").write(text)
sys.path[:0] = [tmp, clone]
import level_design as L  # noqa: E402

assert os.path.dirname(os.path.abspath(L.__file__)) == os.path.abspath(tmp)
for name in names:
    d = L.unfurnished(json.load(open(os.path.join(clone, "specs", name + ".json"), encoding="utf-8")))
    del L._MOVE_LOG[:]
    on = copy.deepcopy(d)
    L.furnish(on)
    standing = {v["name"] for v in on["volumes"]}
    by_host = collections.defaultdict(list)
    for host, hx, hy, qx, qy, why in L._MOVE_LOG:
        by_host[host].append((math.hypot(qx - hx, qy - hy), qx, qy, why))
    rooms = {L._room_tag(r): r for r in on["rooms"]}
    for host, rows in by_host.items():
        tag = host.rsplit("_", 2)[-2]
        room = rooms[tag]
        x0, y0, x1, y1 = room["bounds"]
        print("%s %s/%s (%.0f m2, reserves %r): %s %s -- %d spot(s) asked; %s" % (
            name, room["id"], room.get("story", 0), (x1 - x0) * (y1 - y0),
            L.reserves_routes(on, room, L.club_building_id(on)), host,
            "STANDS" if host in standing else "GOES", len(rows), dict(collections.Counter(r[3] for r in rows))))
        for dist, qx, qy, why in rows[:6]:
            print("     %6.2f m  (%7.2f, %7.2f)  %s" % (dist, qx, qy, why))
shutil.rmtree(tmp)
