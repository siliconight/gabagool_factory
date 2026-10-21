"""Attribute every endpoint `route_cost.py` could not stand a body at in the AUTHORED arm: for each, the obstacles
within its snap radius plus a body of it, each named by what made it (a wall box, a stair body, a slab hole, or the
volume and its height). Reads route_cost.json beside this file and the specs it names; prints measurements only."""
import collections
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import route_cost as R  # noqa: E402

L = R.L
rows = json.loads((HERE / "route_cost.json").read_text(encoding="utf-8"))
specs = {}
what = collections.Counter()
for r in rows:
    uns = r["arms"]["authored"]["unsnapped"]
    if not uns:
        continue
    d = specs.setdefault(r["spec"], json.loads((R.DC / "specs" / (r["spec"] + ".json")).read_text(encoding="utf-8")))
    story = r["story"]
    sh = L._story_height(d)
    floor = story * sh
    walls = list(L._corridor_obstacles(dict(d, volumes=[], stairs=[]), story, floor, sh))
    for e in uns:
        kind, label, x, y = r["endpoints"][e]
        reach = R.SNAP[kind] + R.R_BODY
        found = []
        for b in walls:
            dd = math.hypot(max(b[0] - x, 0, x - b[2]), max(b[1] - y, 0, y - b[3]))
            if dd < reach:
                found.append(("wall", round(dd, 2), ""))
        for s in d.get("stairs") or []:
            try:
                st = R.Stairwell(**{k: s[k] for k in L._STAIR_FIELDS if k in s})
            except TypeError:
                continue
            if min(st.from_story, st.to_story) <= story < max(st.from_story, st.to_story):
                b = R.stairwell.footprint_rect(st)
                dd = math.hypot(max(b[0] - x, 0, x - b[2]), max(b[1] - y, 0, y - b[3]))
                if dd < reach:
                    found.append(("stair", round(dd, 2), s.get("id", "")))
        for h in d.get("slab_holes") or []:
            if int(h.get("story", 0) or 0) == story:
                b = (h["x"] - h["size_x"] / 2, h["y"] - h["size_y"] / 2, h["x"] + h["size_x"] / 2,
                     h["y"] + h["size_y"] / 2)
                dd = math.hypot(max(b[0] - x, 0, x - b[2]), max(b[1] - y, 0, y - b[3]))
                if dd < reach:
                    found.append(("slab_hole", round(dd, 2), ""))
        for v in d.get("volumes") or []:
            if v.get("collision") == "none" or R.generated(d, v):
                continue
            vz, vh = float(v.get("z", 0)), float(v.get("size_z", 0))
            if not L._on_storey(vz, vh, floor, sh) or L._hung(v, floor):
                continue
            ax, ay = float(v.get("size_x", 1)) / 2, float(v.get("size_y", 1)) / 2
            dd = math.hypot(max(v["x"] - ax - x, 0, x - v["x"] - ax), max(v["y"] - ay - y, 0, y - v["y"] - ay))
            if dd < reach:
                found.append(("volume", round(dd, 2), "%s top %.2f above the floor, foot %.2f"
                              % (v["name"], vz + vh / 2 - floor, vz - vh / 2 - floor)))
        blockers = sorted(found, key=lambda f: f[1])
        what[tuple(sorted({f[0] for f in blockers if f[1] < R.R_BODY + 0.05}))] += 1
        print("%s / %s (storey %d) %s %s at (%.2f, %.2f):" % (r["spec"], r["room"], story, kind, label, x, y))
        for f in blockers[:5]:
            print("     %-9s %.2f m  %s" % f)
print("\nunsnapped endpoints by what stands within a body of them:", dict(what))
