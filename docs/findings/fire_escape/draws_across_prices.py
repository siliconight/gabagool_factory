"""Draws per heading for cold runs 9302, 9303 and 9304, read across the fire escape's two prices (roadmap 156).

    python docs/findings/fire_escape/draws_across_prices.py > docs/findings/fire_escape/draws_9302_9304.out.txt

`price/` priced 9303 against 9302 (9302 the control twice); `price_9304/` priced 9304 against 9303 (9303 the control
twice). Draw counts are exact, so 9302 against 9304 can be read across the two -- IF 9303, measured in both, reads
the same at every heading, which this checks first and prints. Frame times are not compared across prices.
Prints what it measured and stops; a report in a shape it does not know stops it.
"""
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def tab(rel):
    d = json.loads((HERE / rel).read_text(encoding="utf-8"))
    if d.get("schema") != "level_factory.perf_stations.v1" or not d.get("complete"):
        raise SystemExit("UNKNOWN SHAPE: %s" % rel)
    return {(r["station"], h["yaw"]): h for r in d["rows"] for h in r["headings"]}


a = tab("price/perf_control_1.json")          # 9302
c1 = tab("price/perf_control_2.json")         # 9302 again
b = tab("price/perf_glow.json")               # 9303
m = tab("price_9304/perf_glow.json")          # 9304
m2 = tab("price_9304/perf_control_1.json")    # 9303, measured again in the 9304 price
if not set(a) == set(b) == set(m) == set(m2) == set(c1):
    raise SystemExit("STATIONS DIFFER between the prices")
print("draws per heading, exact counts, 53 headings; 9302 and 9303 from the 9303 price, 9304 from the 9304 price")
print("the instrument across the two prices: 9303 measured in each, headings whose draws differ: %d"
      % sum(1 for k in a if b[k]["draws"] != m2[k]["draws"]))
print("9302 measured twice in the 9303 price, headings whose draws differ: %d"
      % sum(1 for k in a if a[k]["draws"] != c1[k]["draws"]))
for name, x in (("9303 - 9302 (unmerged)", b), ("9304 - 9302 (merged)", m)):
    d = [x[k]["draws"] - a[k]["draws"] for k in sorted(a, key=str)]
    print("%-24s mean %+.1f  least %+d  most %+d  histogram %s"
          % (name, sum(d) / len(d), min(d), max(d), sorted(Counter(d).items())))
d = sorted(((m[k]["draws"] - a[k]["draws"], b[k]["draws"] - a[k]["draws"], k) for k in a),
           key=lambda t: (-t[0], str(t[2])))
print("the five headings the merged fire escape costs most against 9302 (merged, unmerged, heading):")
for t in d[:5]:
    print("   %+3d  %+3d  %s %s" % (t[0], t[1], t[2][0], t[2][1]))
