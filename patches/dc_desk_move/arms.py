"""What moving a chairless host costs a route, arm by arm (argv: the arm, the dc0256 clone). Each arm's modules --
the clone's, or the factory's own deli_counter for the control, its move switched by anchored text edits in a temp
copy -- refurnish and shelter Deli Counter 0.255.0's library (the factory's checkout, in memory), census every spec
(`docs/findings/furnish_route_cost/route_cost.py`) and compare it pair by pair, by endpoints, with the factory's census
(`route_cost.json` there, 0.252.0's library, which 0.253.0-0.255.0 left as it was). Counts each seated piece, the
hosts the arm takes away and moves against the shipped library, and the floor share of every room a host moved in.
Writes arms_<arm>.json beside this file -- with every pair the arm moved, by spec, room and endpoints, and every host
that came back, by room -- and prints one summary line.

REFUTED AND KEPT: the first run (arms_*_first.json) counted a host as moved only where it stood in both libraries,
and as gone only where it stood in the shipped one -- and the 25 hosts 0.252.0 took away stand in neither, so it
printed "gone 0, moved 0" for every arm. Only its host counts saw them (desks 239 -> 257, 259, 262). A host that comes
back is now counted as such.

  0255   the factory's deli_counter as shipped: the CONTROL -- it must reproduce the census pair for pair
  A      the clone: a host no chair fits beside moves to the nearest spot where it and its chair stand off the
         room's routes, else goes
  B      A, then, where no spot off the routes takes it, the nearest spot `_host` itself would accept (on a route
         unless the room keeps every piece off them), its chair held to the in-place rescue's rule (off the routes
         the room reserves)
  C      B with the chair's routes relaxed too in that second pass (off them only where the room keeps every piece
         off them)
  final  the clone as shipped: A, and a moved host narrows no pair (`room_necks`, `_narrows`)

A, B AND C WERE MEASURED ON THE CLONE BEFORE THE GUARD (arms_A.json, arms_B.json, arms_C.json): run again now, each
would carry the guard too, the edits above applying to the guarded `_move` as they did to the first.

    python patches/dc_desk_move/arms.py <arm> <dc0256 clone>
"""
import collections
import glob
import json
import os
import pathlib
import re
import shutil
import sys
import tempfile
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
FACTORY = HERE.parents[1]
arm, clone = sys.argv[1], sys.argv[2]
assert arm in ("0255", "A", "B", "C", "final"), arm
src = str(FACTORY / "deli_counter") if arm == "0255" else clone

SECOND_PASS = [
    ('''            for qx, qy in sorted(floor_cands,
                                 key=lambda q: math.hypot(q[0] - hx,
                                                          q[1] - hy)):
''', '''            near = sorted(floor_cands,
                          key=lambda q: math.hypot(q[0] - hx, q[1] - hy))
            for strict, (qx, qy) in ([(True, q) for q in near]
                                     + [(False, q) for q in near]):
'''),
    ('''                if on_protected_route(ways, qx, qy, sx, sy):
                    continue
''', '''                if (strict or keep_all) and on_protected_route(
                        ways, qx, qy, sx, sy):
                    continue
'''),
]
EDITS = {
    "0255": [], "A": [], "final": [],
    "B": SECOND_PASS + [('''                             rescue=True, keep_off=ways)
''', '''                             rescue=True, keep_off=ways if strict else None)
''')],
    "C": SECOND_PASS + [('''                             rescue=True, keep_off=ways)
''', '''                             rescue=True,
                             keep_off=ways if (strict or keep_all) else ())
''')],
}
tmp = tempfile.mkdtemp(prefix="dc_move_arm_%s_" % arm)
for f in glob.glob(os.path.join(src, "*.py")) + [os.path.join(src, "agent_contract.json")]:
    shutil.copy2(f, tmp)
p = os.path.join(tmp, "level_design.py")
text = open(p, encoding="utf-8").read()
assert ("def _move(" in text) == (arm != "0255"), arm
for old, new in EDITS[arm]:
    assert text.count(old) == 1, (arm, old[:60])
    text = text.replace(old, new)
open(p, "w", encoding="utf-8", newline="\n").write(text)
sys.path.insert(0, tmp)
import level_design as L  # noqa: E402
import migrate_furnish_recipes  # noqa: E402,F401
import migrate_shelter  # noqa: E402
import partition_bounds  # noqa: E402,F401
import stairwell  # noqa: E402,F401
import spec_types  # noqa: E402,F401
sys.path.insert(0, str(FACTORY / "docs" / "findings" / "furnish_route_cost"))
import route_cost as R  # noqa: E402

assert os.path.samefile(R.L.__file__, p), R.L.__file__

