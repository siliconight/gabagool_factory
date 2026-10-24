"""Every node of a .glb whose mesh's bounds are rod-shaped -- two sides under THIN, the third over LONG -- in the glb's
own frame (glTF: metres, Y up; a node's translation added, its rotation and scale NOT applied, so a turned node's
bounds are reported as authored and flagged). Measurements only: name, translation, size, whether it is turned.

    python glb_rods.py <file.glb> [THIN] [LONG]
"""
import json
import struct
import sys

path = sys.argv[1]
THIN = float(sys.argv[2]) if len(sys.argv) > 2 else 0.15
LONG = float(sys.argv[3]) if len(sys.argv) > 3 else 0.8
raw = open(path, "rb").read()
magic, _ver, _len = struct.unpack_from("<4sII", raw, 0)
assert magic == b"glTF", "not a binary glTF: %r" % magic
clen, ctype = struct.unpack_from("<I4s", raw, 12)
assert ctype == b"JSON", ctype
g = json.loads(raw[20:20 + clen])
meshes = g.get("meshes", [])
acc = g.get("accessors", [])
n_rods = 0
for node in g.get("nodes", []):
    if "mesh" not in node:
        continue
    lo, hi = [1e9] * 3, [-1e9] * 3
    for prim in meshes[node["mesh"]].get("primitives", []):
        a = acc[prim["attributes"]["POSITION"]]
        if "min" not in a:
            continue
        lo = [min(x, y) for x, y in zip(lo, a["min"])]
        hi = [max(x, y) for x, y in zip(hi, a["max"])]
    if lo[0] > hi[0]:
        continue
    size = [h - l for l, h in zip(lo, hi)]
    s = sorted(size)
    if s[0] < THIN and s[1] < THIN and s[2] > LONG:
        t = node.get("translation", [0, 0, 0])
        centre = [t[i] + (lo[i] + hi[i]) / 2.0 for i in range(3)]
        turned = bool(node.get("rotation") or node.get("scale") or node.get("matrix"))
        print("ROD %-40s centre (%.3f, %.3f, %.3f) size (%.3f, %.3f, %.3f) turned=%s" % (
            node.get("name"), centre[0], centre[1], centre[2], size[0], size[1], size[2], turned))
        n_rods += 1
print("%d mesh nodes, %d rod-shaped (THIN %.2f, LONG %.2f)" % (
    sum(1 for n in g.get("nodes", []) if "mesh" in n), n_rods, THIN, LONG))
