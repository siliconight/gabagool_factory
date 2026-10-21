"""Which part of 0.252.0 costs a route? Each variant of the dc_seats clone's furnish -- its features switched by
anchored text edits in a temp copy of the clone's modules -- refurnishes and shelters Deli Counter 0.251.0's library
(the factory's checkout, in memory) and censuses every spec (`docs/findings/furnish_route_cost/route_cost.py`), then
compares it pair by pair, by endpoints, with the factory's census of 0.251.0's library (`route_cost.json` there), and
counts the chairs. Writes variants_<name>.json beside this file and prints one summary line.

The features, all on in the clone (0.252.0 as first built):
  own    a host's chairs from its own stream, not the room's
  undo   a piece that seats one or more is undone when none of its chairs clears, and the next spot tried
  lo1    a dining table seats one to four, where it seated none to four
  every  a table tries every side, the first n that clear seated
and two that are not in it:
  first  every side tried only for a table's first chair: past its n drawn sides, a side is tried only while none
         has seated (needs `every`)
  tuck   no chair pulled out: every table chair 0.2 m off its table, where 40 % stood 0.3 to 0.55 m off

    python patches/dc_table_chairs/variants.py <name> <feature,feature,...> <dc_seats clone>
"""
import collections
import glob
import json
import os
import pathlib
import re
import shutil
import sys
import tempfile
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
FACTORY = HERE.parents[1]
name, features, clone = sys.argv[1], set(filter(None, sys.argv[2].split(","))), sys.argv[3]
assert features <= {"own", "undo", "lo1", "every", "first", "tuck"}, features
assert "first" not in features or "every" in features

# ---- the variant's modules: the clone's, its features switched off or on --------------------------------------
OFF = {
    "own": ('            srng = random.Random("%s:%s:%.2f:%.2f:seats" % (\n'
            '                base_seed, host["name"].rsplit("_", 1)[0], px, py))\n',
            '            srng = rng\n'),
    "undo": ("                        if lo >= 1 and not got:\n", "                        if False:\n"),
    "lo1": ('(1.6, 0.9, 0.74)), "floor", seats=("table", 1, 4)),', '(1.6, 0.9, 0.74)), "floor", seats=("table", 0, 4)),'),
    "every": ("                for ex, ey in long_sides + ends:\n",
              "                for ex, ey in (long_sides + ends)[:n]:\n"),
}
ON = {
    "first": ("                if n_set >= n:\n                    break\n",
              "                if n_set >= n or (j >= n and n_set >= 1):\n                    break\n"),
    "tuck": ("if srng.random() < 0.4", "if srng.random() < 0.0"),
}
tmp = tempfile.mkdtemp(prefix="dc_variant_%s_" % name)
for f in glob.glob(os.path.join(clone, "*.py")) + [os.path.join(clone, "agent_contract.json")]:
    shutil.copy2(f, tmp)
p = os.path.join(tmp, "level_design.py")
text = open(p, encoding="utf-8").read()
for feat, (old, new) in OFF.items():
    if feat not in features:
        assert text.count(old) == 1, (feat, text.count(old))
        text = text.replace(old, new)
for feat, (old, new) in ON.items():
    if feat in features:
        assert text.count(old) == 1, (feat, text.count(old))
        text = text.replace(old, new)
open(p, "w", encoding="utf-8", newline="\n").write(text)
sys.path.insert(0, tmp)
import level_design as L  # noqa: E402
import migrate_furnish_recipes  # noqa: E402,F401
import migrate_shelter  # noqa: E402
import partition_bounds  # noqa: E402,F401
import stairwell  # noqa: E402,F401
import spec_types  # noqa: E402,F401
sys.path.insert(0, str(FACTORY / "docs" / "findings" / "furnish_route_cost"))
import route_cost as R  # noqa: E402

assert os.path.samefile(R.L.__file__, p), R.L.__file__

