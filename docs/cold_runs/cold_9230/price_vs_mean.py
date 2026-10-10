"""Per-heading price of a subject against its two controls' mean (the 9227 reading)."""
import json, statistics as st, sys
d = sys.argv[1]
def heads(n):
    rows = json.load(open(f"{d}/perf_{n}.json", encoding="utf-8"))["rows"]
    out = []
    for r in rows:
        for h in r["headings"]:
            out.append((r["station"], h["yaw"], h["draws"], h["ms_p95"], h.get("split_perturbed"), h.get("pass_spread_ms"), [p["draws"] for p in h["passes"]]))
    return out
c1, c2, g = heads("control_1"), heads("control_2"), heads("glow")
assert len(c1) == len(c2) == len(g)
dd, dm = [], []
for a, b, s in zip(c1, c2, g):
    assert a[0] == b[0] == s[0] and a[1] == b[1] == s[1]
    cd = (a[2] + b[2]) / 2; cm = (a[3] + b[3]) / 2
    dd.append(s[2] - cd); dm.append(s[3] - cm)
    flag = " FLIP" if (s[4] or a[4] or b[4]) else ""
    print(f"{a[0]:<22} yaw {a[1]:>5}  draws c {a[2]:>5} {b[2]:>5}  s {s[2]:>5}  +{s[2]-cd:>6.1f}   p95 c {a[3]:.2f} {b[3]:.2f} s {s[3]:.2f} {s[3]-cm:+.2f}  passes s {s[6]} c1 {a[6]}{flag}")
print("draws vs controls' mean: median %.1f  min %.1f  max %.1f" % (st.median(dd), min(dd), max(dd)))
print("p95 ms vs controls' mean: median %+.2f  min %+.2f  max %+.2f" % (st.median(dm), min(dm), max(dm)))
print("controls between themselves, p95 |c1-c2| median %.2f max %.2f" % (st.median(abs(a[3]-b[3]) for a,b in zip(c1,c2)), max(abs(a[3]-b[3]) for a,b in zip(c1,c2))))
print("frame p95 control mean median %.2f ms" % st.median((a[3]+b[3])/2 for a,b in zip(c1,c2)))
