"""Coplanar faces from DIFFERENT meshes: the geometry that z-fights.

WHAT Z-FIGHTING ACTUALLY IS, so the check measures the cause and not a symptom.
Two triangles that lie in the same plane and overlap in that plane give the
depth buffer no way to order them, so which one draws wins per-pixel and flips
as the camera moves a fraction. One frame differs from the next in a way that
reads as shimmer or jitter.

THE DISCRIMINATOR IS "DIFFERENT MESHES", AND IT IS THE WHOLE CHECK. A floor is
tessellated into hundreds of coplanar triangles and that is fine -- they are
edge-to-edge, from one mesh, and never overlap. Two SEPARATE meshes sharing a
plane and covering the same ground is a different thing entirely: somebody
emitted a surface twice. So a plane group drawn from a single mesh node is
skipped outright, which prunes almost everything and leaves the real cases.

WHAT IT DELIBERATELY DOES NOT LOOK AT. Nodes whose names carry `-colonly` or
`-convcolonly` are collision geometry; Godot imports them invisible, so they
cannot z-fight with anything. Including them would flag every visual/collision
dual mesh in the file -- which is the file being correct, not broken.

WHAT IT REPORTS, and the honest limit of it. Overlap is tested as an in-plane
bounding-box intersection rather than exact triangle-triangle overlap. That can
call two triangles overlapping when they only interleave, so a finding is a
place to LOOK rather than a proven defect. It cannot miss a true duplicate,
which is the case that matters.

    python tools\\check_coplanar.py                     # every built building
    python tools\\check_coplanar.py path\\to\\one.glb
    python tools\\check_coplanar.py --tol 0.002         # plane match tolerance

Exit 0 clean, 1 found something, 2 could not check.
"""
import argparse
import json
import pathlib
import struct
import sys
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from factory_paths import factory_root                        # noqa: E402

#: glTF componentType -> (struct code, byte width)
CTYPE = {5120: ("b", 1), 5121: ("B", 1), 5122: ("h", 2),
         5123: ("H", 2), 5125: ("I", 4), 5126: ("f", 4)}
NCOMP = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}
COLLISION_HINTS = ("-colonly", "-convcolonly", "_colonly", "_convcolonly")
#: Overlap must exceed this on BOTH in-plane axes to count. Abutting geometry
#: shares an edge exactly, and exact in floating point is not exact.
EPS = 1e-6


def read_glb(path):
    """(gltf_json, binary_chunk). Raises on anything that is not a real glb."""
    raw = pathlib.Path(path).read_bytes()
    if raw[:4] != b"glTF":
        raise ValueError(f"{path}: not a glb (no glTF magic)")
    n = len(raw)
    off, js, bin_ = 12, None, b""
    while off + 8 <= n:
        ln, kind = struct.unpack_from("<II", raw, off)
        body = raw[off + 8: off + 8 + ln]
        if kind == 0x4E4F534A:
            js = json.loads(body.decode("utf-8"))
        elif kind == 0x004E4942:
            bin_ = body
        off += 8 + ln + (-ln % 4)
    if js is None:
        raise ValueError(f"{path}: no JSON chunk")
    return js, bin_


def accessor(g, bin_, idx):
    """Flat list of numbers for accessor `idx`, honouring byteStride."""
    a = g["accessors"][idx]
    code, width = CTYPE[a["componentType"]]
    ncomp = NCOMP[a["type"]]
    count = a["count"]
    if "bufferView" not in a:
        return [0] * (count * ncomp)
    bv = g["bufferViews"][a["bufferView"]]
    base = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    stride = bv.get("byteStride") or (width * ncomp)
    out = []
    for i in range(count):
        out.extend(struct.unpack_from("<" + code * ncomp, bin_, base + i * stride))
    return out


