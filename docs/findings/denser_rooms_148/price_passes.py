"""The price again, by each heading's TWO PASSES rather than its headline. The harness measures every heading twice and
reports the first pass's draws; at a heading it marks `split_perturbed` the passes disagree -- 9368's extraction_16 at
yaw 90 drew 1,322 then 1,230, and 9369's 1,228 then 1,320, the same two states in the other order -- so a headline
difference there is partly WHICH state the first pass caught. This compares the smaller pass with the smaller and the
larger with the larger, for the control's two runs and for the change, and prints the frame time beside them. Prints
what it measured and stops.

    python price_passes.py price_9368_a.json price_9368_a2.json price_9369_b.json
"""
import json
import statistics
import sys


def load(path):
    d = json.load(open(path, encoding="utf-8"))
    if d.get("schema") != "level_factory.perf_stations.v1" or not d.get("complete"):
        raise SystemExit(f"{path}: not a complete perf_stations.v1 report")
    out = {}
    for row in d["rows"]:
        for h in row["headings"]:
            passes = h.get("passes")
            if not passes or len(passes) < 2:
                raise SystemExit(f"{path}: {row['station']} {h['yaw']} carries {len(passes or [])} passes, not two")
            ds = sorted(p["draws"] for p in passes)
            out[(row["station"], float(h["yaw"]))] = (ds[0], ds[-1], h["ms_median"], h["split_perturbed"])
    return out


a, a2, b = (load(p) for p in sys.argv[1:4])
keys = sorted(set(a) & set(a2) & set(b))
assert len(keys) == len(a) == len(b), (len(a), len(a2), len(b), len(keys))
ctl = [(k, a2[k][0] - a[k][0], a2[k][1] - a[k][1]) for k in keys]
chg = [(k, b[k][0] - a[k][0], b[k][1] - a[k][1]) for k in keys]
print(f"{len(keys)} headings, two passes each")
print(f"  the control (9368 run twice): smaller pass differs at {sum(1 for _k, lo, _h in ctl if lo)}, "
      f"larger at {sum(1 for _k, _l, hi in ctl if hi)}")
print(f"  the change (9369 against 9368): smaller pass differs at {sum(1 for _k, lo, _h in chg if lo)}, "
      f"larger at {sum(1 for _k, _l, hi in chg if hi)}")
moved = [(k, lo, hi) for k, lo, hi in chg if lo or hi]
print(f"  {'station':22s} {'yaw':>5s} {'passes 9368':>14s} {'smaller':>8s} {'larger':>7s} {'ms after-mean':>14s}")
for k, lo, hi in moved:
    base = (a[k][2] + a2[k][2]) / 2.0
    print(f"  {k[0]:22s} {k[1]:5.0f} {a[k][0]:6d}/{a[k][1]:<6d} {lo:+8d} {hi:+7d} {b[k][2] - base:+14.3f}")
los = [lo for _k, lo, _h in moved]
his = [hi for _k, _l, hi in moved]
if moved:
    print(f"  where either pass moved ({len(moved)} headings): smaller pass median {statistics.median(los):+.0f} "
          f"(min {min(los):+d}, max {max(los):+d}); larger pass median {statistics.median(his):+.0f} "
          f"(min {min(his):+d}, max {max(his):+d})")
    neg = [(k, lo, hi) for k, lo, hi in moved if lo < 0 or hi < 0]
    print(f"  headings where a pass draws FEWER after: {len(neg)}" +
          ("".join(f"\n    {k[0]} {k[1]:.0f}: {lo:+d} / {hi:+d}" for k, lo, hi in neg)))
