"""Coplanar-surface fights across a COMPOSED site, not one building at a time.

WHY THIS HAD TO EXIST, and why four rounds of measurement missed what it finds.

zfight_gate, probe_fights and sweep_fights all read a single .glb. A building is
clean when nothing inside it fights. But a level is a building PLUS the site
Lot lays under and around it, and those two solids first share a coordinate
frame when cater composes the scene. Every per-building sweep this session was
honest and every one was structurally blind to that pair.

It found the first one already: Lot's ground plate topped out at y = 0 and so
does a building's ground-floor slab, with GROUND_HOLE_INSET deliberately leaving
a 0.45 m ring of overlap around every building -- roughly 59 m^2 of coplanar
up-facing surface hugging the inside of every exterior wall. No single-building
instrument could see it. This one can, and anything else of that shape.

WHAT IT READS. A cater-written site .tscn:

  * StaticBody3D box nodes -- ground tiles, roads, paths, courtyards, cover,
    kerbs, perimeter walls -- sized from the BoxMesh sub-resource their `mesh`
    child points at, placed by the node's Transform3D.
  * building instances -- `instance=ExtResource(...)` pointing at a .glb --
    expanded to their per-node visual boxes and pushed through the instance
    transform, so a building contributes its walls and slabs individually
    rather than as one lump.

Then the same rule the rest of the toolchain uses, imported from zfight_gate
rather than restated: real interpenetration on every axis, a SAME-FACING face
pair within TOL, shared area >= AREA_MIN.

WHAT `exposed` MEANS, same as sweep_fights: of the fights the gate reports, the
ones with nothing covering the OUTWARD side of the shared plane -- the direction
a camera must look from to see it. That is the column that corresponds to what
you see standing in the level.

TWO LIMITS, named rather than discovered later.

  * Rotated boxes (a road or path at an angle) are reduced to their world AABB,
    which is much larger than the box -- a 3 m ribbon running diagonally across
    45 m becomes a 45 x 49 m block. That invents overlaps that do not exist, and
    ONE inflated box is enough to do it, so any finding touching a rotated node
    is marked ~ and is a lead, not a fact. Measured on coldrun_pawn_job: all
    three paths are rotated, and the "158 m^2 path_0 <-> path_1" this reported
    on its first run is an artefact of exactly this. An oriented-box test would
    remove the caveat; until then, unmarked findings are the ones to trust.
  * Box extents inside a .glb come from the POSITION accessor min/max, so a
    slab with a stairwell hole cut through it still reports as solid there.

    python site_fights.py <project_dir> [--scene X.tscn] [--top 30]

Reads and prints. Writes nothing.
"""
import argparse
import math
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from factory_paths import factory_root  # noqa: E402

AXIS = "XYZ"

_SUB = re.compile(r'\[sub_resource type="BoxMesh" id="([^"]+)"\]\s*\n'
                  r'size = Vector3\(([^)]+)\)')
_EXT = re.compile(r'\[ext_resource type="PackedScene" path="res://([^"]+)" '
                  r'id="([^"]+)"\]')
_NODE = re.compile(r'\[node name="([^"]+)" type="([^"]+)" parent="([^"]+)"\]'
                   r'(?:\s*\ntransform = Transform3D\(([^)]+)\))?')
_INST = re.compile(r'\[node name="([^"]+)" parent="([^"]+)" '
                   r'instance=ExtResource\("([^"]+)"\)\]'
                   r'(?:\s*\ntransform = Transform3D\(([^)]+)\))?')
_MESHREF = re.compile(r'\[node name="[^"]+" type="MeshInstance3D" '
                      r'parent="\./([^"]+)"\]\s*\nmesh = SubResource\("([^"]+)"\)')


def _m(vals):
    """Godot's 12-float Transform3D (3 basis columns then origin) -> 3x4."""
    f = [float(v) for v in vals.split(",")]
    return [[f[0], f[3], f[6], f[9]],
            [f[1], f[4], f[7], f[10]],
            [f[2], f[5], f[8], f[11]]]


def _apply(m, p):
    return tuple(m[i][0] * p[0] + m[i][1] * p[1] + m[i][2] * p[2] + m[i][3]
                 for i in range(3))


def _aabb(m, lo, hi):
    pts = [_apply(m, (x, y, z))
           for x in (lo[0], hi[0]) for y in (lo[1], hi[1])
           for z in (lo[2], hi[2])]
    return ([min(p[i] for p in pts) for i in range(3)],
            [max(p[i] for p in pts) for i in range(3)])


def _rotated(m):
    """True when the basis is not axis-aligned, so the AABB overstates the box."""
    for i in range(3):
        col = [m[r][i] for r in range(3)]
        if sum(1 for v in col if abs(v) > 1e-6) != 1:
            return True
    return False


