"""Route by route, what a clone did over the specs it changed: the factory's census (its version read from its own
header line; `docs/findings/furnish_route_cost/route_cost.json`) against `census_changed.py`'s json of the clone
(argv[1]).
A pair is matched by its two endpoints (kind, label and position), not its index. Per arm ratio -- FURNISHED /
AUTHORED, all of furnishing, and FURNISHED / FUNCTIONAL, the dressing alone -- it counts the pairs that crossed over
the guide's 10 % and those that came back under it, and sums every pair's excess over its authored length (metres a
body walks more, summed); and the pairs whose furnished bottleneck crossed two abreast either way. Writes
pairs_compare.out.txt beside this file.

    python patches/dc_marker_routes/pairs_compare.py <census_changed json>
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
F = HERE.parents[1]
sys.path.insert(0, str(F / "docs" / "findings" / "furnish_route_cost"))
import route_cost as R  # noqa: E402

after = json.load(open(sys.argv[1], encoding="utf-8"))
FIND = F / "docs" / "findings" / "furnish_route_cost"
BASE = open(FIND / "route_cost.out.txt", encoding="utf-8").readline()
BASE = BASE.split(" over ", 1)[1].split("'s library", 1)[0] if " over " in BASE else "the factory's census"
specs = {r["spec"] for r in after}
before = [r for r in json.load(open(F / "docs/findings/furnish_route_cost/route_cost.json", encoding="utf-8"))
          if r["spec"] in specs]


def pairs(rows):
    out = {}
    for r in rows:
        e = r["endpoints"]
        for p in range(len(e)):
            for q in range(p + 1, len(e)):
                k = "%d-%d" % (p, q)
                key = (r["spec"], r["room"], tuple(e[p][:2]) + tuple(round(v, 2) for v in e[p][2:4]),
                       tuple(e[q][:2]) + tuple(round(v, 2) for v in e[q][2:4]))
                arms = {a: (r["arms"][a]["length"].get(k), r["arms"][a]["bottleneck"].get(k, 0.0))
                        for a in r["arms"]}
                out[key] = arms
    return out


b, a = pairs(before), pairs(after)
common = sorted(set(b) & set(a))
lines = [("== the %d specs the clone changed: %d pairs in the census of " + BASE + ", %d in the clone's, %d matched by "
          "their endpoints")
         % (len(specs), len(b), len(a), len(common))]
for num, den, what in (("furnished", "authored", "FURNISHED / AUTHORED, all of furnishing"),
                       ("furnished", "functional", "FURNISHED / FUNCTIONAL, the dressing alone")):
    up, down, ex_b, ex_a, worse = 0, 0, 0.0, 0.0, []
    for k in common:
        if den not in b[k] or den not in a[k]:
            continue
        (lb, _), (db, _) = b[k][num], b[k][den]
        (la, _), (da, _) = a[k][num], a[k][den]
        if not (lb and db and la and da):
            continue
        rb, ra = lb / db, la / da
        ex_b += lb - db
        ex_a += la - da
        if rb <= 1.10 < ra:
            up += 1
            worse.append((ra - rb, k, rb, ra))
        elif ra <= 1.10 < rb:
            down += 1
    lines.append("%s: over 10 %% %d pairs came back under, %d crossed over; excess over the denominator summed "
                 "%.1f m -> %.1f m" % (what, down, up, ex_b, ex_a))
    for d, k, rb, ra in sorted(worse, reverse=True):
        lines.append("    crossed over: %s %s  %s -> %s  %.3f -> %.3f" % (k[0], k[1], k[2][1], k[3][1], rb, ra))
lost, gained = [], []
for k in common:
    bb, ba = b[k]["furnished"][1], a[k]["furnished"][1]
    if bb >= R.TWO_ABREAST > ba:
        lost.append(k)
    elif ba >= R.TWO_ABREAST > bb:
        gained.append(k)
lines.append("furnished bottleneck: two abreast -> single file %d pairs, single file -> two abreast %d pairs"
             % (len(lost), len(gained)))
for k in lost:
    lines.append("    narrowed: %s %s  %s -> %s  %.2f -> %.2f m wide" % (k[0], k[1], k[2][1], k[3][1],
                                                                       2 * b[k]["furnished"][1],
                                                                       2 * a[k]["furnished"][1]))
txt = "\n".join(lines) + "\n"
(HERE / "pairs_compare.out.txt").write_text(txt, encoding="utf-8", newline="\n")
print(txt)
