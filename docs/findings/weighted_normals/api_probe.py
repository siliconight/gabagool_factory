"""Weighted normals on four parts, through Zoo's own build path, read back
out of the GLB the exporter wrote (roadmap 214, trial 1).

Run inside Blender, background:

    C:\\blender\\blender.exe -b --factory-startup --python api_probe.py -- <zoo root> <out dir>

Prints what it measured and stops:
- the Blender version, and which custom-normal calls a MESH INSTANCE answers
  to. Run 1 asked `hasattr(bpy.types.Mesh, name)` instead, which said False
  for all four, including `normals_split_custom_set`, the call this probe
  then made successfully. The RNA class does not list them; the instance
  does. Kept so the class check is not trusted again.
- per part, read from each exported GLB: the vertex count; on box parts,
  the angle in degrees between each big-face corner's normal and its face's
  normal (triangles over `BIG` m2), max and mean; and how far each vertex
  normal moved between the two states (Zoo today; area-weighted).
- whether removing the `custom_normal` attribute puts the default normals
  back. Run 1 tried zero vectors through `normals_split_custom_set`, which
  in Blender 5.1.1 did NOT: the weighted normals stayed.

Frame: Blender world, Z up, metres; the GLB is Y up, which changes no angle.
"""
import json
import math
import os
import struct
import sys

import bmesh
import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
ZOO, OUT = argv[0], argv[1]
sys.path.insert(0, ZOO)
os.makedirs(OUT, exist_ok=True)

from zoo_keeper.bpylayer import export, geometry  # noqa: E402

BEVEL = 0.014                  # the top of simple_car's genome style range
BIG = 0.01                     # m2: a triangle on a large face


def say(*a):
    print("[wn]", *a)


def _box(bm):
    geometry.add_box(bm, (0.0, 0.0, 0.0), (0.60, 0.40, 0.50))


def _tank(bm):
    geometry.add_cylinder(bm, (0.0, 0.0, 0.0), 0.30, 0.80, segments=14)


#: name: (shape, smooth angle, is a box). 50 is `SMOOTH_ANGLE_DEG`, Zoo's
#: default; 1.0 and 30.0 are what recipes pass to keep a part faceted or a
#: chamfer hard (`fire_hydrant`, `counter`, ...).
PARTS = {
    "crate_50": (_box, geometry.SMOOTH_ANGLE_DEG, True),
    "crate_30": (_box, 30.0, True),
    "crate_1": (_box, 1.0, True),
    "tank_50": (_tank, geometry.SMOOTH_ANGLE_DEG, False),
}


def build(name, shape, angle):
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    bm = bmesh.new()
    shape(bm)
    obj = geometry.bm_to_object(bm, name, coll, finish=True, bevel=BEVEL,
                                smooth_angle=angle)
    return coll, obj


def fans(bm):
    """Corner groups that share one normal: a vertex's corners joined across
    every smooth, two-faced edge at that vertex."""
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for f in bm.faces:
        for lp in f.loops:
            parent[lp] = lp
    for v in bm.verts:
        for e in v.link_edges:
            if not e.smooth or len(e.link_faces) != 2:
                continue
            f0, f1 = e.link_faces
            l0 = next(lp for lp in f0.loops if lp.vert == v)
            l1 = next(lp for lp in f1.loops if lp.vert == v)
            parent[find(l0)] = find(l1)
    groups = {}
    for lp in parent:
        groups.setdefault(find(lp), []).append(lp)
    return list(groups.values())


def area_weighted(me):
    """Per-corner normals: each fan's face normals summed by face area."""
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.normal_update()
    out = {}
    for group in fans(bm):
        n = [0.0, 0.0, 0.0]
        for lp in group:
            a = lp.face.calc_area()
            for i in range(3):
                n[i] += lp.face.normal[i] * a
        k = math.sqrt(sum(c * c for c in n)) or 1.0
        for lp in group:
            out[lp] = (n[0] / k, n[1] / k, n[2] / k)    # keyed by the loop itself
    corner = [out[lp] for f in bm.faces for lp in f.loops]   # from_mesh order
    bm.free()
    return corner


