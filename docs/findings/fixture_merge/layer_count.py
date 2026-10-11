"""Count a fixtures GLB's submissions: one per primitive of every visual mesh node.

    python docs/findings/fixture_merge/layer_count.py <a.glb> [<b.glb> ...]

Reads each GLB's JSON chunk (no third-party parser) and prints, per file, its mesh nodes, its
submissions -- a visual mesh node's every primitive, colliders (`-colonly` names) left out because
Godot imports them as shapes, not draws -- its `LuxEmit_*` markers, and the submissions by
material. Godot draws one surface of one MeshInstance3D per submission. It prints what it measured
and stops.
"""
import json
import struct
import sys


def gltf(path):
    raw = open(path, "rb").read()
    if raw[:4] != b"glTF":
        raise SystemExit("%s: not a GLB" % path)
    ln, kind = struct.unpack_from("<I4s", raw, 12)
    if kind != b"JSON":
        raise SystemExit("%s: first chunk is %r, not JSON" % (path, kind))
    return json.loads(raw[20:20 + ln])


def count(path):
    j = gltf(path)
    mats = [m.get("name", "") for m in j.get("materials", [])]
    nodes = [n for n in j.get("nodes", []) if "mesh" in n and "colonly" not in n.get("name", "").lower()]
    by_mat = {}
    subs = 0
    for n in nodes:
        for prim in j["meshes"][n["mesh"]]["primitives"]:
            name = mats[prim["material"]] if "material" in prim else "(none)"
            by_mat[name] = by_mat.get(name, 0) + 1
            subs += 1
    marks = sum(1 for n in j.get("nodes", []) if n.get("name", "").startswith("LuxEmit"))
    return len(nodes), subs, marks, by_mat


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for p in sys.argv[1:]:
        nodes, subs, marks, by_mat = count(p)
        print("[layer] %s: %d visual mesh nodes, %d submissions, %d LuxEmit markers" % (p, nodes, subs, marks))
        for name in sorted(by_mat):
            print("[layer]   %-60s %4d" % (name, by_mat[name]))
