"""Read-only: per kit-module GLB (wall_/window_/doorway_/breach_), its meshes,
their materials and triangles, plus the module's bounding size from the
POSITION accessors' min/max (glTF local frame, metres, Y up). Prints only.
"""
import json
import os
import struct
import sys

root = sys.argv[1]
for fn in sorted(os.listdir(root)):
    if not fn.endswith(".glb") or not fn.startswith(("wall_", "window_", "doorway_", "breach_")):
        continue
    data = open(os.path.join(root, fn), "rb").read()
    clen = struct.unpack_from("<I", data, 12)[0]
    gj = json.loads(data[20:20 + clen].decode("utf-8"))
    acc = gj["accessors"]
    mats = gj.get("materials", [])
    rows = []
    lo = [1e9] * 3
    hi = [-1e9] * 3
    tot = 0
    for m in gj.get("meshes", []):
        for p in m["primitives"]:
            a = acc[p["attributes"]["POSITION"]]
            for k in range(3):
                lo[k] = min(lo[k], a["min"][k])
                hi[k] = max(hi[k], a["max"][k])
            t = acc[p["indices"]]["count"] // 3
            tot += t
            mn = mats[p["material"]]["name"] if "material" in p else "<none>"
            rows.append((m.get("name"), mn, t, a["count"]))
    size = [round(hi[k] - lo[k], 2) for k in range(3)]
    print("%s  size(x,y,z)=%s  meshes=%d  tris=%d" % (fn, size, len(rows), tot))
    for r in rows:
        print("     %-34s %-40s tris %4d verts %4d" % r)
