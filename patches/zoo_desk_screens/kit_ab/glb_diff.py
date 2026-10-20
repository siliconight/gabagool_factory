"""The desk A/B: each arm's GLBs read off their glTF JSON chunk -- materials (name, emissive factor, textures),
meshes (name, primitives, vertices, triangles, materials, a hash of the positions), images (name, bytes) -- and the two arms side by side. Prints what it read."""
import hashlib
import json
import pathlib
import struct
import sys


def glb(path):
    b = path.read_bytes()
    magic, ver, length = struct.unpack_from("<III", b, 0)
    if magic != 0x46546C67:
        raise SystemExit("UNRECOGNISED: %s is not a GLB" % path)
    clen, ctype = struct.unpack_from("<II", b, 12)
    if ctype != 0x4E4F534A:
        raise SystemExit("UNRECOGNISED: %s's first chunk is not JSON" % path)
    j = json.loads(b[20:20 + clen].decode("utf-8"))
    off = 20 + clen
    blen, btype = struct.unpack_from("<II", b, off)
    if btype != 0x004E4942:
        raise SystemExit("UNRECOGNISED: %s's second chunk is not BIN" % path)
    return j, len(b), b[off + 8:off + 8 + blen]


def summary(path):
    g, n, bin_ = glb(path)
    acc = g.get("accessors") or []
    mats = []
    for m in g.get("materials") or []:
        pbr = m.get("pbrMetallicRoughness") or {}
        mats.append((m.get("name"), tuple(round(v, 3) for v in m.get("emissiveFactor") or (0, 0, 0)),
                     "base_tex" if "baseColorTexture" in pbr else "", "emit_tex" if "emissiveTexture" in m else "",
                     tuple(round(v, 3) for v in (m.get("extensions") or {}).get("KHR_materials_emissive_strength",
                                                                                {}).values())))
    meshes = []
    for me in g.get("meshes") or []:
        verts = sum(acc[p["attributes"]["POSITION"]]["count"] for p in me["primitives"])
        tris = sum((acc[p["indices"]]["count"] // 3) if "indices" in p else 0 for p in me["primitives"])
        names = [((g.get("materials") or [])[p["material"]].get("name") if "material" in p else None)
                 for p in me["primitives"]]
        pos = b""
        for p in me["primitives"]:
            a = acc[p["attributes"]["POSITION"]]
            bv = g["bufferViews"][a["bufferView"]]
            start = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
            pos += bin_[start:start + a["count"] * 12]
        meshes.append((me.get("name"), len(me["primitives"]), verts, tris, names,
                       hashlib.sha256(pos).hexdigest()[:12]))
    imgs = [(i.get("name"), (g.get("bufferViews") or [])[i["bufferView"]]["byteLength"] if "bufferView" in i else None)
            for i in g.get("images") or []]
    return {"bytes": n, "materials": mats, "meshes": meshes, "images": imgs}


def main(argv):
    a, b = pathlib.Path(argv[0]), pathlib.Path(argv[1])
    names = sorted({p.name for p in a.glob("*.glb")} | {p.name for p in b.glob("*.glb")})
    for name in names:
        print("==", name)
        sa, sb = summary(a / name), summary(b / name)
        print("  bytes %d -> %d" % (sa["bytes"], sb["bytes"]))
        for key in ("materials", "meshes", "images"):
            ka, kb = sa[key], sb[key]
            print("  %s: %d -> %d" % (key, len(ka), len(kb)))
            for x in kb:
                if x not in ka:
                    print("    only in b:", x)
            for x in ka:
                if x not in kb:
                    print("    only in a:", x)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
