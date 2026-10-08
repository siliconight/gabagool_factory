"""The headings that see the getaway van: where the 'off' package draws fewer
than the 'on' one, with each heading's frame-time difference beside the
control's at the same heading. Prints what it measured and stops.

    python van_headings.py van_on.json van_on2.json van_off.json
"""
import json
import sys


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


a, a2, b = (load(p) for p in sys.argv[1:4])
keys = sorted(set(a) & set(a2) & set(b))
seen = [k for k in keys if b[k]["draws"] != a[k]["draws"]]
print(f"{len(keys)} headings; the van is drawn at {len(seen)} (off draws fewer)")
print(f"  {'station':22s} {'yaw':>5s} {'draws on':>9s} {'off-on':>7s} "
      f"{'on ms':>7s} {'off-mean ms':>12s} {'control ms':>11s} {'p95 off-mean':>13s}")
for k in seen:
    base = (a[k]["ms_median"] + a2[k]["ms_median"]) / 2.0
    base95 = (a[k]["ms_p95"] + a2[k]["ms_p95"]) / 2.0
    print(f"  {k[0]:22s} {k[1]:5.0f} {a[k]['draws']:9d} {b[k]['draws'] - a[k]['draws']:+7d} "
          f"{base:7.3f} {b[k]['ms_median'] - base:+12.3f} {a2[k]['ms_median'] - a[k]['ms_median']:+11.3f} "
          f"{b[k]['ms_p95'] - base95:+13.3f}")
others = [k for k in keys if k not in seen]
d_seen = [b[k]["ms_median"] - (a[k]["ms_median"] + a2[k]["ms_median"]) / 2.0 for k in seen]
d_rest = [b[k]["ms_median"] - (a[k]["ms_median"] + a2[k]["ms_median"]) / 2.0 for k in others]
ctl = [a2[k]["ms_median"] - a[k]["ms_median"] for k in keys]
if d_seen:
    print(f"  where it is drawn: off - mean(on) median ms, mean {sum(d_seen) / len(d_seen):+.3f} "
          f"(n {len(d_seen)}); elsewhere mean {sum(d_rest) / max(1, len(d_rest)):+.3f} (n {len(d_rest)}); "
          f"control spread {min(ctl):+.3f} to {max(ctl):+.3f}")