def _yaw_rect(m, sx, sz):
    """The four world XZ corners of a box under a YAW-only basis.

    A yaw rotation spins the box about the vertical, so its top and bottom
    faces stay horizontal: the PLANE of a Y-axis face pair is exact even when
    the AABB is not. Only the shared AREA needs the true footprint, which is
    this rectangle rather than its bounding box.
    """
    hx, hz = sx / 2.0, sz / 2.0
    pts = []
    for dx, dz in ((-hx, -hz), (hx, -hz), (hx, hz), (-hx, hz)):
        wx = m[0][0] * dx + m[0][2] * dz + m[0][3]
        wz = m[2][0] * dx + m[2][2] * dz + m[2][3]
        pts.append((wx, wz))
    return pts


def _clip_area(subject, clip):
    """Sutherland-Hodgman: area of the intersection of two convex polygons."""
    out = list(subject)
    n = len(clip)
    for i in range(n):
        if not out:
            return 0.0
        a, b = clip[i], clip[(i + 1) % n]
        ex, ez = b[0] - a[0], b[1] - a[1]

        def side(p):
            return ex * (p[1] - a[1]) - ez * (p[0] - a[0])

        prev, res = out[-1], []
        sprev = side(prev)
        for cur in out:
            scur = side(cur)
            if scur >= 0:
                if sprev < 0:
                    t = sprev / (sprev - scur)
                    res.append((prev[0] + t * (cur[0] - prev[0]),
                                prev[1] + t * (cur[1] - prev[1])))
                res.append(cur)
            elif sprev >= 0:
                t = sprev / (sprev - scur)
                res.append((prev[0] + t * (cur[0] - prev[0]),
                            prev[1] + t * (cur[1] - prev[1])))
            prev, sprev = cur, scur
        out = res
    if len(out) < 3:
        return 0.0
    a2 = 0.0
    for i in range(len(out)):
        x1, z1 = out[i]
        x2, z2 = out[(i + 1) % len(out)]
        a2 += x1 * z2 - x2 * z1
    return abs(a2) / 2.0


def _yaw_only(m):
    """True when the basis is a pure rotation about the vertical axis."""
    return (abs(m[1][0]) < 1e-6 and abs(m[1][2]) < 1e-6
            and abs(m[0][1]) < 1e-6 and abs(m[2][1]) < 1e-6
            and abs(m[1][1] - 1.0) < 1e-6)


def site_boxes(zg, proj, scene):
    """[(name, (lo, hi), rotated_flag, xz_polygon_or_None)] per opaque solid."""
    text = (proj / scene).read_text(encoding="utf-8")
    sizes = {sid: [float(v) for v in vals.split(",")]
             for sid, vals in _SUB.findall(text)}
    mesh_of = {node: sid for node, sid in _MESHREF.findall(text)}
    ext = {rid: p for p, rid in _EXT.findall(text)}

    out = []
    for name, ntype, _parent, xf in _NODE.findall(text):
        sid = mesh_of.get(name)
        if sid is None or sid not in sizes:
            continue
        sx, sy, sz = sizes[sid]
        m = _m(xf) if xf else _m("1,0,0,0,1,0,0,0,1,0,0,0")
        lo = (-sx / 2, -sy / 2, -sz / 2)
        hi = (sx / 2, sy / 2, sz / 2)
        blo, bhi = _aabb(m, lo, hi)
        # Yaw-only boxes keep their true XZ footprint so a Y-axis overlap area
        # is measured rather than approximated; anything else falls back to the
        # AABB corners and stays flagged.
        poly = _yaw_rect(m, sx, sz) if _yaw_only(m) else None
        out.append((f"site:{name}", (blo, bhi), _rotated(m), poly))

    cache = {}
    for name, _parent, rid, xf in _INST.findall(text):
        ref = ext.get(rid)
        if not ref or not ref.endswith(".glb"):
            continue
        glb = proj / ref
        if not glb.exists():
            print(f"  WARNING {ref} not in the project -- {name} contributes "
                  f"nothing. That is a gap in the check, not a pass.")
            continue
        if ref not in cache:
            cache[ref] = zg._node_world_boxes(str(glb))
        m = _m(xf) if xf else _m("1,0,0,0,1,0,0,0,1,0,0,0")
        rot = _rotated(m)
        for nm, (lo, hi) in cache[ref]:
            blo, bhi = _aabb(m, lo, hi)
            poly = ([(blo[0], blo[2]), (bhi[0], blo[2]),
                     (bhi[0], bhi[2]), (blo[0], bhi[2])] if not rot else None)
            out.append((f"{name}:{nm}", (blo, bhi), rot, poly))
    return out


