"""Compare the GEOMETRY two GLBs draw, independent of how it is split into nodes.

    python glb_geometry.py <a.glb> <b.glb>      compare
    python glb_geometry.py <a.glb>              describe one

Applies every node's world transform (TRS or matrix, through the parent
chain) to its mesh, then summarises per material:
  * nodes / primitives -- what the file costs in submissions;
  * triangles, total area, and the area-weighted centroid -- invariants of a
    surface that do not depend on which diagonal a quad was split along, so
    a merge that re-triangulates a rectangle reads as unchanged, as it is;
  * the SET of unique corners (position 1 mm, normal 0.01, uv 0.001) -- every
    vertex of every face, with its normal and texture coordinate, and also
    invariant to the diagonal.
Prints what it measured and, comparing, every material whose numbers differ.
A file that is not a GLB, or a primitive without POSITION, FAILS.
"""
import collections
import json
import math
import struct
import sys

_COMP = {5120: ("b", 1), 5121: ("B", 1), 5122: ("h", 2), 5123: ("H", 2), 5125: ("I", 4), 5126: ("f", 4)}
_N = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def load(path):
    b = open(path, "rb").read()
    magic, _ver, _len = struct.unpack_from("<III", b, 0)
    if magic != 0x46546C67:
        raise SystemExit(f"{path}: not a GLB")
    clen, ctype = struct.unpack_from("<II", b, 12)
    if ctype != 0x4E4F534A:
        raise SystemExit(f"{path}: first chunk is not JSON")
    g = json.loads(b[20:20 + clen])
    off = 20 + clen
    blen, btype = struct.unpack_from("<II", b, off)
    if btype != 0x004E4942:
        raise SystemExit(f"{path}: second chunk is not BIN")
    return g, b[off + 8:off + 8 + blen]


def accessor(g, binb, i):
    a = g["accessors"][i]
    bv = g["bufferViews"][a["bufferView"]]
    fmt, size = _COMP[a["componentType"]]
    n = _N[a["type"]]
    stride = bv.get("byteStride") or size * n
    base = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    out = []
    for k in range(a["count"]):
        vals = struct.unpack_from("<%d%s" % (n, fmt), binb, base + k * stride)
        if a.get("normalized") and fmt != "f":
            m = float((1 << (8 * size - (1 if fmt.islower() else 0))) - 1)
            vals = tuple(v / m for v in vals)
        out.append(vals)
    return out


def _mat_mul(a, b):
    return [[sum(a[r][k] * b[k][c] for k in range(4)) for c in range(4)] for r in range(4)]


def _local(node):
    if "matrix" in node:
        m = node["matrix"]          # column-major
        return [[m[c * 4 + r] for c in range(4)] for r in range(4)]
    tx, ty, tz = node.get("translation", (0.0, 0.0, 0.0))
    qx, qy, qz, qw = node.get("rotation", (0.0, 0.0, 0.0, 1.0))
    sx, sy, sz = node.get("scale", (1.0, 1.0, 1.0))
    r = [[1 - 2 * (qy * qy + qz * qz), 2 * (qx * qy - qz * qw), 2 * (qx * qz + qy * qw)],
         [2 * (qx * qy + qz * qw), 1 - 2 * (qx * qx + qz * qz), 2 * (qy * qz - qx * qw)],
         [2 * (qx * qz - qy * qw), 2 * (qy * qz + qx * qw), 1 - 2 * (qx * qx + qy * qy)]]
    return [[r[0][0] * sx, r[0][1] * sy, r[0][2] * sz, tx],
            [r[1][0] * sx, r[1][1] * sy, r[1][2] * sz, ty],
            [r[2][0] * sx, r[2][1] * sy, r[2][2] * sz, tz],
            [0.0, 0.0, 0.0, 1.0]]


def _apply(m, p, w=1.0):
    return tuple(m[r][0] * p[0] + m[r][1] * p[1] + m[r][2] * p[2] + m[r][3] * w for r in range(3))


def summarise(path):
    g, binb = load(path)
    nodes = g.get("nodes", [])
    parent = {}
    for i, n in enumerate(nodes):
        for c in n.get("children", []):
            parent[c] = i

    def world(i):
        m = _local(nodes[i])
        while i in parent:
            i = parent[i]
            m = _mat_mul(_local(nodes[i]), m)
        return m

    mats = [m.get("name", "?") for m in g.get("materials", [])]
    per = collections.defaultdict(lambda: {"prims": 0, "tris": 0, "area": 0.0,
                                           "cen": [0.0, 0.0, 0.0], "corners": set()})
    mesh_nodes = 0
    for i, n in enumerate(nodes):
        if "mesh" not in n:
            continue
        mesh_nodes += 1
        w = world(i)
        for prim in g["meshes"][n["mesh"]]["primitives"]:
            at = prim["attributes"]
            if "POSITION" not in at:
                raise SystemExit(f"{path}: a primitive without POSITION")
            name = mats[prim["material"]] if "material" in prim else "(none)"
            P = [_apply(w, p) for p in accessor(g, binb, at["POSITION"])]
            Nn = ([_apply(w, v, 0.0) for v in accessor(g, binb, at["NORMAL"])]
                  if "NORMAL" in at else [(0.0, 0.0, 0.0)] * len(P))
            UV = accessor(g, binb, at["TEXCOORD_0"]) if "TEXCOORD_0" in at else [(0.0, 0.0)] * len(P)
            idx = [v[0] for v in accessor(g, binb, prim["indices"])] if "indices" in prim else list(range(len(P)))
            d = per[name]
            d["prims"] += 1
            for t in range(0, len(idx), 3):
                a, b, c = (P[idx[t]], P[idx[t + 1]], P[idx[t + 2]])
                u = [b[k] - a[k] for k in range(3)]
                v = [c[k] - a[k] for k in range(3)]
                cr = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
                ar = 0.5 * math.sqrt(sum(x * x for x in cr))
                d["tris"] += 1
                d["area"] += ar
                for k in range(3):
                    d["cen"][k] += ar * (a[k] + b[k] + c[k]) / 3.0
            for k in idx:
                nl = Nn[k]
                ln = math.sqrt(sum(x * x for x in nl)) or 1.0
                d["corners"].add((tuple(round(x, 3) for x in P[k]),
                                  tuple(round(x / ln, 2) for x in nl),
                                  tuple(round(x, 3) for x in UV[k])))
                d.setdefault("raw", set()).add((P[k], tuple(x / ln for x in nl), tuple(UV[k])))
    return {"nodes": len(nodes), "mesh_nodes": mesh_nodes, "per": per}


