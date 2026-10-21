"""Read-only: placed triangles (GLB visual triangles x placements in site.tscn)
and placed surfaces (visual primitives x placements) for Lot's cover props.
Visual = node name without a -col/-colonly/-convcolonly suffix and mesh
referenced by a node. Prints only.
"""
import json
import os
import re
import struct
import sys
from collections import Counter

pkg = sys.argv[1]
t = open(os.path.join(pkg, "site.tscn"), encoding="utf-8").read()
ext = {}
for m in re.finditer(r'\[ext_resource type="([^"]+)"[^\]]*path="([^"]+)"[^\]]*id="([^"]+)"\]', t):
    ext[m.group(3)] = m.group(2)
inst = Counter()
for m in re.finditer(r'instance=ExtResource\("([^"]+)"\)', t):
    inst[ext[m.group(1)]] += 1


def glb_stats(path):
    data = open(path, "rb").read()
    clen = struct.unpack_from("<I", data, 12)[0]
    gj = json.loads(data[20:20 + clen].decode("utf-8"))
    acc = gj["accessors"]
    tris = 0
    surf = 0
    for n in gj.get("nodes", []):
        if "mesh" not in n:
            continue
        if re.search(r"-(col|colonly|convcolonly)$", n.get("name", "")):
            continue
        for p in gj["meshes"][n["mesh"]]["primitives"]:
            surf += 1
            tris += acc[p["indices"]]["count"] // 3
    return tris, surf


rows = []
for path, n in inst.items():
    fp = os.path.join(pkg, path.replace("res://", ""))
    if not fp.endswith(".glb") or not os.path.exists(fp):
        continue
    tr, sf = glb_stats(fp)
    rows.append((tr * n, sf * n, n, tr, sf, os.path.basename(fp)))
rows.sort(reverse=True)
tt = sum(r[0] for r in rows)
ts = sum(r[1] for r in rows)
print("cover archetypes placed: %d, placements %d, placed tris %d, placed surfaces %d" % (
    len(rows), sum(r[2] for r in rows), tt, ts))
print("%10s %8s %5s %7s %5s  %s" % ("placed_tri", "plc_surf", "n", "tris", "surf", "glb"))
for r in rows[:15]:
    print("%10d %8d %5d %7d %5d  %s" % r)
