"""The headings that see Deli Counter 0.246.0 and 0.247.0's change: where cold run 9369's package draws differently
from 9368's (the control, Deli Counter 0.245.0, run twice), each with its frame-time difference beside the control's
at the same heading. Copied from `docs/findings/car_wear_44/price_headings.py` unchanged but this docstring: ``before``
and ``before2`` are one package run twice, ``after`` the other. Prints what it measured and stops.

    python price_headings.py price_9368_a.json price_9368_a2.json price_9369_b.json
"""
import json
import statistics
import sys


def load(path):
    d = json.load(open(path, encoding="utf-8"))
    if d.get("schema") != "level_factory.perf_stations.v1" or not d.get("rows"):
        raise SystemExit(f"{path}: not a perf_stations.v1 report with rows")
    if not d.get("complete"):
        raise SystemExit(f"{path}: the report says it is not complete")
    out = {}
    for row in d["rows"]:
        for h in row.get("headings") or []:
            for k in ("yaw", "draws", "ms_median", "ms_p95", "split_perturbed"):
                if k not in h:
                    raise SystemExit(f"{path}: heading without {k!r}")
            out[(row["station"], float(h["yaw"]))] = h
    return out, d.get("geometry") or {}


(a, ga), (a2, ga2), (b, gb) = (load(p) for p in sys.argv[1:4])
keys = sorted(set(a) & set(a2) & set(b))
if len(keys) != len(a) or len(keys) != len(b):
    raise SystemExit(f"the reports' headings differ: {len(a)}, {len(a2)}, {len(b)}, {len(keys)} shared")
moved = [k for k in keys if b[k]["draws"] != a[k]["draws"]]
ctl_moved = [k for k in keys if a2[k]["draws"] != a[k]["draws"]]
print(f"{len(keys)} headings; draws differ before -> after at {len(moved)}; the control's two runs differ at "
      f"{len(ctl_moved)}")
print(f"  {'station':22s} {'yaw':>5s} {'before':>7s} {'after-before':>13s} {'perturbed':>9s} "
      f"{'after-mean ms':>14s} {'control ms':>11s} {'p95 after-mean':>15s}")
for k in moved:
    base = (a[k]["ms_median"] + a2[k]["ms_median"]) / 2.0
    base95 = (a[k]["ms_p95"] + a2[k]["ms_p95"]) / 2.0
    pert = a[k]["split_perturbed"] or a2[k]["split_perturbed"] or b[k]["split_perturbed"]
    print(f"  {k[0]:22s} {k[1]:5.0f} {a[k]['draws']:7d} {b[k]['draws'] - a[k]['draws']:+13d} {str(pert):>9s} "
          f"{b[k]['ms_median'] - base:+14.3f} {a2[k]['ms_median'] - a[k]['ms_median']:+11.3f} "
          f"{b[k]['ms_p95'] - base95:+15.3f}")
d_moved = [b[k]["ms_median"] - (a[k]["ms_median"] + a2[k]["ms_median"]) / 2.0 for k in moved]
d_rest = [b[k]["ms_median"] - (a[k]["ms_median"] + a2[k]["ms_median"]) / 2.0 for k in keys if k not in moved]
ctl = [a2[k]["ms_median"] - a[k]["ms_median"] for k in keys]
ddraw = [b[k]["draws"] - a[k]["draws"] for k in moved]
if moved:
    print(f"  draws after - before where they moved: median {statistics.median(ddraw):+.0f}, "
          f"min {min(ddraw):+d}, max {max(ddraw):+d}")
    print(f"  ms_median after - mean(before): where draws moved mean {statistics.mean(d_moved):+.3f} "
          f"(n {len(d_moved)}); elsewhere mean {statistics.mean(d_rest) if d_rest else 0.0:+.3f} (n {len(d_rest)}); "
          f"the control's spread {min(ctl):+.3f} to {max(ctl):+.3f}, mean |control| "
          f"{statistics.mean(abs(c) for c in ctl):.3f}")
for name, g in (("before", ga), ("before2", ga2), ("after", gb)):
    print(f"  {name:8s} mesh_instances {g.get('mesh_instances')} texture_mem_bytes {g.get('texture_mem_bytes')} "
          f"buffer_mem_bytes {g.get('buffer_mem_bytes')} video_mem_bytes {g.get('video_mem_bytes')}")
