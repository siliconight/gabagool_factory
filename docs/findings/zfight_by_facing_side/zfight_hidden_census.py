"""zfight_gate's pairs, re-judged: is anything on the side the two faces FACE?
Measures; names no cause.

    python zfight_hidden_census.py <compose lot dir> [--list]

For each composed building package under the lot dir: zfight_gate's own raw
pairs (coplanar_fights, greybox-against-greybox excluded, as check_package
excludes them), counted three ways --
  gate      what check_package reports (visible_fights: a third solid with
            matter on BOTH sides of the plane buries a pair);
  facing    a pair is hidden when solids within GAP m of the plane, on the side
            the faces face, jointly cover the shared rectangle, in 2-D, to the
            gate's TOL (float32 seams in a tiled slab are 2.4e-7 m wide: the
            first version of this check had no tolerance and called every seam
            a hole);
  ground    as facing, and a pair facing DOWN at the package's lowest level is
            hidden too (nothing is below a building's lowest floor).
GAP is 0.05 m: a face whose outward side is shut within 5 cm cannot be seen by
any camera that fits in a level.
"""
import os
import sys
from collections import Counter

sys.path.insert(0, r"C:\Projects\gabagool_studios\gabagool_factory\deli_counter")
import zfight_gate as Z  # noqa: E402

GAP = float(__import__("os").environ.get("ZF_GAP", "0.05"))


def covered(rlo, rhi, o, cands, tol):
    xs = sorted({rlo[o[0]], rhi[o[0]]} | {c for s, h in cands for c in (s[o[0]], h[o[0]]) if rlo[o[0]] < c < rhi[o[0]]})
    ys = sorted({rlo[o[1]], rhi[o[1]]} | {c for s, h in cands for c in (s[o[1]], h[o[1]]) if rlo[o[1]] < c < rhi[o[1]]})
    for xa, xb in zip(xs, xs[1:]):
        for ya, yb in zip(ys, ys[1:]):
            mx, my = (xa + xb) / 2, (ya + yb) / 2
            if not any(s[o[0]] - tol <= mx <= h[o[0]] + tol and s[o[1]] - tol <= my <= h[o[1]] + tol
                       for s, h in cands):
                return False
    return True


def judge(solids, ground):
    raw = [f for f in Z.coplanar_fights(solids, Z.TOL, Z.AREA_MIN, Z.PEN_MIN)
           if not (f["a"].startswith("base:") and f["b"].startswith("base:"))]
    floor_y = min(b[0][1] for _n, b in solids)
    left = []
    for f in raw:
        ax, plane, rlo, rhi = f["_rect"]
        i, j = f["_ij"]
        o = [k for k in range(3) if k != ax]
        if f["side"] == "min":
            if ground and ax == 1 and plane <= floor_y + Z.TOL:
                continue
            cands = [(slo, shi) for k, (nm, (slo, shi)) in enumerate(solids)
                     if k not in (i, j) and slo[ax] <= plane - Z.OCCLUDE_MARGIN and shi[ax] >= plane - GAP]
        else:
            cands = [(slo, shi) for k, (nm, (slo, shi)) in enumerate(solids)
                     if k not in (i, j) and shi[ax] >= plane + Z.OCCLUDE_MARGIN and slo[ax] <= plane + GAP]
        if not covered(rlo, rhi, o, cands, Z.TOL):
            left.append(f)
    return raw, left


def main():
    lot = sys.argv[1]
    for b in sorted(os.listdir(lot)):
        pkg = os.path.join(lot, b)
        if not os.path.isfile(os.path.join(pkg, "site.tscn")):
            continue
        solids = []
        for f in sorted(os.listdir(pkg)):
            if f.endswith("_base.glb"):
                solids += [("base:" + nm, bx) for nm, bx in Z._node_world_boxes(os.path.join(pkg, f))]
        solids += Z._scene_module_boxes(pkg, "site.tscn")
        gate = Z.check_package(pkg)["pairs"]
        raw, facing = judge(solids, ground=False)
        _raw, both = judge(solids, ground=True)
        print("%-24s raw %3d | gate %3d | facing %3d | facing + ground %3d" % (b, len(raw), gate, len(facing), len(both)))
        if "--list" in sys.argv:
            for f in both:
                print("      %-36s ~ %-36s axis %d %s @ %.3f  %.2f m2"
                      % (f["a"][:36], f["b"][:36], f["axis"], f["side"], f["plane"], f["area"]))


if __name__ == "__main__":
    main()
