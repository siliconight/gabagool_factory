"""What a module GLB holds, read off its own JSON chunk: meshes, primitives per mesh, materials, nodes, and each
POSITION accessor's bounds (metres, glTF's Y up). No dependency: a GLB is a 12-byte header and length-prefixed chunks.

    python patches/zoo_crowd_barrier/glb_facts.py <file.glb> [...]

Prints what it read and stops.
"""
import json
import struct
import sys

for path in sys.argv[1:]:
    data = open(path, "rb").read()
    magic, version, length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or length != len(data):
        raise SystemExit("FAIL: %s is not a whole GLB" % path)
    clen, ctype = struct.unpack_from("<I4s", data, 12)
    if ctype != b"JSON":
        raise SystemExit("FAIL: %s's first chunk is not JSON" % path)
    g = json.loads(data[20:20 + clen].decode("utf-8"))
    meshes = g.get("meshes", [])
    print(path)
    print("   nodes %d: %s" % (len(g.get("nodes", [])), [n.get("name") for n in g.get("nodes", [])]))
    print("   materials %d: %s" % (len(g.get("materials", [])), [m.get("name") for m in g.get("materials", [])]))
    for m in meshes:
        print("   mesh %r: %d primitive(s)" % (m.get("name"), len(m.get("primitives", []))))
        for p in m.get("primitives", []):
            acc = g["accessors"][p["attributes"]["POSITION"]]
            print("      POSITION %d verts, min %s max %s, material %s" % (
                acc.get("count"), [round(v, 4) for v in acc.get("min", [])],
                [round(v, 4) for v in acc.get("max", [])], p.get("material")))
