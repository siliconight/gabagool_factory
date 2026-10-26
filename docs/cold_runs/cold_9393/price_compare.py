"""Compare `price.py`'s three arms heading by heading: draws and median frame time against `ctrl`, with `ctrl2` (the
same package priced again) as the instrument's spread. Prints per-arm totals and the paired differences; fails on a
report whose shape it does not recognise. Measurements only.

    python docs/cold_runs/cold_9393/price_compare.py
"""
import json
import pathlib
import statistics

HERE = pathlib.Path(__file__).resolve().parent
ARMS = ("ctrl", "lf0242", "ctrl2")


def headings(arm):
    d = json.loads((HERE / ("price_%s.json" % arm)).read_text(encoding="utf-8"))
    assert d.get("schema") == "level_factory.perf_stations.v1" and d.get("complete") is True, (arm, d.get("schema"))
    out = {}
    for i, row in enumerate(d["rows"]):
        key_row = row.get("station") or row.get("name") or row.get("anchor") or str(i)
        for h in row["headings"]:
            out[(str(key_row), float(h["yaw"]))] = (int(h["draws"]), float(h["ms_median"]), float(h["ms_p95"]))
    assert out, arm
    return out


H = {a: headings(a) for a in ARMS}
keys = sorted(set.intersection(*(set(v) for v in H.values())))
print("headings in every arm: %d (of %s)" % (len(keys), {a: len(v) for a, v in H.items()}))
for a in ARMS:
    print("%-6s draws total %7d  median ms mean %.3f  p95 ms mean %.3f" % (
        a, sum(H[a][k][0] for k in keys), statistics.mean(H[a][k][1] for k in keys),
        statistics.mean(H[a][k][2] for k in keys)))
for a in ("ctrl2", "lf0242"):
    dd = [H[a][k][0] - H["ctrl"][k][0] for k in keys]
    dm = [H[a][k][1] - H["ctrl"][k][1] for k in keys]
    print("%-6s - ctrl: draws %+d total (min %+d, max %+d a heading); median ms mean %+.3f, median of diffs %+.3f, "
          "max %+.3f" % (a, sum(dd), min(dd), max(dd), statistics.mean(dm), statistics.median(dm), max(dm)))