# ---- refurnish and census 0.251.0's library ------------------------------------------------------------------
SEATED = {k: v["seats"] for k, v in L._PIECES.items() if v.get("seats")}
HOST = re.compile(r"^(?P<key>%s)_(?P<tag>r[0-9a-f]{8})_(?P<seq>\d+)$" % "|".join(sorted(SEATED, key=len, reverse=True)))
CHAIR = re.compile(r"^[a-z_]+?_(?P<tag>r[0-9a-f]{8})_(?P<seq>\d+)_\d+$")
t0 = time.time()
rows, chairless, chairs, pieces = [], collections.Counter(), collections.Counter(), 0
for sp in sorted(glob.glob(str(FACTORY / "deli_counter" / "specs" / "*.json"))):
    nm = os.path.basename(sp)[:-5]
    if nm.startswith("lf_"):
        continue
    d = json.load(open(sp, encoding="utf-8"))
    if not d.get("rooms"):
        continue
    migrate_furnish_recipes.migrate(d)
    migrate_shelter.migrate(d)
    rows.extend(R.measure_spec(d, nm))
    hosts, seen = {}, collections.Counter()
    for v in d["volumes"]:
        m = HOST.match(v["name"])
        if m:
            hosts[(m.group("tag"), m.group("seq"))] = m.group("key")
        m = CHAIR.match(v["name"])
        if m:
            seen[(m.group("tag"), m.group("seq"))] += 1
    for k, key in hosts.items():
        chairs[key] += seen[k]
        chairless[key] += seen[k] == 0
    tags = {L._room_tag(r) for r in d["rooms"]}
    pieces += sum(1 for v in d["volumes"] if migrate_furnish_recipes.furnished_by_this_pass(v, tags))


def pairs(rws):
    out = {}
    for r in rws:
        e = r["endpoints"]
        for a in range(len(e)):
            for b in range(a + 1, len(e)):
                k = "%d-%d" % (a, b)
                key = (r["spec"], r["room"], tuple(e[a][:2]) + tuple(round(x, 2) for x in e[a][2:4]),
                       tuple(e[b][:2]) + tuple(round(x, 2) for x in e[b][2:4]))
                out[key] = {arm: (r["arms"][arm]["length"].get(k), r["arms"][arm]["bottleneck"].get(k, 0.0))
                            for arm in r["arms"]}
    return out


base = pairs(json.load(open(FACTORY / "docs" / "findings" / "furnish_route_cost" / "route_cost.json",
                            encoding="utf-8")))
now = pairs(rows)
common = set(base) & set(now)
over_b = over_a = up = down = closed_b = closed_a = narrow_b = narrow_a = 0
excess_b = excess_a = 0.0
ratios = []
for k in common:
    (lfb, bfb), (lab, bab) = base[k]["furnished"], base[k]["authored"]
    (lfa, bfa), (laa, baa) = now[k]["furnished"], now[k]["authored"]
    if lfb and lab and lfa and laa:
        rb, ra = lfb / lab, lfa / laa
        ratios.append(ra)
        over_b += rb > 1.10
        over_a += ra > 1.10
        up += rb <= 1.10 < ra
        down += ra <= 1.10 < rb
        excess_b += lfb - lab
        excess_a += lfa - laa
    closed_b += bab >= R.C_BAKE > bfb
    closed_a += baa >= R.C_BAKE > bfa
    narrow_b += bab >= R.TWO_ABREAST > bfb
    narrow_a += baa >= R.TWO_ABREAST > bfa
v = np.array(ratios)
summary = {
    "variant": name, "features": sorted(features), "pairs": len(common), "seconds": round(time.time() - t0),
    "over_10pct": [over_b, over_a], "crossed_over": up, "came_back_under": down,
    "excess_m": [round(excess_b, 1), round(excess_a, 1)], "closed_to_bake": [closed_b, closed_a],
    "narrowed_to_single_file": [narrow_b, narrow_a], "p99": round(float(np.percentile(v, 99)), 3),
    "max": round(float(v.max()), 3), "pieces": pieces,
    "chairless": {k: chairless[k] for k in ("table_dining", "desk", "table_cocktail", "table_count")},
    "chairs": {k: chairs[k] for k in ("table_dining", "desk", "table_count")},
}
(HERE / ("variants_%s.json" % name)).write_text(json.dumps(summary, indent=1), encoding="utf-8", newline="\n")
print(json.dumps(summary))
shutil.rmtree(tmp, ignore_errors=True)
