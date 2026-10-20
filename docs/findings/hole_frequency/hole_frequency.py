"""How often a generated LEVEL carries a hole in a floor, mission by mission. A probe: prints what it measured and stops.

The walker, 2026-10-20: "stairs and ladders should be the primary way to get between floors in this game...with the
holes in floors being somewhat rare...but still at our disposal to use if needed/desired to add some more ways to
navigate levels". Rarity is a property of levels, not of specs, so this counts per level.

WHAT A HOLE IS HERE. A vertical link Deli Counter judged a drop carries a `cause` key in the built gameplay record
(`deli_counter.py` `_vertical_links`, 0.236.0); a roof hatch carries none. A drop whose cause is `stair` opens into a
stair's own well and adds no hole of its own, so it is not counted. Everything else is a hole a player sees: `cut`,
`broken`, `hatch`, and an uncaused drop (no cause found -- a bare hole, layout_lint L28).

WHERE A LEVEL'S BUILDINGS COME FROM.
  * A brief with `building_count` 2 or more draws a lot from Deli Counter's built library: replayed here with Level
    Factory's own `building_library.lot_for_brief(themed=True)` over the staged brief's candidate seeds
    (`seed_base + 101 k`, as a batch's are) -- the replay `docs/findings/hole_causes_265/lot_replay.py --check 9328`
    reproduced three graded lots of three. The Empties a lot also places carry no drop.
  * A brief with `building_count` 1 builds its own building from Deli Counter's preset per candidate, `lf_<mission>_
    <seed>`, which is not in the library when this runs. Those rows come from `census_holes.json` (the factory's
    `docs/findings/hole_causes_265/`, built 2026-10-20 while the transients were on disk) and say which drops the
    preset gives every candidate; they are labelled as such.

    python docs/findings/hole_frequency/hole_frequency.py [--seeds N] [--json OUT] [--lf DIR]

`--lf` replays with another Level Factory checkout (a clone carrying a change, say): its `building_library` draws the
lots. When that module has `holes_wanted` (0.221.0, roadmap 269), a single-building mission's line also says how many
of its candidates the rate leaves their preset's holes.
"""
import argparse
import collections
import glob
import json
import os
import re
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
_LF = sys.argv[sys.argv.index("--lf") + 1] if "--lf" in sys.argv else os.path.join(F, "level_factory")
sys.path.insert(0, _LF)
from packages.pipeline import building_library as bl  # noqa: E402

LIB = os.path.join(F, "deli_counter", "build")
TRANSIENTS = os.path.join(F, "docs", "findings", "hole_causes_265", "census_holes.json")


def holes_of(spec):
    """[(kind, cause, role)] of the drops in a built spec a player sees as a hole."""
    p = os.path.join(LIB, spec + ".gameplay.json")
    g = json.load(open(p, encoding="utf-8"))
    if "vertical_links" not in g:
        raise SystemExit("UNKNOWN SHAPE: %s has no vertical_links (keys %s)" % (p, sorted(g)))
    return [(v.get("kind"), v.get("cause"), v.get("role")) for v in g["vertical_links"]
            if "cause" in v and v.get("cause") != "stair"]


def briefs():
    latest = {}
    for p in glob.glob(os.path.join(F, "docs", "cold_runs", "cold_*", "briefs", "*.json")):
        n = int(re.search(r"cold_(\d+)", p).group(1))
        key = os.path.basename(p)[:-5]
        if key not in latest or n > latest[key][0]:
            latest[key] = (n, p)
    return latest


ap = argparse.ArgumentParser()
ap.add_argument("--seeds", type=int, default=12)
ap.add_argument("--json", default=None)
ap.add_argument("--lf", default=None, help="a Level Factory checkout to draw with")
a = ap.parse_args()
print("[draw] Level Factory at %s, version %s" % (_LF, open(os.path.join(_LF, "VERSION"), encoding="utf-8").read().strip()))

lib_holes = {}
for p in glob.glob(os.path.join(LIB, "*.gameplay.json")):
    s = os.path.basename(p)[:-len(".gameplay.json")]
    h = holes_of(s)
    if h:
        lib_holes[s] = h
