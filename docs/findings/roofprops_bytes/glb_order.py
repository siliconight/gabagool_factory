"""Where two builds of one roof-props GLB differ, and whether it is geometry or order (roadmap 247).

    python docs/findings/roofprops_bytes/glb_order.py <glb A> <glb B>

Reads both files' glTF JSON and binary chunks and prints:
- whether the JSON chunks are identical, and how many binary bytes differ;
- for every accessor holding a differing byte, the mesh attribute it serves, how many of its values moved and the
  largest move (float accessors);
- for every mesh holding a differing byte, whether its triangles are the same set (each triangle's three
  positions rounded to 0.1 mm, rotated to start at its smallest, so winding counts and rotation does not), and the
  runs of vertex indices whose positions differ, with whether that span is a permutation of the same positions.

Prints what it measured and stops. A file that is not a binary glTF prints UNKNOWN SHAPE.
"""
import json
import struct
import sys

SIZE = {5126: 4, 5125: 4, 5123: 2, 5121: 1}
WIDTH = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}
FMT = {5126: "f", 5125: "I", 5123: "H", 5121: "B"}


def _load(path):
    b = open(path, "rb").read()
    if b[:4] != b"glTF":
        sys.exit(f"UNKNOWN SHAPE: {path} is not a binary glTF")
    clen = struct.unpack_from("<I", b, 12)[0]
    js = b[20:20 + clen]
    o = 20 + clen
    blen = struct.unpack_from("<I", b, o)[0]
    return js, json.loads(js), b[o + 8:o + 8 + blen]


def _span(doc, i):
    acc = doc["accessors"][i]
    bv = doc["bufferViews"][acc["bufferView"]]
    start = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    return start, start + acc["count"] * WIDTH[acc["type"]] * SIZE[acc["componentType"]]


def _values(doc, buf, i):
    acc = doc["accessors"][i]
    start, _end = _span(doc, i)
    return struct.unpack_from(f"<{acc['count'] * WIDTH[acc['type']]}{FMT[acc['componentType']]}", buf, start)


def _positions(doc, buf, prim):
    f = _values(doc, buf, prim["attributes"]["POSITION"])
    return [tuple(round(c, 4) for c in f[3 * k:3 * k + 3]) for k in range(len(f) // 3)]


def _triangles(doc, buf, mesh):
    out = []
    for prim in mesh["primitives"]:
        p, idx = _positions(doc, buf, prim), _values(doc, buf, prim["indices"])
        for t in range(0, len(idx), 3):
            tri = [p[idx[t]], p[idx[t + 1]], p[idx[t + 2]]]
            k = min(range(3), key=lambda j: tri[j])
            out.append(tuple(tri[k:] + tri[:k]))
    return sorted(out)


def main():
    ja, da, ba = _load(sys.argv[1])
    jb, db, bb = _load(sys.argv[2])
    diff = [i for i, (x, y) in enumerate(zip(ba, bb)) if x != y]
    print(f"JSON identical: {ja == jb}; binary {len(ba)} vs {len(bb)} bytes, {len(diff)} differ")
    if ja != jb or not diff:
        return
    uses = {}
    for m in da["meshes"]:
        for prim in m["primitives"]:
            for k, v in prim["attributes"].items():
                uses.setdefault(v, []).append((m["name"], k))
            uses.setdefault(prim["indices"], []).append((m["name"], "indices"))
    meshes = set()
    for i, acc in enumerate(da["accessors"]):
        start, end = _span(da, i)
        hits = sum(1 for d in diff if start <= d < end)
        if not hits:
            continue
        meshes.update(name for name, _k in uses.get(i, []))
        line = f"accessor {i} {acc['type']} x{acc['count']}: {hits} bytes differ; serves {uses.get(i)}"
        if acc["componentType"] == 5126:
            va, vb = _values(da, ba, i), _values(db, bb, i)
            moved = [abs(x - y) for x, y in zip(va, vb) if x != y]
            line += f"; {len(moved)} of {len(va)} values moved, the largest by {max(moved):.6g}"
        print(line)
    for name in sorted(meshes):
        ma = next(m for m in da["meshes"] if m["name"] == name)
        mb = next(m for m in db["meshes"] if m["name"] == name)
        ta, tb = _triangles(da, ba, ma), _triangles(db, bb, mb)
        print(f"mesh {name}: {len(ta)} vs {len(tb)} triangles, the same set: {ta == tb}")
        pa, pb = _positions(da, ba, ma["primitives"][0]), _positions(db, bb, mb["primitives"][0])
        d = [k for k in range(min(len(pa), len(pb))) if pa[k] != pb[k]]
        if d:
            runs, s = [], d[0]
            for x, y in zip(d, d[1:]):
                if y != x + 1:
                    runs.append((s, x))
                    s = y
            runs.append((s, d[-1]))
            lo, hi = d[0], d[-1]
            print(f"   {len(d)} of {len(pa)} vertices differ, in runs {runs}; the span {lo}-{hi} a permutation of "
                  f"the same positions: {sorted(pa[lo:hi + 1]) == sorted(pb[lo:hi + 1])}")


if __name__ == "__main__":
    main()
