"""Zoo 1.87.0's weighted normals through the whole Blender path: the export,
the merge, and ingest (roadmap 214, trial 1).

Run inside Blender, background, once per Zoo tree:

    C:\\blender\\blender.exe -b --factory-startup --python export_probe.py -- <zoo root> <out dir> build
    C:\\blender\\blender.exe -b --factory-startup --python export_probe.py -- <zoo root> <out dir> ingest <file.glb>

`build` prints, read from each GLB the exporter wrote:
- ONE PART, the bevelled 0.6 x 0.4 x 0.5 m crate of `api_probe.py`, exported
  with and without `weighted_normals` (a 1.86.0 tree has no such keyword and
  says so);
- TWO PARTS of one family and one material, which the merge packs into one
  mesh: the GLB's mesh count, and the big-face splay of the packed mesh.
  1.87.0 must carry the weighted normals through the merge;
- and writes `pair_authored.glb`: the same two parts, unmerged, every corner
  normal set to +Z -- normals no build would make, so a reader can tell an
  author's normals from recomputed ones.

`ingest <file.glb>` runs `bpylayer.ingest.ingest` on that file and prints the
output's mesh count and the share of its normals within 0.5 degrees of up
(glTF +Y, Blender's +Z). Kept, it is all of them.

Big-face splay: degrees between each corner's normal and its face's normal on
triangles over 0.01 m2. Frame: the GLB's, Y up; no angle depends on it.
"""
import json
import math
import os
import struct
import sys

import bmesh
import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
ZOO, OUT, MODE = argv[0], argv[1], argv[2]
sys.path.insert(0, ZOO)
os.makedirs(OUT, exist_ok=True)

from zoo_keeper.bpylayer import export, geometry  # noqa: E402

SIZE = (0.60, 0.40, 0.50)
BEVEL = 0.014
BIG = 0.01


def say(*a):
    print("[wn]", *a)


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
    meshes = 0
    for mesh in doc["meshes"]:
        for prim in mesh["primitives"]:
            if "NORMAL" not in prim["attributes"]:
                continue
            meshes += 1
            base = len(pos)
            pos += acc(prim["attributes"]["POSITION"])
            nor += acc(prim["attributes"]["NORMAL"])
            idx += [base + t[0] for t in acc(prim["indices"])]
    return meshes, pos, nor, idx


def _deg(a, b):
    d = sum(x * y for x, y in zip(a, b))
    return math.degrees(math.acos(max(-1.0, min(1.0, d))))


def splay(pos, nor, idx):
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


def row(label, path):
    meshes, pos, nor, idx = read_glb(path)
    s = splay(pos, nor, idx)
    say(label, "meshes %d, verts %d, tris %d, big-face corners %d, splay max %.2f mean %.2f deg"
        % (meshes, len(pos), len(idx) // 3, len(s), max(s), sum(s) / len(s)))


def fresh(name):
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    return coll


def crate(coll, name, centre, mat=None):
    bm = bmesh.new()
    geometry.add_box(bm, centre, SIZE)
    obj = geometry.bm_to_object(bm, name, coll, finish=True, bevel=BEVEL)
    if mat is not None:
        obj.data.materials.append(mat)
    return obj


def export_with(coll, path, **kw):
    try:
        export.export_glb(path, coll, share_textures=False, **kw)
        return True
    except TypeError as exc:          # a 1.86.0 export_glb has no such keyword
        say("  export_glb%r refused: %s" % (tuple(kw), exc))
        return False


def build():
    say("zoo", ZOO)
    for label, kw in (("one part, default", {}),
                      ("one part, weighted_normals=False", {"weighted_normals": False})):
        coll = fresh("one")
        crate(coll, "Crate", (0.0, 0.0, 0.0))
        p = os.path.join(OUT, "one_%s.glb" % ("off" if kw else "default"))
        if export_with(coll, p, **kw):
            row(label, p)
    mat = bpy.data.materials.new("M_Probe")
    coll = fresh("pair")
    crate(coll, "Crate_a", (0.0, 0.0, 0.0), mat)
    crate(coll, "Crate_b", (1.0, 0.0, 0.0), mat)
    p = os.path.join(OUT, "pair_merged.glb")
    export_with(coll, p)
    row("two parts, one family and material, merged", p)
    for obj in coll.objects:
        obj.data.normals_split_custom_set([(0.0, 0.0, 1.0)] * len(obj.data.loops))
    p = os.path.join(OUT, "pair_authored.glb")
    export_with(coll, p, merge_parts=False, weighted_normals=False) or \
        export_with(coll, p, merge_parts=False)
    meshes, pos, nor, idx = read_glb(p)
    up = sum(_deg((0.0, 1.0, 0.0), n) < 0.5 for n in nor)
    say("wrote pair_authored.glb: meshes %d, normals within 0.5 deg of up %d of %d"
        % (meshes, up, len(nor)))


def ingest(src):
    from zoo_keeper.bpylayer import ingest as ingest_mod
    say("zoo", ZOO)
    res = ingest_mod.ingest(src, OUT, name="pair", collision=False)
    p = os.path.join(OUT, "pair.glb")
    meshes, pos, nor, idx = read_glb(p)
    up = sum(_deg((0.0, 1.0, 0.0), n) < 0.5 for n in nor)
    say("ingested %s -> meshes %d, normals within 0.5 deg of up %d of %d"
        % (os.path.basename(src), meshes, up, len(nor)))
    return res


if MODE == "build":
    build()
else:
    ingest(argv[3])
