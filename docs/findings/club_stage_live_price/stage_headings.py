"""The price at the headings that face a stage, beside the level-wide one.

    python stage_headings.py club_on.json club_on2.json club_live.json

`price_robust.py` summarises every station x heading. The stage lights reach
5.35 and 6.53 m, so most of those 53 views cannot see them, and a level-wide
median can hide a cost that lives in two of them. This prints, for each
heading, the median frame of the two controls and of the live copy, and the
live copy's difference from the controls' mean against the controls' own
difference -- the named stage-facing headings first, then the five largest
differences anywhere, then the differences split by each station's distance
from the nearer stage.

Stage-facing, from the reports' own positions (Godot frame, metres; a yaw
of 0 looks along -Z, 90 along -X, 270 along +X -- `perf_stations.gd`'s
`_sample` sets `rotation.y` to the yaw):
- `patrol_point_18` (-63.47, 1.6, 12.725), yaw 0: the main stage, Godot
  (-62, 7), 5.9 m ahead;
- `defender_spawn_15` (-72, 1.6, -4), yaw 270: the VIP stage, Godot
  (-67, -5), 5.1 m ahead.

Prints what it measured and stops. An unrecognised shape FAILS.
"""
import json
import math
import statistics
import sys

FACING = [("patrol_point_18", 0.0, "main stage, 5.9 m ahead"),
          ("defender_spawn_15", 270.0, "VIP stage, 5.1 m ahead")]


def load(path):
    d = json.load(open(path, encoding="utf-8"))
    if d.get("schema") != "level_factory.perf_stations.v1" or not d.get("rows"):
        raise SystemExit(f"{path}: not a perf_stations.v1 report with rows")
    out = {}
    for row in d["rows"]:
        for h in row.get("headings") or []:
            for k in ("yaw", "draws", "ms_median", "ms_p95"):
                if k not in h:
                    raise SystemExit(f"{path}: heading without {k!r}")
            out[(row["station"], float(h["yaw"]))] = h
    return out


def line(k, a, a2, b, note=""):
    base = (a[k]["ms_median"] + a2[k]["ms_median"]) / 2.0
    ctrl = a2[k]["ms_median"] - a[k]["ms_median"]
    print(f"  {k[0]:20s} {k[1]:5.0f}  draws {a[k]['draws']:5d} {a2[k]['draws']:5d} {b[k]['draws']:5d}  "
          f"ms median {a[k]['ms_median']:6.3f} {a2[k]['ms_median']:6.3f} {b[k]['ms_median']:6.3f}  "
          f"live - mean {b[k]['ms_median'] - base:+6.3f}  control {ctrl:+6.3f}  {note}")


def positions(path):
    """Station -> (x, z), Godot metres, from the report's own rows."""
    d = json.load(open(path, encoding="utf-8"))
    out = {}
    for row in d["rows"]:
        p = row.get("pos")
        if not isinstance(p, list) or len(p) != 3:
            raise SystemExit(f"{path}: station {row.get('station')!r} without a 3-vector pos")
        out[row["station"]] = (float(p[0]), float(p[2]))
    return out


a, a2, b = (load(p) for p in sys.argv[1:4])
for st, yaw, _note in FACING:
    if (st, yaw) not in a or (st, yaw) not in a2 or (st, yaw) not in b:
        raise SystemExit(f"{st} at yaw {yaw:g} is not in every report")
print("columns: on, on2, live")
print("facing a stage:")
for st, yaw, note in FACING:
    line((st, yaw), a, a2, b, note)
keys = sorted(set(a) & set(a2) & set(b))


def delta(k):
    return b[k]["ms_median"] - (a[k]["ms_median"] + a2[k]["ms_median"]) / 2.0


diffs = sorted(keys, key=lambda k: -abs(delta(k)))
print("the five largest |live - mean| anywhere:")
for k in diffs[:5]:
    line(k, a, a2, b)

# BY DISTANCE FROM A STAGE: a station's distance to the nearer stage, in plan
# (x, z). The bands are the gap the stations fall into on this site: 5.1 to
# 17.0 m, then nothing nearer than 52.3 m.
STAGES = [(-62.0, 7.0), (-67.0, -5.0)]
NEAR, FAR = 17.0, 50.0
pos = positions(sys.argv[1])
dist = {k: min(math.dist(pos[k[0]], s) for s in STAGES) for k in keys}
near = [k for k in keys if dist[k] <= NEAR]
far = [k for k in keys if dist[k] > FAR]
print(f"by distance from the nearer stage ({len(keys)} headings):")
for label, ks in ((f"within {NEAR:g} m", near), (f"beyond {FAR:g} m", far)):
    xs = [delta(k) for k in ks]
    print(f"  {label:14s} n {len(xs):2d}  live - mean: mean {statistics.mean(xs):+6.3f}  "
          f"median {statistics.median(xs):+6.3f}")
# RETRACTED, kept above what replaced it: a count of how many of the nine
# largest |live - mean| stand within 17 m of a stage. On club_live.json the
# ninth place is a tie at 0.075 ms between a near heading and a far one, so
# the count read 7 sorted by size and 8 sorted by sign. A number that a tie
# decides is not evidence; the split above is.
