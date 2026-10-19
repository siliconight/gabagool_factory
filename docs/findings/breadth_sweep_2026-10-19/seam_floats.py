"""The floats at deli_a03's seam, exactly: every vertex of the storey-1 slab collider (`slab_col_1-colonly`) and the
up-stair's discharge plate collider (`stair1col_discharge_0-convcolonly`) whose x lies within 1 cm of local -13.0, with
repr(), plus each node's own translation / rotation / scale -- the package's GLB, the very file the engine loaded on
cold run 9333. A probe: prints what it measured and stops.

    python seam_floats.py <package dir>

Frame: the building's glTF frame (metres; x east, y up; plan y = -glTF z); the site places the building at
x -51, z -2.51 (`site.tscn`, node b0), so local x -13.0 is site x -64.0.
"""
import os
import struct
import sys

from pygltflib import GLTF2

pkg = os.path.abspath(sys.argv[1])
glb = os.path.join(pkg, "lot", "deli_a03", "site_base.glb")
g = GLTF2().load(glb)
blob = g.binary_blob()
SIZE = {5126: 4, 5123: 2, 5125: 4, 5121: 1}
FMT = {5126: "f", 5123: "H", 5125: "I", 5121: "B"}
NCOMP = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}
WANT = ("slab_col_1-colonly", "stair1col_discharge_0-convcolonly")


def read(ai):
    a = g.accessors[ai]
    bv = g.bufferViews[a.bufferView]
    n = NCOMP[a.type]
    stride = bv.byteStride or SIZE[a.componentType] * n
    base = (bv.byteOffset or 0) + (a.byteOffset or 0)
    return [struct.unpack_from("<%d%s" % (n, FMT[a.componentType]), blob, base + i * stride) for i in range(a.count)]


parents = {}
for i, nd in enumerate(g.nodes):
    for c in nd.children or []:
        parents[c] = i
print("glb", glb, os.path.getsize(glb), "bytes")
for i, nd in enumerate(g.nodes):
    if nd.name not in WANT:
        continue
    chain = []
    p = parents.get(i)
    while p is not None:
        chain.append(g.nodes[p].name)
        p = parents.get(p)
    print("node", repr(nd.name), "parents", chain or "(scene root)")
    print("   translation", nd.translation, "rotation", nd.rotation, "scale", nd.scale, "matrix", nd.matrix)
    for pi, prim in enumerate(g.meshes[nd.mesh].primitives):
        pos = read(prim.attributes.POSITION)
        acc = g.accessors[prim.attributes.POSITION]
        print("   primitive %d: %d vertices, accessor min %r max %r" % (pi, len(pos), acc.min, acc.max))
        near = sorted({p for p in pos if abs(p[0] - (-13.0)) < 0.01})
        for p in near:
            print("      x %r  y %r  z %r   (x + 13.0 = %r)" % (p[0], p[1], p[2], p[0] + 13.0))
        if not near:
            print("      no vertex within 1 cm of x -13.0")