def node_world(g):
    """{node_index: (name, 4x4 row-major world matrix as 16 floats)}."""
    def trs(nd):
        if "matrix" in nd:                       # glTF stores column-major
            m = nd["matrix"]
            return [m[0], m[4], m[8], m[12], m[1], m[5], m[9], m[13],
                    m[2], m[6], m[10], m[14], m[3], m[7], m[11], m[15]]
        t = nd.get("translation", [0, 0, 0])
        r = nd.get("rotation", [0, 0, 0, 1])
        s = nd.get("scale", [1, 1, 1])
        x, y, z, w = r
        rot = [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w),
               2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w),
               2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]
        return [rot[0] * s[0], rot[1] * s[1], rot[2] * s[2], t[0],
                rot[3] * s[0], rot[4] * s[1], rot[5] * s[2], t[1],
                rot[6] * s[0], rot[7] * s[1], rot[8] * s[2], t[2],
                0, 0, 0, 1]

    def mul(a, b):
        return [sum(a[r * 4 + k] * b[k * 4 + c] for k in range(4))
                for r in range(4) for c in range(4)]

    nodes = g.get("nodes", [])
    world = {}

    def walk(i, parent):
        nd = nodes[i]
        m = mul(parent, trs(nd))
        world[i] = (nd.get("name", f"node{i}"), m)
        for c in nd.get("children", []):
            walk(c, m)

    ident = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    roots = set(range(len(nodes)))
    for nd in nodes:
        roots -= set(nd.get("children", []))
    for i in sorted(roots):
        walk(i, ident)
    return world


def triangles(path):
    """[(node_name, (ax,ay,az), (bx,by,bz), (cx,cy,cz))] in file space."""
    g, bin_ = read_glb(path)
    out = []
    for idx, (name, m) in node_world(g).items():
        nd = g["nodes"][idx]
        if "mesh" not in nd:
            continue
        if any(h in name.lower() for h in COLLISION_HINTS):
            continue
        for prim in g["meshes"][nd["mesh"]].get("primitives", []):
            if prim.get("mode", 4) != 4:              # triangles only
                continue
            pos = prim.get("attributes", {}).get("POSITION")
            if pos is None:
                continue
            p = accessor(g, bin_, pos)
            verts = [(p[i], p[i + 1], p[i + 2]) for i in range(0, len(p), 3)]
            ids = (accessor(g, bin_, prim["indices"]) if "indices" in prim
                   else list(range(len(verts))))
            wv = []
            for vx, vy, vz in verts:
                wv.append((m[0] * vx + m[1] * vy + m[2] * vz + m[3],
                           m[4] * vx + m[5] * vy + m[6] * vz + m[7],
                           m[8] * vx + m[9] * vy + m[10] * vz + m[11]))
            for i in range(0, len(ids) - 2, 3):
                out.append((name, wv[ids[i]], wv[ids[i + 1]], wv[ids[i + 2]]))
    return out


def plane_of(a, b, c):
    """(unit normal, offset). None for a degenerate triangle."""
    u = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    v = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2],
         u[0] * v[1] - u[1] * v[0])
    ln = (n[0] ** 2 + n[1] ** 2 + n[2] ** 2) ** 0.5
    if ln < 1e-12:
        return None
    n = (n[0] / ln, n[1] / ln, n[2] / ln)
    # Fold antiparallel normals together: a face and its back are the same plane.
    for comp in n:
        if abs(comp) > 1e-9:
            if comp < 0:
                n = (-n[0], -n[1], -n[2])
            break
    return n, n[0] * a[0] + n[1] * a[1] + n[2] * a[2]


