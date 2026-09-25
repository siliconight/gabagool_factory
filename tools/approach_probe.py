"""How many angularly distinct directions can a body ARRIVE at the objective from?

WHY A REPLACEMENT IS NEEDED, and it is a measurement rather than an opinion.
`site_tactical._distinct_routes_to` iterates the objective's neighbours in the
BUILDING graph. Lot 0.77.0 joins every building with a door onto the same road
-- correctly; buildings on a street ARE connected -- so on a street-fronted site
that graph is complete and the objective's degree is always `n - 1`. Measured
over every generated spec on disk, 2026-09-25:

    sites WITH roads      approaches == buildings - 1 in 78 of 78
    sites WITHOUT roads   approaches == buildings - 1 in  8 of 16

So on any site this factory now produces, `objective_approaches` is a
restatement of `building_count - 1`. It cannot tell a row from a courtyard or a
T from a crossroads, and adding a fourth building moves it from 2 to 3 without
changing the level's shape at all (`docs/experiments/approaches_9500/`: n=4
gave 3, n=5 gave 4, both exactly at the ceiling).

WHAT THE RECIPE ACTUALLY ASKED FOR is in `site_layout_lint`'s own words for its
S5 check: the objective's approaches should come from far enough apart "so one
defender angle cannot hold every approach". That is a question about SPACE. S5
has the right intent and the wrong input -- it takes its angles from the same
building-graph edges, so it inherits the same degeneracy.

WHAT THIS MEASURES INSTEAD. A player does not arrive from the direction of
another building; they arrive ALONG A STREET. So:

  * find the objective's door spurs -- the paths Level Factory emits from a
    building to the sidewalk, which is where its frontage actually is;
  * find which road each door lands on, and where along it;
  * each road gives up to TWO arrivals at that door, one from each direction
    along the carriageway;
  * an arm's LENGTH is how much street there is to arrive along in that
    direction.

A mid-block building on one street has 2. A corner building with doors on two
streets has up to 4 -- which is what the walker's own archetype note means by
"four corners become natural anchors", and what no building-graph measure can
see.

NO THRESHOLD IN THIS VERSION, DELIBERATELY. Whether a 6 m stub counts as an
approach is a question nobody here has data for, and picking a number now would
be the cheap observable standing in for the expensive truth that this repo
keeps paying for. So every arm is reported WITH ITS LENGTH and nothing is
filtered; a floor can be set later against real walks, and the derivation
written down when it is. `CLAUDE.md`: a probe prints what it measured and stops.

WHAT IT DOES NOT DO, and this is the one thing the old measure did better.
`_distinct_routes_to` at least asked whether the spawn could REACH each
neighbour without passing through the objective. This counts arrivals at the
objective's frontage and does not check that a body can get to the far end of
each arm. An arm's length is a partial proxy -- a 15 m stub is not much of an
approach -- but a long arm that dead-ends against the plate would still be
counted. Reachability is the next thing to add, and until it is, read the run
lengths beside the count rather than the count alone.

    python tools/approach_probe.py [target] [--json out.json] [--eps 25]
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lot"))

#: Two arrival bearings closer than this are the same direction. 25 deg is
#: CHOSEN, not derived -- it is roughly the angle at which two streets stop
#: reading as one, and nothing here has been measured against a player. It is a
#: knob for exactly that reason: `--eps` moves it and the report prints it.
DEFAULT_EPS_DEG = 25.0


def _unit(ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy)
    if L <= 1e-9:
        return None, 0.0
    return (dx / L, dy / L), L


def _road_for(point, roads):
    """(index, t, axis, length) of the road whose BAND holds `point`.

    A door spur stops ON the sidewalk, short of the centre line -- Level
    Factory puts it there so Lot does not read it as a street crossing -- so
    the test is the band's half-width, not the carriageway's. Returns the
    NEAREST qualifying road: a corner door sits inside two bands where they
    overlap at a junction, and the one it fronts is the closer.
    """
    px, py = point
    best = None
    for i, r in enumerate(roads):
        a, b = r.get("a"), r.get("b")
        if not (a and b):
            continue
        axis, L = _unit(a[0], a[1], b[0], b[1])
        if axis is None:
            continue
        t = ((px - a[0]) * axis[0] + (py - a[1]) * axis[1]) / L
        t = max(0.0, min(1.0, t))
        cx, cy = a[0] + axis[0] * t * L, a[1] + axis[1] * t * L
        perp = math.hypot(px - cx, py - cy)
        half = float(r.get("width", 10.0)) / 2.0 + float(r.get("sidewalk", 3.0))
        if perp <= half + 0.5 and (best is None or perp < best[0]):
            best = (perp, i, t, axis, L)
    if best is None:
        return None
    _, i, t, axis, L = best
    return i, t, axis, L


def _bearing(dx, dy):
    return math.degrees(math.atan2(dy, dx)) % 360.0


def _spread(bearings):
    """The angular span the directions occupy: 360 minus the widest gap.

    The same quantity `site_layout_lint` S5 computes, on a different input.
    Note S5 carries a branch that cannot fire -- `if len(angs) > 1 else 0`
    inside a block already guarded by `len(angs) >= 2` -- which is harmless
    there and is not reproduced here.
    """
    if len(bearings) < 2:
        return 0.0
    s = sorted(bearings)
    gaps = [(s[i] - s[i - 1]) % 360.0 for i in range(len(s))]
    return 360.0 - max(gaps)


def arrivals(spec, eps_deg=DEFAULT_EPS_DEG):
    """Every way in, or a refusal saying why the question could not be asked."""
    objv = spec.get("objective")
    if not objv:
        return {"ok": False, "error": "no objective declared"}
    roads = spec.get("roads") or []
    if not roads:
        return {"ok": False, "error": "no roads: this measure is about streets, "
                                      "and a site without them has none to "
                                      "arrive along"}
    raw = [p for p in (spec.get("paths") or []) if p.get("a") and p.get("b")]
    doors = [p for p in raw if p.get("building") == objv]
    attribution = "declared"
    if not doors:
        # SPECS OLDER THAN LF 0.109.2 record the door and not whose door it is.
        # Fall back to Lot's own rule rather than a second one: nearest centre,
        # and only when clearly nearest. Labelled, because recovering this by
        # distance is precisely what the `building` key was added to avoid.
        import site_tactical as _st
        centres = {b.get("id"): tuple(b.get("at", (0.0, 0.0)))
                   for b in (spec.get("buildings") or []) if b.get("id")}
        doors = [p for p in raw
                 if p.get("building") is None
                 and _st._building_at(tuple(p["a"]), centres) == objv]
        attribution = "inferred"
    if not doors:
        return {"ok": False,
                "error": f"objective {objv!r} has no door spur, declared or "
                         f"attributable; without one there is no frontage to "
                         f"arrive AT, and a count of 0 would read as a finding "
                         f"rather than an absence"}

    arms = []
    for d in doors:
        got = _road_for(d["b"], roads)
        if got is None:
            arms.append({"road": None, "skipped": "door lands in no road band"})
            continue
        i, t, axis, L = got
        for sign, run in ((-1.0, t * L), (+1.0, (1.0 - t) * L)):
            arms.append({
                "road": i,
                "bearing": round(_bearing(sign * axis[0], sign * axis[1]), 1),
                "run_m": round(run, 1),
                "door": [round(v, 2) for v in d["b"]],
            })

    live = [a for a in arms if a.get("bearing") is not None]
    # dedupe: two arrivals within eps are one direction. Longest run wins, so
    # the figure reported for a direction is the street there is most of.
    live.sort(key=lambda a: -a["run_m"])
    kept = []
    for a in live:
        if all(min((a["bearing"] - k["bearing"]) % 360.0,
                   (k["bearing"] - a["bearing"]) % 360.0) > eps_deg
               for k in kept):
            kept.append(a)
    kept.sort(key=lambda a: a["bearing"])

    return {"ok": True, "objective": objv, "doors": len(doors),
            "attribution": attribution,
            "roads_fronted": sorted({a["road"] for a in live}),
            "arms_raw": len(live), "approaches": len(kept),
            "spread_deg": round(_spread([a["bearing"] for a in kept]), 1),
            "eps_deg": eps_deg, "arrivals": kept}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target", nargs="?", default=".")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--eps", type=float, default=DEFAULT_EPS_DEG)
    args = ap.parse_args(argv)

    from level_recipe_census import find_specs
    import site_tactical as st

    specs = find_specs(Path(args.target))
    if not specs:
        print(f"approach_probe: no site specs under {args.target}")
        return 2

    rows, refused = [], []
    for p in specs:
        try:
            spec = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            refused.append((p.parent.name, f"unreadable: {exc}"))
            continue
        r = arrivals(spec, args.eps)
        if not r["ok"]:
            refused.append((p.parent.name, r["error"]))
            continue
        n = len(spec.get("buildings") or [])
        old = st.analyze(spec)["intel"].get("objective_approaches")
        r.update({"candidate": str(p.parent), "buildings": n,
                  "old_measure": old, "old_equals_n_minus_1": old == n - 1})
        rows.append(r)

    inferred = sum(1 for r in rows if r.get("attribution") == "inferred")
    print(f"approach probe: {len(rows)} site(s) measured, {len(refused)} refused"
          f"   (eps {args.eps:.0f} deg)")
    if inferred:
        print(f"  of those, {inferred} had the objective's door attributed BY "
              f"DISTANCE, not\n  declared -- specs older than LF 0.109.2's "
              f"`building` key. Discount them\n  if the question is about "
              f"what the pipeline records rather than what it drew.")
    for name, why in refused[:8]:
        print(f"  REFUSED {name}: {why}")
    if not rows:
        print("\nREFUSED: nothing measured, so no distribution below would "
              "mean anything.")
        return 2

    print("\n  SPATIAL APPROACHES (arrivals along a street, deduped at eps)")
    dist = collections.Counter(r["approaches"] for r in rows)
    for k in sorted(dist):
        print("    %-5d %4d  %s" % (k, dist[k], "#" * min(40, dist[k])))

    print("\n  AGAINST THE OLD MEASURE")
    old = collections.Counter(r["old_measure"] for r in rows)
    for k in sorted(old, key=lambda v: (v is None, v)):
        print("    old=%-5s %4d" % (k, old[k]))
    pinned = sum(1 for r in rows if r["old_equals_n_minus_1"])
    print("    old measure == buildings-1 in %d of %d" % (pinned, len(rows)))
    same = sum(1 for r in rows if r["approaches"] == r["old_measure"])
    print("    the two agree on %d of %d" % (same, len(rows)))

    print("\n  DOES IT DISCRIMINATE? A measure pinned to the building count "
          "cannot\n  distinguish two layouts, which is the whole reason for "
          "this one.")
    by_n = collections.defaultdict(collections.Counter)
    for r in rows:
        by_n[r["buildings"]][r["approaches"]] += 1
    for n in sorted(by_n):
        print("    buildings=%d -> spatial approaches %s"
              % (n, dict(sorted(by_n[n].items()))))

    print("\n  SPREAD (360 minus the widest gap; S5 wants >= 90)")
    sp = [r["spread_deg"] for r in rows]
    if sp:
        sp_sorted = sorted(sp)
        print("    min %.0f  median %.0f  max %.0f   under 90: %d of %d"
              % (sp_sorted[0], sp_sorted[len(sp_sorted) // 2], sp_sorted[-1],
                 sum(1 for v in sp if v < 90.0), len(sp)))

    runs = sorted(a["run_m"] for r in rows for a in r["arrivals"])
    if runs:
        print("\n  ARM LENGTHS, unfiltered and on purpose: how much street "
              "there is\n  to arrive along. No floor is applied -- nobody has "
              "data for one yet.")
        print("    min %.1f m  median %.1f m  max %.1f m   under 20 m: %d of %d"
              % (runs[0], runs[len(runs) // 2], runs[-1],
                 sum(1 for v in runs if v < 20.0), len(runs)))

    print("\n  This probe reports and gates nothing.")

    if args.json:
        args.json.write_text(json.dumps(
            {"schema": "lf.approach_probe.v1", "eps_deg": args.eps,
             "measured": len(rows), "refused": len(refused),
             "rows": rows}, indent=1), encoding="utf-8")
        print(f"  wrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