fit, unfit = bl.themed_report(bl.index(LIB)[0])
fit_ids = {e["id"] for e in fit}
print("[library] %d built specs carry a hole a player sees; %d of them in the %d shells a themed lot can draw:"
      % (len(lib_holes), len(set(lib_holes) & fit_ids), len(fit_ids)))
for s in sorted(lib_holes):
    print("    %-24s %-5s %s" % (s, "lot" if s in fit_ids else "-", lib_holes[s]))

trans = collections.defaultdict(list)
for r in json.load(open(TRANSIENTS, encoding="utf-8")):
    if "kind" in r and r["spec"].startswith("lf_") and r.get("cause") != "stair":
        m = re.match(r"lf_(.+)_(\d+)$", r["spec"])
        trans[m.group(1)].append((m.group(2), r["kind"], r.get("cause"), r.get("role")))

out = {"library": lib_holes, "missions": {}}
print("\n[missions] the latest staged brief of each, %d candidate seeds a lot mission" % a.seeds)
print("    %-26s %-22s %-6s %-10s %-9s %s" % ("mission", "archetype", "count", "levels", "holes", "which"))
for mission, (n, p) in sorted(briefs().items()):
    b = json.load(open(p, encoding="utf-8"))
    if "building_count" not in b or "archetype" not in b:
        raise SystemExit("UNKNOWN SHAPE: %s has no building_count / archetype" % p)
    count = int(b["building_count"] or 1)
    if count < 2:
        rows = trans.get(mission, [])
        seeds = sorted({r[0] for r in rows})
        per_seed = collections.Counter(r[0] for r in rows)
        levels = "every" if rows else "none seen"
        if rows and hasattr(bl, "holes_wanted"):
            batch = json.load(open(os.path.join(os.path.dirname(os.path.dirname(p)), "batch.json"), encoding="utf-8"))
            rate = bl.floor_hole_rate(types.SimpleNamespace(floor_holes=b.get("floor_holes")))
            kept = sum(bl.holes_wanted("%s.candidate.seed_%d" % (mission, int(batch["seed_base"]) + 101 * k), rate)
                       for k in range(a.seeds))
            levels = "%d of %d" % (kept, a.seeds)
        print("    %-26s %-22s %-6s %-10s %-9s %s" % (
            mission, b["archetype"], count, levels,
            "%d-%d a level" % (min(per_seed.values()), max(per_seed.values())) if rows else "-",
            "the preset, from %d built transients: %s" % (len(seeds), sorted({r[1:] for r in rows})) if rows
            else "no transient of it in census_holes.json"))
        out["missions"][mission] = {"path": "single", "transients": rows}
        continue
    batch = json.load(open(os.path.join(os.path.dirname(os.path.dirname(p)), "batch.json"), encoding="utf-8"))
    model = types.SimpleNamespace(lot_library=LIB, building_count=count, archetype=b["archetype"],
                                  cluster=b.get("cluster", ""))
    base = int(batch["seed_base"])
    per, which = [], collections.Counter()
    for k in range(a.seeds):
        seed = base + 101 * k
        lot, _inc = bl.lot_for_brief(model, "%s.candidate.seed_%d" % (mission, seed), themed=True)
        names = [os.path.basename(e["glb"])[:-4] for e in lot]
        hs = [(nm, h) for nm in names for h in lib_holes.get(nm, [])]
        per.append(len(hs))
        for nm, h in hs:
            which["%s %s" % (nm, h[1] or "uncaused")] += 1
    with_hole = sum(1 for x in per if x)
    print("    %-26s %-22s %-6s %-10s %-9s %s" % (mission, b["archetype"], count, "%d of %d" % (with_hole, a.seeds),
                                                 "%.2f a level" % (sum(per) / len(per)), dict(which)))
    out["missions"][mission] = {"path": "lot", "seed_base": base, "holes_per_level": per, "which": dict(which)}
if a.json:
    json.dump(out, open(a.json, "w", encoding="utf-8"), indent=1, sort_keys=True)
