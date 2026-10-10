"""Roadmap 221: which face of the building each merged dressing mesh's vertices lie on.

    python docs/findings/patina_cover_normals/merge_faces.py <building>_dressing.glb [...]

Zoo merges a building's covers per side and material (`CoverN_concrete`, ...; Zoo 1.68.0), so
that a side enters and leaves view together. For every mesh, this counts its vertices by the
face they lie nearest: N, S, E, W by which outer edge of the dressing's own bounds the vertex is
closest to, in the horizontal plane, and UP for those within 0.3 m of the top. A per-side mesh
whose vertices lie on its own side is culled with that side; one holding the opposite face's
too is not.

Frame: the GLB's own, glTF Y-up metres; north is -Z (Godot is plan (x, -y)). It reads the
accessors directly, with no Godot and no Blender. It prints what it measured and stops.
"""
import json
import struct
import sys
from collections import Counter


def _glb(path):
    raw = open(path, "rb").read()
    if raw[:4] != b"glTF":
        raise SystemExit(f"{path}: not a GLB")
    n, kind = struct.unpack_from("<I4s", raw, 12)
    if kind != b"JSON":
        raise SystemExit(f"{path}: first chunk is not JSON")
    doc = json.loads(raw[20:20 + n])
    off = 20 + n
    bn, bkind = struct.unpack_from("<I4s", raw, off)
    return doc, raw[off + 8:off + 8 + bn] if bkind == b"BIN\x00" else b""


def _positions(doc, blob, acc_i):
    acc = doc["accessors"][acc_i]
    if acc.get("type") != "VEC3" or acc.get("componentType") != 5126:
        raise SystemExit(f"accessor {acc_i}: not float VEC3 positions")
    view = doc["bufferViews"][acc["bufferView"]]
    start = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
    stride = view.get("byteStride", 12)
    return [struct.unpack_from("<3f", blob, start + i * stride) for i in range(acc["count"])]


def main(paths):
    for path in paths:
        doc, blob = _glb(path)
        meshes = {}
        for node in doc.get("nodes", []):
            if "mesh" not in node:
                continue
            if any(k in node for k in ("matrix", "rotation", "scale")) or node.get("translation", [0, 0, 0]) != [0, 0, 0]:
                raise SystemExit(f"{path}: node {node.get('name')} is transformed; this reads raw positions")
            pts = []
            for prim in doc["meshes"][node["mesh"]]["primitives"]:
                pts += _positions(doc, blob, prim["attributes"]["POSITION"])
            meshes[node.get("name", "?")] = pts
        allp = [p for ps in meshes.values() for p in ps]
        x0, x1 = min(p[0] for p in allp), max(p[0] for p in allp)
        z0, z1 = min(p[2] for p in allp), max(p[2] for p in allp)
        top = max(p[1] for p in allp)
        print(f"{path}: x {x0:.2f}..{x1:.2f}, z {z0:.2f}..{z1:.2f}, top {top:.2f} (glTF frame)")
        for name in sorted(meshes):
            c = Counter()
            for x, y, z in meshes[name]:
                if y > top - 0.3:
                    c["UP"] += 1
                    continue
                d = {"W": x - x0, "E": x1 - x, "N": z - z0, "S": z1 - z}
                c[min(d, key=d.get)] += 1
            print(f"  {name:28s} " + "  ".join(f"{k} {c[k]:5d}" for k in ("N", "S", "E", "W", "UP")))


if __name__ == "__main__":
    main(sys.argv[1:])
