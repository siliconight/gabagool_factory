"""Did the paint survive the move from material to vertex? For every vertex
of every `metal_painted` primitive of a car built before Zoo 1.59.0, the
base colour glTF computes -- baseColorFactor x COLOR_0 -- against the same
product at the same position in the car built after. Prints what it
measured; matches vertices by position (to 0.1 mm) and says how many it
could not match. Triangle counts compared too.

    python colour_check.py <before dir> <after dir>
"""
import json
import pathlib
import struct
import sys

COMP = {5126: ("f", 4), 5123: ("H", 2), 5121: ("B", 1), 5125: ("I", 4)}
NCOMP = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}
NORM = {5123: 65535.0, 5121: 255.0}


def load(p):
    b = pathlib.Path(p).read_bytes()
    jl = struct.unpack_from("<I", b, 12)[0]
    doc = json.loads(b[20:20 + jl])
    off = 20 + jl
    bl = struct.unpack_from("<I", b, off)[0]
    return doc, b[off + 8:off + 8 + bl]


def read(doc, binc, ai):
    a = doc["accessors"][ai]
    bv = doc["bufferViews"][a["bufferView"]]
    fmt, size = COMP[a["componentType"]]
    n = NCOMP[a["type"]]
    stride = bv.get("byteStride") or size * n
    base = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    out = []
    for i in range(a["count"]):
        vals = struct.unpack_from("<" + fmt * n, binc, base + i * stride)
        if a.get("normalized") and a["componentType"] in NORM:
            vals = tuple(v / NORM[a["componentType"]] for v in vals)
        out.append(vals)
    return out


def painted(p, white=False):
    """{position (0.1 mm): base colour rgb} over metal_painted primitives, and tris.
    ``white`` reads every COLOR_0 as 1.0: the control, a tint that never landed."""
    doc, binc = load(p)
    cols, tris = {}, 0
    for m in doc["meshes"]:
        for pr in m["primitives"]:
            idx = pr.get("indices")
            tris += (doc["accessors"][idx]["count"] if idx is not None else
                     doc["accessors"][pr["attributes"]["POSITION"]]["count"]) // 3
            if "material" not in pr:          # a collision proxy carries none
                continue
            mat = doc["materials"][pr["material"]]
            if "metal_painted" not in mat.get("name", ""):
                continue
            f = mat.get("pbrMetallicRoughness", {}).get("baseColorFactor", [1, 1, 1, 1])
            pos = read(doc, binc, pr["attributes"]["POSITION"])
            c0 = (read(doc, binc, pr["attributes"]["COLOR_0"]) if "COLOR_0" in pr["attributes"] and not white
                  else [(1.0, 1.0, 1.0, 1.0)] * len(pos))
            for xyz, c in zip(pos, c0):
                k = tuple(round(v * 10000) for v in xyz)
                cols.setdefault(k, []).append(tuple(f[i] * c[i] for i in range(3)))
    return cols, tris


def main():
    before, after = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    worst_all = 0.0
    for pb in sorted(before.glob("prop_simple_car_*.glb")):
        pa = after / pb.name
        cb, tb = painted(pb)
        ca, ta = painted(pa)
        unmatched, worst, n = 0, 0.0, 0
        for k, vs in cb.items():
            if k not in ca:
                unmatched += 1
                continue
            # a position can carry several corners; compare the sets of colours
            for v in vs:
                d = min(max(abs(v[i] - w[i]) for i in range(3)) for w in ca[k])
                worst = max(worst, d)
                n += 1
        worst_all = max(worst_all, worst)
        print("%-50s tris %d -> %d   painted corners compared %d, positions unmatched %d of %d, "
              "worst |delta| in base colour %.4f" % (pb.name, tb, ta, n, unmatched, len(cb), worst))
    print("worst over every car: %.4f" % worst_all)
    # THE CONTROL. The first run of this check had none, and a monkeypatched
    # one written afterwards whitened only VEC4 colours while this exporter
    # writes COLOR_0 as VEC3 -- so the "control" read the same 0.0036 and
    # could not have seen a missing tint. This one reads the after cars as if
    # their tint never landed, and must come out far from the real reading.
    ctrl = 0.0
    for pb in sorted(before.glob("prop_simple_car_*.glb")):
        cb, _t = painted(pb)
        ca, _t = painted(after / pb.name, white=True)
        for k, vs in cb.items():
            for v in vs:
                if k in ca:
                    ctrl = max(ctrl, min(max(abs(v[i] - w[i]) for i in range(3)) for w in ca[k]))
    print("control, the after cars read with no tint: worst |delta| %.4f" % ctrl)


if __name__ == "__main__":
    main()
