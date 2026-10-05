"""Per-station deltas against the MEAN of two control runs, with unstable
stations named, and the light-cap census compared.

    python price_robust.py <A.json> <A2.json> <B.json> [<C.json>]

A and A2 are one package measured twice; B (and C) are measured against their
mean. A station x heading whose median frame differs between A and A2 by more
than 1.0 ms is UNSTABLE -- one of the two runs hitched there -- and is listed,
then left out of a second summary, so a hitch is shown rather than averaged in.
Prints what it measured and stops. An unrecognised shape FAILS.
"""
import json
import statistics
import sys

UNSTABLE_MS = 1.0


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
    census = (d["rows"][0].get("light_census") or {})
    return out, census


def summary(label, xs):
    print(f"  {label:34s} median {statistics.median(xs):+8.3f}  mean {statistics.mean(xs):+8.3f}  "
          f"min {min(xs):+8.3f}  max {max(xs):+8.3f}  (n {len(xs)})")


a, ca = load(sys.argv[1])
a2, _ = load(sys.argv[2])
others = [(p, load(p)) for p in sys.argv[3:]]
keys = sorted(set(a) & set(a2))
unstable = [k for k in keys if abs(a[k]["ms_median"] - a2[k]["ms_median"]) > UNSTABLE_MS]
print(f"{len(keys)} station x heading pairs; unstable between the two controls (> {UNSTABLE_MS} ms): {len(unstable)}")
for k in unstable:
    print(f"  {k[0]:24s} {k[1]:6.1f}: A {a[k]['ms_median']:.3f}  A2 {a2[k]['ms_median']:.3f}  "
          f"(p95 {a[k]['ms_p95']:.2f} / {a2[k]['ms_p95']:.2f})")
stable = [k for k in keys if k not in unstable]
summary("control A2 - A, ms median, stable", [a2[k]["ms_median"] - a[k]["ms_median"] for k in stable])
for path, (b, cb) in others:
    ks = [k for k in keys if k in b]
    base = {k: (a[k]["ms_median"] + a2[k]["ms_median"]) / 2.0 for k in ks}
    base95 = {k: (a[k]["ms_p95"] + a2[k]["ms_p95"]) / 2.0 for k in ks}
    print(f"{path}:")
    summary("draws, B - A", [b[k]["draws"] - a[k]["draws"] for k in ks])
    summary("ms median, B - mean(A,A2), all", [b[k]["ms_median"] - base[k] for k in ks])
    summary("ms median, B - mean(A,A2), stable", [b[k]["ms_median"] - base[k] for k in ks if k in stable])
    summary("ms p95, B - mean(A,A2), stable", [b[k]["ms_p95"] - base95[k] for k in ks if k in stable])
    print(f"  light cap: {cb.get('over_cap')} of {cb.get('meshes')} meshes over {cb.get('cap')}, "
          f"worst {cb.get('worst')} ({cb.get('worst_mesh')})")
    over = cb.get("over_list") or []
    covers = [o for o in over if "Cover" in str(o.get("mesh", ""))]
    print(f"  of the listed over-cap meshes, covers: {len(covers)} of {len(over)}")
    for o in covers[:12]:
        print(f"    {o.get('lights'):3}  {o.get('mesh')}")
print(f"control census: {ca.get('over_cap')} of {ca.get('meshes')} over, worst {ca.get('worst')} ({ca.get('worst_mesh')})")
