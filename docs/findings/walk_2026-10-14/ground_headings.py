"""The ground's price, heading by heading (roadmap 252): where the shaded ground costs what.

Reads a price's three reports (`perf_control_1.json`, `perf_glow.json`, `perf_control_2.json`, the fixed-station
harness's `level_factory.perf_stations.v1`) and prints, for every heading, the subject's draws and p95 against
the two controls' mean, sorted by the p95 difference; then how many headings sit outside the controls' own
spread at that heading. Measures and stops.

    python docs/findings/walk_2026-10-14/ground_headings.py docs/findings/walk_2026-10-14/ground_shaded [N]
"""
import json
import pathlib
import sys


def headings(doc):
    if doc.get("schema") != "level_factory.perf_stations.v1" or not doc.get("complete"):
        raise SystemExit("UNKNOWN SHAPE: schema %r, complete %r" % (doc.get("schema"), doc.get("complete")))
    out = {}
    for row in doc.get("rows") or []:
        for h in row.get("headings") or []:
            if "draws" not in h or "ms_p95" not in h:
                raise SystemExit("UNKNOWN SHAPE: a heading without draws or ms_p95: %r" % sorted(h))
            out[(row.get("station"), h.get("yaw"))] = (int(h["draws"]), float(h["ms_p95"]))
    if not out:
        raise SystemExit("UNKNOWN SHAPE: no headings")
    return out


def main():
    out = pathlib.Path(sys.argv[1])
    top = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    c1, g, c2 = (headings(json.loads((out / ("perf_%s.json" % n)).read_text(encoding="utf-8")))
                 for n in ("control_1", "glow", "control_2"))
    rows = []
    for k in c1:
        cd = (c1[k][0] + c2[k][0]) / 2.0
        cm = (c1[k][1] + c2[k][1]) / 2.0
        spread = abs(c1[k][1] - c2[k][1])
        rows.append((g[k][1] - cm, g[k][0] - cd, spread, k, c1[k], g[k], c2[k]))
    rows.sort(key=lambda r: -r[0])
    print("%-28s %5s %8s %8s %8s %8s %8s %8s %7s" % ("station:yaw", "+drw", "c1 p95", "sub p95", "c2 p95",
                                                      "+p95", "spread", "c1 drw", "sub drw"))
    for dm, dd, spread, k, a, s, b in rows[:top]:
        print("%-28s %+5.1f %8.2f %8.2f %8.2f %+8.2f %8.2f %8d %7d" % (
            "%s:%s" % k, dd, a[1], s[1], b[1], dm, spread, a[0], s[0]))
    beyond = [r for r in rows if r[0] > r[2] and r[0] > 0]
    print("headings where the subject's p95 exceeds the controls' mean by more than their own spread: %d of %d"
          % (len(beyond), len(rows)))
    print("draws added: min %+d, median %+.1f, max %+d" % (
        min(r[1] for r in rows), sorted(r[1] for r in rows)[len(rows) // 2], max(r[1] for r in rows)))


if __name__ == "__main__":
    main()
