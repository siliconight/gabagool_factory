"""Which buildings a mission's lot places, replayed offline: Level Factory's own `building_library.lot_for_brief`
over a staged brief and a run of candidate seeds, against Deli Counter's built library.

A probe: prints what it measured and stops. Used to find a seed whose lot holds a building with a `broken` or a
`hatch` floor hole, so a cold run can prove those causes in a shipped package (roadmap 265). The library is the one
the site log names (`deli_counter/build`); the seed base is the staged batch's; candidate seeds step by 101, as a
batch's do. The lot is drawn with `themed=True`, the pool the cold runs' site log reports for both legs ("102 of 127
shell(s) can carry a theme -- keyed on the brief, so this is the same pool in every invocation").

REFUTED, KEPT: the first replay also drew `themed=False` and found a different lot for every precinct seed, which read
as "the walk test grades one lot and the package ships another". Cold run 9328's driver log and art log say otherwise
-- the art leg dressed exactly the buildings its shell leg graded -- and `--check 9328` below reproduces all three
of its graded lots with `themed=True`. The unthemed draw is not one Level Factory makes.

    python docs/findings/hole_causes_265/lot_replay.py [--seeds N]        # every staged brief, N seeds each
    python docs/findings/hole_causes_265/lot_replay.py --check 9328       # replay a run's candidates, compare
"""
import argparse
import glob
import json
import os
import re
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(F, "level_factory"))
from packages.pipeline import building_library as bl  # noqa: E402

LIB = os.path.join(F, "deli_counter", "build")
HOLES = {"rowhouse_raid": "broken; its hatch the stair's", "apartment_walkup_a01": "broken + hatch",
         "07_police_station": "hatch", "pvp_station_ref": "hatch", "warehouse_a02": "hatch",
         "corner_deli_heist_01": "cut + hatch", "cr_deli": "cut + hatch", "night_deli": "cut + hatch",
         "deli_a01": "cut", "deli_a02": "cut", "deli_a03": "cut", "foundry_heist_vertical": "hatch; one uncaused"}


def _model(brief_path):
    b = json.load(open(brief_path, encoding="utf-8"))
    if "building_count" not in b or "archetype" not in b:
        raise SystemExit("UNKNOWN SHAPE: %s has no building_count / archetype (keys %s)" % (brief_path, sorted(b)))
    batch = json.load(open(os.path.join(os.path.dirname(os.path.dirname(brief_path)), "batch.json"), encoding="utf-8"))
    if "seed_base" not in batch:
        raise SystemExit("UNKNOWN SHAPE: %s's batch has no seed_base" % brief_path)
    return (types.SimpleNamespace(lot_library=LIB, building_count=b["building_count"], archetype=b["archetype"],
                                  cluster=b.get("cluster", "")), int(batch["seed_base"]), b.get("candidate_count", 3))


def _lot(model, mission, seed):
    lot, _inc = bl.lot_for_brief(model, "%s.candidate.seed_%d" % (mission, seed), themed=True)
    return [os.path.basename(e["glb"])[:-4] for e in lot]


ap = argparse.ArgumentParser()
ap.add_argument("--seeds", type=int, default=12)
ap.add_argument("--check", type=int, default=None, help="a cold run number: replay its candidates and compare")
a = ap.parse_args()
if a.check:
    run = os.path.join(F, "docs", "cold_runs", "cold_%d" % a.check)
    (brief,) = glob.glob(os.path.join(run, "briefs", "*.json"))
    mission = os.path.basename(brief)[:-5]
    model, base, n = _model(brief)
    log = open(os.path.join(run, "driver.log"), encoding="utf-8").read()
    bad = 0
    for k in range(n):
        seed = base + 101 * k
        m = re.search(r"%s\.lot_assemble\.candidate\.seed_%d: (.*)" % (re.escape(mission), seed), log)
        if not m:
            raise SystemExit("cold run %d's driver log has no lot for seed %d" % (a.check, seed))
        ran = sorted(g[:-4] for g in m.group(1).split() if not g.startswith("gs_empty_rowhome"))
        got = sorted(_lot(model, mission, seed))
        bad += got != ran
        print("seed %d replay %s | cold %d %s | %s" % (seed, got, a.check, ran, "MATCH" if got == ran else "DIFFERS"))
    print("[lot replay] %d of %d candidates reproduced" % (n - bad, n))
    sys.exit(0)
latest = {}
for p in glob.glob(os.path.join(F, "docs", "cold_runs", "cold_*", "briefs", "*.json")):
    n = int(re.search(r"cold_(\d+)", p).group(1))
    key = os.path.basename(p)[:-5]
    if key not in latest or n > latest[key][0]:
        latest[key] = (n, p)
for mission, (n, p) in sorted(latest.items()):
    model, base, _c = _model(p)
    hits = []
    for k in range(a.seeds):
        seed = base + 101 * k
        found = [b for b in _lot(model, mission, seed) if b in HOLES]
        if found:
            hits.append("seed %d: %s" % (seed, ", ".join("%s (%s)" % (b, HOLES[b]) for b in found)))
    print("%-28s archetype %-22s brief cold_%d, seed base %d" % (mission, model.archetype, n, base))
    for h in hits:
        print("    " + h)
