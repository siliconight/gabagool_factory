import json, os, sys
from collections import Counter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "pixelcoat", "build")
WANT = "0.16.0"
vers, kinds, n = Counter(), set(), 0
for dp, dns, fns in os.walk(BUILD):
    for fn in fns:
        if not fn.endswith(".pack.json"):
            continue
        n += 1
        with open(os.path.join(dp, fn), "r", encoding="utf-8") as fh:
            d = json.load(fh)
        vers[d.get("tool_version")] += 1
        if d.get("material_kind"):
            kinds.add(d["material_kind"])
print("packs read: %d" % n)
if n == 0:
    print("REFUSING TO CONCLUDE -- zero packs found under %s" % BUILD)
    sys.exit(2)
for v, c in vers.most_common():
    print("  tool_version %-10s %d pack(s)" % (v, c))
print("distinct material_kind values: %d" % len(kinds))
print("  %s" % ", ".join(sorted(kinds)))
bad = {v: c for v, c in vers.items() if v != WANT}
if bad:
    print("STAMP MISMATCH -- expected every pack to say %s, found %s" % (WANT, bad))
    sys.exit(1)
print("ALL %d PACKS STAMPED %s" % (n, WANT))
