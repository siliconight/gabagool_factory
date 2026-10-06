"""Split each meshed node of a dressing GLB into index-connected components
and box each one (node TRS applied, GLB/Godot frame). Then run Deli Counter's
own `circulation.prop_conflicts` with the node boxes and with the component
boxes, against the building's own circulation volumes. Measures; names no
cause.

    python cover_components.py <dressing.glb> <slots.json> <gameplay.json>
"""
import json
import struct
import sys

sys.path.insert(0, r"C:\Projects\gabagool_studios\gabagool_factory\deli_counter")
import circulation  # noqa: E402
import zfight_gate  # noqa: E402
from pygltflib import GLTF2  # noqa: E402

FMT = {5120: "b", 5121: "B", 5122: "h", 5123: "H", 5125: "I", 5126: "f"}
NCOMP = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def read_accessor(g, blob, idx):
    acc = g.accessors[idx]
    bv = g.bufferViews[acc.bufferView]
    n = NCOMP[acc.type]
    fmt = FMT[acc.componentType]
    size = struct.calcsize(fmt)
    stride = bv.byteStride or size * n
    base = (bv.byteOffset or 0) + (acc.byteOffset or 0)
    out = []
    for i in range(acc.count):
        off = base + i * stride
        vals = struct.unpack_from("<" + fmt * n, blob, off)
        out.append(vals if n > 1 else vals[0])
    return out


def components(n_verts, tris):
    parent = list(range(n_verts))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a, b, c in tris:
        ra, rb, rc = find(a), find(b), find(c)
        parent[rb] = ra
        parent[find(rc)] = ra
    groups = {}
    for v in range(n_verts):
        groups.setdefault(find(v), []).append(v)
    return list(groups.values())


def component_boxes(glb):
    g = GLTF2().load(glb)
    blob = g.binary_blob()
    out = []
    for nd in g.nodes:
        if nd.mesh is None or "colonly" in (nd.name or "").lower():
            continue
        m = zfight_gate._trs_matrix(nd)
        k = 0
        for p in g.meshes[nd.mesh].primitives:
            pos = read_accessor(g, blob, p.attributes.POSITION)
            idx = read_accessor(g, blob, p.indices) if p.indices is not None else list(range(len(pos)))
            # WELD BY POSITION FIRST. Faces carry their own vertices (split
            # normals and UVs), so index connectivity alone returns one plane
            # per face -- zero thickness, which `_pen` can never flag.
            weld, ids = {}, []
            for q in pos:
                key = tuple(round(c, 4) for c in q)
                ids.append(weld.setdefault(key, len(weld)))
            tris = [(ids[idx[i]], ids[idx[i + 1]], ids[idx[i + 2]])
                    for i in range(0, len(idx) - 2, 3)]
            first = {}
            for v, w in enumerate(ids):
                first.setdefault(w, v)
            for comp in components(len(weld), tris):
                comp = [first[w] for w in comp]
                pts = [zfight_gate._apply(m, pos[v]) for v in comp]
                lo = [min(q[i] for q in pts) for i in range(3)]
                hi = [max(q[i] for q in pts) for i in range(3)]
                out.append(("%s#%d" % (nd.name, k), (lo, hi)))
                k += 1
    return out


def main():
    glb, slots_p, gp_p = sys.argv[1:4]
    slots = json.load(open(slots_p, encoding="utf-8"))
    gp = json.load(open(gp_p, encoding="utf-8"))
    vols = circulation.circulation_volumes(slots, gp)
    nodes = zfight_gate._node_world_boxes(glb)
    comps = component_boxes(glb)
    by_node = {}
    for name, _ in comps:
        by_node[name.split("#")[0]] = by_node.get(name.split("#")[0], 0) + 1
    print("volumes %d | nodes %d | components %d" % (len(vols), len(nodes), len(comps)))
    print("components per node:", by_node)
    cn = circulation.prop_conflicts(nodes, vols)
    cc = circulation.prop_conflicts(comps, vols)
    print("conflicts with node boxes: %d" % len(cn))
    print("conflicts with component boxes: %d" % len(cc))
    for c in sorted(cc, key=lambda c: -c["penetration"])[:12]:
        lo, hi = dict(comps)[c["prop"]]
        print("   %-44s %-28s pen %.3f  size %s" % (
            c["prop"], c["volume"], c["penetration"],
            [round(hi[i] - lo[i], 2) for i in range(3)]))


if __name__ == "__main__":
    main()
