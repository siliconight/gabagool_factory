"""Is there a HOLE in this plate, at this point? Pure stdlib, no Blender.

    python probe_glb_void.py --selftest
    python probe_glb_void.py <file.glb> --at <x> <z>
    python probe_glb_void.py <file.glb> --at 16.0 -11.55        # the bank_branch ladder

## Why this exists

The ladder diagnosis (LADDER_INTO_SOLID_ROOF.md) closes on an INFERENCE at its
last step. Measured, all of it:

  * the walk bot stalled against a collider named `Roof` at ladder-local 3.90,
    which is world 8.10 -- the exact underside of the top slab;
  * Deli Counter's own `slab_col_2-colonly` HAS the hole, corners 15.45 / 16.55
    / -10.90, precisely where `ladder_geom.through_hole` puts it;
  * no node named `Roof` exists among the 762 in `site_base.glb`;
  * `roofs._slot` hardcodes no `voids` key, and `_record_roof_slots` ran before
    any hole existed.

Inferred, not measured: that the `Roof` collider is therefore Zoo's
`roof_rockay_01_w4000.glb`, laid over the cut slab with no opening. The device
bridge refuses that file -- it is a hardlink out of the content-addressed cache
-- so it was never opened.

THAT INFERENCE IS THE ONE THING A BLENDER REBUILD WOULD BE SPENT ON, so it is
worth one command. This probe answers it directly: does the roof plate's own
geometry cover the point the ladder climbs through?

    covered  -> the roof is solid there. The diagnosis holds.
    open     -> the roof already has the hole, and the diagnosis is WRONG.
                Do not rebuild; come back with this output instead.

## The calibration case

`site_base.glb` carries both answers in one file, so the probe is proved against
known-good and known-bad before it is trusted anywhere else. The ladder runs
storey 1 -> 2, and `_ladders` appends `SlabHole(story=s+1)`, so:

    slab_col_2-colonly   at (16.0, -11.55)  MUST read open    (the cut slab)
    slab_col_1-colonly   at (16.0, -11.55)  MUST read covered (no hole there)

One file, both directions, real shipped geometry. A probe that only proves it
can find a hole cannot tell you it would not also find one in solid plate --
the lesson `module_extents --kit` paid for with a fixture that agreed with a
wrong reader.
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path


# ------------------------------------------------------------------ glTF read
def _chunks(data: bytes):
    if data[:4] != b"glTF":
        raise ValueError("not a binary glTF")
    off, js, bins = 12, None, b""
    while off < len(data):
        ln, ty = struct.unpack_from("<II", data, off)
        body = data[off + 8: off + 8 + ln]
        if ty == 0x4E4F534A:
            js = json.loads(body)
        elif ty == 0x004E4942:
            bins = body
        off += 8 + ln
    if js is None:
        raise ValueError("no JSON chunk")
    return js, bins


def _accessor(js, bins, idx):
    acc = js["accessors"][idx]
    bv = js["bufferViews"][acc["bufferView"]]
    base = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    ctype, atype, n = acc["componentType"], acc["type"], acc["count"]
    fmt = {5120: "b", 5121: "B", 5122: "h", 5123: "H", 5125: "I",
           5126: "f"}[ctype]
    ncomp = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}[atype]
    size = struct.calcsize(fmt) * ncomp
    stride = bv.get("byteStride") or size
    out = []
    for i in range(n):
        v = struct.unpack_from("<" + fmt * ncomp, bins, base + i * stride)
        out.append(v if ncomp > 1 else v[0])
    return out


def _node_matrix(node):
    """The node's local transform as a 4x4, row-major. TRS or an explicit
    matrix; glTF says matrix wins if present."""
    if "matrix" in node:                       # glTF matrices are COLUMN-major
        m = node["matrix"]
        return [[m[0], m[4], m[8], m[12]], [m[1], m[5], m[9], m[13]],
                [m[2], m[6], m[10], m[14]], [m[3], m[7], m[11], m[15]]]
    t = node.get("translation", [0.0, 0.0, 0.0])
    r = node.get("rotation", [0.0, 0.0, 0.0, 1.0])       # xyzw
    s = node.get("scale", [1.0, 1.0, 1.0])
    x, y, z, w = r
    rot = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
           [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
           [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    return [[rot[i][j] * s[j] for j in range(3)] + [t[i]] for i in range(3)] \
        + [[0.0, 0.0, 0.0, 1.0]]


def _mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)]
            for i in range(4)]


def _apply(m, p):
    return tuple(m[i][0] * p[0] + m[i][1] * p[1] + m[i][2] * p[2] + m[i][3]
                 for i in range(3))


def triangles(data: bytes, name_filter: str = None):
    """Every triangle in world (file-root) space, with the node it came from."""
    js, bins = _chunks(data)
    nodes = js.get("nodes", [])
    out = []

    def walk(idx, parent):
        node = nodes[idx]
        m = _mul(parent, _node_matrix(node))
        nm = node.get("name", "")
        if "mesh" in node and (name_filter is None or name_filter in nm):
            for prim in js["meshes"][node["mesh"]].get("primitives", []):
                if prim.get("mode", 4) != 4:          # TRIANGLES only
                    continue
                pos = [_apply(m, p)
                       for p in _accessor(js, bins, prim["attributes"]["POSITION"])]
                idxs = (_accessor(js, bins, prim["indices"])
                        if "indices" in prim else list(range(len(pos))))
                for i in range(0, len(idxs) - 2, 3):
                    out.append((nm, pos[idxs[i]], pos[idxs[i + 1]],
                                pos[idxs[i + 2]]))
        for c in node.get("children", []):
            walk(c, m)

    eye = [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]
    roots = js.get("scenes", [{}])[js.get("scene", 0)].get(
        "nodes", list(range(len(nodes))))
    for r in roots:
        walk(r, eye)
    return out


# ------------------------------------------------------------------ the test
def _covers(tri, x, z, eps=1e-9):
    """Does this triangle cover (x, z) in plan view? Sign-of-cross-product,
    which is exact for a point strictly inside and inclusive on an edge."""
    (_, a, b, c) = tri
    ax, az, bx, bz, cx, cz = a[0], a[2], b[0], b[2], c[0], c[2]
    d1 = (x - bx) * (az - bz) - (ax - bx) * (z - bz)
    d2 = (x - cx) * (bz - cz) - (bx - cx) * (z - cz)
    d3 = (x - ax) * (cz - az) - (cx - ax) * (z - az)
    neg = (d1 < -eps) or (d2 < -eps) or (d3 < -eps)
    pos = (d1 > eps) or (d2 > eps) or (d3 > eps)
    return not (neg and pos)


def probe(data: bytes, x: float, z: float, name_filter: str = None) -> dict:
    tris = triangles(data, name_filter)
    hits = [t for t in tris if _covers(t, x, z)]
    xs = [p[0] for t in tris for p in t[1:]]
    zs = [p[2] for t in tris for p in t[1:]]
    ys = [p[1] for t in tris for p in t[1:]]
    return {
        "triangles": len(tris),
        "nodes": sorted({t[0] for t in tris}),
        "bbox_x": (min(xs), max(xs)) if xs else None,
        "bbox_y": (min(ys), max(ys)) if ys else None,
        "bbox_z": (min(zs), max(zs)) if zs else None,
        "covering": len(hits),
        "covering_y": sorted({round(p[1], 3) for t in hits for p in t[1:]}),
    }


def report(label: str, r: dict, x: float, z: float) -> bool:
    print(f"  {label}")
    print(f"    nodes            {', '.join(r['nodes']) or '(unnamed)'}")
    print(f"    triangles        {r['triangles']}")
    if r["bbox_x"]:
        print(f"    bbox x           {r['bbox_x'][0]:8.3f} .. {r['bbox_x'][1]:8.3f}")
        print(f"    bbox y           {r['bbox_y'][0]:8.3f} .. {r['bbox_y'][1]:8.3f}")
        print(f"    bbox z           {r['bbox_z'][0]:8.3f} .. {r['bbox_z'][1]:8.3f}")
    covered = r["covering"] > 0
    print(f"    at ({x}, {z})   {r['covering']} triangle(s) cover it"
          f"  ->  {'COVERED (solid here)' if covered else 'OPEN (a hole here)'}")
    if covered and r["covering_y"]:
        print(f"    covering y       {r['covering_y']}")
    return covered


# ------------------------------------------------------------------ selftest
def _selftest(site_base: Path) -> int:
    """Both answers out of one shipped file. See the module docstring."""
    if not site_base.is_file():
        print(f"[selftest] cannot find {site_base}")
        print("[selftest] pass the path to a building's site_base.glb as the "
              "second argument")
        return 2
    data = site_base.read_bytes()
    x, z = 16.0, -11.55
    print(f"[selftest] calibrating on {site_base.name} at ({x}, {z})\n")
    cut = probe(data, x, z, name_filter="slab_col_2")
    solid = probe(data, x, z, name_filter="slab_col_1")
    a = report("slab_col_2  (the slab the ladder passes -- Deli Counter cut it)",
               cut, x, z)
    print()
    b = report("slab_col_1  (a storey lower -- no ladder hole here)",
               solid, x, z)
    print()
    bad = 0
    if a:
        print("[selftest] FAIL: the cut slab reads COVERED. The probe cannot "
              "see a hole that `module_extents` measured at these exact "
              "corners, so nothing below it is trustworthy.")
        bad = 1
    if not b:
        print("[selftest] FAIL: the uncut slab reads OPEN. The probe reports "
              "holes that are not there, which is the expensive direction.")
        bad = 1
    if not bad:
        print("[selftest] the probe finds the hole that is there and not the "
              "one that is not")
    return bad


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        rest = [a for a in argv if a != "--selftest"]
        default = Path("workspaces/lot-demo-ws/.level_factory/preview/"
                       "lot_demo_001_walk/"
                       "lot/bank_branch_a04/site_base.glb")
        return _selftest(Path(rest[0]) if rest else default)

    if not argv:
        print(__doc__.splitlines()[2].strip())
        print(__doc__.splitlines()[3].strip())
        return 2
    glb = Path(argv[0])
    if not glb.is_file():
        print(f"not a file: {glb}")
        return 2
    if "--at" not in argv:
        print("--at <x> <z> is required: the point to test, in the file's own "
              "coordinates (glTF is Y-up, so x/z is the plan view)")
        return 2
    i = argv.index("--at")
    x, z = float(argv[i + 1]), float(argv[i + 2])
    nf = argv[argv.index("--node") + 1] if "--node" in argv else None
    print()
    covered = report(glb.name, probe(glb.read_bytes(), x, z, nf), x, z)
    print()
    if covered:
        print("  COVERED. The plate has no opening at that point.")
    else:
        print("  OPEN. The plate already has an opening there.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
