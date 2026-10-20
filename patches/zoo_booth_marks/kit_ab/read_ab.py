"""Read the booth A/B: each arm's four payphone modules out of their GLBs -- meshes, triangles, materials, images and
the hash of each mesh's positions -- and the paint atlases in _tex.

    python read_ab.py            (in _runs/booth_ab)
"""
import hashlib
import json
import pathlib
import struct

HERE = pathlib.Path(__file__).resolve().parent


def glb(path):
    raw = path.read_bytes()
    ln, _kind = struct.unpack_from("<I4s", raw, 12)
    doc = json.loads(raw[20:20 + ln])
    off = 20 + ln
    bln, _bk = struct.unpack_from("<I4s", raw, off)
    blob = raw[off + 8:off + 8 + bln]
    return doc, blob


def accessor_bytes(doc, blob, i):
    a = doc["accessors"][i]
    v = doc["bufferViews"][a["bufferView"]]
    start = v.get("byteOffset", 0) + a.get("byteOffset", 0)
    size = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[a["type"]] * {5126: 4, 5123: 2, 5125: 4}[a["componentType"]]
    return blob[start:start + size * a["count"]], a["count"]


def module(path):
    doc, blob = glb(path)
    meshes = []
    for m in doc.get("meshes", []):
        tris, pos = 0, hashlib.sha256()
        for p in m["primitives"]:
            _b, n = accessor_bytes(doc, blob, p["indices"])
            tris += n // 3
            pb, _n = accessor_bytes(doc, blob, p["attributes"]["POSITION"])
            pos.update(pb)
        meshes.append((m["name"], tris, pos.hexdigest()[:12]))
    mats = [m["name"] for m in doc.get("materials", [])]
    imgs = [i.get("name") or i.get("uri") for i in doc.get("images", [])]
    return meshes, mats, imgs


for arm in ("a", "b"):
    print("== arm", arm)
    for p in sorted((HERE / arm).glob("*.glb")):
        meshes, mats, imgs = module(p)
        print(p.name, p.stat().st_size, "bytes")
        for name, tris, h in meshes:
            print("   mesh", name, tris, "tris, positions", h)
        print("   materials", mats)
        print("   images", imgs)
    for t in sorted((HERE / arm / "_tex").glob("Payphone*.png")):
        print("   atlas", t.name, t.stat().st_size, hashlib.sha256(t.read_bytes()).hexdigest()[:12])
