"""Compare perf_stations reports: per station, mean over headings of draws
and median frame ms, for a control pair (same package twice) and a change.

    python compare_prices.py <control_a.json> <control_b.json> <change.json>

Prints what it measured: per-station draws (control a, b, change) and median
ms; the control pair's spread is the instrument's floor. No cause is named.
Refuses a report whose shape it does not recognise.
"""
import json
import statistics
import sys


def load(p):
    d = json.load(open(p, encoding="utf-8"))
    if not d.get("complete") or not isinstance(d.get("rows"), list):
        raise SystemExit(f"{p}: incomplete or unrecognised report")
    out = {}
    for r in d["rows"]:
        hs = r.get("headings")
        if not hs or "draws" not in hs[0] or "ms_median" not in hs[0]:
            raise SystemExit(f"{p}: station {r.get('station')} has no draws/ms_median")
        out[r["station"]] = (statistics.mean(h["draws"] for h in hs),
                             statistics.mean(h["ms_median"] for h in hs),
                             statistics.mean(h["ms_p95"] for h in hs))
    return d["geometry"], out


ga, a = load(sys.argv[1])
gb, b = load(sys.argv[2])
gc, c = load(sys.argv[3])
print("geometry  control a:", ga, "\n          control b:", gb, "\n          change   :", gc)
print(f"{'station':28s} {'draws a':>8s} {'draws b':>8s} {'draws chg':>9s} | {'ms a':>6s} {'ms b':>6s} {'ms chg':>6s} {'chg-mean(a,b)':>13s} {'|a-b|':>6s} | p95 chg")
rows = []
for st in a:
    if st not in b or st not in c:
        continue
    da, ma, pa = a[st]
    db, mb, pb = b[st]
    dc, mc, pc = c[st]
    ctrl = (ma + mb) / 2.0
    rows.append((dc - (da + db) / 2.0, mc - ctrl, abs(ma - mb)))
    print(f"{st:28s} {da:8.1f} {db:8.1f} {dc:9.1f} | {ma:6.2f} {mb:6.2f} {mc:6.2f} {mc - ctrl:+13.2f} {abs(ma - mb):6.2f} | {pc:6.2f}")
print(f"\nover {len(rows)} stations: draws change - control mean {statistics.mean(r[0] for r in rows):+.1f}; "
      f"median ms change - control mean {statistics.mean(r[1] for r in rows):+.3f}; "
      f"control |a-b| mean {statistics.mean(r[2] for r in rows):.3f}, max {max(r[2] for r in rows):.3f}")
