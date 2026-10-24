"""Triangles of a .glb lying wholly inside an XZ rectangle, per node and material, in the glb's own frame (glTF:
metres, Y up; node translations applied down the tree, rotations and scales NOT -- a turned node is flagged).
Measurements only: per node and material, how many triangles, and their bounds.

    python glb_faces_in_rect.py <file.glb> <x0> <x1> <z0> <z1>
"""
import json
import struct
import sys

import numpy as np

path = sys.argv[1]
X0, X1, Z0, Z1 = (float(a) for a in sys.argv[2:6])
raw = open(path, "rb").read()
assert raw[:4] == b"glTF", "not a binary glTF"
clen = struct.unpack_from("<I", raw, 12)[0]
g = json.loads(raw[20:20 + clen])
b0 = 20 + clen
blen = struct.unpack_from("<I", raw, b0)[0]
blob = raw[b0 + 8:b0 + 8 + blen]
COMP = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}
DT = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8}


def arr(i):
    a = g["accessors"][i]
    v = g["bufferViews"][a["bufferView"]]
    off = v.get("byteOffset", 0) + a.get("byteOffset", 0)
    n = COMP[a["type"]]
    assert "byteStride" not in v or v["byteStride"] == n * np.dtype(DT[a["componentType"]]).itemsize, "strided view"
    out = np.frombuffer(blob, dtype=DT[a["componentType"]], count=a["count"] * n, offset=off)
    return out.reshape(-1, n) if n > 1 else out


mats = g.get("materials", [])
total = 0


def walk(ni, off, turned):
    global total
    nd = g["nodes"][ni]
    t = np.array(nd.get("translation", [0, 0, 0]), dtype=float) + off
    turned = turned or bool(nd.get("rotation") or nd.get("scale") or nd.get("matrix"))
    if "mesh" in nd:
        for p in g["meshes"][nd["mesh"]]["primitives"]:
            P = arr(p["attributes"]["POSITION"]).astype(float) + t
            idx = arr(p["indices"]) if "indices" in p else np.arange(len(P))
            T = P[idx.reshape(-1, 3)]
            inside = ((T[:, :, 0] >= X0) & (T[:, :, 0] <= X1) & (T[:, :, 2] >= Z0) & (T[:, :, 2] <= Z1)).all(axis=1)
            k = int(inside.sum())
            if k:
                sel = T[inside].reshape(-1, 3)
                total += k
                print("IN %-28s mat=%-34s tris %4d  lo %s hi %s turned=%s" % (
                    nd.get("name"), mats[p["material"]].get("name") if "material" in p else None, k,
                    np.round(sel.min(axis=0), 4).tolist(), np.round(sel.max(axis=0), 4).tolist(), turned))
    for c in nd.get("children", []):
        walk(c, t, turned)


for root in g["scenes"][g.get("scene", 0)]["nodes"]:
    walk(root, np.zeros(3), False)
print("%d triangles wholly inside x %.3f..%.3f z %.3f..%.3f" % (total, X0, X1, Z0, Z1))
