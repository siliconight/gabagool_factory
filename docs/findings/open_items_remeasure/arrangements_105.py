"""Roadmap 105 re-measured: does Lot build one arrangement of buildings, or one per seed?

105 (2026-09-06) said the site plan -- how many buildings, where they sit, which faces address the street -- had
never been varied or measured, and asked first for a measurement: the same brief at several seeds, the plans
compared by building positions and the space between them. A cold run holds exactly that: one brief, three seeded
candidates. This reads each candidate's drawn site spec (`site.site.drawn.json`: the mission's `buildings` with
`archetype`, `at`, `rot`; the urban street's Empties as `blockers`; the `roads`) and prints each plan, then how the
plans differ pairwise: the archetype sets, the buildings standing at the same spot and facing, the Empties' sets
and spots, the roads. It measures and stops; what a plan is worth to a fight is Laser Tag's reading.

    python docs/findings/open_items_remeasure/arrangements_105.py <workspace> <mission> [seeds ...]
"""
import json
import pathlib
import sys


def plan(ws, mission, seed):
    p = (pathlib.Path(ws) / ".level_factory" / "jobs" / ("%s.lot_assemble.candidate.seed_%s" % (mission, seed))
         / "1" / "out" / "site.site.drawn.json")
    d = json.loads(p.read_text(encoding="utf-8"))
    bld = [(b["id"], b["archetype"], tuple(round(float(v), 2) for v in b["at"]), int(b.get("rot", 0)),
            (b.get("front") or {}).get("wall")) for b in d.get("buildings") or []]
    emp = [(e["id"], e["archetype"], tuple(round(float(v), 2) for v in e["at"]), int(e.get("rot", 0)))
           for e in d.get("blockers") or []]
    roads = [(tuple(round(float(v), 1) for v in r["a"]), tuple(round(float(v), 1) for v in r["b"]), r.get("width"))
             for r in d.get("roads") or []]
    return {"buildings": bld, "empties": emp, "roads": roads, "objective": d.get("objective"),
            "shape": d.get("site_shape"), "grammar": d.get("road_grammar_resolved") or d.get("road_grammar")}


def main():
    ws, mission = sys.argv[1], sys.argv[2]
    seeds = sys.argv[3:] or ["9003", "9104", "9205"]
    plans = {s: plan(ws, mission, s) for s in seeds}
    for s, p in plans.items():
        print("== seed_%s: %d mission buildings, %d Empties, %d roads; site_shape %s; grammar %s" % (
            s, len(p["buildings"]), len(p["empties"]), len(p["roads"]), p["shape"], str(p["grammar"])[:60]))
        for b in p["buildings"]:
            print("   %-3s %-20s at %-18s rot %3d  front %s" % b)
        print("   Empties: " + ", ".join("%s@%s/%d" % (a, at, r) for _i, a, at, r in p["empties"])[:300])
    print("== pairwise")
    for i, a in enumerate(seeds):
        for b in seeds[i + 1:]:
            pa, pb = plans[a], plans[b]
            arch_a = sorted(x[1] for x in pa["buildings"])
            arch_b = sorted(x[1] for x in pb["buildings"])
            spots_a = {(x[1], x[2], x[3]) for x in pa["buildings"]}
            spots_b = {(x[1], x[2], x[3]) for x in pb["buildings"]}
            emp_a = {(x[1], x[2], x[3]) for x in pa["empties"]}
            emp_b = {(x[1], x[2], x[3]) for x in pb["empties"]}
            print("   seed_%s vs seed_%s: archetypes %s; buildings at the same spot and facing %d of %d; "
                  "Empties %s (%d of %d at the same spot); roads %s"
                  % (a, b, "the same set" if arch_a == arch_b else "DIFFER (%s | %s)" % (arch_a, arch_b),
                     len(spots_a & spots_b), max(len(spots_a), len(spots_b)),
                     "the same set" if sorted(x[0] for x in emp_a) == sorted(x[0] for x in emp_b) else "differ",
                     len(emp_a & emp_b), max(len(emp_a), len(emp_b)),
                     "the same" if pa["roads"] == pb["roads"] else "differ"))


if __name__ == "__main__":
    main()
