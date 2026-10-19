"""Measure every open floor Deli Counter's baseline holds: where the two rooms meet, which stretches of that line no
partition covers, whether the line is the footprint's own edge, whether the two rooms already share a door, and what
stands near the stretch -- the facts a table that walls or opens each pair has to be written against (roadmap 260).

    python pairs.py [--json OUT]

Reads `deli_counter/open_floor_baseline.json` and each named spec under `deli_counter/specs/`, and asks Deli Counter's
own functions: `layout_lint.open_floors` (L26's reading), `layout_lint._story_parts`, `layout_lint.graph` (the rooms
each opening joins) and `tactical.OPEN_FLOOR_M`. Prints what it measured and stops; it changes nothing.
Coordinates are a spec's own: metres, the footprint centred on 0, x and y in plan.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DC = os.path.abspath(os.path.join(HERE, "..", "..", "..", "deli_counter"))
sys.path.insert(0, DC)
import layout_lint  # noqa: E402
import tactical     # noqa: E402

LINE_TOL = 0.05     # tactical.open_edge's own tolerance for a partition on the line


def uncovered(parts, axis, line, lo, hi):
    """The stretches of [lo, hi] on the line that no same-axis partition on it covers, as (start, end) pairs."""
    cover = sorted((max(lo, min(s, e)), min(hi, max(s, e))) for a, p, s, e in parts
                   if a == axis and abs(p - line) < LINE_TOL and min(hi, max(s, e)) > max(lo, min(s, e)))
    out, at = [], lo
    for s, e in cover:
        if s > at:
            out.append((at, s))
        at = max(at, e)
    if at < hi:
        out.append((at, hi))
    return out


def near(spec, story, axis, line, lo, hi, reach=2.0):
    """Stairs, ladders, ramps, vertical links and slab holes whose point or box lies within `reach` m of the stretch."""
    hits = []
    for key in ("stairs", "ladders", "ramps", "vertical_links", "slab_holes"):
        for it in spec.get(key, []) or []:
            st = it.get("story", it.get("from_story"))
            to = it.get("to_story", st)
            if st is None or not (min(st, to) <= story <= max(st, to)):
                continue
            if "x" in it and "y" in it:
                u, v = (it["y"], it["x"]) if axis == "Y" else (it["x"], it["y"])
                if lo - reach <= u <= hi + reach and abs(v - line) <= reach:
                    hits.append("%s %s at (%g, %g)" % (key, it.get("id") or it.get("kind", ""), it["x"], it["y"]))
            elif "bounds" in it:
                x0, y0, x1, y1 = it["bounds"]
                if axis == "Y":
                    if x0 - reach <= line <= x1 + reach and y1 >= lo - reach and y0 <= hi + reach:
                        hits.append("%s box %s" % (key, it["bounds"]))
                elif y0 - reach <= line <= y1 + reach and x1 >= lo - reach and x0 <= hi + reach:
                    hits.append("%s box %s" % (key, it["bounds"]))
    return hits


def main(argv):
    base = json.load(open(os.path.join(DC, "open_floor_baseline.json"), encoding="utf-8"))["open_floors"]
    rows = []
    for name in sorted(base):
        spec = json.load(open(os.path.join(DC, "specs", name + ".json"), encoding="utf-8"))
        hx, hy = spec["footprint_x"] / 2.0, spec["footprint_y"] / 2.0
        edges, _ = layout_lint.graph(spec)
        roles = {r["id"]: r.get("role", "") for r in spec.get("rooms", [])}
        for f in layout_lint.open_floors(spec):
            pair = "%s|%s" % (f["a"], f["b"])
            parts = layout_lint._story_parts(spec, f["story"])
            gaps = uncovered(parts, f["axis"], f["pos"], f["lo"], f["hi"])
            half = hx if f["axis"] == "Y" else hy
            joins = sorted({k for n, k in edges.get(f["a"], ()) if n == f["b"]})
            rows.append({"spec": name, "story": f["story"], "pair": pair, "axis": f["axis"], "line": f["pos"],
                         "lo": f["lo"], "hi": f["hi"], "uncovered_m": round(f["uncovered"], 3),
                         "gaps": [[round(a, 3), round(b, 3)] for a, b in gaps],
                         "on_footprint_edge": abs(abs(f["pos"]) - half) < 0.05,
                         "joined_by": joins, "roles": [roles.get(f["a"], ""), roles.get(f["b"], "")],
                         "baselined": pair in base[name],
                         "near": near(spec, f["story"], f["axis"], f["pos"], f["lo"], f["hi"])})
    for r in rows:
        print("%-22s s%-2s %-36s %s=%-7g %s unc %.2f  edge:%s  joined:%s  near:%d %s" % (
            r["spec"], r["story"], r["pair"], "x" if r["axis"] == "Y" else "y", r["line"],
            r["gaps"], r["uncovered_m"], "FOOTPRINT" if r["on_footprint_edge"] else "inside",
            ",".join(r["joined_by"]) or "-", len(r["near"]), "; ".join(r["near"])[:80]))
    print("%d open floors in %d specs; %d baselined; %d on the footprint's own edge; %d already joined by a walkable "
          "opening" % (len(rows), len({r["spec"] for r in rows}), sum(r["baselined"] for r in rows),
                       sum(r["on_footprint_edge"] for r in rows),
                       sum(bool(set(r["joined_by"]) & set(layout_lint.WALK_KINDS)) for r in rows)))
    if "--json" in argv:
        with open(argv[argv.index("--json") + 1], "w", encoding="utf-8", newline="\n") as fh:
            json.dump(rows, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