def read_glb(path):
    with open(path, "rb") as f:
        data = f.read()
    jlen = struct.unpack_from("<I", data, 12)[0]
    doc = json.loads(data[20:20 + jlen])
    binary = data[20 + jlen + 8:]

    def acc(i):
        a = doc["accessors"][i]
        bv = doc["bufferViews"][a["bufferView"]]
        off = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
        n = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[a["type"]]
        fmt = {5126: "f", 5123: "H", 5125: "I", 5121: "B"}[a["componentType"]]
        stride = bv.get("byteStride") or struct.calcsize("<" + fmt * n)
        return [struct.unpack_from("<" + fmt * n, binary, off + k * stride)
                for k in range(a["count"])]

    pos, nor, idx = [], [], []
    for mesh in doc["meshes"]:
        for prim in mesh["primitives"]:
            base = len(pos)
            pos += acc(prim["attributes"]["POSITION"])
            nor += acc(prim["attributes"]["NORMAL"])
            idx += [base + t[0] for t in acc(prim["indices"])]
    return pos, nor, idx


def _deg(a, b):
    d = sum(x * y for x, y in zip(a, b))
    return math.degrees(math.acos(max(-1.0, min(1.0, d))))


def splay(pos, nor, idx):
    """Degrees between vertex normals and their face normal, on big faces."""
    angles = []
    for t in range(0, len(idx), 3):
        a, b, c = (pos[i] for i in idx[t:t + 3])
        u = [b[i] - a[i] for i in range(3)]
        w = [c[i] - a[i] for i in range(3)]
        fn = [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2],
              u[0] * w[1] - u[1] * w[0]]
        ln = math.sqrt(sum(x * x for x in fn))
        if ln / 2.0 < BIG:
            continue
        fn = [x / ln for x in fn]
        angles += [_deg(fn, nor[i]) for i in idx[t:t + 3]]
    return angles


def export_and_read(coll, path):
    export.export_glb(path, coll, merge_parts=True, share_textures=False)
    return read_glb(path)


say("blender", bpy.app.version_string)
for name, (shape, angle, is_box) in PARTS.items():
    coll, obj = build(name, shape, angle)
    me = obj.data
    if name == "crate_50":
        for api in ("normals_split_custom_set", "normals_split_custom_set_from_vertices",
                    "corner_normals", "has_custom_normals"):
            say("class hasattr Mesh.%s" % api, hasattr(bpy.types.Mesh, api),
                "| instance", hasattr(me, api))
    p0, n0, i0 = export_and_read(coll, os.path.join(OUT, name + "_today.glb"))
    me.normals_split_custom_set(area_weighted(me))
    p1, n1, i1 = export_and_read(coll, os.path.join(OUT, name + "_weighted.glb"))
    row = [name, "smooth %g" % angle, "verts %d -> %d" % (len(p0), len(p1)),
           "tris %d -> %d" % (len(i0) // 3, len(i1) // 3)]
    if len(p0) == len(p1) and p0 == p1:
        moved = [_deg(a, b) for a, b in zip(n0, n1)]
        row.append("normals moved: max %.2f deg, %d of %d over 1 deg"
                   % (max(moved), sum(m > 1.0 for m in moved), len(moved)))
    else:
        row.append("positions differ: no per-vertex comparison")
    say(*row)
    if is_box:
        for label, (p, n, i) in (("today", (p0, n0, i0)), ("weighted", (p1, n1, i1))):
            s = splay(p, n, i)
            say("  ", name, label, "big-face corners %d, splay max %.2f mean %.2f deg"
                % (len(s), max(s), sum(s) / len(s)))
    if name == "crate_50":
        say("  corner attributes after set",
            sorted(a.name for a in me.attributes if a.domain == "CORNER"))
        me.attributes.remove(me.attributes["custom_normal"])
        p2, n2, i2 = export_and_read(coll, os.path.join(OUT, name + "_cleared.glb"))
        s = splay(p2, n2, i2)
        say("  ", name, "after removing custom_normal: has_custom_normals",
            me.has_custom_normals, "| splay max %.2f mean %.2f deg" % (max(s), sum(s) / len(s)))
