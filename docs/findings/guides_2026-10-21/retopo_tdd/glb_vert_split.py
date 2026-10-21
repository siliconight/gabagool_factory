"""Read-only: per GLB group, render vertices (POSITION accessor count, which in
glTF is already one vertex per unique corner attribute set) against unique
positions (POSITION values quantised to 0.1 mm, per primitive), and triangles.

ratio_split = render_verts / unique_positions  -> how many GPU vertices each
3D point became (UV seams, hard normals, colour splits, material splits are
already applied by the exporter). verts_per_tri for scale.
Frame: glTF local space of each mesh, metres. Prints only.
"""
import json
import os
import struct
import sys
from collections import defaultdict

ROOT = sys.argv[1]


def read_glb(path):
    with open(path, "rb") as f:
        data = f.read()
    magic, ver, length = struct.unpack_from("<4sII", data, 0)
    clen, ctype = struct.unpack_from("<II", data, 12)
    gj = json.loads(data[20:20 + clen].decode("utf-8"))
    off = 20 + clen
    bin_ = b""
    if off < len(data):
        blen, btype = struct.unpack_from("<II", data, off)
        bin_ = data[off + 8: off + 8 + blen]
    return gj, bin_


def group_of(rel):
    parts = rel.replace("\\", "/").split("/")
    if parts[0] == "lot":
        if len(parts) >= 4 and parts[2] == "art":
            return "lot/*/art/" + parts[3]
        return "lot/*/(site_base glb)"
    return parts[0]


G = defaultdict(lambda: [0, 0, 0, 0])  # verts, unique_pos, tris, prims
worst = defaultdict(list)
for dp, dn, fns in os.walk(ROOT):
    dn[:] = [d for d in dn if d != ".godot"]
    for fn in fns:
        if not fn.endswith(".glb"):
            continue
        p = os.path.join(dp, fn)
        rel = os.path.relpath(p, ROOT)
        g = group_of(rel)
        gj, bin_ = read_glb(p)
        acc = gj.get("accessors", [])
        bvs = gj.get("bufferViews", [])
        fv = fu = ft = 0
        for mesh in gj.get("meshes", []):
            for prim in mesh.get("primitives", []):
                a = acc[prim["attributes"]["POSITION"]]
                n = a["count"]
                bv = bvs[a["bufferView"]]
                base = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
                stride = bv.get("byteStride", 12)
                seen = set()
                for i in range(n):
                    x, y, z = struct.unpack_from("<fff", bin_, base + i * stride)
                    seen.add((round(x * 1e4), round(y * 1e4), round(z * 1e4)))
                if "indices" in prim:
                    t = acc[prim["indices"]]["count"] // 3
                else:
                    t = n // 3
                fv += n
                fu += len(seen)
                ft += t
                G[g][3] += 1
        G[g][0] += fv
        G[g][1] += fu
        G[g][2] += ft
        if fu:
            worst[g].append((fv / fu, fn, fv, fu, ft))

for g in sorted(G):
    v, u, t, pr = G[g]
    print("%-28s prims %5d  render_verts %8d  unique_pos %8d  ratio %.2f  tris %8d  verts/tri %.2f" % (
        g, pr, v, u, (v / u if u else 0), t, (v / t if t else 0)))
    for r in sorted(worst[g], reverse=True)[:3]:
        print("     worst ratio %.2f  %s  (verts %d, unique %d, tris %d)" % r)
