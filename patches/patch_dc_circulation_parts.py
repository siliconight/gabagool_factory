"""Deli Counter 0.191.0: the circulation gate boxes the dressing's PARTS, and
excuses a stair's own guards from its stair.

MEASURED (`docs/findings/presentation_gates/` at the factory root).
- Every cold run from 9164 to 9187 failed this gate on every building with
  covers: 9, 48, 28 and 27 conflicts on the four measured in 9187.
- Zoo merges a building's covers per side per material (1.68.0). One node
  then carries dozens of strips, and its box is the building's, about
  6.7 x 7.1 x 12 m on gs_empty_rowhome_l. Every doorway lay inside one.
- Boxed by part (position-welded, index-connected components), the same four
  read 0, and a 1 m crate planted in a doorway is caught at 0.95 m.
- In the shell arm, office's `stair_guard_back_10` stood 0.26 m inside
  `office_stair_0`. It is a fall guard a storey above its flight's foot,
  inside the "full vertical column" by design.
- The same arm's real finding stays: deli_a01's `counter_island_upper_hall_2`,
  0.8 m inside `deli_stair_up`.

    python patch_dc_circulation_parts.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CIRC = ROOT / "deli_counter" / "circulation.py"

CONST_OLD = '''DOOR_TRIM_PEN = 0.12

# facing -> outward (approach) unit vector in Blender XY, same convention as
'''
CONST_NEW = '''DOOR_TRIM_PEN = 0.12

#: `deli_counter.py` `_stair_guards` names each guard volume
#: ``stair_guard_{kind}_{k}``, and every volume is role ``prop``. A guard
#: stands at its own stair's hole edge by design -- a back guard a storey
#: above its flight's foot, inside the full column -- so it is EXCUSED from
#: stair volumes and listed as such (0.191.0). In a doorway or a ladder's
#: climb volume it is a prop like any other. Not linked to its own stair: a
#: guard of one stair inside another's column would be excused too.
GUARD_PREFIX = "stair_guard_"

#: Two vertices this close are one corner (metres, GLB space). A box's faces
#: carry their own vertices for split normals and UVs, and are one part.
WELD_M = 1e-4

# facing -> outward (approach) unit vector in Blender XY, same convention as
'''

SHELL_OLD = '''    props = shell_prop_boxes(shell_glb, gameplay)
    vols = circulation_volumes(slots_manifest, gameplay)
    conflicts = prop_conflicts(props, vols)
    roles = (gameplay or {}).get("surface_roles") or {}
    declared = sum(1 for r in roles.values() if r == "prop")
    blind = declared > 0 and not props
    out = {"ok": (not conflicts) and not blind,
           "volumes": len(vols), "props": len(props),
           "declared_props": declared, "conflicts": conflicts[:50]}
'''
SHELL_NEW = '''    props = shell_prop_boxes(shell_glb, gameplay)
    vols = circulation_volumes(slots_manifest, gameplay)
    found = prop_conflicts(props, vols)
    # A stair's guard at its own hole's edge (`GUARD_PREFIX`): excused from
    # stair volumes, and returned, so a reader sees what was not counted.
    excused = [c for c in found if c["prop"].startswith(GUARD_PREFIX)
               and c["volume"].startswith("stair:")]
    conflicts = [c for c in found if c not in excused]
    roles = (gameplay or {}).get("surface_roles") or {}
    declared = sum(1 for r in roles.values() if r == "prop")
    blind = declared > 0 and not props
    out = {"ok": (not conflicts) and not blind,
           "volumes": len(vols), "props": len(props),
           "declared_props": declared, "conflicts": conflicts[:50],
           "excused": excused[:50]}
'''

DRESS_OLD = '''def check_dressing(dressing_glb, slots_manifest, gameplay):
    """Package-level gate: does a dressing GLB keep circulation clear?

    Returns {ok, volumes, props, conflicts:[{prop, volume, penetration}]}.
    Needs pygltflib (same dep the placement/z-fight gates already use).
    """
    import zfight_gate
    props = zfight_gate._node_world_boxes(dressing_glb)
    vols = circulation_volumes(slots_manifest, gameplay)
    conflicts = prop_conflicts(props, vols)
    return {"ok": not conflicts, "volumes": len(vols), "props": len(props),
            "conflicts": conflicts[:50]}
'''
DRESS_NEW = '''_GLTF_FMT = {5120: "b", 5121: "B", 5122: "h", 5123: "H", 5125: "I", 5126: "f"}
_GLTF_N = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def _accessor(g, blob, i):
    """An accessor's elements: tuples for vectors, numbers for scalars."""
    import struct
    acc = g.accessors[i]
    bv = g.bufferViews[acc.bufferView]
    n = _GLTF_N[acc.type]
    fmt = _GLTF_FMT[acc.componentType]
    stride = bv.byteStride or struct.calcsize(fmt) * n
    base = (bv.byteOffset or 0) + (acc.byteOffset or 0)
    out = []
    for k in range(acc.count):
        v = struct.unpack_from("<" + fmt * n, blob, base + k * stride)
        out.append(v if n > 1 else v[0])
    return out


