"""Means over every station heading of three perf_stations reports, and the
pairwise differences: python perf_table.py <before.json> <after.json>
<before2.json>. Prints the table the findings quote; nothing else."""
import json
import pathlib
import statistics
import sys


def load(p):
    d = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    rows = []
    for st in d["rows"]:
        for h in st["headings"]:
            rows.append((st["station"], h["yaw"], h["ms_median"], h["ms_p95"], h["gpu_ms"], h["draws"]))
    lights = None
    lc = d["rows"][0].get("light_census") if d["rows"] else None
    if isinstance(lc, dict):
        lights = lc.get("lights") or lc.get("total") or lc.get("count")
    return d, rows, lights


def means(rows):
    return [statistics.fmean(r[i] for r in rows) for i in (2, 3, 4, 5)]


def main():
    tags = sys.argv[1:4]
    data = [load(t) for t in tags]
    print("| package | mean median ms | mean p95 ms | mean GPU ms | mean draws | headings |")
    print("|---|---|---|---|---|---|")
    for t, (d, rows, lights) in zip(tags, data):
        m = means(rows)
        print("| %s | %.2f | %.2f | %.2f | %.1f | %d |" % (pathlib.Path(t).stem, m[0], m[1], m[2], m[3], len(rows)))
    (_, a, _), (_, b, _), (_, c, _) = data
    key = lambda r: (r[0], r[1])
    ia = {key(r): r for r in a}
    ib = {key(r): r for r in b}
    ic = {key(r): r for r in c}
    common = [k for k in ia if k in ib and k in ic]
    for label, x, y, i in (("median ms, after minus before", ib, ia, 2), ("GPU ms,    after minus before", ib, ia, 4),
                           ("draws,     after minus before", ib, ia, 5), ("control, before2 minus before (median ms)", ic, ia, 2),
                           ("control, before2 minus before (GPU ms)", ic, ia, 4)):
        diffs = [x[k][i] - y[k][i] for k in common]
        print("    %-44s mean %+.2f  max |%.2f|" % (label, statistics.fmean(diffs), max(abs(v) for v in diffs)))
    print("    stations x headings compared: %d" % len(common))


if __name__ == "__main__":
    main()
