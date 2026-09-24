#!/usr/bin/env python3
"""Score every generated site against the level recipe's `approaches` line.

WHY THIS RAN BEFORE A GATE WAS WRITTEN. `docs/LEVEL_RECIPE.md`'s MVP asks for
`approaches: min 3`, and `tools/repetition_census.py` set the house rule for
why a threshold comes second: a tool has no taste, so it reports and a person
decides. Measuring first turned out to matter more than usual here.

WHAT IT FOUND, on 79 real site specs -- every candidate the factory has on
disk:

    objective_approaches   0   38 specs
                           1   37 specs
                           2    4 specs
                           3+   0 specs

The MVP's `min: 3` would have failed ONE HUNDRED PERCENT of levels ever
generated, and half of them score zero. Before reading that as a verdict on
the levels, look at the graph it is computed over. On cold run 9077's shipped
package -- reported as a genuine zero-intervention run:

    adjacency            {b0: [b1], b1: [b0], b2: []}
    isolated_buildings   ['b2']
    warning              "buildings with no declared path-route from 'b0': b2"
    objective_approaches 1

THE MEASURE IS NOT WRONG ABOUT THE GRAPH. THE GRAPH IS WRONG ABOUT THE LEVEL.
`site_tactical.build_graph` is explicit that it uses building-to-building
paths only -- "paths to raw points don't connect buildings and are ignored
here (they're still geometry in the scene)". Level Factory emits a chain of
consecutive paths and DROPS any segment that crosses a road, deliberately
(cold run 9049: a path cut across a cross street mid-block as an 8 m
sidewalk-skinned band). What it emits instead is a spur from every building to
the sidewalk, and the street carries the connection.

So every building reaches every other one, on foot, down the street -- and the
graph says two of three are connected and the third is isolated. An approaches
gate over this graph would measure path authoring, not the level.

THAT WARNING IS ALREADY BEING PRINTED AND NOBODY READS IT, which is the third
instance of that shape found this week (`test_navgate_population` fires only
after a library rebuild; the z-fight gate fails every run and blocks nothing,
roadmap 177). A red light that changes no behaviour is the pattern, not the
individual instrument.

WHAT HAS TO HAPPEN BEFORE THE GATE. The site graph must include street
connectivity: two buildings whose spurs reach the same road are connected via
that road, with a crossing where they sit on opposite sides. Until then this
tool reports and gates nothing, and says so.

    python tools/level_recipe_census.py
    python tools/level_recipe_census.py --json out.json
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOT = ROOT / "lot"
SPEC_NAME = "site.json"
#: The MVP's ask. Recorded so the gap is visible, NOT applied -- see the
#: module docstring for why nothing here returns a verdict.
RECIPE_MIN_APPROACHES = 3


def find_specs(target: Path) -> list:
    """Every candidate site spec under `target`.

    `os.walk`, not `glob`: the specs live under `<ws>/.level_factory/temp/...`
    and neither `glob.glob` nor `Path.rglob` matches a path component that
    begins with a dot, so the obvious pattern returns zero against 79 files.
    The same trap cost `site_plan_census` its first run.
    """
    out = []
    for dirpath, _dirnames, filenames in os.walk(target):
        if SPEC_NAME not in filenames:
            continue
        # `themed/site.json` is the same candidate re-written for the art pass
        if os.path.basename(dirpath) == "themed":
            continue
        if "candidate_seed" not in dirpath:
            continue
        out.append(Path(dirpath) / SPEC_NAME)
    return sorted(out)


def score(path: Path, st) -> dict:
    """One spec's approach intel, taken from LOT'S OWN analyzer.

    Not re-implemented here. Two spellings of one measure is how the number a
    gate reports drifts from the number the tool computes, and this repo has
    paid for that more than once.
    """
    row = {"path": str(path), "candidate": path.parent.name, "ok": False,
           "error": ""}
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        row["error"] = f"unreadable: {exc}"
        return row
    if not d.get("objective"):
        row["error"] = "no objective declared"
        return row
    rep = st.analyze(d)
    intel = rep.get("intel") or {}
    adj = st.build_graph(d)
    row.update({
        "ok": True,
        "buildings": len(d.get("buildings") or []),
        "bld_to_bld_paths": len([p for p in (d.get("paths") or [])
                                 if "from" in p and "to" in p]),
        "roads": len(d.get("roads") or []),
        "approaches": intel.get("objective_approaches"),
        "isolated": list(intel.get("isolated_buildings") or []),
        "graph_edges": sum(len(v) for v in adj.values()) // 2,
        "warnings": list(rep.get("warnings") or []),
    })
    return row


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target", nargs="?", default=str(ROOT / "workspaces"),
                    type=Path)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args(argv)

    if not LOT.is_dir():
        print("level_recipe_census: no lot repo beside this one; the measure "
              "is Lot's and this refuses to re-implement it")
        return 2
    sys.path.insert(0, str(LOT))
    import site_tactical as st

    specs = find_specs(args.target)
    rows = [score(p, st) for p in specs]
    ok = [r for r in rows if r["ok"]]
    bad = [r for r in rows if not r["ok"]]

    print(f"level recipe census: {len(specs)} site spec(s), "
          f"{len(ok)} scored, {len(bad)} refused")
    for r in bad[:8]:
        print(f"  REFUSED {r['candidate']}: {r['error']}")
    if not ok:
        print("\nREFUSED: nothing scored, so no distribution below would mean "
              "anything.")
        return 2

    dist = collections.Counter(r["approaches"] for r in ok)
    print("\n  objective_approaches   (Lot's own `_distinct_routes_to`)")
    for k in sorted(dist, key=lambda v: (v is None, v)):
        bar = "#" * min(40, dist[k])
        print("    %-5s %4d  %s" % (k, dist[k], bar))
    meets = sum(1 for r in ok if (r["approaches"] or 0) >= RECIPE_MIN_APPROACHES)
    print("\n    the recipe asks for >= %d: %d of %d specs meet it"
          % (RECIPE_MIN_APPROACHES, meets, len(ok)))

    iso = [r for r in ok if r["isolated"]]
    print("\n  SITES WITH AN ISOLATED BUILDING  %d of %d" % (len(iso), len(ok)))
    if iso:
        print("    Lot already prints this as a warning on every one of them, "
              "and nothing reads it.")
        names = collections.Counter(len(r["isolated"]) for r in iso)
        for k in sorted(names):
            print("      %d isolated building(s): %d site(s)" % (k, names[k]))

    edges = collections.Counter(r["graph_edges"] for r in ok)
    blds = collections.Counter(r["buildings"] for r in ok)
    print("\n  THE GRAPH THE MEASURE RUNS ON")
    print("    buildings per site      %s"
          % dict(sorted(blds.items())))
    print("    building-to-building edges %s"
          % dict(sorted(edges.items())))
    print("    roads per site          %s"
          % dict(sorted(collections.Counter(r["roads"] for r in ok).items())))
    print("\n    A site of 3 buildings with 1 edge and 2 roads is not a site "
          "with one connection.\n    Every building gets a spur to the "
          "sidewalk and the street carries the rest;\n    `build_graph` counts "
          "building-to-building paths only, by its own docstring.")

    print("\n  This tool reports and gates nothing. An approaches gate over "
          "this graph would\n  measure path authoring rather than the level -- "
          "see docs/LEVEL_RECIPE.md.")

    if args.json:
        args.json.write_text(json.dumps(
            {"schema": "lf.level_recipe_census.v1",
             "recipe_min_approaches": RECIPE_MIN_APPROACHES,
             "scored": len(ok), "refused": len(bad),
             "approaches_distribution": {str(k): v for k, v in dist.items()},
             "sites_with_isolated_building": len(iso),
             "rows": rows}, indent=1), encoding="utf-8")
        print(f"  wrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