def check(path, tol, cap):
    tris = triangles(path)
    if not tris:
        return None, "no visual triangles (all collision, or an empty file)"

    groups = defaultdict(list)
    for name, a, b, c in tris:
        pl = plane_of(a, b, c)
        if pl is None:
            continue
        n, d = pl
        key = (round(n[0] / tol) * tol, round(n[1] / tol) * tol,
               round(n[2] / tol) * tol, round(d / tol) * tol)
        groups[key].append((name, a, b, c))

    findings, skipped = [], 0
    for key, tset in groups.items():
        names = {t[0] for t in tset}
        if len(names) < 2:          # one mesh tessellating its own surface
            continue
        if len(tset) > cap:
            skipped += 1
            continue
        # in-plane bounds per triangle, dropping the axis the normal dominates
        nx, ny, nz = key[0], key[1], key[2]
        drop = max(range(3), key=lambda i: abs((nx, ny, nz)[i]))
        keep = [i for i in range(3) if i != drop]
        boxes = []
        for name, a, b, c in tset:
            us = [p[keep[0]] for p in (a, b, c)]
            vs = [p[keep[1]] for p in (a, b, c)]
            boxes.append((name, min(us), max(us), min(vs), max(vs), a))
        for i in range(len(boxes)):
            n1, u0, u1, v0, v1, at = boxes[i]
            for j in range(i + 1, len(boxes)):
                n2, x0, x1, y0, y1, _ = boxes[j]
                if n1 == n2:
                    continue
                # EPS, not zero. Two boxes that abut share an edge exactly, and
                # `u1 <= x0` on floats lets a 1e-16 difference read as overlap.
                # Measured on cr_deli: a segment pair reported ten faces, of
                # which eight were its four side planes touching edge-on and two
                # were the real finding. An instrument that cannot tell abutment
                # from overlap inflates the count fivefold and buries the case
                # that matters.
                if (u1 - x0 <= EPS or x1 - u0 <= EPS
                        or v1 - y0 <= EPS or y1 - v0 <= EPS):
                    continue
                findings.append((n1, n2, at))
                break
    return (findings, skipped), None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("glb", nargs="*", help="glb files; default is every built building")
    ap.add_argument("--tol", type=float, default=0.002,
                    help="plane match tolerance in metres (default: %(default)s)")
    ap.add_argument("--cap", type=int, default=3000,
                    help="skip a plane group larger than this (default: %(default)s)")
    ap.add_argument("--show", type=int, default=4, help="examples per file")
    args = ap.parse_args()

    files = [pathlib.Path(p) for p in args.glb]
    if not files:
        build = factory_root() / "deli_counter" / "build"
        if not build.is_dir():
            print(f"no {build} -- nothing has been built. Pass a .glb explicitly.")
            return 2
        files = sorted(build.glob("*.glb"))
    if not files:
        print("no .glb files to check")
        return 2

    total, cannot = 0, 0
    print(f"  {'building':<28}{'coplanar cross-mesh overlaps':>30}")
    print("  " + "-" * 58)
    detail = []
    for f in files:
        try:
            res, why = check(f, args.tol, args.cap)
        except Exception as e:                                  # noqa: BLE001
            print(f"  {f.name:<28}{'COULD NOT READ':>30}   {type(e).__name__}: {e}")
            cannot += 1
            continue
        if res is None:
            print(f"  {f.name:<28}{'-':>30}   {why}")
            continue
        findings, skipped = res
        total += len(findings)
        note = f"   ({skipped} dense group(s) not paired)" if skipped else ""
        print(f"  {f.name:<28}{len(findings):>30}{note}")
        if findings:
            detail.append((f.name, findings))

    for name, findings in detail:
        print(f"\n  {name}")
        pairs = defaultdict(list)
        for n1, n2, at in findings:
            pairs[tuple(sorted((n1, n2)))].append(at)
        for (n1, n2), where in sorted(pairs.items(),
                                      key=lambda kv: -len(kv[1]))[:args.show]:
            x, y, z = where[0]
            print(f"    {len(where):>5} face(s)  {n1}  <->  {n2}")
            print(f"           first at ({x:.2f}, {y:.2f}, {z:.2f}) in building space")
        if len(pairs) > args.show:
            print(f"    ... and {len(pairs) - args.show} more mesh pair(s)")

    print()
    if cannot:
        print(f"  {cannot} file(s) could not be read. A check that did not run is "
              f"not a check that passed.")
        return 2
    if total:
        print(f"  {total} overlapping coplanar face pair(s) across "
              f"{len(detail)} building(s).")
        print(f"  These are places to LOOK: bounds overlap is a proxy for true "
              f"triangle overlap,\n  so a finding can be interleaving rather "
              f"than duplication. A true duplicate\n  cannot hide from it.")
        return 1
    print("  No two meshes share a plane and cover the same ground.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