def dressing_part_boxes(glb_path):
    """[(node#k, (lo, hi))] in GLB/Godot space: each meshed visual node split
    into its PARTS, the position-welded, index-connected pieces of its mesh.

    WHY PARTS (0.191.0). Zoo merges a building's covers per side per material
    (1.68.0), so one node carries dozens of strips and its box is the
    building's. Every doorway lay inside one, and every building with covers
    failed this gate on every cold run from 9164 to 9187. A part is a strip,
    which is what `DOOR_TRIM_PEN` was written against.

    WELDED FIRST. Faces carry their own vertices for split normals and UVs,
    so index connectivity alone returns one component per face: a plane of
    zero thickness, which `_pen` can never flag. Measured on 9187's
    gs_empty_rowhome_l: 1,452 planes unwelded, 196 parts welded.

    The node's own TRS is applied, as `zfight_gate._node_world_boxes` applies
    it; a parent's transform is not, there as here.
    """
    import zfight_gate
    from pygltflib import GLTF2
    g = GLTF2().load(glb_path)
    blob = g.binary_blob()
    out = []
    for nd in g.nodes:
        if nd.mesh is None or "colonly" in (nd.name or "").lower():
            continue
        m = zfight_gate._trs_matrix(nd)
        k = 0
        for prim in g.meshes[nd.mesh].primitives:
            pos = _accessor(g, blob, prim.attributes.POSITION)
            idx = (_accessor(g, blob, prim.indices) if prim.indices is not None
                   else list(range(len(pos))))
            weld, ids = {}, []
            for q in pos:
                ids.append(weld.setdefault(
                    tuple(round(c / WELD_M) for c in q), len(weld)))
            parent = list(range(len(weld)))

            def find(a):
                while parent[a] != a:
                    parent[a] = parent[parent[a]]
                    a = parent[a]
                return a

            for t in range(0, len(idx) - 2, 3):
                a = find(ids[idx[t]])
                parent[find(ids[idx[t + 1]])] = a
                parent[find(ids[idx[t + 2]])] = a
            groups = {}
            for v, w in enumerate(ids):
                groups.setdefault(find(w), []).append(v)
            for verts in groups.values():
                pts = [zfight_gate._apply(m, pos[v]) for v in verts]
                out.append(("%s#%d" % (nd.name or "node", k),
                            ([min(p[i] for p in pts) for i in range(3)],
                             [max(p[i] for p in pts) for i in range(3)])))
                k += 1
    return out


def check_dressing(dressing_glb, slots_manifest, gameplay):
    """Package-level gate: does a dressing GLB keep circulation clear?

    Returns {ok, volumes, nodes, props, conflicts:[{prop, volume,
    penetration}]}. ``props`` counts PARTS (`dressing_part_boxes`), named
    ``node#k``; ``nodes`` the meshed nodes they came from.
    Needs pygltflib (same dep the placement/z-fight gates already use).
    """
    import zfight_gate
    nodes = zfight_gate._node_world_boxes(dressing_glb)
    props = dressing_part_boxes(dressing_glb)
    vols = circulation_volumes(slots_manifest, gameplay)
    conflicts = prop_conflicts(props, vols)
    return {"ok": not conflicts, "volumes": len(vols), "nodes": len(nodes),
            "props": len(props), "conflicts": conflicts[:50]}
'''

DOC_OLD = '''    Returns ``{ok, volumes, props, declared_props, conflicts:[...]}``.
'''
DOC_NEW = '''    Returns ``{ok, volumes, props, declared_props, conflicts:[...],
    excused:[...]}``; ``excused`` is a stair's guards inside its stair.
'''

EDITS = [(CONST_OLD, CONST_NEW), (DOC_OLD, DOC_NEW), (SHELL_OLD, SHELL_NEW),
         (DRESS_OLD, DRESS_NEW)]


def main():
    data = CIRC.read_bytes()
    assert b"\r\n" not in data, "circulation.py is LF"
    text = data.decode("utf-8")
    for old, new in EDITS:
        n = text.count(old)
        assert n == 1, ("anchor matched %d times" % n, old[:70])
        text = text.replace(old, new)
    CIRC.write_bytes(text.encode("utf-8"))
    print("circulation.py: parts, and a stair's guards excused from its stair")


if __name__ == "__main__":
    main()