def exposed_of(zg, boxes, findings):
    """Findings with nothing covering the outward side of the shared plane."""
    index = {nm: k for k, (nm, _b, _r, _p) in enumerate(boxes)}
    out = []
    for f in findings:
        ia, ib = index[f["a"]], index[f["b"]]
        alo, ahi = boxes[ia][1]
        blo, bhi = boxes[ib][1]
        ax, side, plane = f["axis"], f["side"], f["plane"]
        rlo = [max(alo[k], blo[k]) for k in range(3)]
        rhi = [min(ahi[k], bhi[k]) for k in range(3)]
        o = [k for k in range(3) if k != ax]
        covered = False
        for k, (_nm, (slo, shi), _r, _p) in enumerate(boxes):
            if k in (ia, ib):
                continue
            if side == "max":
                ok = (slo[ax] <= plane + zg.TOL
                      and shi[ax] >= plane + zg.OCCLUDE_MARGIN)
            else:
                ok = (shi[ax] >= plane - zg.TOL
                      and slo[ax] <= plane - zg.OCCLUDE_MARGIN)
            if ok and all(slo[q] <= rlo[q] + zg.TOL and shi[q] >= rhi[q] - zg.TOL
                          for q in o):
                covered = True
                break
        if not covered:
            out.append(f)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("project", help="a cater-written Godot project folder")
    ap.add_argument("--scene", default=None,
                    help="site scene name; default is the single non-walk tscn")
    ap.add_argument("--top", type=int, default=30)
    ap.add_argument("--all", action="store_true",
                    help="list every fight, not just the exposed ones")
    args = ap.parse_args()

    root = factory_root()
    dc = root / "deli_counter"
    sys.path.insert(0, str(dc))
    import zfight_gate as zg

    proj = pathlib.Path(args.project)
    if not proj.is_absolute():
        proj = (root / proj).resolve()
    if not (proj / "project.godot").is_file():
        raise SystemExit(f"no project.godot in {proj}. Nothing checked -- and a "
                         f"check that did not run is not a check that passed.")

    if args.scene:
        scene = args.scene
    else:
        cands = [p.name for p in sorted(proj.glob("*.tscn"))
                 if not p.stem.endswith(("_walk", "_navqa"))]
        if len(cands) != 1:
            raise SystemExit(f"expected one site .tscn in {proj}, found "
                             f"{cands}. Pass --scene.")
        scene = cands[0]

    boxes = site_boxes(zg, proj, scene)
    if not boxes:
        raise SystemExit(f"no solids read from {scene}. Nothing checked.")
    plain = [(nm, b) for nm, b, _r, _p in boxes]
    rot = {nm for nm, _b, r, _p in boxes if r}

    vis, buried = zg.visible_fights(plain)

    # RE-MEASURE horizontal overlaps from the true footprints. A yaw-rotated
    # path reduced to its AABB reported a 158 m^2 overlap with another path it
    # very likely never touches. The face PLANE was right and the AREA was not,
    # so only the area is recomputed -- and a pair whose true shared footprint
    # falls under AREA_MIN was never a fight at all.
    poly_of = {nm: p for nm, _b, _r, p in boxes}
    kept, phantom = [], 0
    for f in vis:
        pa, pb = poly_of.get(f["a"]), poly_of.get(f["b"])
        if f["axis"] == 1 and pa and pb:
            area = _clip_area(pa, pb)
            if area < zg.AREA_MIN:
                phantom += 1
                continue
            f["area"] = round(area, 3)
            f["measured"] = True
        kept.append(f)
    vis = kept
    exp = exposed_of(zg, boxes, vis)
    show = vis if args.all else exp

    print(f"project  {proj}")
    print(f"scene    {scene}")
    print(f"solids   {len(boxes)}  ({len(rot)} rotated, AABB approximated)")
    print(f"fights   {len(vis)} visible, {len(exp)} exposed, "
          f"{len(buried)} entombed")
    if phantom:
        print(f"         {phantom} dropped: true footprint overlap below "
              f"AREA_MIN once measured\n         rather than approximated from "
              f"the bounding box\n")
    else:
        print()

    show = sorted(show, key=lambda f: -f["area"])
    for f in show[:args.top]:
        # `=` means the area is the true footprint intersection, not an AABB
        # estimate, so a rotated box is no longer a caveat on that finding.
        mark = ("  " if f.get("measured") or not (f["a"] in rot or f["b"] in rot)
                else " ~")
        print(f"{mark}{f['area']:>8.2f} m^2  {AXIS[f['axis']]} {f['side']:<3} "
              f"@ {f['plane']:<9} {f['a']}  <->  {f['b']}")
    if len(show) > args.top:
        print(f"  ... {len(show) - args.top} more")

    pair = {}
    for f in exp:
        ka = f["a"].split(":", 1)[0]
        kb = f["b"].split(":", 1)[0]
        pair[tuple(sorted((ka, kb)))] = pair.get(tuple(sorted((ka, kb))), 0) + 1
    if pair:
        print("\nexposed by source pair:")
        for k in sorted(pair, key=lambda k: -pair[k]):
            print(f"  {pair[k]:>5}  {k[0]}  <->  {k[1]}")
    n_marked = sum(1 for f in show if (f["a"] in rot or f["b"] in rot)
                   and not f.get("measured"))
    print(f"\n  ~ marks a pair where EITHER box is rotated. Those overlaps are "
          f"computed\n  from an inflated AABB and may not exist -- read them as "
          f"leads, not facts.\n  {n_marked} of {len(show)} shown are marked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
