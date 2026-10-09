"""The fans where weighing by area moves a corner normal furthest, per species
(roadmap 214, trial 1).

Run inside Blender, background, against a 1.87.0 Zoo tree:

    C:\\blender\\blender.exe -b --factory-startup --python fan_probe.py -- <zoo root> <out dir> <species> [...]

Builds each species at its genome's default corner the way `census.py` does,
then for every visual part, BEFORE any custom normal is set (the parts are
read after their custom normals are removed): the default corner normals
Blender computes, the area-weighted ones `core.normals` computes, and the
angle between them. Prints the five corners that moved most, each with its
fan:
- `faces`, how many faces the fan joins;
- `spread`, the largest angle between two of its faces' normals;
- `coherence`, |sum of area x normal| / sum of area: 1 when the faces are
  parallel, near 0 when their normals cancel;
- the smallest and largest face area in it, cm2.
Then, over every corner of every part, how many moved more than 45 degrees
and the coherence of their fans, so a cutoff can be read off a distribution
rather than chosen.

Prints what it measured and stops.
"""
import json
import math
import os
import sys

argv = sys.argv[sys.argv.index("--") + 1:]
ZOO, OUT, SPECIES = argv[0], os.path.abspath(argv[1]), argv[2:]
sys.path.insert(0, ZOO)
sys.path.insert(0, os.path.join(ZOO, "tools"))
os.makedirs(OUT, exist_ok=True)

import bpy  # noqa: E402
import coplanar_census as cc  # noqa: E402
from zoo_keeper.bpylayer import build  # noqa: E402
from zoo_keeper.core import kit, normals, partnames  # noqa: E402


def say(*a):
    print("[fan]", *a)


def _deg(a, b):
    la = math.sqrt(sum(x * x for x in a)) or 1.0
    lb = math.sqrt(sum(x * x for x in b)) or 1.0
    d = sum(x * y for x, y in zip(a, b)) / (la * lb)
    return math.degrees(math.acos(max(-1.0, min(1.0, d))))


def fans_of(faces, smooth, sharp):
    """The same grouping `core.normals` makes, returned as corner groups."""
    offset, total = [], 0
    for f in faces:
        offset.append(total)
        total += len(f)
    parent = list(range(total))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    edges = {}
    for fi, f in enumerate(faces):
        n = len(f)
        for k in range(n):
            a, b = f[k], f[(k + 1) % n]
            if a == b:
                continue
            key = (a, b) if a < b else (b, a)
            ka, kb = (k, (k + 1) % n) if a < b else ((k + 1) % n, k)
            edges.setdefault(key, []).append((fi, ka, kb, a < b))
    for key, uses in edges.items():
        if len(uses) != 2 or frozenset(key) in sharp:
            continue
        (f0, a0, b0, u0), (f1, a1, b1, u1) = uses
        if u0 == u1 or not (smooth[f0] and smooth[f1]):
            continue
        for c0, c1 in ((offset[f0] + a0, offset[f1] + a1), (offset[f0] + b0, offset[f1] + b1)):
            parent[find(c0)] = find(c1)
    owner = []
    for fi, f in enumerate(faces):
        owner += [fi] * len(f)
    return [find(c) for c in range(total)], owner


def part(obj, rows):
    me = obj.data
    if me.has_custom_normals:
        me.attributes.remove(me.attributes["custom_normal"])
    polys = me.polygons
    if not len(polys):
        return
    faces = [list(p.vertices) for p in polys]
    fn = [tuple(p.normal) for p in polys]
    area = [p.area for p in polys]
    smooth = [p.use_smooth for p in polys]
    sharp = {frozenset(e.vertices) for e in me.edges if e.use_edge_sharp}
    weighted = normals.weighted_corner_normals(faces, fn, area, smooth, sharp)
    default = [tuple(c.vector) for c in me.corner_normals]
    group, owner = fans_of(faces, smooth, sharp)
    members = {}
    for c, g in enumerate(group):
        members.setdefault(g, set()).add(owner[c])
    for c in range(len(default)):
        fs = sorted(members[group[c]])
        s = [0.0, 0.0, 0.0]
        tot = 0.0
        for fi in fs:
            for i in range(3):
                s[i] += fn[fi][i] * area[fi]
            tot += area[fi]
        coh = math.sqrt(sum(x * x for x in s)) / tot if tot > 0 else 0.0
        spread = max((_deg(fn[a], fn[b]) for a in fs for b in fs), default=0.0)
        rows.append({"part": obj.name, "moved": _deg(default[c], weighted[c]),
                     "faces": len(fs), "spread": spread, "coherence": coh,
                     "amin": min(area[f] for f in fs) * 1e4,
                     "amax": max(area[f] for f in fs) * 1e4})


def main():
    roles = cc._role_map(kit)
    for sp in SPECIES:
        with open(os.path.join(ZOO, "zoo_keeper", "genome", "species", sp + ".json"),
                  encoding="utf-8") as f:
            g = json.load(f)
        dims = cc._corner_dims(g, "default")
        cc._clear(bpy)
        role, size_mod = roles.get(sp, ("prop", "full"))
        slot = {"slot_id": f"{sp}_0", "role": role, "size_mod": size_mod, "style": 1,
                "fit": {"dims": dims, "pivot": "center"}}
        if role == "prop":
            slot["species"] = sp
        plan = kit.plan_kit({"building_id": "fan_probe", "slots": [slot]},
                            theme="delco_1997", style=1)
        res = build.build_module(plan["modules"][0], OUT, theme="delco_1997", style=1,
                                 options={"save_blend": False})
        coll = bpy.data.collections[res["stem"]]
        rows = []
        for obj in coll.objects:
            if obj.type == "MESH" and not obj.name.endswith(partnames.COL_SUFFIXES):
                part(obj, rows)
        rows.sort(key=lambda r: -r["moved"])
        say(sp, "corners", len(rows))
        for r in rows[:5]:
            say("   moved %6.2f deg  faces %2d  spread %6.2f deg  coherence %.3f  "
                "area %.3g..%.3g cm2  %s" % (r["moved"], r["faces"], r["spread"],
                                             r["coherence"], r["amin"], r["amax"], r["part"]))
        far = [r for r in rows if r["moved"] > 45.0]
        near = [r for r in rows if r["moved"] <= 45.0]
        for label, rs in (("moved > 45", far), ("moved <= 45", near)):
            if rs:
                cs = sorted(r["coherence"] for r in rs)
                say("   %s: %d corners, coherence min %.3f median %.3f max %.3f"
                    % (label, len(rs), cs[0], cs[len(cs) // 2], cs[-1]))


main()
