"""Roadmap 266's price: the fixed-station harness's reports for the control arm (twice) and the merged arm, side by
side -- draws and p95 frame time at every station and heading, and the lights-per-object census.

    python docs/findings/interior_merge_266/price_table.py <control_a.json> <control_b.json> <merged.json>

Reads `level_factory.perf_stations.v1` reports (`level_factory/tools/perf_stations_run.py`): `rows[]`, each with a
`station`, `pos` and `headings[]` of `yaw`, `draws`, `ms_p95`. A report of another shape, or two reports whose stations
or headings differ, FAIL: a table of two levels' stations is not a comparison. The two control runs are the same
bytes measured twice; their difference is the instrument's floor, and a merged-arm delta inside it is not a finding.
Prints what it measured and stops.
"""
import json
import statistics
import sys


def load(path):
    r = json.load(open(path, encoding="utf-8"))
    if r.get("schema") != "level_factory.perf_stations.v1" or not isinstance(r.get("rows"), list):
        raise SystemExit("UNRECOGNISED: %s is %r, not a level_factory.perf_stations.v1 report" % (path, r.get("schema")))
    out = {}
    for row in r["rows"]:
        for h in row["headings"]:
            out[(row["station"], float(h["yaw"]))] = (int(h["draws"]), float(h["ms_p95"]))
    lc = r["rows"][0].get("light_census") or {}
    return out, r.get("geometry") or {}, lc


def main(argv):
    (a, ga, la), (b, gb, lb), (m, gm, lm) = load(argv[0]), load(argv[1]), load(argv[2])
    if not (set(a) == set(b) == set(m)):
        raise SystemExit("MISMATCH: the three reports do not hold the same stations and headings")
    print("%-22s %5s %7s %7s %7s %8s %8s %8s %7s" % ("station", "yaw", "draws A", "draws B", "merged", "p95 A",
                                                    "p95 B", "merged", "d p95"))
    dd, dp, noise = [], [], []
    for k in sorted(a):
        da, pa = a[k]
        db, pb = b[k]
        dm, pm = m[k]
        ctl = (pa + pb) / 2.0
        dd.append(dm - (da + db) / 2.0)
        dp.append(pm - ctl)
        noise.append(abs(pa - pb))
        print("%-22s %5.0f %7d %7d %7d %8.2f %8.2f %8.2f %+7.2f" % (k[0], k[1], da, db, dm, pa, pb, pm, pm - ctl))
    n = len(a)
    print()
    print("%d station-headings. Draws: control %d and %d in all, merged %d (%+.1f a heading, median %+.0f, most %+d)"
          % (n, sum(v[0] for v in a.values()), sum(v[0] for v in b.values()), sum(v[0] for v in m.values()),
             statistics.mean(dd), statistics.median(dd), int(min(dd))))
    print("p95: control means %.3f and %.3f ms, merged %.3f ms; merged minus the controls' mean %+.3f ms a heading "
          "(median %+.3f); the controls differ by %.3f ms a heading (median %.3f, most %.3f) -- the floor"
          % (statistics.mean(v[1] for v in a.values()), statistics.mean(v[1] for v in b.values()),
             statistics.mean(v[1] for v in m.values()), statistics.mean(dp), statistics.median(dp),
             statistics.mean(noise), statistics.median(noise), max(noise)))
    worst = lambda d: max(d.items(), key=lambda kv: kv[1][1])
    for name, d in (("control A", a), ("control B", b), ("merged", m)):
        k, (dr, p) = worst(d)
        print("worst heading, %-9s: %s yaw %.0f -- %.2f ms p95, %d draws" % (name, k[0], k[1], p, dr))
    for name, g in (("control A", ga), ("control B", gb), ("merged", gm)):
        print("%-9s: %s mesh instances, %s nodes, video memory %.1f MiB" % (
            name, g.get("mesh_instances"), g.get("nodes"), (g.get("video_mem_bytes") or 0) / 1048576.0))
    for name, lc in (("control A", la), ("control B", lb), ("merged", lm)):
        p = lc.get("paired") or {}
        print("%-9s lights per object: by reach %s of %s meshes over the cap of %s; paired %s over, %s lightmap users"
              % (name, lc.get("over_cap"), lc.get("meshes"), lc.get("cap"), p.get("over_cap"),
                 p.get("lightmap_users")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
