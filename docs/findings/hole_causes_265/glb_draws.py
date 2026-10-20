"""Materials and draw submissions of each Zoo module (.glb) in a folder, read off its glTF JSON chunk.

A probe: prints what it measured and stops. A submission is one primitive of a mesh a node draws; nodes named
`-colonly` are collision and not drawn.

    python docs/findings/hole_causes_265/glb_draws.py <folder of .glb> [<substring of the name>]
"""
import glob
import json
import os
import struct
import sys

d = sys.argv[1]
sub = sys.argv[2] if len(sys.argv) > 2 else ""
for p in sorted(glob.glob(os.path.join(d, "*.glb"))):
    if sub not in os.path.basename(p):
        continue
    b = open(p, "rb").read()
    magic, _ver, _length = struct.unpack_from("<III", b, 0)
    assert magic == 0x46546C67, p
    clen, ctype = struct.unpack_from("<II", b, 12)
    assert ctype == 0x4E4F534A, p
    g = json.loads(b[20:20 + clen])
    meshes = g.get("meshes", [])
    nodes = g.get("nodes", [])
    drawn = sum(len(meshes[n["mesh"]]["primitives"]) for n in nodes
                if "mesh" in n and not n.get("name", "").endswith("-colonly"))
    mats = sorted({m.get("name") for m in g.get("materials", [])})
    print("%-72s materials %d  draws %d  %s" % (os.path.basename(p)[:-4], len(mats), drawn, ", ".join(mats)))
