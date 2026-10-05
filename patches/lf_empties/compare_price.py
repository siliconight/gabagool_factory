"""Compare two perf_stations reports per station and heading, with a control.

    python compare_price.py <A.json> <B.json> <A2.json>

A and A2 are the SAME package measured twice -- their difference is the
instrument's noise. B is the package under test. Prints, over every
station x heading present in all three: draws, objects and median frame ms,
as B - A and as A2 - A. Prints what it measured and stops.

Schema read off a real report (`_runs/perf_inner/ab_a.json`,
`level_factory.perf_stations.v1`): `rows[]` with `station` and `headings[]`
each carrying `yaw`, `draws`, `objects`, `ms_median`, `ms_p95`. An
unrecognised shape FAILS rather than comparing nothing.
"""
import json
import statistics
import sys


def load(path):
    d = json.load(open(path, encoding="utf-8"))
    if d.get("schema") != "level_factory.perf_stations.v1" or not d.get("rows"):
        raise SystemExit(f"{path}: not a perf_stations.v1 report with rows")
    out = {}
    for row in d["rows"]:
        for h in row.get("headings") or []:
            for k in ("yaw", "draws", "objects", "ms_median", "ms_p95"):
                if k not in h:
                    raise SystemExit(f"{path}: heading without {k!r}: {sorted(h)}")
            out[(row["station"], float(h["yaw"]))] = h
    if not out:
        raise SystemExit(f"{path}: no headings")
    return out, d.get("complete")


a, ca = load(sys.argv[1])
b, cb = load(sys.argv[2])
a2, ca2 = load(sys.argv[3])
keys = sorted(set(a) & set(b) & set(a2))
print(f"complete: A {ca}, B {cb}, A2 {ca2}; {len(keys)} station x heading pairs in all three "
      f"(A {len(a)}, B {len(b)}, A2 {len(a2)})")
if not keys:
    raise SystemExit("no common station x heading")


def deltas(x, y, field):
    return [y[k][field] - x[k][field] for k in keys]


for field in ("draws", "objects", "ms_median", "ms_p95"):
    test = deltas(a, b, field)
    ctrl = deltas(a, a2, field)
    print(f"{field:10s} B-A  median {statistics.median(test):+9.3f}  mean {statistics.mean(test):+9.3f}  "
          f"min {min(test):+9.3f}  max {max(test):+9.3f}")
    print(f"{'':10s} A2-A median {statistics.median(ctrl):+9.3f}  mean {statistics.mean(ctrl):+9.3f}  "
          f"min {min(ctrl):+9.3f}  max {max(ctrl):+9.3f}")
worst = sorted(keys, key=lambda k: b[k]["draws"] - a[k]["draws"], reverse=True)[:5]
print("largest draw increases (station, yaw: A -> B draws, A -> B ms_median):")
for k in worst:
    print(f"  {k[0]:24s} {k[1]:6.1f}: {a[k]['draws']} -> {b[k]['draws']}, "
          f"{a[k]['ms_median']:.3f} -> {b[k]['ms_median']:.3f}")
