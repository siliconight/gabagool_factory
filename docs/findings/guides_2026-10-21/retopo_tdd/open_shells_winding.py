"""Read-only: how many OPAQUE visual primitives in a package's GLBs are open
shells, i.e. would show a hole if their back faces were culled.

Per primitive: weld vertices by position (quantised to 0.1 mm, glTF local
frame), build undirected edges from the triangle list, and count BOUNDARY
edges (used by exactly one triangle). 0 boundary edges = closed shell (back
faces never visible from outside if winding is consistent); > 0 = open.
Visual = node-referenced mesh whose node name has no -col/-colonly/
-convcolonly suffix. Material alphaMode read from the GLB. Prints only;
a measurement of topology, not a verdict on what culling would hide.
"""
import json
import os
import re
import struct
import sys
from collections import Counter, defaultdict

ROOT = sys.argv[1]


def load(path):
    d = open(path, "rb").read()
    n = struct.unpack_from("<I", d, 12)[0]
    g = json.loads(d[20:20 + n])
    off = 20 + n
    blen = struct.unpack_from("<I", d, off)[0]
    return g, d[off + 8: off + 8 + blen]


def read_acc(g, b, ai):
    a = g["accessors"][ai]
    bv = g["bufferViews"][a["bufferView"]]
    base = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    ct = a["componentType"]
    n = a["count"]
    if a["type"] == "VEC3" and ct == 5126:
        st = bv.get("byteStride", 12)
        return [struct.unpack_from("<fff", b, base + i * st) for i in range(n)]
    if a["type"] == "SCALAR":
        fmt, sz = {5121: ("<B", 1), 5123: ("<H", 2), 5125: ("<I", 4)}[ct]
        return [struct.unpack_from(fmt, b, base + i * sz)[0] for i in range(n)]
    raise ValueError("unexpected accessor %s/%s" % (a["type"], ct))


def group_of(rel):
    parts = rel.replace("\\", "/").split("/")
    if parts[0] == "lot":
        if len(parts) >= 4 and parts[2] == "art":
            return "lot/*/art/" + parts[3]
        return "lot/*/(site_base)"
    return parts[0]


res = defaultdict(Counter)
examples = defaultdict(list)
for dp, dn, fns in os.walk(ROOT):
    dn[:] = [x for x in dn if x != ".godot"]
    for fn in fns:
        if not fn.endswith(".glb"):
            continue
        p = os.path.join(dp, fn)
        rel = os.path.relpath(p, ROOT)
        grp = group_of(rel)
        g, b = load(p)
        mats = g.get("materials", [])
        used = set()
        for node in g.get("nodes", []):
            if "mesh" in node and not re.search(r"-(col|colonly|convcolonly)$", node.get("name", "")):
                used.add(node["mesh"])
        for mi in used:
            for prim in g["meshes"][mi]["primitives"]:
                mat = mats[prim["material"]] if "material" in prim else {}
                if mat.get("alphaMode", "OPAQUE") != "OPAQUE":
                    continue
                pos = read_acc(g, b, prim["attributes"]["POSITION"])
                idx = read_acc(g, b, prim["indices"]) if "indices" in prim else list(range(len(pos)))
                key = {}
                wid = []
                for v in pos:
                    k = (round(v[0] * 1e4), round(v[1] * 1e4), round(v[2] * 1e4))
                    wid.append(key.setdefault(k, len(key)))
                ec = Counter()
                de = Counter()
                vol = 0.0
                for t in range(0, len(idx) - 2, 3):
                    a, c, e = wid[idx[t]], wid[idx[t + 1]], wid[idx[t + 2]]
                    pa, pc, pe = pos[idx[t]], pos[idx[t + 1]], pos[idx[t + 2]]
                    vol += (pa[0] * (pc[1] * pe[2] - pc[2] * pe[1]) - pa[1] * (pc[0] * pe[2] - pc[2] * pe[0]) + pa[2] * (pc[0] * pe[1] - pc[1] * pe[0])) / 6.0
                    for u, v in ((a, c), (c, e), (e, a)):
                        if u != v:
                            ec[(min(u, v), max(u, v))] += 1
                            de[(u, v)] += 1
                boundary = sum(1 for k, v in ec.items() if v == 1)
                # a manifold edge (exactly two triangles) walked the SAME way by both is a flip;
                # edges used 3+ times are touching parts that a position weld joined -- not judged
                same_dir = sum(1 for (u, v), n in ec.items() if n == 2 and (de[(u, v)] == 2 or de[(v, u)] == 2))
                res[grp]["nonmanifold_edges"] += sum(1 for n in ec.values() if n > 2)
                if same_dir:
                    res[grp]["inconsistent_winding_prims"] += 1
                if not boundary:
                    res[grp]["closed_vol_pos" if vol > 0 else "closed_vol_nonpos"] += 1
                res[grp]["opaque_prims"] += 1
                if boundary:
                    res[grp]["open"] += 1
                    res[grp]["open_tris"] += len(idx) // 3
                    examples[grp].append((boundary, fn, mat.get("name", "?")))
                else:
                    res[grp]["closed"] += 1
                res[grp]["tris"] += len(idx) // 3

for grp in sorted(res):
    r = res[grp]
    print("%-24s opaque prims %4d  closed %4d (outward %4d, inward/zero %3d)  open %4d  flipped-manifold-edge prims %3d  edges used 3+ times %5d" % (
        grp, r["opaque_prims"], r["closed"], r["closed_vol_pos"], r["closed_vol_nonpos"], r["open"], r["inconsistent_winding_prims"], r["nonmanifold_edges"]))
