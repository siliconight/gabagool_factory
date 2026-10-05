"""Count mesh nodes and primitives in each building's dressing GLB.

    python glb_census.py <package_dir> [--names]

Reads the GLB's JSON chunk only. A primitive is one surface, which Godot
submits as one draw call when its node is visible. Groups mesh nodes by
the name with trailing digits/underscored indices stripped, so the kinds of
cover show. --names prints ten raw node names from the first GLB and stops.
Fails on a file that is not a glTF binary.
"""
import collections
import json
import pathlib
import re
import struct
import sys

pkg = pathlib.Path(sys.argv[1])
files = sorted(pkg.glob("lot/*/art/dressing/*_dressing.glb"))
if not files:
    raise SystemExit(f"{pkg}: no lot/*/art/dressing/*_dressing.glb")


def gltf(path):
    b = path.read_bytes()
    magic, ver, length = struct.unpack_from("<III", b, 0)
    if magic != 0x46546C67:
        raise SystemExit(f"{path}: not a GLB")
    clen, ctype = struct.unpack_from("<II", b, 12)
    if ctype != 0x4E4F534A:
        raise SystemExit(f"{path}: first chunk is not JSON")
    return json.loads(b[20:20 + clen])


if "--names" in sys.argv:
    g = gltf(files[0])
    for n in g.get("nodes", [])[:10]:
        print(n.get("name"), "mesh" in n)
    raise SystemExit(0)


def kind(name):
    return re.sub(r"(_\d+|\.\d+|_[0-9a-f]{6,})+$", "", name or "?")


tot = collections.Counter()
tot_prims = collections.Counter()
print("%-24s %6s %6s %6s  %s" % ("building", "nodes", "meshN", "prims", "materials"))
for f in files:
    g = gltf(f)
    meshes = g.get("meshes", [])
    mesh_nodes = [n for n in g.get("nodes", []) if "mesh" in n]
    prims = sum(len(meshes[n["mesh"]]["primitives"]) for n in mesh_nodes)
    mats = [m.get("name") for m in g.get("materials", [])]
    print("%-24s %6d %6d %6d  %s" % (f.parent.parent.parent.name, len(g.get("nodes", [])),
                                     len(mesh_nodes), prims, ",".join(sorted(set(mats)))))
    for n in mesh_nodes:
        k = kind(n.get("name"))
        tot[k] += 1
        tot_prims[k] += len(meshes[n["mesh"]]["primitives"])
print()
print("mesh nodes / primitives by name kind (all buildings):")
for k, v in sorted(tot.items(), key=lambda kv: -kv[1]):
    print("  %-32s %6d %6d" % (k, v, tot_prims[k]))
print("  %-32s %6d %6d" % ("TOTAL", sum(tot.values()), sum(tot_prims.values())))
