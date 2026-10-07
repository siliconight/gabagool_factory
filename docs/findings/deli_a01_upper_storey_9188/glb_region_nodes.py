"""Every mesh node of a building GLB whose box touches a region, visual and
collision-only alike, in the BUILDING frame. Measures; names no cause.

    python glb_region_nodes.py <a.glb> [<b.glb>] --box x0 x1 y0 y1 z0 z1

Building frame: x, y as in the spec and gameplay.json, z up (metres). The
GLB is Y-up, so a GLB point (gx, gy, gz) is building (gx, -gz, gy) -- the
inverse of circulation.to_godot_aabb. Each node's own TRS is applied, as
zfight_gate._node_world_boxes applies it; a parent's transform is not.
Refuses a node with a parent that carries a transform, rather than
reporting a box in the wrong place.

With two GLBs, prints the nodes only in a, only in b, and in both with a
box that moved by more than 1 mm.
"""
import os
import sys

sys.path.insert(0, r"C:\Projects\gabagool_studios\gabagool_factory\deli_counter")
import zfight_gate  # noqa: E402
from circulation import _accessor  # noqa: E402
from pygltflib import GLTF2  # noqa: E402


def boxes(path):
    g = GLTF2().load(path)
    blob = g.binary_blob()
    parent_of = {}
    for i, nd in enumerate(g.nodes):
        for c in nd.children or []:
            parent_of[c] = i
    out = {}
    for i, nd in enumerate(g.nodes):
        if nd.mesh is None:
            continue
        p = parent_of.get(i)
        if p is not None:
            pn = g.nodes[p]
            if pn.matrix or pn.translation or pn.rotation or pn.scale:
                ident = (not pn.matrix and (pn.translation or [0, 0, 0]) == [0, 0, 0]
                         and (pn.rotation or [0, 0, 0, 1]) == [0, 0, 0, 1]
                         and (pn.scale or [1, 1, 1]) == [1, 1, 1])
                if not ident:
                    raise SystemExit("node %r has a transformed parent %r; refusing" % (nd.name, pn.name))
        m = zfight_gate._trs_matrix(nd)
        lo = [1e9] * 3
        hi = [-1e9] * 3
        for prim in g.meshes[nd.mesh].primitives:
            for q in _accessor(g, blob, prim.attributes.POSITION):
                w = zfight_gate._apply(m, q)
                b = (w[0], -w[2], w[1])          # GLB -> building frame
                for k in range(3):
                    lo[k] = min(lo[k], b[k])
                    hi[k] = max(hi[k], b[k])
        name = nd.name or ("node%d" % i)
        while name in out:
            name += "'"
        out[name] = (lo, hi)
    return out


def touches(bx, box):
    lo, hi = bx
    return all(lo[k] <= box[2 * k + 1] and hi[k] >= box[2 * k] for k in range(3))


def fmt(bx):
    lo, hi = bx
    return "x %7.2f..%7.2f  y %6.2f..%6.2f  z %5.2f..%5.2f" % (lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])


def main():
    argv = sys.argv[1:]
    i = argv.index("--box")
    box = [float(v) for v in argv[i + 1:i + 7]]
    glbs = argv[:i]
    sets = []
    for p in glbs:
        b = boxes(p)
        hit = {n: bx for n, bx in b.items() if touches(bx, box)}
        print("%s: %d mesh nodes, %d touch the box" % (os.path.basename(os.path.dirname(os.path.dirname(p))) or p, len(b), len(hit)))
        sets.append(hit)
    if len(sets) == 1:
        for n, bx in sorted(sets[0].items(), key=lambda kv: kv[1][0]):
            print("   %-48s %s" % (n[:48], fmt(bx)))
        return
    a, b = sets
    print("== only in a:")
    for n in sorted(set(a) - set(b)):
        print("   %-48s %s" % (n[:48], fmt(a[n])))
    print("== only in b:")
    for n in sorted(set(b) - set(a)):
        print("   %-48s %s" % (n[:48], fmt(b[n])))
    print("== in both, moved > 1 mm:")
    for n in sorted(set(a) & set(b)):
        d = max(abs(a[n][j][k] - b[n][j][k]) for j in (0, 1) for k in range(3))
        if d > 1e-3:
            print("   %-48s a %s\n   %-48s b %s" % (n[:48], fmt(a[n]), "", fmt(b[n])))
    print("== in both, unmoved: %d" % sum(1 for n in set(a) & set(b)
                                          if max(abs(a[n][j][k] - b[n][j][k]) for j in (0, 1) for k in range(3)) <= 1e-3))


if __name__ == "__main__":
    main()
