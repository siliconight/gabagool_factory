"""Copy a package and set one material's glTF alphaMode in every GLB that has
it, leaving every other byte of the package alone. Used to price the blended
chain-link fabric (Zoo 1.78.0) against the alpha test it replaced (1.77.0:
MASK, cutoff 0.5) on the same level.

    python fabric_mask_variant.py <package> <dest> <material> MASK 0.5

Prints each GLB it rewrote and the material's mode before and after. Refuses
when the material is found nowhere.
"""
import json
import pathlib
import shutil
import struct
import sys


def rewrite(path, material, mode, cutoff):
    b = path.read_bytes()
    magic, version, length = struct.unpack_from("<4sII", b, 0)
    assert magic == b"glTF" and version == 2 and length == len(b), path
    jlen, jtype = struct.unpack_from("<I4s", b, 12)
    assert jtype == b"JSON", path
    gl = json.loads(b[20:20 + jlen])
    rest = b[20 + jlen:]
    changed = []
    for m in gl.get("materials", []):
        if m.get("name") == material:
            before = m.get("alphaMode", "OPAQUE")
            m["alphaMode"] = mode
            if mode == "MASK":
                m["alphaCutoff"] = cutoff
            else:
                m.pop("alphaCutoff", None)
            changed.append((before, mode))
    if not changed:
        return []
    js = json.dumps(gl, separators=(",", ":")).encode("utf-8")
    js += b" " * ((4 - len(js) % 4) % 4)
    out = struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(js) + len(rest))
    out += struct.pack("<I4s", len(js), b"JSON") + js + rest
    path.write_bytes(out)
    return changed


def main():
    pkg, dest, material, mode, cutoff = (pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]),
                                         sys.argv[3], sys.argv[4], float(sys.argv[5]))
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(pkg, dest)
    hits = 0
    for glb in sorted(dest.rglob("*.glb")):
        ch = rewrite(glb, material, mode, cutoff)
        if ch:
            hits += 1
            print(glb.relative_to(dest), ch)
    if not hits:
        raise SystemExit(f"{material} found in no GLB under {dest}; nothing priced")
    print(hits, "GLB(s) rewritten")


if __name__ == "__main__":
    main()