SEATED = {k: v["seats"] for k, v in L._PIECES.items() if v.get("seats")}
HOST = re.compile(r"^(?P<key>%s)_(?P<tag>r[0-9a-f]{8})_(?P<seq>\d+)$" % "|".join(sorted(SEATED, key=len, reverse=True)))
CHAIR = re.compile(r"^[a-z_]+?_(?P<tag>r[0-9a-f]{8})_(?P<seq>\d+)_\d+$")
t0 = time.time()
rows, chairless, chairs, hosts_n = [], collections.Counter(), collections.Counter(), collections.Counter()
gone, moved, back, shares, pieces = [], [], [], [], 0
for sp in sorted(glob.glob(str(FACTORY / "deli_counter" / "specs" / "*.json"))):
    nm = os.path.basename(sp)[:-5]
    if nm.startswith("lf_"):
        continue
    shipped = json.load(open(sp, encoding="utf-8"))
    if not shipped.get("rooms"):
        continue
    d = json.loads(json.dumps(shipped))
    migrate_furnish_recipes.migrate(d)
    migrate_shelter.migrate(d)
    rows.extend(R.measure_spec(d, nm))
    was = {v["name"]: v for v in shipped["volumes"] if HOST.match(str(v.get("name") or ""))}
    now = {v["name"]: v for v in d["volumes"] if HOST.match(str(v.get("name") or ""))}
    gone += ["%s %s" % (nm, n) for n in sorted(set(was) - set(now))]
    rooms = {L._room_tag(r): r for r in d["rooms"]}
    for n in sorted(set(now) - set(was)):
        room = rooms[HOST.match(n).group("tag")]
        back.append("%s %s/%s %s (%.2f, %.2f)" % (nm, room["id"], room.get("story", 0), n, now[n]["x"], now[n]["y"]))
        shares.append("%s %s: %.1f -> %.1f %%" % (nm, room["id"], 100 * L.room_floor_share(shipped, room),
                                                  100 * L.room_floor_share(d, room)))
    for n in sorted(set(was) & set(now)):
        a, b = was[n], now[n]
        if (a["x"], a["y"]) != (b["x"], b["y"]):
            room = rooms[HOST.match(n).group("tag")]
            moved.append("%s %s (%.2f, %.2f) -> (%.2f, %.2f)" % (nm, n, a["x"], a["y"], b["x"], b["y"]))
            shares.append("%s %s: %.1f -> %.1f %%" % (nm, room["id"], 100 * L.room_floor_share(shipped, room),
                                                      100 * L.room_floor_share(d, room)))
    seen = collections.Counter()
    keys = {}
    for v in d["volumes"]:
        m = HOST.match(v["name"])
        if m:
            keys[(m.group("tag"), m.group("seq"))] = m.group("key")
        m = CHAIR.match(v["name"])
        if m:
            seen[(m.group("tag"), m.group("seq"))] += 1
    for k, key in keys.items():
        hosts_n[key] += 1
        chairs[key] += seen[k]
        chairless[key] += seen[k] == 0
    tags = {L._room_tag(r) for r in d["rooms"]}
    pieces += sum(1 for v in d["volumes"] if migrate_furnish_recipes.furnished_by_this_pass(v, tags))


def pairs(rws):
    out = {}
    for r in rws:
        e = r["endpoints"]
        for a in range(len(e)):
            for b in range(a + 1, len(e)):
                k = "%d-%d" % (a, b)
                key = (r["spec"], r["room"], tuple(e[a][:2]) + tuple(round(x, 2) for x in e[a][2:4]),
                       tuple(e[b][:2]) + tuple(round(x, 2) for x in e[b][2:4]))
                out[key] = {a_: (r["arms"][a_]["length"].get(k), r["arms"][a_]["bottleneck"].get(k, 0.0))
                            for a_ in r["arms"]}
    return out


base = pairs(json.load(open(FACTORY / "docs" / "findings" / "furnish_route_cost" / "route_cost.json",
                            encoding="utf-8")))
now = pairs(rows)
common = set(base) & set(now)
differ = sum(1 for k in common if base[k] != now[k])


def _arm(v):
    """(length, bottleneck) of one arm of one pair, rounded for the record."""
    return [None if v[0] is None else round(v[0], 2), round(v[1], 3)]


differing = [{"spec": k[0], "room": k[1], "a": list(k[2]), "b": list(k[3]),
              "shipped": {a_: _arm(base[k][a_]) for a_ in ("authored", "furnished")},
              "arm": {a_: _arm(now[k][a_]) for a_ in ("authored", "furnished")}}
             for k in sorted(common, key=str) if base[k] != now[k]]
over_b = over_a = up = down = closed_b = closed_a = narrow_b = narrow_a = 0
ratios = []
for k in common:
    (lfb, bfb), (lab, bab) = base[k]["furnished"], base[k]["authored"]
    (lfa, bfa), (laa, baa) = now[k]["furnished"], now[k]["authored"]
    if lfb and lab and lfa and laa:
        rb, ra = lfb / lab, lfa / laa
        ratios.append(ra)
        over_b += rb > 1.10
        over_a += ra > 1.10
        up += rb <= 1.10 < ra
        down += ra <= 1.10 < rb
    closed_b += bab >= R.C_BAKE > bfb
    closed_a += baa >= R.C_BAKE > bfa
    narrow_b += bab >= R.TWO_ABREAST > bfb
    narrow_a += baa >= R.TWO_ABREAST > bfa
v = np.array(ratios)
summary = {
    "arm": arm, "pairs": [len(base), len(now), len(common)], "pairs_differing": differ,
    "seconds": round(time.time() - t0), "over_10pct": [over_b, over_a], "crossed_over": up,
    "came_back_under": down, "closed_to_bake": [closed_b, closed_a], "narrowed_to_single_file": [narrow_b, narrow_a],
    "p99": round(float(np.percentile(v, 99)), 3), "max": round(float(v.max()), 3), "pieces": pieces,
    "hosts": dict(hosts_n), "chairless": dict(chairless), "chairs": dict(chairs),
    "gone_vs_shipped": gone, "moved_vs_shipped": moved, "back_vs_shipped": back,
    "floor_share_of_rooms_moved_in": shares, "pairs_moved": differing,
}
(HERE / ("arms_%s.json" % arm)).write_text(json.dumps(summary, indent=1), encoding="utf-8", newline="\n")
print(json.dumps({k: summary[k] for k in summary if k not in ("gone_vs_shipped", "moved_vs_shipped", "back_vs_shipped",
                                                               "floor_share_of_rooms_moved_in", "pairs_moved")}))
print("gone %d, moved %d, back %d, pairs moved %d" % (len(gone), len(moved), len(back), len(differing)))
shutil.rmtree(tmp, ignore_errors=True)
