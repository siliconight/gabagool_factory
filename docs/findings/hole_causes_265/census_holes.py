"""Every drop link in a Deli Counter library, its rooms and cause, and the slots `hole_causes` derives for it.

A probe: prints what it measured and stops. Reads the specs, not a build: the slots are what `hole_causes.hole_slots`
returns for each spec dict, as the builder asks it. For each link it also prints the nearest built wall face to the
hole's edge on the storey above and on the storey below (metres; under 0 a wall stands across the edge) -- the room
the edge's 0.30 m band has before it reaches into a wall.

    python docs/findings/hole_causes_265/census_holes.py [<deli_counter repo>] [--out <file.json>]

The repo defaults to the factory's deli_counter/; --out defaults to census_holes.json beside this file.
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("repo", nargs="?", default=os.path.join(HERE, "..", "..", "..", "deli_counter"))
ap.add_argument("--out", default=os.path.join(HERE, "census_holes.json"))
args = ap.parse_args()
REPO = os.path.abspath(args.repo)
sys.path.insert(0, REPO)
import hole_causes as HC  # noqa: E402
import layout_lint  # noqa: E402

rows = []
for p in sorted(glob.glob(os.path.join(REPO, "specs", "*.json"))):
    spec = json.load(open(p, encoding="utf-8"))
    links = HC.drop_links(spec)
    if not links:
        continue
    name = os.path.basename(p)[:-5]
    slots, notes = HC.hole_slots(spec, lambda m: 1)
    walls = layout_lint.built_walls(spec)
    for v in links:
        up, dn = HC._rooms_at(spec, v["story"], float(v["x"]), float(v["y"]))
        cause = HC.cause_for(spec, v)
        hole = HC._rect(v)
        near = {}
        for st in (int(v["story"]), int(v["story"]) - 1):
            best = None
            for label, s, n, plane, half, spans in walls:
                if s != st:
                    continue
                lo_n, hi_n = (hole[0], hole[2]) if n == 0 else (hole[1], hole[3])
                lo_a, hi_a = (hole[1], hole[3]) if n == 0 else (hole[0], hole[2])
                if not any(a < hi_a + HC.BAND and b > lo_a - HC.BAND for a, b in spans):
                    continue
                gap = max(lo_n - (plane + half), (plane - half) - hi_n)
                if best is None or gap < best[0]:
                    best = (round(gap, 3), label)
            near[st] = best
        rows.append({
            "spec": name, "kind": v.get("kind"), "role": v.get("role"), "story": v["story"],
            "xy": [v["x"], v["y"]], "size": [round(hole[2] - hole[0], 3), round(hole[3] - hole[1], 3)],
            "above": up["id"] if up else None, "below": dn["id"] if dn else None, "cause": cause,
            "stair_share": round(HC.stair_share(spec, v), 3),
            "form": HC.form_for(spec, v, cause) if cause in ("cut", "broken") else None,
            "wall_above": near[int(v["story"])], "wall_below": near[int(v["story"]) - 1]})
    for x in slots:
        # 0.236.0 returned (slot, entry, box center, box size); 0.236.1 (slot, entry, boxes)
        s = x[0]
        rows.append({"spec": name, "slot": s["slot_id"], "species": s["species"], "form": s["form"],
                     "stock": s["stock"], "variant": s["variant"], "rot": s["transform"]["rot_y"],
                     "dims": s["fit"]["dims"], "center": [round(q, 3) for q in s["transform"]["translation"]]})
    for n in notes:
        rows.append({"spec": name, "note": n})
for r in rows:
    print(json.dumps(r))
links = [r for r in rows if "kind" in r]
print("[census] %d drop links in %d specs; %s, uncaused %d; slots %d; notes %d" % (
    len(links), len({r["spec"] for r in links}),
    ", ".join("%s %d" % (c, sum(1 for r in links if r["cause"] == c)) for c in HC.CAUSES + (HC.STAIR,)),
    sum(1 for r in links if not r["cause"]), sum(1 for r in rows if "slot" in r),
    sum(1 for r in rows if "note" in r)))
json.dump(rows, open(args.out, "w", encoding="utf-8"), indent=1)
