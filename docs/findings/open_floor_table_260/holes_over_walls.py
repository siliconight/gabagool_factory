"""Walls standing under a slab hole: for every spec, each partition of storey s whose centreline runs under a hole
that opens the floor of storey s + 1 -- its own ceiling -- with the stretch it runs there and any opening of the
wall inside that stretch. A probe: prints what it measured and stops.

Holes are read three ways and kept apart, because they are three different things:

  slab_holes   authored `slab_holes` (an atrium, a shaft, a drop);
  link:<role>  `vertical_links` of kind floor_hole or hatch that cut the slab (the builder's `_vertical_links`
               appends them to slab_holes at build time, so a link authored in both is one hole, listed once);
  stair:<id>   the cut each `cut_slabs` stair makes, `stairwell.flight_rect(st, s)` filed under s + 1 exactly as
               `stairwell.slab_openings` files it -- the FOOTPRINT, margins included, so a wall beside a flight
               stands under its hole's margin by design.

The centreline decides and the bound is strict, as `partition_bounds.hole_cuts` decides for a wall over a hole in
its own floor (roadmap 114): a wall seated exactly on a hole's edge is the hole's enclosure, not a wall under it.
Frame: building-local plan metres, x east, y north (the spec's own frame). Opening centres are
`partition_bounds.host_openings`' (the graph's convention, unsnapped).

    python holes_over_walls.py <deli_counter dir> <specs dir> <out.json>
"""
import glob
import json
import os
import sys

DC = os.path.abspath(sys.argv[1])
SPECS = os.path.abspath(sys.argv[2])
OUT = os.path.abspath(sys.argv[3])
sys.path.insert(0, DC)
os.chdir(DC)
import partition_bounds as PB  # noqa: E402
import spec_loader  # noqa: E402
import stairwell  # noqa: E402


def holes(d, spec):
    """{slab storey: [(source, (x0, y0, x1, y1))]}, deduped by rect within a storey."""
    out = {}

    def add(story, source, x, y, sx, sy):
        r = (round(x - sx / 2, 4), round(y - sy / 2, 4), round(x + sx / 2, 4), round(y + sy / 2, 4))
        lst = out.setdefault(int(story), [])
        for i, (src, rr) in enumerate(lst):
            if rr == r:
                if source not in src.split("+"):
                    lst[i] = (src + "+" + source, rr)
                return
        lst.append((source, r))

    for h in d.get("slab_holes") or []:
        add(h["story"], "slab_holes", float(h["x"]), float(h["y"]), float(h["size_x"]), float(h["size_y"]))
    # the builder's own condition and default size (deli_counter.py `_vertical_links`: `v.size_x or 1.5`)
    for v in d.get("vertical_links") or []:
        if (v.get("kind") in ("floor_hole", "hatch") and v.get("cut_slab", True)
                and v.get("story") is not None and v.get("x") is not None):
            add(v["story"], "link:%s" % (v.get("role") or v["kind"]), float(v["x"]), float(v["y"]),
                float(v.get("size_x") or 1.5), float(v.get("size_y") or 1.5))
    for k, st in enumerate(spec.stairs or []):
        if not getattr(st, "cut_slabs", True):
            continue
        lo, hi = min(st.from_story, st.to_story), max(st.from_story, st.to_story)
        for s in range(lo, hi):
            x0, y0, x1, y1 = stairwell.flight_rect(st, s)
            name = getattr(st, "id", None) or "stair_%d" % k
            add(s + 1, "stair:%s" % name, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0)
    return out


rows, errors, n_specs = [], [], 0
for path in sorted(glob.glob(os.path.join(SPECS, "*.json"))):
    name = os.path.basename(path)[:-5]
    try:
        d = json.load(open(path, encoding="utf-8"))
        if not isinstance(d, dict) or "partitions" not in d:
            continue
        spec = spec_loader.spec_from_dict(d)
    except Exception as ex:  # noqa: BLE001 -- a spec the loader refuses is reported, not skipped silently
        errors.append({"spec": name, "error": "%s: %s" % (type(ex).__name__, ex)})
        continue
    n_specs += 1
    hs = holes(d, spec)
    for pi, p in enumerate(d.get("partitions") or []):
        s = int(p.get("story", 0))
        above = hs.get(s + 1, [])
        if not above:
            continue
        ax = str(p.get("axis", "X")).upper()
        lo, hi = sorted((float(p["start"]), float(p["end"])))
        for src, rect in above:
            for c0, c1 in PB.hole_cuts(ax, float(p["pos"]), [rect]):
                a, b = max(lo, c0), min(hi, c1)
                if b - a <= 1e-6:
                    continue
                ops = [{"centre": round(c, 4), "width": w, "tag": t}
                       for c, w, t in PB.host_openings(d, p, False)
                       if c + w / 2 > a and c - w / 2 < b]
                across = (rect[0], rect[2]) if ax == "Y" else (rect[1], rect[3])
                rows.append({"spec": name, "partition": pi, "story": s, "axis": ax, "pos": p["pos"],
                             "run": [lo, hi], "hole_story": s + 1, "hole": list(rect), "source": src,
                             "under": [round(a, 4), round(b, 4)], "under_m": round(b - a, 4),
                             "inside_by_m": round(min(float(p["pos"]) - across[0], across[1] - float(p["pos"])), 4),
                             "openings_under": ops})

json.dump({"specs_read": n_specs, "errors": errors, "rows": rows}, open(OUT, "w", encoding="utf-8"), indent=1)
by_kind = {}
for r in rows:
    k = r["source"].split(":")[0].split("+")[0]
    by_kind[k] = by_kind.get(k, 0) + 1
print("specs read", n_specs, "| refused by the loader", len(errors), "| walls under a hole in their ceiling",
      len(rows), by_kind)
for r in rows:
    if not r["source"].startswith("stair:"):
        print("  %-34s p%-3d s%d %s@%-6s run %-15s hole %-28s %-34s under %s (%.2f m), inside by %.3f m, openings %s"
              % (r["spec"], r["partition"], r["story"], r["axis"], r["pos"], r["run"], r["hole"], r["source"],
                 r["under"], r["under_m"], r["inside_by_m"], [o["tag"] for o in r["openings_under"]]))
