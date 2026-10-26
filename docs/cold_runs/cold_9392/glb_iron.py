"""Cold run 9392: in a building GLB, every mesh primitive whose material's base colour is the door hardware's iron
(Zoo doors.IRON, 0.06/0.06/0.065 linear) or whose material or node name names a knob, hardware or railing -- its node,
mesh, material, and whether it carries TEXCOORD_0 (Level Factory's world skin makes a surface with UV density
world-triplanar and leaves one without alone, and the Empties' per-side merge keys on that). Measurements only.

    python glb_iron.py <building.glb> [...]
"""
import json
import struct
import sys

for path in sys.argv[1:]:
    b = open(path, "rb").read()
    assert b[:4] == b"glTF", "%s is not a GLB" % path
    n = struct.unpack_from("<I", b, 12)[0]
    g = json.loads(b[20:20 + n])
    mats = g.get("materials", [])
    owners = {}
    for i, nd in enumerate(g.get("nodes", [])):
        if "mesh" in nd:
            owners.setdefault(nd["mesh"], []).append(nd.get("name", "#%d" % i))
    print(path)
    hits = 0
    for mi, m in enumerate(g.get("meshes", [])):
        for p in m.get("primitives", []):
            mat = mats[p["material"]] if "material" in p else {}
            name = mat.get("name", "")
            col = mat.get("pbrMetallicRoughness", {}).get("baseColorFactor", [1, 1, 1, 1])
            iron = all(abs(a - e) < 0.004 for a, e in zip(col[:3], (0.06, 0.06, 0.065)))
            nodes = ",".join(owners.get(mi, []))
            words = (name + " " + nodes + " " + m.get("name", "")).lower()
            if iron or any(w in words for w in ("knob", "hardware", "railing")):
                hits += 1
                print("  node %s mesh %s material %s colour %s iron %s TEXCOORD_0 %s" % (
                    nodes, m.get("name"), name, [round(c, 4) for c in col[:3]], iron,
                    "TEXCOORD_0" in p["attributes"]))
    print("  %d primitive(s)" % hits)
