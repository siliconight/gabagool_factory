"""Compare `price.py`'s three reports heading by heading: the subject against the controls' mean, beside the controls'
own a - b (the instrument's floor). Reads perf_control_a.json, perf_control_b.json, perf_subject.json beside this file;
writes nothing; refuses a report it does not recognise.

    python docs/findings/bank_interior/compare.py
"""
import json
import pathlib
import statistics as st

HERE = pathlib.Path(__file__).resolve().parent


def load(tag):
    d = json.loads((HERE / ("perf_%s.json" % tag)).read_text(encoding="utf-8"))
    assert d.get("schema") == "level_factory.perf_stations.v1" and d.get("complete") is True, (tag, d.get("schema"))
    out = {}
    for row in d["rows"]:
        name = row.get("name") or row.get("station")
        assert name, ("a row without a station name", sorted(row))
        for h in row["headings"]:
            out[(name, h["yaw"])] = (h["draws"], h["ms_p95"])
    assert out, tag
    return out


a, b, s = load("control_a"), load("control_b"), load("subject")
keys = sorted(set(a) & set(b) & set(s))
assert keys and len(keys) == len(a) == len(b) == len(s), (len(keys), len(a), len(b), len(s))
dd = [s[k][0] - (a[k][0] + b[k][0]) / 2.0 for k in keys]
dp = [s[k][1] - (a[k][1] + b[k][1]) / 2.0 for k in keys]
fd = [a[k][0] - b[k][0] for k in keys]
fp = [a[k][1] - b[k][1] for k in keys]
print("headings:", len(keys))
print("draws, subject - controls' mean: median %+.1f, largest %+.1f, smallest %+.1f"
      % (st.median(dd), max(dd), min(dd)))
print("p95 ms, subject - controls' mean: median %+.3f, largest %+.3f, smallest %+.3f"
      % (st.median(dp), max(dp), min(dp)))
print("the controls' own a - b: draws median %+.1f, largest |%.1f|; p95 ms median %+.3f, largest |%.3f|"
      % (st.median(fd), max(abs(x) for x in fd), st.median(fp), max(abs(x) for x in fp)))
w = max(keys, key=lambda k: s[k][1])
print("the subject's worst heading: %s yaw %s -- draws %d (controls %d, %d), p95 %.2f ms (controls %.2f, %.2f)"
      % (w[0], w[1], s[w][0], a[w][0], b[w][0], s[w][1], a[w][1], b[w][1]))
for k in sorted(keys, key=lambda k: -abs(s[k][0] - (a[k][0] + b[k][0]) / 2.0))[:5]:
    print("  %-22s yaw %5s draws %5d vs %5d/%5d   p95 %6.2f vs %6.2f/%6.2f"
          % (k[0], k[1], s[k][0], a[k][0], b[k][0], s[k][1], a[k][1], b[k][1]))
