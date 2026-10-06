"""For every Laser Tag evaluation refused on UNREACHABLE_SPAWN in the cold-run
workspaces: which enemy, where it stands (level frame: x, y north, metres),
and which declared rect contains it -- a mission building's footprint, a
blocker (Empty or not), or none. Measures; names no cause.

    python unreachable_spawns.py [first_run] [last_run]
"""
import glob
import json
import math
import os
import re
import sys

WS = "C:/Projects/gabagool_studios/gabagool_factory/workspaces"
lo, hi = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (9100, 9999)


def rect_of(x, y, sx, sy):
    return (x - sx / 2.0, y - sy / 2.0, x + sx / 2.0, y + sy / 2.0)


def inside(p, r):
    return r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]


def node_xy(text, name):
    m = re.search(r'\[node name="%s"[^\]]*\]\r?\ntransform = Transform3D\(([^)]*)\)' % re.escape(name), text)
    if not m:
        return None
    v = [float(x) for x in m.group(1).split(",")]
    return (v[9], -v[11])          # Godot (x, z) -> level (x, y north)


for ws in sorted(glob.glob(WS + "/cold-*-ws")):
    run = int(re.search(r"cold-(\d+)-ws", ws).group(1))
    if not lo <= run <= hi:
        continue
    for rep in sorted(glob.glob(ws + "/.level_factory/jobs/*laser_tag_evaluate*/out/lasertag.report.json")):
        d = json.load(open(rep, encoding="utf-8"))
        bad = [f for f in d.get("findings", []) if f.get("type") == "UNREACHABLE_SPAWN"]
        if not bad:
            continue
        job = os.path.basename(os.path.dirname(os.path.dirname(rep)))
        cand = job.split(".candidate.")[-1]
        stage = glob.glob(ws + "/.level_factory/staging/*laser_tag_evaluate.candidate.%s" % cand)
        if not stage:
            print(run, cand, "NO STAGING DIR")
            continue
        lvl = open(stage[0] + "/level.tscn", encoding="utf-8").read()
        drawn = json.load(open(stage[0] + "/site.site.drawn.json", encoding="utf-8"))
        rects = []
        for b in drawn.get("buildings", []):
            fp = b.get("footprint") or b.get("_footprint")
            if fp:
                fx, fy = float(fp[0]), float(fp[1])
                if int(round(float(b.get("rot", 0) or 0))) % 180 == 90:
                    fx, fy = fy, fx
                rects.append(("building " + str(b.get("id")) + " " + str(b.get("archetype") or ""),
                              rect_of(float(b["at"][0]), float(b["at"][1]), fx, fy)))
        for bk in drawn.get("blockers", []):
            rects.append(("blocker %s %s%s" % (bk.get("id"), bk.get("archetype"), " (Empty)" if bk.get("empty") else ""),
                          rect_of(float(bk["at"][0]), float(bk["at"][1]),
                                  float(bk.get("size_x", 12.0) or 12.0), float(bk.get("size_y", 12.0) or 12.0))))
        for f in bad:
            name = f["message"].split(" ")[0]
            p = node_xy(lvl, name)
            hits = [lab for lab, r in rects if p and inside(p, r)]
            near = sorted((min(abs(p[0] - r[0]), abs(p[0] - r[2]), abs(p[1] - r[1]), abs(p[1] - r[3])), lab)
                          for lab, r in rects) if p else []
            print("%d %s %s at %s -> inside: %s%s" % (
                run, cand, name, tuple(round(c, 2) for c in p) if p else None,
                hits or "nothing declared",
                "" if hits else "; nearest edge %.2f m (%s)" % near[0] if near else ""))