def describe(s, label):
    prims = sum(d["prims"] for d in s["per"].values())
    print(f"{label}: {s['mesh_nodes']} mesh nodes, {prims} primitives")
    for m, d in sorted(s["per"].items()):
        c = [x / d["area"] for x in d["cen"]] if d["area"] else [0, 0, 0]
        print(f"  {m:44s} prims {d['prims']:4d}  tris {d['tris']:6d}  area {d['area']:11.4f}  "
              f"centroid ({c[0]:.4f}, {c[1]:.4f}, {c[2]:.4f})  corners {len(d['corners'])}")


def main():
    a = summarise(sys.argv[1])
    describe(a, sys.argv[1])
    if len(sys.argv) < 3:
        return
    b = summarise(sys.argv[2])
    describe(b, sys.argv[2])
    diffs = 0
    for m in sorted(set(a["per"]) | set(b["per"])):
        da, db = a["per"].get(m), b["per"].get(m)
        if da is None or db is None:
            print(f"DIFF {m}: only in {'B' if da is None else 'A'}")
            diffs += 1
            continue
        why = []
        if da["tris"] != db["tris"]:
            why.append(f"tris {da['tris']} vs {db['tris']}")
        if abs(da["area"] - db["area"]) > 1e-6 * max(1.0, da["area"]):
            why.append(f"area {da['area']:.6f} vs {db['area']:.6f}")
        ca = [x / da["area"] for x in da["cen"]] if da["area"] else [0, 0, 0]
        cb = [x / db["area"] for x in db["cen"]] if db["area"] else [0, 0, 0]
        if max(abs(ca[k] - cb[k]) for k in range(3)) > 1e-4:
            why.append(f"centroid {ca} vs {cb}")
        only_a, only_b = da["corners"] - db["corners"], db["corners"] - da["corners"]
        if only_a or only_b:
            # A CORNER THAT ROUNDS ACROSS A BOUNDARY IS NOT A MOVED CORNER.
            # Pair each unmatched corner with its nearest unmatched partner and
            # say how far apart they really are; float32 positions at 10-30 m
            # carry ~2e-6 m of noise, which rounds 2.8505 either way.
            worst_p = worst_n = worst_uv = 0.0
            pool = sorted(only_b)
            for ca_ in sorted(only_a):
                best = None
                for cb_ in pool:
                    dp = math.dist(ca_[0], cb_[0])
                    dn = max(abs(x - y) for x, y in zip(ca_[1], cb_[1]))
                    du = max(abs(x - y) for x, y in zip(ca_[2], cb_[2]))
                    key = (dp + dn + du, dp, dn, du)
                    if best is None or key < best:
                        best = key
                if best is not None:
                    worst_p, worst_n, worst_uv = (max(worst_p, best[1]), max(worst_n, best[2]),
                                                  max(worst_uv, best[3]))
            why.append(f"corners only in A {len(only_a)}, only in B {len(only_b)}; nearest "
                       f"partner at most {worst_p:.4f} m, normal {worst_n:.3f}, uv {worst_uv:.4f} "
                       f"(of the rounded values)")
        if why:
            diffs += 1
            print(f"DIFF {m}: " + "; ".join(why))
        if "--exact" in sys.argv:
            print(f"EXACT {m}: " + exact(da.get("raw", set()), db.get("raw", set())))
    print(f"materials differing: {diffs}")


def _nearest(src, dst):
    """Max over ``src`` vertices of the distance to the nearest ``dst`` vertex
    whose normal is within 0.01 and uv within 0.001 -- unrounded, through a
    1 cm spatial hash. Returns (max distance, vertices with no partner)."""
    cell = 0.01
    grid = collections.defaultdict(list)
    for v in dst:
        grid[tuple(int(math.floor(c / cell)) for c in v[0])].append(v)
    worst, lost = 0.0, 0
    for p, n, uv in src:
        key = tuple(int(math.floor(c / cell)) for c in p)
        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for q, qn, quv in grid.get((key[0] + dx, key[1] + dy, key[2] + dz), ()):
                        if max(abs(a - b) for a, b in zip(n, qn)) > 0.01:
                            continue
                        if max(abs(a - b) for a, b in zip(uv, quv)) > 0.001:
                            continue
                        dd = math.dist(p, q)
                        if best is None or dd < best:
                            best = dd
        if best is None:
            lost += 1
        else:
            worst = max(worst, best)
    return worst, lost


def exact(ra, rb):
    wa, la = _nearest(ra, rb)
    wb, lb = _nearest(rb, ra)
    return (f"{len(ra)} / {len(rb)} unique vertices; every A vertex within {wa!r} m of a B vertex "
            f"({la} with none within 1 cm), every B within {wb!r} m of an A ({lb} with none)")


if __name__ == "__main__":
    main()
