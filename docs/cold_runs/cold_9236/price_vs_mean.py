"""Per-heading price of a subject against its two controls' mean (the 9227 reading).

    python price_vs_mean.py <price dir>     # perf_control_1.json, perf_glow.json, perf_control_2.json

Headings are matched by (station, yaw), never by order: the harness's reports list stations in
the order they were measured, which differs between runs. Prints a row a heading -- the draws and
the p95 of the two controls and the subject, the subject's difference from the controls' mean, and
the two passes' draws of each run -- then the medians. A heading is flagged FLIP when its two
passes of one run disagree by more than 100 draws: an occlusion edge the nudge tips either way,
whose report takes the first pass, so a delta there is the flip's and not the subject's unless all
three runs fell the same way (`split_perturbed` is set on every heading and is not the flag).
"""
import json
import statistics as st
import sys


def heads(d, name):
    rows = json.load(open(f"{d}/perf_{name}.json", encoding="utf-8"))["rows"]
    out = {}
    for r in rows:
        for h in r["headings"]:
            out[(r["station"], float(h["yaw"]))] = (
                h["draws"], h["ms_p95"], [p["draws"] for p in h["passes"]], h.get("pass_spread_ms"))
    return out


def main(d):
    c1, c2, g = heads(d, "control_1"), heads(d, "control_2"), heads(d, "glow")
    assert set(c1) == set(c2) == set(g), (len(c1), len(c2), len(g))
    dd, dm, cc = [], [], []
    for k in sorted(g):
        a, b, s = c1[k], c2[k], g[k]
        cd = (a[0] + b[0]) / 2.0
        cm = (a[1] + b[1]) / 2.0
        dd.append(s[0] - cd)
        dm.append(s[1] - cm)
        cc.append(abs(a[1] - b[1]))
        flip = any(len(p) > 1 and abs(p[0] - p[1]) > 100 for p in (a[2], b[2], s[2]))
        print(f"{k[0]:<22} yaw {k[1]:>5}  draws c {a[0]:>5} {b[0]:>5} s {s[0]:>5} {s[0] - cd:+7.1f}   "
              f"p95 c {a[1]:.2f} {b[1]:.2f} s {s[1]:.2f} {s[1] - cm:+.2f}   passes s {s[2]} c1 {a[2]} c2 {b[2]}"
              f"{'  FLIP' if flip else ''}")
    print("draws vs controls' mean: median %.1f  min %.1f  max %.1f" % (st.median(dd), min(dd), max(dd)))
    print("p95 ms vs controls' mean: median %+.2f  min %+.2f  max %+.2f" % (st.median(dm), min(dm), max(dm)))
    print("controls between themselves, p95 |c1-c2|: median %.2f  max %.2f" % (st.median(cc), max(cc)))
    print("frame p95 at the controls' mean, median over headings: %.2f ms"
          % st.median((c1[k][1] + c2[k][1]) / 2.0 for k in g))
    spread = st.median(cc)
    print("headings with p95 delta over the controls' %.2f ms spread: %d of %d; over 0.10 ms: %d"
          % (spread, sum(1 for x in dm if x > spread), len(dm), sum(1 for x in dm if x > 0.10)))


if __name__ == "__main__":
    main(sys.argv[1])
